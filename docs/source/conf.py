"""Sphinx configuration for meteopendata2netcdf."""

import sys
from pathlib import Path

# Chemin vers src/ pour que autodoc trouve le package sans installation
sys.path.insert(0, str(Path("../../src").resolve()))

project = "meteopendata2netcdf"
author  = "Miki"
copyright = "2026, Miki"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",            # docstrings style Google
    "sphinx.ext.viewcode",            # liens [source]
    "sphinx.ext.intersphinx",         # cross-refs Python, xarray, numpy
    "sphinx_autodoc_typehints",       # types dans les signatures
    "myst_parser",                    # support Markdown (.md)
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "xarray": ("https://docs.xarray.dev/en/stable", None),
    "numpy":  ("https://numpy.org/doc/stable", None),
}

html_theme = "sphinx_rtd_theme"

# CORRECTION 1 : ne déclarer _static que s'il existe physiquement.
# Git n'indexe pas les dossiers vides — un dossier _static/ vide committé
# avec un .gitkeep résoudrait aussi le problème, mais conditionner ici
# est plus robuste (pas de dépendance à une convention de dépôt).
_static_path = Path(__file__).parent / "_static"
html_static_path = ["_static"] if _static_path.exists() else []

# Même logique pour _templates (précaution symétrique)
_templates_path = Path(__file__).parent / "_templates"
templates_path = ["_templates"] if _templates_path.exists() else []

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# ── autodoc ───────────────────────────────────────────────────────────
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"

# CORRECTION 2 (partielle) : éviter les descriptions dupliquées.
# autodoc génère automatiquement la doc depuis __init__.py via automodule,
# puis depuis les autoclass explicites dans api.rst.
# En activant autodoc_default_options sur __init__ ET en répétant
# les classes dans api.rst, chaque symbole est documenté deux fois.
# On désactive ici l'indexation automatique des membres de __init__
# pour laisser les autoclass de api.rst être les descriptions canoniques.
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
    "no-index": False,
}

napoleon_google_docstring = True
napoleon_numpy_docstring  = False
