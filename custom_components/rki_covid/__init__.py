"""RKI Covid numbers integration."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
from homeassistant import config_entries, core
from homeassistant.helpers import update_coordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from rki_covid_parser.parser import RkiCovidParser

from custom_components.rki_covid.const import DOMAIN
from custom_components.rki_covid.data import DistrictData

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the component into HomeAssistant."""
    _LOGGER.debug("setup component.")
    parser = RkiCovidParser(async_get_clientsession(hass))

    # Make sure coordinator is initialized.
    await get_coordinator(hass, parser)

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up component from a config entry."""
    _LOGGER.debug("setup component from config entry.")
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
    _LOGGER.debug("init#async_unload_entry()")
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    return unload_ok


async def get_coordinator(hass: core.HomeAssistant, parser: RkiCovidParser):
    """Get the data update coordinator."""
    _LOGGER.debug("initialize the data coordinator.")
    if DOMAIN in hass.data:
        return hass.data[DOMAIN]

    async def async_get_districts():
        """Fetch data from rki-covid-parser library.

        Here the data for each district is loaded.
        """
        _LOGGER.debug("fetch data from rki-covid-parser.")
        try:
            with async_timeout.timeout(10):
                # return {case.county: case for case in await api.load_districts()}
                await parser.load_data()

                items = {}

                # districts
                for d in parser.districts:
                    district = parser.districts[d]

                    items[district.county] = DistrictData(
                        district.name,
                        district.county,
                        district.state,
                        district.population,
                        district.cases,
                        district.deaths,
                        district.casesPerWeek,
                        district.recovered,
                        district.weekIncidence,
                        district.casesPer100k,
                        district.newCases,
                        district.newDeaths,
                        district.newRecovered,
                        district.lastUpdate,
                    )

                # states
                for s in parser.states:
                    state = parser.states[s]
                    name = "BL " + state.name
                    items[name] = DistrictData(
                        name,
                        None,
                        None,
                        state.population,
                        state.cases,
                        state.deaths,
                        state.casesPerWeek,
                        state.recovered,
                        state.weekIncidence,
                        state.casesPer100k,
                        state.newCases,
                        state.newDeaths,
                        state.newRecovered,
                        state.lastUpdate,
                    )

                # country
                items["Deutschland"] = DistrictData(
                    "Deutschland",
                    None,
                    None,
                    parser.country.population,
                    parser.country.cases,
                    parser.country.deaths,
                    parser.country.casesPerWeek,
                    parser.country.recovered,
                    parser.country.weekIncidence,
                    parser.country.casesPer100k,
                    parser.country.newCases,
                    parser.country.newDeaths,
                    parser.country.newRecovered,
                    parser.country.lastUpdate,
                )

                return items

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            raise update_coordinator.UpdateFailed(
                f"Error reading data from rki-covid-parser: {err}"
            )

    hass.data[DOMAIN] = update_coordinator.DataUpdateCoordinator(
        hass,
        logging.getLogger(__name__),
        name=DOMAIN,
        update_method=async_get_districts,
        update_interval=timedelta(hours=3),
    )
    await hass.data[DOMAIN].async_refresh()
    return hass.data[DOMAIN]
