"""Custom exceptions for meteopendata2netcdf."""


class DownloadError(RuntimeError):
    """Raised when the ECMWF open-data download fails."""


class DatasetBuildError(RuntimeError):
    """Raised when cfgrib cannot build a coherent xr.Dataset from the GRIB2 file."""
