"""RKI Covid numbers integration."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
from homeassistant import config_entries, core
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.rki_covid.api import RKICovidAPI
from custom_components.rki_covid.const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the component into HomeAssistant."""
    api = RKICovidAPI(async_get_clientsession(hass))

    # Make sure coordinator is initialized.
    await get_coordinator(hass, api)

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up RKI Covid numbers from a config entry."""
    # Forward the setup to the sensor platform.
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    return unload_ok


async def get_coordinator(hass: core.HomeAssistant, api: RKICovidAPI):
    """Get the data update coordinator."""
    if DOMAIN in hass.data:
        return hass.data[DOMAIN]

    async def async_get_districts():
        try:
            with async_timeout.timeout(10):
                return {case.county: case for case in await api.load_districts()}
        except (asyncio.TimeoutError, aiohttp.ClientError):
            raise update_coordinator.UpdateFailed

    hass.data[DOMAIN] = update_coordinator.DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_districts,
        update_interval=timedelta(hours=3),
    )
    await hass.data[DOMAIN].async_refresh()
    return hass.data[DOMAIN]
