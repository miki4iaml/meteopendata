"""Placeholder tests — replace with real tests in a future PR."""
import meteopendata2netcdf

def test_version_is_string() -> None:
    assert isinstance(meteopendata2netcdf.__version__, str)
    assert len(meteopendata2netcdf.__version__) > 0

def test_public_api() -> None:
    """All symbols declared in __all__ must be importable."""
    for name in meteopendata2netcdf.__all__:
        assert hasattr(meteopendata2netcdf, name), f"Missing from public API: {name}"
