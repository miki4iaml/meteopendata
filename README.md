# meteopendata2netcdf

[![CI](https://github.com/your-username/meteopendata2netcdf/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/meteopendata2netcdf/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/meteopendata2netcdf/badge/?version=latest)](https://meteopendata2netcdf.readthedocs.io)
[![PyPI](https://img.shields.io/pypi/v/meteopendata2netcdf)](https://pypi.org/project/meteopendata2netcdf)
[![Python](https://img.shields.io/pypi/pyversions/meteopendata2netcdf)](https://pypi.org/project/meteopendata2netcdf)
[![License: BSD-3](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)

Leverages open-data weather information via the NetCDF interface.

Download ECMWF IFS open-data surface forecasts (temperature, wind, humidity)
via [ecmwf-opendata](https://github.com/ecmwf/ecmwf-opendata) and export them
to NetCDF.

Uses HTTP **Byte-Range** requests: only the bytes corresponding to the requested
parameters and forecast steps are transferred, not the full GRIB2 files.

## Installation

```bash
pip install meteopendata2netcdf
```

> [!NOTE]
> **eccodes** must be installed on your system (required by cfgrib):
> `apt-get install libeccodes-dev` on Linux · `brew install eccodes` on macOS ·
> bundled in the cfgrib wheel on Windows.

## Quick start

```python
from meteopendata2netcdf import IFSSurfaceDownloader

dl = IFSSurfaceDownloader(output_dir="./ifs_output")
result = dl.download()          # latest IFS run, GRIB2 + xr.Dataset
result.to_netcdf("ifs_surface.nc")
print(result.dataset)
```

```bash
# CLI
meteopendata2netcdf --output ./data/ifs --netcdf ifs_surface.nc
meteopendata2netcdf --source aws --time 0 --log-level DEBUG
```

## Parameters

| Short name | Description                    | Unit  | Height |
|------------|--------------------------------|-------|--------|
| `2t`       | 2-metre temperature            | K     | 2 m    |
| `2d`       | 2-metre dewpoint (humidity)    | K     | 2 m    |
| `10u`      | 10-metre U-wind component      | m s⁻¹ | 10 m   |
| `10v`      | 10-metre V-wind component      | m s⁻¹ | 10 m   |

Forecast steps: **0, 6, 12, … 72 h** (every 6 h). Model: IFS HRES oper, 0.25°.

## Documentation

Full documentation: https://meteopendata2netcdf.readthedocs.io

## Licence

BSD 3-Clause — see [LICENSE](LICENSE).
