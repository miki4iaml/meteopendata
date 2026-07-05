"""Tests for _exceptions.py."""

import pytest

from meteopendata2netcdf import DatasetBuildError, DownloadError


def test_download_error_is_runtime_error() -> None:
    assert issubclass(DownloadError, RuntimeError)


def test_dataset_build_error_is_runtime_error() -> None:
    assert issubclass(DatasetBuildError, RuntimeError)


def test_download_error_message() -> None:
    exc = DownloadError("server unreachable")
    assert "server unreachable" in str(exc)


def test_dataset_build_error_message() -> None:
    exc = DatasetBuildError("cfgrib returned nothing")
    assert "cfgrib returned nothing" in str(exc)


def test_download_error_can_be_raised_and_caught() -> None:
    with pytest.raises(DownloadError, match="timeout"):
        raise DownloadError("timeout")


def test_dataset_build_error_can_be_raised_and_caught() -> None:
    with pytest.raises(DatasetBuildError, match="empty"):
        raise DatasetBuildError("empty")
