"""REST API for RKI Covid numbers."""

from datetime import datetime
import logging
from typing import Iterable

from aiohttp import ClientError, ClientSession

from custom_components.rki_covid.const import BASE_API_URL, ENDPOINT_DISTRICTS
from custom_components.rki_covid.data import DistrictData

_LOGGER = logging.getLogger(__name__)


class RKICovidAPI:
    """REST API for RKI Covid numbers."""

    def __init__(self, session: ClientSession):
        """Initialize the REST API."""
        self.session = session

    async def load_districts(self) -> Iterable:
        """Return a specific district."""
        response = await self.session.get(
            url=f"{BASE_API_URL}{ENDPOINT_DISTRICTS}", allow_redirects=True
        )
        if response.status == 200:
            data = await response.json()

            results = []

            last_update = data["meta"]["lastUpdate"]
            for dis in data["data"]:
                district = data["data"][dis]

                name = district["name"]
                county = district["county"]
                state = district["state"]
                population = district["population"]
                cases = district["cases"]
                deaths = district["deaths"]
                casesPerWeek = district["casesPerWeek"]
                recovered = district["recovered"]
                week_incidence = round(district["weekIncidence"], 2)
                cases_per_100k = round(district["casesPer100k"], 2)
                new_cases = district["delta"]["cases"]
                new_deaths = district["delta"]["deaths"]
                new_recovered = district["delta"]["recovered"]

                lastUpdate = datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S.%f%z")

                results.append(
                    DistrictData(
                        name=name,
                        county=county,
                        state=state,
                        population=population,
                        count=cases,
                        deaths=deaths,
                        casesPerWeek=casesPerWeek,
                        recovered=recovered,
                        weekIncidence=week_incidence,
                        casesPer100k=cases_per_100k,
                        newCases=new_cases,
                        newDeaths=new_deaths,
                        newRecovered=new_recovered,
                        lastUpdate=lastUpdate,
                    )
                )
            return results

        else:
            _LOGGER.error(f"Request failed {response}")

        raise ClientError(response)
