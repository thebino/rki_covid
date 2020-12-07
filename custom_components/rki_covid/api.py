"""REST API for RKI Covid numbers."""

import logging
from typing import Iterable

from aiohttp import ClientError, ClientSession

from custom_components.rki_covid.const import BASE_API_URL
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
            url=f"{BASE_API_URL}/api/districts", allow_redirects=True
        )
        if response.status == 200:
            data = await response.json()

            results = []

            last_update = data["lastUpdate"]
            for district in data["districts"]:
                name = district["name"]
                county = district["county"]
                count = district["count"]
                deaths = district["deaths"]
                week_incidence = round(district["weekIncidence"], 2)
                cases_per_100k = round(district["casesPer100k"], 2)
                cases_per_population = round(district["casesPerPopulation"], 2)

                results.append(
                    DistrictData(
                        name=name,
                        county=county,
                        count=count,
                        deaths=deaths,
                        weekIncidence=week_incidence,
                        casesPer100k=cases_per_100k,
                        casesPerPopulation=cases_per_population,
                        lastUpdate=last_update,
                    )
                )
            return results

        else:
            _LOGGER.error(f"Request failed {response}")

        raise ClientError(response)
