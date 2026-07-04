"""GRIB2 → xr.Dataset loading logic."""

from __future__ import annotations

import logging
from pathlib import Path

import cfgrib
import xarray as xr

from ._exceptions import DatasetBuildError

logger = logging.getLogger(__name__)


def load_surface_dataset(grib_path: Path) -> xr.Dataset:
    """Load a multi-parameter IFS surface GRIB2 file into a single xr.Dataset.

    IFS surface fields span two distinct heights:

    * ``heightAboveGround = 2 m``  → ``t2m``, ``d2m``
    * ``heightAboveGround = 10 m`` → ``u10``, ``v10``

    ``cfgrib`` groups GRIB messages by their scalar coordinate values, so fields
    at different heights cannot be merged automatically by ``xr.open_dataset()``;
    it raises a ``DatasetBuildError`` and silently drops the conflicting variables.

    This function calls ``cfgrib.open_datasets()`` instead (plural), which returns
    one coherent ``xr.Dataset`` per height group, then:

    1. Sorts each group by ``valid_time``.
    2. Stores the original height as a ``height_m`` attribute on each variable.
    3. Drops the scalar ``heightAboveGround`` coordinate (source of the conflict).
    4. Merges all groups with ``xr.merge(compat="override")``.

    Args:
        grib_path: Path to the GRIB2 file produced by :func:`retrieve_grib`.

    Returns:
        ``xr.Dataset`` containing all four surface variables (``t2m``, ``d2m``,
        ``u10``, ``v10``) along the ``valid_time`` dimension, loaded into memory.

    Raises:
        DatasetBuildError: If cfgrib returns no datasets or the merged result is empty.
    """
    logger.info("Loading dataset from %s", grib_path)

    raw_datasets: list[xr.Dataset] = cfgrib.open_datasets(
        path=str(grib_path),
        backend_kwargs={
            "filter_by_keys": {"typeOfLevel": "heightAboveGround"},
            "indexpath": "",
            "decode_timedelta": True,
        },
    )

    if not raw_datasets:
        raise DatasetBuildError(
            f"cfgrib returned no datasets for {grib_path}. "
            "The GRIB2 file may be empty or contain no heightAboveGround fields."
        )

    logger.debug(
        "%d cfgrib group(s) found: %s",
        len(raw_datasets),
        [
            {
                "vars": list(ds.data_vars),
                "height": float(ds.coords["heightAboveGround"])
                if "heightAboveGround" in ds.coords
                else None,
            }
            for ds in raw_datasets
        ],
    )

    processed: list[xr.Dataset] = []
    for ds in raw_datasets:
        height: float | None = (
            float(ds.coords["heightAboveGround"])
            if "heightAboveGround" in ds.coords
            else None
        )

        if "valid_time" in ds.coords:
            ds = ds.sortby("valid_time")

        # Annotate each variable with its original height level.
        for var in ds.data_vars:
            if height is not None:
                ds[var].attrs["height_m"] = height

        if height is not None:
            ds = ds.drop_vars("heightAboveGround")

        processed.append(ds)

    merged: xr.Dataset = xr.merge(processed, compat="override")

    if not merged.data_vars:
        raise DatasetBuildError(
            f"Merged dataset from {grib_path} is empty. "
            "Check that the GRIB2 file contains heightAboveGround fields."
        )

    merged = merged.load()
    n_steps = merged.dims.get("valid_time", merged.dims.get("step", "?"))
    logger.info("Dataset loaded: vars=%s, %s steps", list(merged.data_vars), n_steps)
    return merged
