"""Make the component configurable via the UI."""

import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from . import RKICovidAPI, get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RKICovidNumbersConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """RKI Covid numbers config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    _options = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Invoke when a user initiates a flow via the user interface."""
        api = RKICovidAPI(async_get_clientsession(self.hass))

        errors: Dict[str, str] = {}

        if self._options is None:
            # add default county as first item
            # self._options = {CONF_COUNTY: "LK Munich"}
            self._options = {}

            # add items from coordinator
            coordinator = await get_coordinator(self.hass, api)
            for case in sorted(coordinator.data.values(), key=lambda case: case.county):
                self._options[case.county] = case.county

        if user_input is not None:
            await self.async_set_unique_id(user_input["county"])
            self._abort_if_unique_id_configured()

            # User is done adding sensors, create the config entry.
            return self.async_create_entry(
                title=self._options[user_input["county"]], data=user_input
            )

        # Show user input for adding sensors.
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("county"): vol.In(self._options)}),
            errors=errors,
        )
