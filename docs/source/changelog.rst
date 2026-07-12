.. _changelog:

Changelog
=========

Toutes les modifications notables sont documentées ici.
Le format suit `Keep a Changelog <https://keepachangelog.com/fr/1.1.0/>`_
et le versionnage suit `PEP 440 <https://peps.python.org/pep-0440/>`_ /
`Semantic Versioning <https://semver.org/lang/fr/>`_.

.. note::

   Les versions ``0.x.yb0`` sont des versions bêta : l'API publique peut
   évoluer entre versions mineures. La version **1.0.0** marquera la
   stabilisation de l'API.

Unreleased
----------

*(rien pour l'instant)*

0.2b0 (2026-06-28)
-------------------

**Corrections**

* Correction du backend setuptools : remplacement de
  ``setuptools.backends.legacy:build`` (non disponible dans les environnements
  avec setuptools < 69) par ``setuptools.build_meta`` (stable depuis
  setuptools 40).
* Correction des erreurs mypy :

  * Ajout de ``[[tool.mypy.overrides]]`` pour ``cfgrib`` et
    ``ecmwf-opendata`` (packages sans stubs).
  * ``DownloadResult.to_netcdf()`` : ``**kwargs: Any`` (ANN401 ignoré),
    passage de ``str(out)`` pour sélectionner la bonne surcharge xarray.
  * ``_cli.py`` : ``cast(Source, args.source)`` remplace le
    ``type: ignore[arg-type]``.

* Correction des caractères EN DASH (U+2013) détectés par ruff RUF001 :
  remplacés par des traits d'union ASCII.
* Correction des fixtures de test : utilisation de ``np.datetime64`` pour
  les coordonnées temporelles (``datetime`` timezone-aware non sérialisable
  par le backend NetCDF4 xarray).
* Correction de ``test_cli.py`` : variable ``MockCls`` renommée ``mock_cls``
  (règle ruff N806).

**CI/CD**

* Ajout de ``release: types: [published]`` et ``workflow_dispatch`` dans
  ``publish.yml`` pour que la création d'une release via l'IHM GitHub
  déclenche bien la publication sur PyPI.
* Ajout de ``[tool.ruff.lint.per-file-ignores]`` pour exempter les tests
  des règles ANN.

0.1b0 (2026-06-28)
-------------------

**Ajouts**

* Première version bêta publique.
* ``IFSSurfaceDownloader`` : téléchargement des champs de surface IFS
  (``2t``, ``2d``, ``10u``, ``10v``) via ``ecmwf-opendata`` (HTTP
  Byte-Range), échéances 0 à 72 h par pas de 6 h.
* ``DownloadResult`` : dataclass encapsulant GRIB2, ``xr.Dataset`` et
  métadonnées du run. Méthode ``to_netcdf()`` pour l'export NetCDF.
* Gestion du problème de groupes GRIB multiples (hauteurs 2 m et 10 m)
  via ``cfgrib.open_datasets()`` et fusion ``xr.merge()``.
* Point d'entrée CLI ``meteopendata2netcdf`` avec options ``--source``,
  ``--time``, ``--netcdf``, ``--no-dataset``, ``--log-level``.
* Suite de tests complète (46 tests, couverture > 80 %), zéro dépendance
  réseau (mocking complet de ``ecmwf-opendata`` et ``cfgrib``).
* CI multi-OS (Linux, Windows, macOS) × Python (3.12, 3.13) via GitHub
  Actions.
* Publication PyPI via Trusted Publishing OIDC (sans token API stocké).
* Documentation Sphinx hébergée sur Read the Docs.
