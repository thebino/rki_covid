# Robert-Koch Institut COVID Numbers

[![GitHub contributors](https://img.shields.io/github/contributors/thebino/rki_covid)](https://github.com/thebino/rki_covid/graphs/contributors)
![Version](https://img.shields.io/github/v/release/thebino/rki_covid)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

The `rki_covid` component is a Home Assistant custom sensor for monitoring regional covid numbers in Germany.


## Installation
### Install with HACS (recommended)
1. Ensure that [HACS](https://community.home-assistant.io/t/custom-component-hacs) is installed.
2. Search for and install the "RKI Covid numbers" integration.
3. Configure the `rki_covid` sensor.
4. Restart Home Assistant.

#### Install manually
1. Download the [latest release](https://github.com/thebino/rki_covid/releases/latest).
2. Unpack the release and copy the `custom_components/rki_covid` directory
   into the `<config dir>/custom_components` directory of your Home Assistant installation.
3. Configure the `rki_covid` sensor.
4. Restart Home Assistant.


## Configure
Add a new integration via `Configuration > Integration` and select your district to monitor.
You can add multiple integrations for different districts.

Each district will add `5 Entities` wich can be added to the Lovelace UI.


## Entities
This integration creates entities in the format `DOMAIN.NAME_entity`.

|Sensor  |Type|Description
|:-----------|:---|:------------
|`sensor.NAME_count`| number | indicates the confirmed cases.
|`sensor.NAME_deaths`| number | indicates the numbers of confirmed death cases.
|`sensor.NAME_weekIncidence`| number | indicates the week incidence per 100.000 inhabitants.
|`sensor.NAME_casesPer100k`| number | indicates cases per 100k.
|`sensor.NAME_casesPerPopulation`| number | indicates cases per population.


## Contribution
See [Contribution](CONTRIBUTING.md) for details.
