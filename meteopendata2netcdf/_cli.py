"""Command-line interface for meteopendata2netcdf."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from ._downloader import IFSSurfaceDownloader, Source
from ._exceptions import DownloadError, DatasetBuildError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meteopendata2netcdf",
        description=(
            "Download ECMWF IFS surface forecasts (temperature, wind, humidity) "
            "for steps 0–72 h (every 6 h) and optionally export to NetCDF."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--output", "-o",
        default="./ifs_output",
        metavar="DIR",
        help="Directory where the GRIB2 (and optional NetCDF) file is saved.",
    )
    parser.add_argument(
        "--source", "-s",
        choices=["ecmwf", "aws", "azure", "google"],
        default="ecmwf",
        help="Data source.",
    )
    parser.add_argument(
        "--time", "-t",
        type=int,
        choices=[0, 12],
        default=None,
        metavar="{0,12}",
        help="IFS run hour (UTC). Default: latest available run.",
    )
    parser.add_argument(
        "--netcdf", "-n",
        metavar="FILE",
        default=None,
        help="If provided, also write the dataset to this NetCDF file path.",
    )
    parser.add_argument(
        "--no-dataset",
        action="store_true",
        help="Skip loading the dataset into memory (GRIB2 output only).",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``meteopendata2netcdf`` CLI command.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code (0 = success, 1 = error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )

    load_ds = not args.no_dataset or (args.netcdf is not None)

    try:
        dl = IFSSurfaceDownloader(
            output_dir=args.output,
            source=args.source,  # type: ignore[arg-type]
        )
        result = dl.download(time=args.time, load_dataset=load_ds)
        print(result)

        if args.netcdf is not None:
            nc_path = result.to_netcdf(args.netcdf)
            print(f"NetCDF written: {nc_path}")

        return 0

    except (ValueError, DownloadError, DatasetBuildError) as exc:
        logging.getLogger(__name__).error("Fatal error: %s", exc)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
