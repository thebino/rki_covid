"""Test the RKI Covid numbers integration config flow."""
import os
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries, data_entry_flow, setup
from rki_covid_parser.parser import RkiCovidParser

from custom_components.rki_covid.const import DOMAIN

from . import MOCK_COUNTRY, MOCK_DISTRICTS, MOCK_STATES


def load_fixture(filename):
    """Load mock data as fixture."""
    path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(path, encoding="utf-8") as fptr:
        return fptr.read()


async def test_successful_config_flow(hass, aiohttp_client):
    """Test a successful config flow with mock data."""
    parser = RkiCovidParser(aiohttp_client)
    parser.load_data = AsyncMock(return_value=None)
    parser.districts = MOCK_DISTRICTS
    parser.states = MOCK_STATES
    parser.country = MOCK_COUNTRY
    with patch(
        "rki_covid_parser.parser.RkiCovidParser",
        return_value=parser,
    ):
        # Initialize a config flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        # Check that the config flow shows the user form
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "user"

        # Enter data into the config flow
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"county": "SK Amberg"},
        )

        # Validate the result
        assert result["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result["title"] == "SK Amberg"
        assert result["result"]


async def test_successful_form(hass, aiohttp_client):
    """Test a successful form with mock data."""
    parser = RkiCovidParser(aiohttp_client)
    parser.load_data = AsyncMock(return_value=None)
    parser.districts = MOCK_DISTRICTS
    parser.states = MOCK_STATES
    parser.country = MOCK_COUNTRY
    with patch(
        "rki_covid_parser.parser.RkiCovidParser",
        return_value=parser,
    ):
        # Setup persisten notifications (will be skipped through a fixture)
        await setup.async_setup_component(hass, "persistent_notification", {})

        # Initialize a config flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        # Check that the config flow
        assert result["type"] == "form"
        assert result["errors"] == {}

        # Enter data into the config flow
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"county": "SK Amberg"},
        )

        # Validate the result
        assert result2["type"] == "create_entry"
        assert result2["title"] == "SK Amberg"
        assert result2["data"] == {"county": "SK Amberg"}
        await hass.async_block_till_done()
