Changelog
=========

0.1b0 (2026-06-28)
-------------------

* Initial beta release.
* IFS HRES surface download: ``2t``, ``2d``, ``10u``, ``10v``, steps 0–72 h.
* GRIB2 output + optional in-memory ``xr.Dataset``.
* ``to_netcdf()`` convenience method on :class:`~meteopendata2netcdf.DownloadResult`.
* CLI entry point ``meteopendata2netcdf``.
* Multi-OS CI (Linux, Windows, macOS) via GitHub Actions.
