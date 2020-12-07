"""Represents a district."""
from dataclasses import dataclass


@dataclass
class DistrictData:
    """District representation class."""

    name: str
    county: str
    count: int
    deaths: int
    weekIncidence: float
    casesPer100k: float
    casesPerPopulation: float
    lastUpdate: str
