# Changelog

All notable changes to this project will be documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.1] - 2026-07-12
- docs: update documentation /sources (ecmwf)
- docs: publish to ReadTheDocs (Autodoc)

## [0.3.0] – 2026-07-11
- docs: updated documentation n badges
- test: cov extended

## [0.2b0] – unreleased

## [0.1b0] – 2026-06-28

### Added
- Initial beta release.
- `IFSSurfaceDownloader`: download IFS HRES surface fields (2t, 2d, 10u, 10v)
  via ecmwf-opendata HTTP Byte-Range, steps 0–72 h every 6 h.
- `DownloadResult.to_netcdf()`: one-shot NetCDF export.
- CLI entry point `meteopendata2netcdf` with `--source`, `--time`, `--netcdf`
  and `--no-dataset` options.
- Multi-OS CI (Linux, Windows, macOS) × Python 3.12/3.13 via GitHub Actions.
- Sphinx documentation hosted on Read the Docs.
