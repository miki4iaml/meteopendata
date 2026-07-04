"""Package-wide constants for IFS surface downloads."""

#: Surface parameters downloaded from IFS open data.
#: - 2t  : 2-metre temperature (K)
#: - 2d  : 2-metre dewpoint temperature (K)  — surface humidity proxy
#: - 10u : 10-metre U-wind component (m s⁻¹)
#: - 10v : 10-metre V-wind component (m s⁻¹)
SURFACE_PARAMS: list[str] = ["2t", "2d", "10u", "10v"]

#: Default forecast steps (hours): 0–72 h every 6 h.
DEFAULT_STEPS: list[int] = list(range(0, 73, 6))

#: IFS HRES operational run hours available via stream=oper.
VALID_RUN_HOURS: frozenset[int] = frozenset({0, 12})

#: ecmwf-opendata model / stream / type strings.
MODEL: str = "ifs"
STREAM: str = "oper"
FORECAST_TYPE: str = "fc"
RESOLUTION: str = "0p25"
