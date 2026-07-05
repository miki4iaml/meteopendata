"""Tests for _grib.py — cfgrib is mocked, no GRIB2 files needed."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest
import xarray as xr

from meteopendata2netcdf._exceptions import DatasetBuildError
from meteopendata2netcdf._grib import load_surface_dataset

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ds_at_height(height: float, varname: str) -> xr.Dataset:
    """Return a minimal Dataset mimicking cfgrib output at a given height.

    Uses ``np.datetime64`` so the dataset can be round-tripped through
    ``to_netcdf()`` without a ``ValueError`` on the time coordinate.
    """
    data = np.ones((2, 3, 3), dtype=np.float32)
    times = np.array(["2026-06-28T00:00:00", "2026-06-28T06:00:00"], dtype="datetime64[ns]")
    ds = xr.Dataset(
        {varname: (["valid_time", "latitude", "longitude"], data)},
        coords={
            "valid_time": times,
            "latitude": [0.0, 1.0, 2.0],
            "longitude": [0.0, 1.0, 2.0],
            "heightAboveGround": height,
        },
    )
    return ds


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestLoadSurfaceDataset:
    def test_empty_cfgrib_output_raises(self, tmp_path: Path) -> None:
        """cfgrib returning [] must raise DatasetBuildError."""
        grib = tmp_path / "empty.grib2"
        grib.write_bytes(b"")
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[]):
            with pytest.raises(DatasetBuildError, match="no datasets"):
                load_surface_dataset(grib)

    def test_single_group_loaded(self, tmp_path: Path) -> None:
        """A single-group GRIB (e.g. only 10m wind) loads without error."""
        grib = tmp_path / "wind.grib2"
        grib.write_bytes(b"")
        ds_10m = _ds_at_height(10.0, "u10")
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[ds_10m]):
            result = load_surface_dataset(grib)
        assert "u10" in result.data_vars
        assert "heightAboveGround" not in result.coords

    def test_two_groups_merged(self, tmp_path: Path) -> None:
        """The standard case: 2m group + 10m group are merged into one Dataset."""
        grib = tmp_path / "surface.grib2"
        grib.write_bytes(b"")
        ds_2m = _ds_at_height(2.0, "t2m")
        ds_10m = _ds_at_height(10.0, "u10")
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[ds_2m, ds_10m]):
            result = load_surface_dataset(grib)
        assert "t2m" in result.data_vars
        assert "u10" in result.data_vars
        assert "heightAboveGround" not in result.coords

    def test_height_stored_as_attribute(self, tmp_path: Path) -> None:
        """Each variable must carry its original height in attrs['height_m']."""
        grib = tmp_path / "surface.grib2"
        grib.write_bytes(b"")
        ds_2m = _ds_at_height(2.0, "t2m")
        ds_10m = _ds_at_height(10.0, "u10")
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[ds_2m, ds_10m]):
            result = load_surface_dataset(grib)
        assert result["t2m"].attrs["height_m"] == 2.0
        assert result["u10"].attrs["height_m"] == 10.0

    def test_valid_time_sorted(self, tmp_path: Path) -> None:
        """valid_time dimension must be in ascending order after loading."""
        grib = tmp_path / "surface.grib2"
        grib.write_bytes(b"")
        # Deliberately reversed order — use np.datetime64 for NetCDF compatibility
        times_reversed = np.array(
            ["2026-06-28T06:00:00", "2026-06-28T00:00:00"], dtype="datetime64[ns]"
        )
        ds = xr.Dataset(
            {
                "t2m": (
                    ["valid_time", "latitude", "longitude"],
                    np.ones((2, 2, 2), dtype=np.float32),
                )
            },
            coords={
                "valid_time": times_reversed,
                "latitude": [0.0, 1.0],
                "longitude": [0.0, 1.0],
                "heightAboveGround": 2.0,
            },
        )
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[ds]):
            result = load_surface_dataset(grib)
        times = result["valid_time"].values
        assert times[0] < times[1], "valid_time must be sorted ascending"

    def test_dataset_without_height_coord(self, tmp_path: Path) -> None:
        """Groups without heightAboveGround coord are handled without error."""
        grib = tmp_path / "no_height.grib2"
        grib.write_bytes(b"")
        ds = xr.Dataset(
            {"msl": (["latitude", "longitude"], np.ones((2, 2), dtype=np.float32))},
            coords={"latitude": [0.0, 1.0], "longitude": [0.0, 1.0]},
        )
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[ds]):
            result = load_surface_dataset(grib)
        assert "msl" in result.data_vars

    def test_merged_empty_raises(self, tmp_path: Path) -> None:
        """If after merge data_vars is empty, DatasetBuildError must be raised."""
        grib = tmp_path / "ghost.grib2"
        grib.write_bytes(b"")
        empty_ds = xr.Dataset()  # no variables at all
        with patch("meteopendata2netcdf._grib.cfgrib.open_datasets", return_value=[empty_ds]):
            with pytest.raises(DatasetBuildError, match="empty"):
                load_surface_dataset(grib)
