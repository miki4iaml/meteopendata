"""Tests for _constants.py — pure values, no mocking needed."""

from meteopendata2netcdf._constants import (
    DEFAULT_STEPS,
    FORECAST_TYPE,
    MODEL,
    RESOLUTION,
    STREAM,
    SURFACE_PARAMS,
    VALID_RUN_HOURS,
)


def test_surface_params_content() -> None:
    assert "2t" in SURFACE_PARAMS
    assert "2d" in SURFACE_PARAMS
    assert "10u" in SURFACE_PARAMS
    assert "10v" in SURFACE_PARAMS
    assert len(SURFACE_PARAMS) == 4


def test_default_steps_range() -> None:
    assert DEFAULT_STEPS[0] == 0
    assert DEFAULT_STEPS[-1] == 72
    # Every step is a multiple of 6
    assert all(s % 6 == 0 for s in DEFAULT_STEPS)
    assert len(DEFAULT_STEPS) == 13  # 0, 6, 12, …, 72


def test_valid_run_hours() -> None:
    assert 0 in VALID_RUN_HOURS
    assert 12 in VALID_RUN_HOURS
    assert 6 not in VALID_RUN_HOURS
    assert 18 not in VALID_RUN_HOURS


def test_model_strings() -> None:
    assert MODEL == "ifs"
    assert STREAM == "oper"
    assert FORECAST_TYPE == "fc"
    assert RESOLUTION == "0p25"
