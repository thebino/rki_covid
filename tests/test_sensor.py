"""Test the RKI Covide numbers integration sensor."""

import os
from unittest.mock import AsyncMock, patch

from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry
from rki_covid_parser.const import (
    DISTRICTS_URL,
    DISTRICTS_URL_NEW_CASES,
    DISTRICTS_URL_NEW_DEATHS,
    DISTRICTS_URL_NEW_RECOVERED,
    DISTRICTS_URL_RECOVERED,
    VACCINATIONS_URL,
)

from custom_components.rki_covid.const import DOMAIN


def load_fixture(filename):
    """Load mock data as fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


async def test_sensor_without_data_coordinator(hass):
    """Test sensor when data coordinator could not be initialized."""
    async_mock = AsyncMock(return_value=None)
    with patch('custom_components.rki_covid.get_coordinator', side_effect=async_mock):
        entry = MockConfigEntry(domain=DOMAIN, data={"county": "SK Amberg"})
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()


async def test_sensor_with_mock_data(hass, aioclient_mock):
    """Test sensor setup with mock data."""
    aioclient_mock.get(DISTRICTS_URL, text=load_fixture("districts.json"))
    aioclient_mock.get(DISTRICTS_URL_RECOVERED, text=load_fixture("recovered.json"))
    aioclient_mock.get(VACCINATIONS_URL, text=load_fixture("germany_vaccinations_by_state.tsv"))
    aioclient_mock.get(DISTRICTS_URL_NEW_CASES, text=load_fixture("new_cases.json"))
    aioclient_mock.get(DISTRICTS_URL_NEW_RECOVERED, text=load_fixture("new_recovered.json"))
    aioclient_mock.get(DISTRICTS_URL_NEW_DEATHS, text=load_fixture("new_deaths.json"))

    entry = MockConfigEntry(domain=DOMAIN, data={"county": "SK Amberg"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.sk_amberg_count")

    assert state
    assert state.state == "1337"


async def test_async_setup(hass):
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True


async def test_sensor_with_invalid_config_entry(hass, aioclient_mock):
    """Test sensor with an invalid config entry should fail with exception."""
    aioclient_mock.get(DISTRICTS_URL, text=load_fixture("districts.json"))
    aioclient_mock.get(DISTRICTS_URL_RECOVERED, text=load_fixture("recovered.json"))
    aioclient_mock.get(VACCINATIONS_URL, text=load_fixture("germany_vaccinations_by_state.tsv"))
    aioclient_mock.get(DISTRICTS_URL_NEW_CASES, text=load_fixture("new_cases.json"))
    aioclient_mock.get(DISTRICTS_URL_NEW_RECOVERED, text=load_fixture("new_recovered.json"))
    aioclient_mock.get(DISTRICTS_URL_NEW_DEATHS, text=load_fixture("new_deaths.json"))

    entry = MockConfigEntry(domain=DOMAIN, data={"county": "SK Invalid"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
