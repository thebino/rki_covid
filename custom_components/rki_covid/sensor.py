"""RKI Covid numbers sensor."""

from dataclasses import dataclass
from datetime import timedelta
import logging
import time
from typing import Any, Callable, Dict, Optional

from aiohttp import ClientError, ClientSession
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import (
    ATTR_CASES_PER_100,
    ATTR_CASES_PER_POPULATION,
    ATTR_COUNT,
    ATTR_COUNTY,
    ATTR_DEATHS,
    ATTR_DISTRICT,
    ATTR_WEEK_INCIDENCE,
    BASE_API_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# wait for x minutes after restart, before refreshing
SCAN_INTERVAL = timedelta(minutes=10)

# configuration keyword
CONF_DISTRICTS = "districts"

# schema for each config entry
DISTRICT_SCHEMA = vol.Schema({vol.Required(CONF_NAME): cv.string})

# schema for each platform sensor
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_DISTRICTS): vol.All(cv.ensure_list, [DISTRICT_SCHEMA])}
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    api = RKICovidAPI(session)
    sensors = [
        RKICovidNumbersSensor(api, district) for district in config[CONF_DISTRICTS]
    ]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Create sensors from a config entry in the integrations UI."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    session = async_get_clientsession(hass)
    api = RKICovidAPI(session)
    sensors = [
        RKICovidNumbersSensor(api, district) for district in config[CONF_DISTRICTS]
    ]
    async_add_entities(sensors, update_before_add=True)


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


class RKICovidAPI:
    """REST API for RKI Covid numbers."""

    def __init__(self, session: ClientSession):
        """initialize the REST API."""
        self.session = session

    async def get_district(self, district: str) -> DistrictData:
        """Return a specific district."""
        response = await self.session.get(
            url=f"{BASE_API_URL}/api/districts", allow_redirects=True
        )
        if response.status == 200:
            data = await response.json()
            _LOGGER.error(f"### RESPONSE CODE = {response.status}")

            last_update = data["lastUpdate"]
            for district in data["districts"]:
                if district["name"] == district:
                    name = (district["name"],)
                    county = (district["county"],)
                    count = (district["count"],)
                    deaths = (district["deaths"],)
                    week_incidence = (district["weekIncidence"],)
                    cases_per_100k = (district["casesPer100k"],)
                    cases_per_population = (district["casesPerPopulation"],)

                    return DistrictData(
                        name=name,
                        county=county,
                        count=count,
                        deaths=deaths,
                        weekIncidence=week_incidence,
                        casesPer100k=cases_per_100k,
                        casesPerPopulation=cases_per_population,
                        lastUpdate=last_update,
                    )
            _LOGGER.error(f"Could not find requested district {district}")

        else:
            _LOGGER.error(f"Request failed {response}")

        raise ClientError(response)


class RKICovidNumbersSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, api: RKICovidAPI, district: Dict[str, str]):
        """Initialize a new sensor."""
        super().__init__()
        self.api = api
        self.district = district["name"]
        self.attrs: Dict[str, Any] = {ATTR_DISTRICT: self.district}
        self._name = district.get("name", self.district)
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.district

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        """Return current state."""
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return attributes."""
        return self.attrs

    async def async_update(self):
        """Fetch new data from API and map it to self.attrs."""
        try:
            _LOGGER.info("Start async_update...")
            s = time.perf_counter()

            district = await self.api.get_district(self.district)
            self.attrs[ATTR_COUNTY] = district.county
            self.attrs[ATTR_COUNT] = district.count
            self.attrs[ATTR_DEATHS] = district.deaths
            self.attrs[ATTR_WEEK_INCIDENCE] = district.weekIncidence
            self.attrs[ATTR_CASES_PER_100] = district.casesPer100k
            self.attrs[ATTR_CASES_PER_POPULATION] = district.casesPerPopulation

            self._state = district.lastUpdate
            self._available = True

            elapsed = time.perf_counter() - s
            _LOGGER.info(
                f"request district from {BASE_API_URL} took {elapsed:0.2f} seconds."
            )
        except ClientError:
            self._available = False
            _LOGGER.exception(f"Error retrieving data from {BASE_API_URL}.")
