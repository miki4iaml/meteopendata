"""Sphinx configuration for meteopendata2netcdf."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path("../../src").resolve()))

project = "meteopendata2netcdf"
author = "Your Name"
copyright = "2026, Your Name"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",       # Google / NumPy docstrings
    "sphinx.ext.viewcode",       # [source] links
    "sphinx.ext.intersphinx",    # cross-refs to Python, xarray, etc.
    "sphinx_autodoc_typehints",  # type hints in signatures
    "myst_parser",               # Markdown support
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "xarray": ("https://docs.xarray.dev/en/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = []

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
