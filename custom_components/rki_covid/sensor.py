"""RKI Covid numbers sensor."""

from datetime import timedelta
import logging
from typing import Callable, Dict, Optional

from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol

from . import get_coordinator
from .api import RKICovidAPI
from .const import ATTRIBUTION, CONF_COUNTY, CONF_DISTRICTS

_LOGGER = logging.getLogger(__name__)

# wait for x minutes after restart, before refreshing
SCAN_INTERVAL = timedelta(minutes=10)

# schema for each config entry
DISTRICT_SCHEMA = vol.Schema({vol.Required(CONF_NAME): cv.string})

# schema for each platform sensor
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DISTRICTS): vol.All(cv.ensure_list, [DISTRICT_SCHEMA]),
    }
)

SENSORS = {
    "count": "mdi:virus",
    "deaths": "mdi:christianity",
    "recovered": "mdi:bottle-tonic-plus-outline",
    "weekIncidence": "mdi:clipboard-pulse",
    "casesPer100k": "mdi:home-group",
    "newCases": "mdi:shield-bug",
    "newDeaths": "mdi:shield-cross",
    "newRecovered": "mdi:shield-sync",
}


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)

    api = RKICovidAPI(session)
    coordinator = await get_coordinator(hass, api)

    districts = config[CONF_DISTRICTS]

    sensors = [
        RKICovidNumbersSensor(coordinator, district["name"], info_type)
        for info_type in SENSORS
        for district in districts
    ]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Create sensors from a config entry in the integrations UI."""
    session = async_get_clientsession(hass)
    api = RKICovidAPI(session)
    coordinator = await get_coordinator(hass, api)

    district = config_entry.data[CONF_COUNTY]
    sensors = [
        RKICovidNumbersSensor(coordinator, district, info_type) for info_type in SENSORS
    ]
    async_add_entities(sensors, update_before_add=True)


class RKICovidNumbersSensor(CoordinatorEntity):
    """Representation of a sensor."""

    name = None
    unique_id = None

    def __init__(
        self,
        coordinator: update_coordinator.DataUpdateCoordinator,
        district: Dict[str, str],
        info_type: str,
    ):
        """Initialize a new sensor."""
        super().__init__(coordinator)

        data = coordinator.data[district]

        self.name = f"{data.county} {info_type}"
        self.unique_id = f"{district}-{info_type}"
        self.district = district
        self.info_type = info_type
        self.updated = data.lastUpdate

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.district in self.coordinator.data
        )

    @property
    def state(self) -> Optional[str]:
        """Return current state."""
        return getattr(self.coordinator.data[self.district], self.info_type)

    @property
    def icon(self):
        """Return the icon."""
        return SENSORS[self.info_type]

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        if (
            self.info_type == "count"
            or self.info_type == "deaths"
            or self.info_type == "recovered"
        ):
            return "people"
        elif self.info_type == "weekIncidence":
            return "#"
        else:
            return "cases"

    @property
    def device_state_attributes(self):
        """Return device attributes."""
        return {
            ATTR_ATTRIBUTION: f"last updated {self.updated.strftime('%d %b, %Y  %H:%M:%S')} \n{ATTRIBUTION}"
        }
