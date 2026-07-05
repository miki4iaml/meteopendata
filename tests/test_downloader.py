"""Tests for _downloader.py — all network calls are mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import xarray as xr

from meteopendata2netcdf import DownloadError, DownloadResult
from meteopendata2netcdf._constants import DEFAULT_STEPS, SURFACE_PARAMS
from meteopendata2netcdf._downloader import IFSSurfaceDownloader, _validate_run_hour

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_RUN_DT = datetime(2026, 6, 28, 0, tzinfo=UTC)


def _make_fake_dataset() -> xr.Dataset:
    """Return a minimal xr.Dataset mimicking IFS surface output.

    Uses ``np.datetime64`` for the ``valid_time`` coordinate so that
    ``xr.Dataset.to_netcdf()`` can serialise it without error.
    timezone-aware Python ``datetime`` objects are not directly supported
    by xarray's NetCDF backend and would raise a ``ValueError``.
    """
    # np.datetime64 is the correct dtype for xarray time coordinates
    times = np.array(["2026-06-28T00:00:00"], dtype="datetime64[ns]")
    lats = np.array([0.0, 1.0])
    lons = np.array([0.0, 1.0])
    data = np.ones((len(times), len(lats), len(lons)), dtype=np.float32)
    return xr.Dataset(
        {
            "t2m": (["valid_time", "latitude", "longitude"], data),
            "d2m": (["valid_time", "latitude", "longitude"], data),
            "u10": (["valid_time", "latitude", "longitude"], data),
            "v10": (["valid_time", "latitude", "longitude"], data),
        },
        coords={
            "valid_time": times,
            "latitude": lats,
            "longitude": lons,
        },
    )


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock ecmwf.opendata.Client: latest() and retrieve() do nothing."""
    client = MagicMock()
    client.latest.return_value = FAKE_RUN_DT
    client.retrieve.return_value = MagicMock()
    return client


@pytest.fixture
def downloader(tmp_output: Path, mock_client: MagicMock) -> IFSSurfaceDownloader:
    """IFSSurfaceDownloader with a mocked ecmwf Client."""
    with patch("meteopendata2netcdf._downloader.Client", return_value=mock_client):
        dl = IFSSurfaceDownloader(output_dir=tmp_output)
    dl._client = mock_client
    return dl


# ---------------------------------------------------------------------------
# _validate_run_hour
# ---------------------------------------------------------------------------


class TestValidateRunHour:
    def test_valid_hours_pass(self) -> None:
        _validate_run_hour(0)
        _validate_run_hour(12)

    def test_invalid_hour_raises(self) -> None:
        with pytest.raises(ValueError, match="must be one of"):
            _validate_run_hour(6)

    def test_invalid_hour_18_raises(self) -> None:
        with pytest.raises(ValueError, match="got 18"):
            _validate_run_hour(18)

    def test_invalid_hour_message_contains_value(self) -> None:
        with pytest.raises(ValueError, match="99"):
            _validate_run_hour(99)


# ---------------------------------------------------------------------------
# IFSSurfaceDownloader.__init__
# ---------------------------------------------------------------------------


class TestIFSSurfaceDownloaderInit:
    def test_default_params(self, downloader: IFSSurfaceDownloader) -> None:
        assert downloader.params == list(SURFACE_PARAMS)

    def test_default_steps(self, downloader: IFSSurfaceDownloader) -> None:
        assert downloader.steps == list(DEFAULT_STEPS)

    def test_custom_params(self, tmp_output: Path, mock_client: MagicMock) -> None:
        with patch("meteopendata2netcdf._downloader.Client", return_value=mock_client):
            dl = IFSSurfaceDownloader(output_dir=tmp_output, params=["2t"])
        dl._client = mock_client
        assert dl.params == ["2t"]

    def test_custom_steps(self, tmp_output: Path, mock_client: MagicMock) -> None:
        with patch("meteopendata2netcdf._downloader.Client", return_value=mock_client):
            dl = IFSSurfaceDownloader(output_dir=tmp_output, steps=[0, 6])
        dl._client = mock_client
        assert dl.steps == [0, 6]

    def test_output_dir_created(self, tmp_path: Path, mock_client: MagicMock) -> None:
        new_dir = tmp_path / "new" / "nested"
        assert not new_dir.exists()
        with patch("meteopendata2netcdf._downloader.Client", return_value=mock_client):
            IFSSurfaceDownloader(output_dir=new_dir)
        assert new_dir.exists()

    def test_source_stored(self, tmp_output: Path, mock_client: MagicMock) -> None:
        with patch("meteopendata2netcdf._downloader.Client", return_value=mock_client):
            dl = IFSSurfaceDownloader(output_dir=tmp_output, source="aws")
        assert dl.source == "aws"


# ---------------------------------------------------------------------------
# IFSSurfaceDownloader.get_latest_run_time
# ---------------------------------------------------------------------------


class TestGetLatestRunTime:
    def test_returns_datetime(self, downloader: IFSSurfaceDownloader) -> None:
        result = downloader.get_latest_run_time()
        assert isinstance(result, datetime)
        assert result == FAKE_RUN_DT

    def test_with_explicit_time_0(self, downloader: IFSSurfaceDownloader) -> None:
        result = downloader.get_latest_run_time(time=0)
        assert isinstance(result, datetime)

    def test_with_explicit_time_12(self, downloader: IFSSurfaceDownloader) -> None:
        result = downloader.get_latest_run_time(time=12)
        assert isinstance(result, datetime)

    def test_invalid_time_raises(self, downloader: IFSSurfaceDownloader) -> None:
        with pytest.raises(ValueError, match="must be one of"):
            downloader.get_latest_run_time(time=6)

    def test_client_error_raises_download_error(self, downloader: IFSSurfaceDownloader) -> None:
        downloader._client.latest.side_effect = ConnectionError("unreachable")
        with pytest.raises(DownloadError, match="Cannot determine"):
            downloader.get_latest_run_time()


# ---------------------------------------------------------------------------
# IFSSurfaceDownloader._build_output_path
# ---------------------------------------------------------------------------


class TestBuildOutputPath:
    def test_filename_format(self, downloader: IFSSurfaceDownloader) -> None:
        path = downloader._build_output_path(FAKE_RUN_DT)
        assert path.name == "ifs_surface_20260628_00z.grib2"

    def test_path_inside_output_dir(self, downloader: IFSSurfaceDownloader) -> None:
        path = downloader._build_output_path(FAKE_RUN_DT)
        assert path.parent == downloader.output_dir

    def test_run_12z(self, downloader: IFSSurfaceDownloader) -> None:
        dt_12z = datetime(2026, 6, 28, 12, tzinfo=UTC)
        path = downloader._build_output_path(dt_12z)
        assert path.name == "ifs_surface_20260628_12z.grib2"


# ---------------------------------------------------------------------------
# IFSSurfaceDownloader._retrieve
# ---------------------------------------------------------------------------


class TestRetrieve:
    def test_calls_client_retrieve(
        self, downloader: IFSSurfaceDownloader, tmp_output: Path
    ) -> None:
        target = tmp_output / "test.grib2"
        downloader._retrieve(run_dt=FAKE_RUN_DT, target=target)
        downloader._client.retrieve.assert_called_once()

    def test_retrieve_failure_raises_download_error(
        self, downloader: IFSSurfaceDownloader, tmp_output: Path
    ) -> None:
        downloader._client.retrieve.side_effect = OSError("disk full")
        target = tmp_output / "test.grib2"
        with pytest.raises(DownloadError, match="Download failed"):
            downloader._retrieve(run_dt=FAKE_RUN_DT, target=target)

    def test_partial_file_removed_on_failure(
        self, downloader: IFSSurfaceDownloader, tmp_output: Path
    ) -> None:
        target = tmp_output / "partial.grib2"
        target.write_bytes(b"partial content")  # simulate partial download
        downloader._client.retrieve.side_effect = OSError("network error")
        with pytest.raises(DownloadError):
            downloader._retrieve(run_dt=FAKE_RUN_DT, target=target)
        # Partial file must be cleaned up
        assert not target.exists()


# ---------------------------------------------------------------------------
# IFSSurfaceDownloader.download
# ---------------------------------------------------------------------------


class TestDownload:
    def test_download_without_dataset(self, downloader: IFSSurfaceDownloader) -> None:
        with patch("meteopendata2netcdf._downloader.load_surface_dataset") as mock_load:
            result = downloader.download(load_dataset=False)
        mock_load.assert_not_called()
        assert result.dataset is None
        assert isinstance(result.grib_path, Path)

    def test_download_with_dataset(self, downloader: IFSSurfaceDownloader) -> None:
        fake_ds = _make_fake_dataset()
        with patch(
            "meteopendata2netcdf._downloader.load_surface_dataset",
            return_value=fake_ds,
        ):
            result = downloader.download(load_dataset=True)
        assert result.dataset is fake_ds

    def test_download_invalid_time_raises(self, downloader: IFSSurfaceDownloader) -> None:
        with pytest.raises(ValueError, match="must be one of"):
            downloader.download(time=3)

    def test_download_result_metadata(self, downloader: IFSSurfaceDownloader) -> None:
        with patch(
            "meteopendata2netcdf._downloader.load_surface_dataset",
            return_value=_make_fake_dataset(),
        ):
            result = downloader.download()
        assert result.run_datetime == FAKE_RUN_DT
        assert result.params == list(SURFACE_PARAMS)
        assert result.steps == list(DEFAULT_STEPS)


# ---------------------------------------------------------------------------
# DownloadResult
# ---------------------------------------------------------------------------


class TestDownloadResult:
    def _make_result(self, dataset: xr.Dataset | None = None) -> DownloadResult:
        return DownloadResult(
            grib_path=Path("/tmp/test.grib2"),
            run_datetime=FAKE_RUN_DT,
            params=["2t", "10u"],
            steps=[0, 6, 12],
            dataset=dataset,
        )

    def test_repr_without_dataset(self) -> None:
        r = self._make_result()
        text = repr(r)
        assert "None" in text
        assert "2026-06-28" in text

    def test_repr_with_dataset(self) -> None:
        r = self._make_result(dataset=_make_fake_dataset())
        text = repr(r)
        assert "Dataset" in text
        assert "t2m" in text

    def test_to_netcdf_raises_without_dataset(self, tmp_path: Path) -> None:
        r = self._make_result()
        with pytest.raises(RuntimeError, match="dataset is None"):
            r.to_netcdf(tmp_path / "out.nc")

    def test_to_netcdf_writes_file(self, tmp_path: Path) -> None:
        r = self._make_result(dataset=_make_fake_dataset())
        out = tmp_path / "out.nc"
        returned_path = r.to_netcdf(out)
        assert returned_path.exists()
        assert returned_path.suffix == ".nc"

    def test_to_netcdf_returns_resolved_path(self, tmp_path: Path) -> None:
        r = self._make_result(dataset=_make_fake_dataset())
        out = tmp_path / "out.nc"
        returned = r.to_netcdf(out)
        assert returned == out.resolve()
