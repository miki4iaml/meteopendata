.. _api:

Référence API
=============

Ce module expose les symboles publics suivants, importables directement
depuis ``meteopendata2netcdf`` :

.. code-block:: python

   from meteopendata2netcdf import (
       IFSSurfaceDownloader,
       DownloadResult,
       DownloadError,
       DatasetBuildError,
   )

Téléchargeur
------------

.. autoclass:: meteopendata2netcdf.IFSSurfaceDownloader
   :members:
   :show-inheritance:

.. autoclass:: meteopendata2netcdf.DownloadResult
   :members:
   :show-inheritance:

Exceptions
----------

.. autoexception:: meteopendata2netcdf.DownloadError
   :show-inheritance:

.. autoexception:: meteopendata2netcdf.DatasetBuildError
   :show-inheritance:

Utilitaires internes
--------------------

Les modules suivants sont internes (préfixe ``_``) et ne font pas partie
de l'API publique stable. Ils sont documentés ici pour les contributeurs.

.. autofunction:: meteopendata2netcdf._grib.load_surface_dataset

.. automodule:: meteopendata2netcdf._constants
   :members:
   :no-index:
