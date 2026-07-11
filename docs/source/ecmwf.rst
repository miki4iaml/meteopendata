.. _source-ecmwf:

Source : ECMWF open data
=========================

.. contents:: Sommaire
   :local:
   :depth: 2


Présentation
------------

L'ECMWF (Centre européen pour les prévisions météorologiques à moyen terme)
publie une partie de ses sorties de modèles en accès libre sous licence
`CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_. Ces données sont
accessibles depuis plusieurs points de distribution :

- **Serveurs ECMWF directs** : ``https://data.ecmwf.int/forecasts/``
- **AWS S3** : ``s3://ecmwf-forecasts``
- **Azure Blob Storage** : accessible via ``ecmwf-opendata``
- **Google Cloud Storage** : accessible via ``ecmwf-opendata``

L'accès est limité à 500 connexions simultanées sur les serveurs directs.
En cas de saturation, les miroirs cloud (AWS recommandé) offrent une
alternative fiable.

.. note::

   En téléchargeant ces données, vous acceptez les conditions de la licence
   CC BY 4.0. Veuillez mentionner l'ECMWF comme source dans toute publication
   ou application utilisant ces données.


Mécanisme de téléchargement : HTTP Byte-Range
---------------------------------------------

Chaque fichier GRIB2 publié par l'ECMWF est accompagné d'un fichier d'index
``.index`` contenant une ligne JSON par message GRIB2, avec notamment les
champs ``_offset`` et ``_length`` indiquant la position en octets de chaque
champ dans le fichier.

La bibliothèque ``ecmwf-opendata`` exploite ces index pour construire des
requêtes HTTP ``Range`` qui ne téléchargent que les octets correspondant aux
paramètres et échéances demandés. Ce mécanisme est transparent pour
l'utilisateur mais a une implication importante : **plus le nombre de paramètres
demandés est faible par rapport au contenu total du fichier, plus le gain de
bande passante est significatif**.

Pour les cas où la majorité des paramètres d'un fichier est nécessaire,
le téléchargement complet (comme le fait ``meteofetch``) est plus efficace
car il évite la surcharge des multiples requêtes Range.


Modèles disponibles
--------------------

IFS HRES oper (intégré — v0.x)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le modèle **IFS** (Integrated Forecasting System) en configuration HRES
(High RESolution) est le modèle opérationnel déterministe de l'ECMWF.

.. list-table::
   :header-rows: 0
   :widths: 35 65

   * - Résolution horizontale
     - 0.25° (~28 km)
   * - Heures de run (UTC)
     - 00Z et 12Z (stream ``oper``)
   * - Horizon de prévision
     - 0 à 144 h (pas 3 h) puis 150 à 360 h (pas 6 h)
   * - Couvert par meteopendata2netcdf
     - 0 à 72 h par pas de 6 h (surface uniquement, v0.x)
   * - Identifiant ecmwf-opendata
     - ``model="ifs"``, ``stream="oper"``, ``type="fc"``

.. note::

   Les runs 06Z et 18Z (stream ``scda``) existent mais ne couvrent que
   jusqu'à 90 h. Ils ne sont pas intégrés dans la version actuelle.

AIFS (prévu — v1.0)
~~~~~~~~~~~~~~~~~~~~~

**AIFS** (Artificial Intelligence/Integrated Forecasting System) est le modèle
de prévision entièrement data-driven de l'ECMWF, basé sur un réseau de
neurones entraîné sur ERA5. Il est disponible sur les mêmes serveurs open data.

.. list-table::
   :header-rows: 0
   :widths: 35 65

   * - Résolution horizontale
     - 0.25°
   * - Heures de run (UTC)
     - 00Z et 12Z
   * - Horizon de prévision
     - 0 à 360 h par pas de 6 h
   * - Statut
     - Prévu pour v1.0

ENFO (prévu — v1.0)
~~~~~~~~~~~~~~~~~~~~~

**ENFO** (ENsemble FOrecasts) est le système de prévision d'ensemble de
l'ECMWF, composé de 50 membres perturbés + 1 membre de contrôle.

.. list-table::
   :header-rows: 0
   :widths: 35 65

   * - Résolution horizontale
     - 0.25°
   * - Nombre de membres
     - 50 + contrôle
   * - Horizon de prévision
     - 0 à 360 h
   * - Complexité d'intégration
     - Dimension ``number`` supplémentaire dans xarray
   * - Statut
     - Prévu pour v1.0


Paramètres intégrés (v0.x)
----------------------------

Les paramètres suivants sont disponibles dans la version actuelle. Ils
correspondent aux champs de surface les plus demandés pour les applications
d'ingénierie et de sciences physiques.

.. list-table::
   :header-rows: 1
   :widths: 12 12 38 12 12 14

   * - Nom court
     - Nom xarray
     - Description
     - Unité
     - Hauteur
     - typeOfLevel
   * - ``2t``
     - ``t2m``
     - Température à 2 mètres
     - K
     - 2 m
     - heightAboveGround
   * - ``2d``
     - ``d2m``
     - Température du point de rosée à 2 m
     - K
     - 2 m
     - heightAboveGround
   * - ``10u``
     - ``u10``
     - Composante U du vent à 10 mètres
     - m s⁻¹
     - 10 m
     - heightAboveGround
   * - ``10v``
     - ``v10``
     - Composante V du vent à 10 mètres
     - m s⁻¹
     - 10 m
     - heightAboveGround

Le point de rosée (``2d``) a été retenu comme proxy d'humidité de surface
car il est directement disponible sur les serveurs ECMWF open data, contrairement
à l'humidité relative (``r``) qui nécessite un calcul intermédiaire.
La conversion Td → RH est triviale si nécessaire :

.. code-block:: python

   import numpy as np

   def dewpoint_to_rh(t2m_K: float, d2m_K: float) -> float:
       """Convertit température et point de rosée en humidité relative (%)."""
       t_C = t2m_K - 273.15
       td_C = d2m_K - 273.15
       rh = 100 * np.exp(17.625 * td_C / (243.04 + td_C)) / \
                  np.exp(17.625 * t_C  / (243.04 + t_C))
       return float(rh)


Paramètres prévus pour les prochaines versions
------------------------------------------------

Les paramètres suivants sont identifiés pour les versions ultérieures.
Les noms courts sont ceux utilisés par l'ECMWF dans ses fichiers GRIB2.

.. list-table::
   :header-rows: 1
   :widths: 15 45 15 25

   * - Nom court
     - Description
     - Unité
     - Version cible
   * - ``tp``
     - Précipitations totales (accumulées)
     - m
     - v0.x
   * - ``ssrd``
     - Rayonnement solaire descendant de courte longueur d'onde (accumulé)
     - J m⁻²
     - v0.x
   * - ``msl``
     - Pression au niveau de la mer
     - Pa
     - v0.x
   * - ``z``
     - Géopotentiel (niveaux de pression)
     - m² s⁻²
     - v1.0
   * - ``t``
     - Température (niveaux de pression)
     - K
     - v1.0
   * - ``u``, ``v``
     - Vent (niveaux de pression)
     - m s⁻¹
     - v1.0
   * - ``q``
     - Humidité spécifique (niveaux de pression)
     - kg kg⁻¹
     - v1.0


Problème technique spécifique : groupes GRIB multiples
-------------------------------------------------------

Les paramètres de surface IFS se répartissent sur deux hauteurs distinctes
dans les fichiers GRIB2 :

- ``heightAboveGround = 2 m`` → ``t2m``, ``d2m``
- ``heightAboveGround = 10 m`` → ``u10``, ``v10``

``cfgrib`` groupe les messages GRIB par valeur de coordonnée scalaire.
``xr.open_dataset()`` (backend cfgrib) ne peut pas fusionner automatiquement
deux groupes dont la coordonnée scalaire ``heightAboveGround`` prend des valeurs
différentes : il lève une ``DatasetBuildError`` et abandonne silencieusement
les variables en conflit.

La fonction ``load_surface_dataset()`` dans ``_grib.py`` résout ce problème
en utilisant ``cfgrib.open_datasets()`` (pluriel), qui retourne une liste de
Datasets cohérents — un par groupe de hauteur — puis fusionne les groupes
après suppression de la coordonnée conflictuelle. Voir :ref:`grib-multigroup`
dans le document de conception pour les détails d'implémentation.


Exemple d'utilisation complet
-------------------------------

.. code-block:: python

   from meteopendata2netcdf import IFSSurfaceDownloader

   # Téléchargement depuis les serveurs ECMWF directs
   dl = IFSSurfaceDownloader(
       output_dir="./data/ifs",
       source="ecmwf",        # ou "aws", "azure", "google"
   )

   # Run le plus récent, tous les paramètres, toutes les échéances par défaut
   result = dl.download()
   print(result)
   # DownloadResult(
   #   run_datetime = 2026-06-28T00:00:00
   #   grib_path    = data/ifs/ifs_surface_20260628_00z.grib2
   #   params       = ['2t', '2d', '10u', '10v']
   #   steps        = [0, 6, 12, ..., 72]
   #   dataset      = Dataset(vars=['t2m', 'd2m', 'u10', 'v10'])
   # )

   # Export NetCDF-CF
   result.to_netcdf("ifs_surface_20260628_00z.nc")

   # Accès direct au Dataset xarray
   ds = result.dataset
   print(ds["t2m"].attrs)   # {'height_m': 2.0, ...}

   # Sous-sélection temporelle
   t2m_48h = ds["t2m"].sel(valid_time="2026-06-30T00:00:00")

   # Via CLI
   # meteopendata2netcdf --source aws --time 0 --netcdf ifs_surface.nc
