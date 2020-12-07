"""Test the RKI Covid numbers integration config flow."""
from homeassistant import config_entries, setup

from custom_components.rki_covid.const import DOMAIN


async def test_form(hass):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"county": "LK München"},
    )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "LK München"
    assert result2["data"] == {
        "county": "LK München",
    }
    await hass.async_block_till_done()
