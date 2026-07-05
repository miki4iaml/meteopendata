"""Tests for _cli.py — IFSSurfaceDownloader is fully mocked."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import xarray as xr

from meteopendata2netcdf._cli import _build_parser, main
from meteopendata2netcdf._exceptions import DatasetBuildError, DownloadError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_RUN_DT = datetime(2026, 6, 28, 0, tzinfo=UTC)


def _make_fake_result(with_dataset: bool = True) -> MagicMock:
    """Return a mock DownloadResult."""
    result = MagicMock()
    result.grib_path = Path("/tmp/ifs_surface_20260628_00z.grib2")
    result.run_datetime = FAKE_RUN_DT
    result.params = ["2t", "2d", "10u", "10v"]
    result.steps = list(range(0, 73, 6))
    if with_dataset:
        result.dataset = xr.Dataset()
    else:
        result.dataset = None
    return result


def _patch_downloader(result: MagicMock) -> MagicMock:
    """Return a mock IFSSurfaceDownloader whose download() returns *result*."""
    dl = MagicMock()
    dl.download.return_value = result
    return dl


# ---------------------------------------------------------------------------
# _build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    def test_returns_argument_parser(self) -> None:
        import argparse

        assert isinstance(_build_parser(), argparse.ArgumentParser)

    def test_default_output(self) -> None:
        args = _build_parser().parse_args([])
        assert args.output == "./ifs_output"

    def test_default_source(self) -> None:
        args = _build_parser().parse_args([])
        assert args.source == "ecmwf"

    def test_default_time_is_none(self) -> None:
        args = _build_parser().parse_args([])
        assert args.time is None

    def test_custom_output(self) -> None:
        args = _build_parser().parse_args(["--output", "/data/ifs"])
        assert args.output == "/data/ifs"

    def test_custom_source_aws(self) -> None:
        args = _build_parser().parse_args(["--source", "aws"])
        assert args.source == "aws"

    def test_time_0(self) -> None:
        args = _build_parser().parse_args(["--time", "0"])
        assert args.time == 0

    def test_time_12(self) -> None:
        args = _build_parser().parse_args(["--time", "12"])
        assert args.time == 12

    def test_no_dataset_flag(self) -> None:
        args = _build_parser().parse_args(["--no-dataset"])
        assert args.no_dataset is True

    def test_netcdf_option(self) -> None:
        args = _build_parser().parse_args(["--netcdf", "out.nc"])
        assert args.netcdf == "out.nc"

    def test_invalid_source_raises_system_exit(self) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args(["--source", "badcloud"])

    def test_invalid_time_raises_system_exit(self) -> None:
        with pytest.raises(SystemExit):
            _build_parser().parse_args(["--time", "6"])


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def _run(self, argv: list[str], result: MagicMock) -> int:
        """Helper: patch IFSSurfaceDownloader and run main(argv)."""
        mock_dl = _patch_downloader(result)
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            return main(argv)

    def test_success_returns_0(self, tmp_path: Path) -> None:
        result = _make_fake_result()
        code = self._run(["--output", str(tmp_path)], result)
        assert code == 0

    def test_no_dataset_flag_passes_false(self, tmp_path: Path) -> None:
        result = _make_fake_result(with_dataset=False)
        mock_dl = _patch_downloader(result)
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            code = main(["--output", str(tmp_path), "--no-dataset"])
        assert code == 0
        # load_dataset must be False when --no-dataset is passed
        call_kwargs = mock_dl.download.call_args
        assert call_kwargs.kwargs.get("load_dataset") is False

    def test_download_error_returns_1(self, tmp_path: Path) -> None:
        mock_dl = MagicMock()
        mock_dl.download.side_effect = DownloadError("server down")
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            code = main(["--output", str(tmp_path)])
        assert code == 1

    def test_dataset_build_error_returns_1(self, tmp_path: Path) -> None:
        mock_dl = MagicMock()
        mock_dl.download.side_effect = DatasetBuildError("cfgrib failed")
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            code = main(["--output", str(tmp_path)])
        assert code == 1

    def test_value_error_returns_1(self, tmp_path: Path) -> None:
        mock_dl = MagicMock()
        mock_dl.download.side_effect = ValueError("bad time")
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            code = main(["--output", str(tmp_path)])
        assert code == 1

    def test_netcdf_written_when_flag_given(self, tmp_path: Path) -> None:
        nc_path = tmp_path / "out.nc"
        result = _make_fake_result()
        result.to_netcdf.return_value = nc_path
        code = self._run(
            ["--output", str(tmp_path), "--netcdf", str(nc_path)],
            result,
        )
        assert code == 0
        result.to_netcdf.assert_called_once_with(str(nc_path))

    def test_load_dataset_true_when_netcdf_requested(self, tmp_path: Path) -> None:
        """--no-dataset + --netcdf: dataset must still be loaded to write NetCDF."""
        nc_path = tmp_path / "out.nc"
        result = _make_fake_result()
        result.to_netcdf.return_value = nc_path
        mock_dl = _patch_downloader(result)
        with patch("meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl):
            main(["--output", str(tmp_path), "--no-dataset", "--netcdf", str(nc_path)])
        call_kwargs = mock_dl.download.call_args
        # Even with --no-dataset, load_dataset must be True when --netcdf is given
        assert call_kwargs.kwargs.get("load_dataset") is True

    def test_source_aws_forwarded(self, tmp_path: Path) -> None:
        result = _make_fake_result()
        mock_dl = _patch_downloader(result)
        with patch(
            "meteopendata2netcdf._cli.IFSSurfaceDownloader", return_value=mock_dl
        ) as mock_cls:
            main(["--output", str(tmp_path), "--source", "aws"])
        call_kwargs = mock_cls.call_args
        assert call_kwargs.kwargs.get("source") == "aws"
