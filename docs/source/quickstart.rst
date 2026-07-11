Quick start
===========

Python API
----------

.. code-block:: python

    from meteopendata2netcdf import IFSSurfaceDownloader

    dl = IFSSurfaceDownloader(output_dir="./ifs_output")
    result = dl.download()          # latest run, GRIB2 + xr.Dataset in memory
    print(result)

    # Export to NetCDF
    result.to_netcdf("ifs_surface.nc")

    # Or access the dataset directly
    ds = result.dataset
    print(ds)

CLI
---

.. code-block:: bash

    # Latest run → GRIB2 only
    meteopendata2netcdf --output ./data/ifs

    # Latest run → GRIB2 + NetCDF
    meteopendata2netcdf --output ./data/ifs --netcdf ifs_surface.nc

    # Run 00Z via AWS, with debug logging
    meteopendata2netcdf --source aws --time 0 --log-level DEBUG

    # Print version
    meteopendata2netcdf --version

Parameters downloaded
---------------------

All fields are at the surface level (``heightAboveGround``):

============  ===========================================  =======
Short name    Description                                  Unit
============  ===========================================  =======
``2t``        2-metre temperature                          K
``2d``        2-metre dewpoint temperature (humidity)      K
``10u``       10-metre U-wind component                    m s⁻¹
``10v``       10-metre V-wind component                    m s⁻¹
============  ===========================================  =======

Forecast steps: 0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72 h.
