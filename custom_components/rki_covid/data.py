"""Represents a district."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DistrictData:
    """District representation class."""

    name: str
    county: str
    state: str
    population: str
    count: int
    deaths: int
    casesPerWeek: int
    recovered: int
    weekIncidence: float
    casesPer100k: float
    newCases: int
    newDeaths: int
    newRecovered: int
    lastUpdate: datetime

class DataCollector:

    def __init__(self):
        self.population = 0
        self.count = 0
        self.deaths = 0
        self.casesPerWeek = 0.0
        self.recovered = 0
        self.weekIncidence = 0.0
        self.casesPer100k = 0.0
        self.newCases = 0
        self.newDeaths = 0
        self.newRecovered = 0
        self.dataCount = 0
