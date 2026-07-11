Installation
============

Requirements
------------

* Python >= 3.12
* A system installation of `eccodes <https://confluence.ecmwf.int/display/ECC>`_
  (required by cfgrib):

  .. code-block:: bash

      # Linux (Debian/Ubuntu)
      sudo apt-get install libeccodes-dev

      # macOS
      brew install eccodes

      # Windows — eccodes is bundled in the cfgrib wheel; no extra step needed.

Install from PyPI
-----------------

.. code-block:: bash

    pip install meteopendata2netcdf

Install from source
-------------------

.. code-block:: bash

    git clone https://github.com/your-username/meteopendata2netcdf.git
    cd meteopendata2netcdf
    pip install -e ".[dev,docs]"
