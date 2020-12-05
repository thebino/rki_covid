"""RKI Covid numbers integration."""
from homeassistant import config_entries, core

from custom_components.rki_covid.const import DOMAIN


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the component into HomeAssistant."""
    hass.data.setdefault(DOMAIN, {})

    # This setup is NOT necessary!
    # See `async_setup_platform` in `sensor.py`
    # This add support for multiple instances.

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(
        hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True
