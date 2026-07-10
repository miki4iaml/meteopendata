meteopendata2netcdf
===================

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   vision
   installation
   quickstart
   sources/index
   design
   contributing
   changelog

|ci| |coverage| |pypi| |python| |docs| |license|

.. |ci| image:: https://github.com/miki4iaml/meteopendata/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/miki4iaml/meteopendata/actions/workflows/ci.yml
   :alt: CI

.. |coverage| image:: https://codecov.io/gh/miki4iaml/meteopendata/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/miki4iaml/meteopendata
   :alt: Coverage

.. |pypi| image:: https://img.shields.io/pypi/v/meteopendata2netcdf
   :target: https://pypi.org/project/meteopendata2netcdf
   :alt: PyPI

.. |python| image:: https://img.shields.io/pypi/pyversions/meteopendata2netcdf
   :target: https://pypi.org/project/meteopendata2netcdf
   :alt: Python versions

.. |docs| image:: https://readthedocs.org/projects/meteopendata2netcdf/badge/?version=latest
   :target: https://meteopendata2netcdf.readthedocs.io
   :alt: Documentation

.. |license| image:: https://img.shields.io/badge/License-BSD_3--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-3-Clause
   :alt: License

**meteopendata2netcdf** est une bibliothèque Python open source qui fiabilise
et standardise la collecte de données météorologiques opendata pour alimenter
des chaînes de traitement scientifique, physique et technique.

Le résultat de chaque collecte est systématiquement un fichier **NetCDF
conforme aux conventions CF**, format de référence dans la communauté
météorologique et climatologique.

* **Dépôt source** : https://github.com/miki4iaml/meteopendata
* **PyPI** : https://pypi.org/project/meteopendata2netcdf
* **Licence** : BSD 3-Clause
* **Auteur** : Miki (miki4ia@gmail.com)
