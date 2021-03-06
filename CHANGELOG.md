# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.5.0] - 2021-04-18
### Added
- Added rki-covid-parser library as datasource

### Removed
- Removed 'corona-zahlen.org' as datasource after repeatedly outage

## [1.4.1] - 2021-02-15
### Added
- Added support for custom base url

## [1.4.0] - 2021-01-29
### Added
- Added state sensors and whole germany

## [1.3.0] - 2021-01-17
### Added
- Added new sensors (newCases, newDeaths, newRecovered)

### Changed
- Changed base url

### Removed
- Sensor (casesPerPopulation)

## [1.2.1] - 2020-12-21
### Changed
- Fixed error log when data update failed

## [1.2.0] - 2020-12-21
### Added
- HACS integration

## [1.1.0] - 2020-12-07
### Added
- Config setup flow for endusers
- Sensors (count, deaths, weekIncidence, casesPer100k, casesPerPopulation)
