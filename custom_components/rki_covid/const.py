"""Constants for the RKI Covid numbers integration."""
DOMAIN = "rki_covid"

ATTRIBUTION = "Data provided by Robert Koch-Institut"

BASE_API_URL = "https://rki-covid-api.now.sh"
ENDPOINT_DISCTRICTS = "/api/districts"

CONF_DISTRICTS = "districts"
ATTR_DISTRICT = "district"

ATTR_COUNTY = "county"
ATTR_COUNT = "count"
ATTR_DEATHS = "deaths"
ATTR_WEEK_INCIDENCE = "weekIncidence"
ATTR_CASES_PER_100 = "casesPer100k"
ATTR_CASES_PER_POPULATION = "casesPerPopulation"
