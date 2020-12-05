"""Tests for the sensor module."""
from aiohttp import ClientError
from pytest_homeassistant.async_mock import AsyncMock, MagicMock

from custom_components.rki_covid.sensor import DistrictData, RKICovidNumbersSensor


async def test_async_update_failed():
    """Tests a failed async_update."""
    api = MagicMock()
    api.get_district = AsyncMock(side_effect=ClientError)

    sensor = RKICovidNumbersSensor(api, {"name": "Berlin"})
    await sensor.async_update()

    assert sensor.available is False
    assert sensor.name == "Berlin"
    assert sensor.unique_id == "Berlin"
    assert sensor.state is None
    assert {"district": "Berlin"} == sensor.attrs


async def test_async_update_success(hass, aioclient_mock):
    """Tests a successful async_update."""
    api = MagicMock()
    api.get_district = AsyncMock(
        side_effect=[
            # response
            DistrictData(
                name="München",
                county="Berlin-Mitte",
                count=30461,
                deaths=366,
                weekIncidence=178.409487503925,
                casesPer100k=2052.31548295206,
                casesPerPopulation=2.05231548295206,
                lastUpdate="02.12.2020, 00:00 Uhr",
            )
        ]
    )

    sensor = RKICovidNumbersSensor(api, {"name": "München"})
    await sensor.async_update()

    expected = {
        "district": "München",
        "county": "Berlin-Mitte",
        "count": 30461,
        "deaths": 366,
        "weekIncidence": 178.409487503925,
        "casesPer100k": 2052.31548295206,
        "casesPerPopulation": 2.05231548295206,
    }

    assert expected == sensor.attrs
    assert expected == sensor.device_state_attributes
    assert sensor.available is True
