"""Shared pytest fixtures for meteopendata2netcdf."""
from __future__ import annotations
from pathlib import Path
import pytest

@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    out = tmp_path / "ifs_output"
    out.mkdir()
    return out
