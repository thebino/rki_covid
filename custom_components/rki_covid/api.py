"""REST API for RKI Covid numbers."""

from datetime import datetime
import logging
from typing import Iterable

from aiohttp import ClientError, ClientSession

from custom_components.rki_covid.const import BASE_API_URL, ENDPOINT_DISTRICTS
from custom_components.rki_covid.data import DistrictData, DataCollector

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

            collectedData = {}
            last_update = data["meta"]["lastUpdate"]
            lastUpdate = datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S.%f%z")

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

                # Count data per state
                if state not in collectedData:
                    collectedData[state] = DataCollector()
                collectedData[state].population = collectedData[state].population + population
                collectedData[state].count = collectedData[state].count + cases
                collectedData[state].deaths = collectedData[state].deaths + deaths
                collectedData[state].casesPerWeek = collectedData[state].casesPerWeek + casesPerWeek
                collectedData[state].recovered = collectedData[state].recovered + recovered
                # weekIncidence is calculated
                # casesPer100k is calculated
                collectedData[state].newCases = collectedData[state].newCases + new_cases
                collectedData[state].newDeaths = collectedData[state].newDeaths + new_deaths
                collectedData[state].newRecovered = collectedData[state].newRecovered + new_recovered
                collectedData[state].dataCount = collectedData[state].dataCount + 1


            germanyTotal = DataCollector()

            for key, value in collectedData.items():
                value.weekIncidence = round(value.casesPerWeek / value.population * 100000, 2)
                value.casesPer100k = round(value.count / value.population * 100000, 2)

                results.append(
                    DistrictData(
                        name="BL " + key,
                        county="BL " + key,
                        state="BL " + key,
                        population=value.population,
                        count=value.count,
                        deaths=value.deaths,
                        casesPerWeek=value.casesPerWeek,
                        recovered=value.recovered,
                        weekIncidence=value.weekIncidence,
                        casesPer100k=value.casesPer100k,
                        newCases=value.newCases,
                        newDeaths=value.newDeaths,
                        newRecovered=value.newRecovered,
                        lastUpdate=lastUpdate
                    )
                )

                # Sum up the total values
                germanyTotal.population = germanyTotal.population + value.population
                germanyTotal.count = germanyTotal.count + value.count
                germanyTotal.deaths = germanyTotal.deaths + value.deaths
                germanyTotal.casesPerWeek = germanyTotal.casesPerWeek + value.casesPerWeek
                germanyTotal.recovered = germanyTotal.recovered + value.recovered
                # weekIncidence is calculated
                # casesPer100k is calculated
                germanyTotal.newCases = germanyTotal.newCases + value.newCases
                germanyTotal.newRecovered = germanyTotal.newRecovered + value.newRecovered
                germanyTotal.newDeaths = germanyTotal.newDeaths + value.newDeaths
                germanyTotal.dataCount = germanyTotal.dataCount + 1

            germanyTotal.casesPer100k = round(germanyTotal.count / germanyTotal.population * 100000, 2)
            germanyTotal.weekIncidence = round(germanyTotal.casesPerWeek / germanyTotal.population * 100000, 2)

            results.append(
                DistrictData(
                    name="Deutschland",
                    county="Deutschland",
                    state="",
                    population=germanyTotal.population,
                    count=germanyTotal.count,
                    deaths=germanyTotal.deaths,
                    casesPerWeek=germanyTotal.casesPerWeek,
                    recovered=germanyTotal.recovered,
                    weekIncidence=germanyTotal.weekIncidence,
                    casesPer100k=germanyTotal.casesPer100k,
                    newCases=germanyTotal.newCases,
                    newDeaths=germanyTotal.newDeaths,
                    newRecovered=germanyTotal.newRecovered,
                    lastUpdate=lastUpdate
                )
            )
            return results

        else:
            _LOGGER.error(f"Request failed {response}")

        raise ClientError(response)
