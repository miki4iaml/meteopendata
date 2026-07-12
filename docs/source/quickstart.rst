.. _quickstart:

Prise en main rapide
====================

.. contents:: Sommaire
   :local:
   :depth: 1


En Python
---------

Télécharger le run IFS le plus récent et l'exporter en NetCDF :

.. code-block:: python

    from meteopendata2netcdf import IFSSurfaceDownloader

    # Initialiser le téléchargeur (répertoire de sortie créé automatiquement)
    dl = IFSSurfaceDownloader(output_dir="./data/ifs")

    # Télécharger le run le plus récent (00Z ou 12Z, auto-détecté)
    result = dl.download()

    print(result)
    # DownloadResult(
    #   run_datetime = 2026-06-28T00:00:00
    #   grib_path    = data/ifs/ifs_surface_20260628_00z.grib2
    #   params       = ['2t', '2d', '10u', '10v']
    #   steps        = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]
    #   dataset      = Dataset(vars=['t2m', 'd2m', 'u10', 'v10'])
    # )

    # Exporter en NetCDF
    result.to_netcdf("ifs_surface.nc")

    # Accéder au Dataset xarray directement
    ds = result.dataset
    print(ds)
    # <xarray.Dataset>
    # Dimensions:     (valid_time: 13, latitude: 721, longitude: 1440)
    # Coordinates:
    #   * valid_time  (valid_time) datetime64[ns] ...
    #   * latitude    (latitude) float64 ...
    #   * longitude   (longitude) float64 ...
    # Data variables:
    #     t2m         (valid_time, latitude, longitude) float32 ...
    #     d2m         (valid_time, latitude, longitude) float32 ...
    #     u10         (valid_time, latitude, longitude) float32 ...
    #     v10         (valid_time, latitude, longitude) float32 ...

    # Sélectionner une échéance
    t2m_24h = ds["t2m"].sel(valid_time=ds.valid_time[4])  # échéance +24h

    # Convertir en degrés Celsius
    t2m_celsius = ds["t2m"] - 273.15

    # Calculer la vitesse du vent
    import numpy as np
    wind_speed = np.sqrt(ds["u10"] ** 2 + ds["v10"] ** 2)


Options du téléchargeur
------------------------

.. code-block:: python

    from meteopendata2netcdf import IFSSurfaceDownloader

    # Choisir la source de données (ecmwf par défaut, aws recommandé en cas
    # de saturation des serveurs ECMWF)
    dl = IFSSurfaceDownloader(
        output_dir="./data/ifs",
        source="aws",          # "ecmwf" | "aws" | "azure" | "google"
    )

    # Cibler un run spécifique (00Z ou 12Z)
    result = dl.download(time=0)   # run 00Z
    result = dl.download(time=12)  # run 12Z

    # Télécharger le GRIB2 uniquement, sans charger en mémoire
    result = dl.download(load_dataset=False)
    print(result.grib_path)   # Path vers le fichier GRIB2
    # result.dataset est None

    # Personnaliser les paramètres et les échéances
    dl = IFSSurfaceDownloader(
        output_dir="./data/ifs",
        params=["2t", "10u", "10v"],         # sans le point de rosée
        steps=[0, 12, 24, 48, 72],           # échéances personnalisées
    )


En ligne de commande
---------------------

.. code-block:: bash

    # Run le plus récent, GRIB2 uniquement
    meteopendata2netcdf --output ./data/ifs

    # Run le plus récent, GRIB2 + export NetCDF
    meteopendata2netcdf --output ./data/ifs --netcdf ifs_surface.nc

    # Run 00Z depuis AWS
    meteopendata2netcdf --source aws --time 0 --netcdf ifs_00z.nc

    # Afficher la version
    meteopendata2netcdf --version

    # Aide complète
    meteopendata2netcdf --help


Paramètres disponibles (v0.x)
-------------------------------

Tous les paramètres sont au niveau surface (``heightAboveGround``) :

.. list-table::
   :header-rows: 1
   :widths: 15 18 40 12 15

   * - Nom court
     - Nom xarray
     - Description
     - Unité
     - Hauteur
   * - ``2t``
     - ``t2m``
     - Température
     - K
     - 2 m
   * - ``2d``
     - ``d2m``
     - Point de rosée (humidité)
     - K
     - 2 m
   * - ``10u``
     - ``u10``
     - Composante U du vent
     - m s⁻¹
     - 10 m
   * - ``10v``
     - ``v10``
     - Composante V du vent
     - m s⁻¹
     - 10 m

Échéances : **0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72 h**
(runs IFS HRES oper 00Z et 12Z, résolution 0.25°).

Pour la liste complète des paramètres prévus dans les prochaines versions,
voir :ref:`source-ecmwf`.
