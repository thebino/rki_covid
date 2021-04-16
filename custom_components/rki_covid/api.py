"""REST API for RKI Covid numbers."""

from datetime import datetime
import logging
from typing import Iterable

from aiohttp import ClientError, ClientSession

from custom_components.rki_covid.const import (
    API_URL_DISTRICT_DATA,
    API_URL_DISTRICT_NEW_CASES,
    API_URL_DISTRICT_NEW_DEATHS,
    API_URL_DISTRICT_NEW_RECOVERED,
    API_URL_DISTRICT_RECOVERED_DATA,
)
from custom_components.rki_covid.data import DataCollector, DistrictData

_LOGGER = logging.getLogger(__name__)


class RKICovidAPI:
    """REST API for RKI Covid numbers."""

    def __init__(self, session: ClientSession):
        """Initialize the REST API."""
        self.session = session

    async def _get_json_data_from_url(self, url):
        response = await self.session.get(
            url=url,
            allow_redirects=True,
        )

        if response.status != 200:
            _LOGGER.error(f"Request failed {response}")
            raise ClientError(response)

        return await response.json(content_type=None)

    async def get_district(self):
        """Get district data from RKI."""
        data = await self._get_json_data_from_url(API_URL_DISTRICT_DATA)
        result = []
        for dataset in data["features"]:
            dataset = dataset["attributes"]
            result.append(
                {
                    "id": dataset["RS"],
                    "name": dataset["GEN"],
                    "county": dataset["county"],
                    "state": dataset["BL"],
                    "population": dataset["EWZ"],
                    "cases": dataset["cases"],
                    "deaths": dataset["deaths"],
                    "casesPerWeek": dataset["cases7_lk"],
                    "weekIncidence": round(
                        dataset["cases7_lk"] / dataset["EWZ"] * 100000, 2
                    ),
                    "casesPer100k": round(
                        dataset["cases"] / dataset["EWZ"] * 100000, 2
                    ),
                    "lastUpdated": dataset["last_update"],
                }
            )
        _LOGGER.debug("Get district data from RKI")
        return result

    async def get_district_recovered(self):
        """Get district recovered data from RKI."""
        data = await self._get_json_data_from_url(API_URL_DISTRICT_RECOVERED_DATA)
        result = []
        for dataset in data["features"]:
            dataset = dataset["attributes"]
            result.append(
                {
                    "id": dataset["IdLandkreis"],
                    "recovered": dataset["recovered"],
                }
            )
        _LOGGER.debug("Get district recovered data from RKI")
        return result

    async def get_district_new_cases(self):
        """Get district new cases data from RKI."""
        data = await self._get_json_data_from_url(API_URL_DISTRICT_NEW_CASES)
        result = []
        for dataset in data["features"]:
            dataset = dataset["attributes"]
            result.append(
                {
                    "id": dataset["IdLandkreis"],
                    "cases": dataset["cases"],
                }
            )
        _LOGGER.debug("Get district new cases data from RKI")
        return result

    async def get_district_new_deaths(self):
        """Get district new deaths data from RKI."""
        data = await self._get_json_data_from_url(API_URL_DISTRICT_NEW_DEATHS)
        result = []
        for dataset in data["features"]:
            dataset = dataset["attributes"]
            result.append(
                {
                    "id": dataset["IdLandkreis"],
                    "deaths": dataset["deaths"],
                }
            )
        _LOGGER.debug("Get district new deaths data from RKI")
        return result

    async def get_district_new_recovered(self):
        """Get district new recovered data from RKI."""
        data = await self._get_json_data_from_url(API_URL_DISTRICT_NEW_RECOVERED)
        result = []
        for dataset in data["features"]:
            dataset = dataset["attributes"]
            result.append(
                {
                    "id": dataset["IdLandkreis"],
                    "recovered": dataset["recovered"],
                }
            )
        _LOGGER.debug("Get district new recovered data from RKI")
        return result

    async def load_districts(self) -> Iterable:
        """Return a specific district."""
        district_data = await self.get_district()
        district_recovered_data = await self.get_district_recovered()
        district_new_cases_data = await self.get_district_new_cases()
        district_new_deaths_data = await self.get_district_new_deaths()
        district_new_recovered_data = await self.get_district_new_recovered()

        def get_by_id(data, id):
            for dataset in data:
                if dataset["id"] == id:
                    return dataset
            return {}

        results = []

        collectedData = {}
        lastUpdate = datetime.strptime(
            district_data[0]["lastUpdated"], "%d.%m.%Y, %H:%M Uhr"
        )

        for dataset in district_data:
            recovered_data = get_by_id(district_recovered_data, dataset["id"])
            new_cases_data = get_by_id(district_new_cases_data, dataset["id"])
            new_deaths_data = get_by_id(district_new_deaths_data, dataset["id"])
            new_recovered_data = get_by_id(district_new_recovered_data, dataset["id"])

            name = dataset["name"]
            county = dataset["county"]
            state = dataset["state"]
            population = dataset["population"]
            cases = dataset["cases"]
            deaths = dataset["deaths"]
            casesPerWeek = dataset["casesPerWeek"]
            recovered = recovered_data.get("recovered", 0)
            week_incidence = dataset["weekIncidence"]
            cases_per_100k = dataset["casesPer100k"]
            new_cases = new_cases_data.get("cases", 0)
            new_deaths = new_deaths_data.get("deaths", 0)
            new_recovered = new_recovered_data.get("recovered", 0)

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
            collectedData[state].population = (
                collectedData[state].population + population
            )
            collectedData[state].count = collectedData[state].count + cases
            collectedData[state].deaths = collectedData[state].deaths + deaths
            collectedData[state].casesPerWeek = (
                collectedData[state].casesPerWeek + casesPerWeek
            )
            collectedData[state].recovered = collectedData[state].recovered + recovered
            # weekIncidence is calculated
            # casesPer100k is calculated
            collectedData[state].newCases = collectedData[state].newCases + new_cases
            collectedData[state].newDeaths = collectedData[state].newDeaths + new_deaths
            collectedData[state].newRecovered = (
                collectedData[state].newRecovered + new_recovered
            )
            collectedData[state].dataCount = collectedData[state].dataCount + 1

        germanyTotal = DataCollector()

        for key, value in collectedData.items():
            value.weekIncidence = round(
                value.casesPerWeek / value.population * 100000, 2
            )
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
                    lastUpdate=lastUpdate,
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

        germanyTotal.casesPer100k = round(
            germanyTotal.count / germanyTotal.population * 100000, 2
        )
        germanyTotal.weekIncidence = round(
            germanyTotal.casesPerWeek / germanyTotal.population * 100000, 2
        )

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
                lastUpdate=lastUpdate,
            )
        )
        return results
