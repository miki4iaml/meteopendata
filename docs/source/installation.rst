.. _installation:

Installation
============

.. contents:: Sommaire
   :local:
   :depth: 1


Prérequis système
-----------------

**Python >= 3.12** est requis. Vérifiez votre version :

.. code-block:: bash

    python --version

**eccodes** est une bibliothèque C requise par ``cfgrib`` pour décoder les
fichiers GRIB2. Son installation dépend de votre système :

.. code-block:: bash

    # Linux (Debian/Ubuntu)
    sudo apt-get install libeccodes-dev

    # macOS
    brew install eccodes

    # Windows
    # eccodes est inclus dans la wheel cfgrib publiée sur PyPI.
    # Aucune installation supplémentaire n'est nécessaire.

.. note::

   Sur les environnements notebooks hébergés (Google Colab, Kaggle,
   environnements Jupyter managés), ``libeccodes-dev`` peut être installé
   avec ``!apt-get install -y libeccodes-dev`` dans une cellule.


Depuis PyPI (recommandé)
-------------------------

.. code-block:: bash

    pip install meteopendata2netcdf

Pour vérifier l'installation :

.. code-block:: bash

    python -c "import meteopendata2netcdf; print(meteopendata2netcdf.__version__)"
    meteopendata2netcdf --version


Depuis le dépôt source
-----------------------

Pour disposer de la dernière version en développement ou contribuer au projet :

.. code-block:: bash

    git clone https://github.com/miki4iaml/meteopendata.git
    cd meteopendata

    # Installation en mode éditable avec les extras de développement
    pip install -e ".[dev]"

    # Avec les extras de documentation en plus
    pip install -e ".[dev,docs]"

Le mode éditable (``-e``) fait pointer Python directement vers ``src/``,
de sorte que toute modification du code source est immédiatement prise en
compte sans réinstallation.


Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 15 55

   * - Package
     - Version min.
     - Rôle
   * - ``ecmwf-opendata``
     - 0.3
     - Client HTTP Byte-Range vers les serveurs ECMWF open data
   * - ``cfgrib``
     - 0.9
     - Lecture des fichiers GRIB2 via eccodes
   * - ``xarray``
     - 2024.1
     - Manipulation des données en tableaux labellisés
   * - ``netCDF4``
     - 1.7
     - Écriture des fichiers NetCDF

Les extras ``[dev]`` ajoutent : ``pytest``, ``pytest-cov``, ``ruff``, ``mypy``.

Les extras ``[docs]`` ajoutent : ``sphinx``, ``sphinx-rtd-theme``,
``sphinx-autodoc-typehints``, ``myst-parser``.
