"""Constants for the RKI Covid numbers integration."""
DOMAIN = "rki_covid"

ATTRIBUTION = "Data provided by Robert Koch-Institut"

# https://api.corona-zahlen.org/docs/endpoints/districts.html

BASE_API_URL = "https://api.corona-zahlen.org/"
ENDPOINT_DISTRICTS = "/api/districts"

# configuration keywords
CONF_DISTRICTS = "districts"
CONF_COUNTY = "county"

# configuration attributes
ATTR_COUNTY = "county"
ATTR_COUNT = "count"
ATTR_DEATHS = "deaths"
ATTR_WEEK_INCIDENCE = "weekIncidence"
ATTR_CASES_PER_100 = "casesPer100k"
ATTR_CASES_PER_POPULATION = "casesPerPopulation"

