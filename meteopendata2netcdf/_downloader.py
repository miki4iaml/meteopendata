"""Core downloader: ECMWF IFS open-data → GRIB2 + xr.Dataset."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

import xarray as xr
from ecmwf.opendata import Client

from ._constants import (
    DEFAULT_STEPS,
    FORECAST_TYPE,
    MODEL,
    RESOLUTION,
    STREAM,
    SURFACE_PARAMS,
    VALID_RUN_HOURS,
)
from ._exceptions import DownloadError
from ._grib import load_surface_dataset

logger = logging.getLogger(__name__)

Source = Literal["ecmwf", "aws", "azure", "google"]


@dataclass
class DownloadResult:
    """Result of a successful IFS surface download.

    Attributes:
        grib_path:    Path to the consolidated GRIB2 file on disk.
        run_datetime: UTC datetime of the downloaded IFS run.
        params:       ECMWF parameter short-names that were requested.
        steps:        Forecast lead times (hours) that were requested.
        dataset:      In-memory ``xr.Dataset`` (``None`` when *load_dataset* is
                      ``False``).
    """

    grib_path: Path
    run_datetime: datetime
    params: list[str] = field(default_factory=list)
    steps: list[int] = field(default_factory=list)
    dataset: xr.Dataset | None = None

    def __repr__(self) -> str:
        ds_info = (
            f"Dataset(vars={list(self.dataset.data_vars)})"
            if self.dataset is not None
            else "None"
        )
        return (
            f"DownloadResult(\n"
            f"  run_datetime = {self.run_datetime.isoformat()}\n"
            f"  grib_path    = {self.grib_path}\n"
            f"  params       = {self.params}\n"
            f"  steps        = {self.steps}\n"
            f"  dataset      = {ds_info}\n"
            f")"
        )

    def to_netcdf(self, path: str | Path, **kwargs: object) -> Path:
        """Write the in-memory dataset to a NetCDF file.

        Args:
            path:   Destination file path (``*.nc``).
            **kwargs: Extra keyword arguments forwarded to ``xr.Dataset.to_netcdf()``.

        Returns:
            Resolved ``Path`` of the written file.

        Raises:
            RuntimeError: If *dataset* is ``None`` (download was called with
                ``load_dataset=False``).
        """
        if self.dataset is None:
            raise RuntimeError(
                "Cannot export to NetCDF: dataset is None. "
                "Re-run download() with load_dataset=True."
            )
        out = Path(path).resolve()
        self.dataset.to_netcdf(out, **kwargs)  # type: ignore[arg-type]
        logger.info("Dataset written to %s", out)
        return out


class IFSSurfaceDownloader:
    """Download IFS surface forecasts (temperature, wind, humidity) via ecmwf-opendata.

    Uses the HTTP Byte-Range mechanism provided by ecmwf-opendata: only the bytes
    corresponding to the requested parameters and steps are transferred per file,
    not the full GRIB2.

    Args:
        output_dir: Directory where GRIB2 files are saved. Created if absent.
        source:     Data source: ``"ecmwf"`` (default), ``"aws"``, ``"azure"``,
                    or ``"google"``.
        params:     ECMWF parameter short-names to download.
                    Defaults to :data:`~._constants.SURFACE_PARAMS`.
        steps:      Forecast lead times in hours.
                    Defaults to :data:`~._constants.DEFAULT_STEPS` (0–72 h, step 6 h).

    Example::

        dl = IFSSurfaceDownloader(output_dir="./ifs_output", source="aws")
        result = dl.download(time=0)
        result.to_netcdf("ifs_surface.nc")
    """

    def __init__(
        self,
        output_dir: str | Path = "./ifs_output",
        source: Source = "ecmwf",
        params: list[str] | None = None,
        steps: list[int] | None = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.source: Source = source
        self.params: list[str] = params if params is not None else list(SURFACE_PARAMS)
        self.steps: list[int] = steps if steps is not None else list(DEFAULT_STEPS)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._client = Client(
            source=self.source,
            model=MODEL,
            resol=RESOLUTION,
            infer_stream_keyword=True,
        )
        logger.info(
            "IFSSurfaceDownloader ready | source=%s params=%s steps=%s",
            self.source,
            self.params,
            self.steps,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_latest_run_time(self, time: int | None = None) -> datetime:
        """Return the UTC datetime of the most recent available IFS run.

        Args:
            time: Target run hour (must be 0 or 12). When ``None`` the most
                  recent run is detected automatically.

        Returns:
            UTC ``datetime`` of the available run.

        Raises:
            ValueError:   If *time* is not 0 or 12.
            DownloadError: If the server cannot be reached or returns no result.
        """
        if time is not None:
            _validate_run_hour(time)

        request: dict[str, object] = {
            "type": FORECAST_TYPE,
            "stream": STREAM,
            "param": self.params[0],
            "step": self.steps[0],
        }
        if time is not None:
            request["time"] = time

        try:
            run_dt: datetime = self._client.latest(**request)
        except Exception as exc:
            raise DownloadError(
                f"Cannot determine the latest IFS run (source={self.source}): {exc}"
            ) from exc

        logger.info("Latest available IFS run: %s", run_dt.isoformat())
        return run_dt

    def download(
        self,
        time: int | None = None,
        load_dataset: bool = True,
    ) -> DownloadResult:
        """Download IFS surface fields and return a :class:`DownloadResult`.

        Args:
            time:         Target run hour (0 or 12). ``None`` → latest available.
            load_dataset: When ``True`` (default), load the GRIB2 into an
                          ``xr.Dataset`` and attach it to the result.

        Returns:
            :class:`DownloadResult` with *grib_path*, *run_datetime*, *params*,
            *steps*, and optionally *dataset*.

        Raises:
            ValueError:   If *time* is not 0 or 12.
            DownloadError: If the download fails.
        """
        if time is not None:
            _validate_run_hour(time)

        run_dt = self.get_latest_run_time(time=time)
        grib_path = self._build_output_path(run_dt)

        logger.info(
            "Starting download | run=%s params=%s steps=%s → %s",
            run_dt.isoformat(),
            self.params,
            self.steps,
            grib_path,
        )

        self._retrieve(run_dt=run_dt, target=grib_path)

        dataset: xr.Dataset | None = None
        if load_dataset:
            dataset = load_surface_dataset(grib_path)

        result = DownloadResult(
            grib_path=grib_path,
            run_datetime=run_dt,
            params=list(self.params),
            steps=list(self.steps),
            dataset=dataset,
        )
        logger.info("Download complete: %s", result)
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _retrieve(self, run_dt: datetime, target: Path) -> None:
        """Issue the ecmwf-opendata Byte-Range request and write the GRIB2 file.

        Args:
            run_dt: UTC datetime of the run to fetch.
            target: Destination GRIB2 file path (overwritten if present).

        Raises:
            DownloadError: If the request fails for any reason.
        """
        request: dict[str, object] = {
            "date": run_dt.strftime("%Y%m%d"),
            "time": run_dt.hour,
            "type": FORECAST_TYPE,
            "stream": STREAM,
            "param": self.params,
            "step": self.steps,
        }
        logger.debug("ecmwf-opendata request: %s", request)

        try:
            self._client.retrieve(request=request, target=str(target))
            logger.info("GRIB2 written: %s", target)
        except Exception as exc:
            if target.exists():
                target.unlink()
                logger.warning("Partial file removed: %s", target)
            raise DownloadError(
                f"Download failed for run={run_dt.isoformat()} "
                f"params={self.params} steps={self.steps}: {exc}"
            ) from exc

    def _build_output_path(self, run_dt: datetime) -> Path:
        """Build the output GRIB2 file path for *run_dt*.

        Format: ``{output_dir}/ifs_surface_{YYYYMMDD}_{HH}z.grib2``
        """
        filename = f"ifs_surface_{run_dt:%Y%m%d}_{run_dt:%H}z.grib2"
        return self.output_dir / filename


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_run_hour(time: int) -> None:
    """Raise ``ValueError`` if *time* is not a valid IFS HRES oper run hour.

    Args:
        time: Run hour to validate.

    Raises:
        ValueError: If *time* is not in :data:`~._constants.VALID_RUN_HOURS`.
    """
    if time not in VALID_RUN_HOURS:
        raise ValueError(
            f"IFS HRES oper run hour must be one of {sorted(VALID_RUN_HOURS)}, got {time!r}."
        )
