"""
meteopendata2netcdf
===================
Download ECMWF IFS open-data surface forecasts and export them to NetCDF.

Quick start::

    from meteopendata2netcdf import IFSSurfaceDownloader

    dl = IFSSurfaceDownloader(output_dir="./output")
    result = dl.download()
    result.dataset.to_netcdf("ifs_surface.nc")
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("meteopendata2netcdf")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

from ._downloader import DownloadResult, IFSSurfaceDownloader
from ._exceptions import DatasetBuildError, DownloadError

__all__ = [
    "__version__",
    "IFSSurfaceDownloader",
    "DownloadResult",
    "DownloadError",
    "DatasetBuildError",
]
