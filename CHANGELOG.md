# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

---

## [1.2.0] - 2026-11-17

### Added

- Added `IMBALANCE_PERCENT` detection method.
- Added environmental imbalance detection between rooms.
- Added support for ventilation balancing use cases.
- Added imbalance metrics:
  - `imbalance`
  - `imbalance_percent`
- Added hysteresis support for all detection methods.
- Added new diagnostic attributes:
  - `hysteresis`
  - `activation_threshold`
  - `release_threshold`
  - `max_score`
- Added dynamic icons based on detection method.
- Added support for room-to-room CO2 balancing automation.

### Improved

- Refactored score calculation to provide a common `max_score` attribute across all methods.
- Improved diagnostics for imbalance detection by exposing the highest and lowest entities in the monitored group.
- Improved statistics reporting.
- Improved handling of outlier entity lists.

### Fixed

- Fixed `max_score` returning `null` when no outliers were detected.
- Fixed support for imbalance detection entity tracking.
- Fixed several Home Assistant 2026 compatibility issues.
- Fixed configuration flow translation loading issues.

---

## [1.1.0] - 2026-11-16

### Added

- Full Home Assistant UI configuration support.
- Config Flow support.
- Options Flow support.
- Dynamic reload of configuration without restarting Home Assistant.
- Unit consistency validation.
- Device registry support.
- Statistics sensor entity.
- Entity name translations.
- Home Assistant localization support.

### Added Detection Methods

- `MAD` (Median Absolute Deviation)
- `SIGMA` (Standard Deviation)
- `PERCENTAGE`
- `ABSOLUTE`

### Added Statistics

- Mean
- Median
- Standard deviation
- MAD
- Outlier count
- Outlier entities

### Improved

- Added robust outlier detection using Modified Z-Score.
- Improved support for small sensor groups.
- Added mixed-unit validation during configuration.

### Fixed

- Fixed UTF-8 translation file issues.
- Fixed Home Assistant thread-safety warnings.
- Fixed coordinator refresh handling.
- Fixed entity translation handling using `translation_key`.

---

## [1.0.0] - 2026-11-15

### Initial Release

### Features

- Binary sensor for anomaly detection.
- Monitoring of multiple Home Assistant sensor entities.
- Average value calculation.
- Detection of sensors deviating from the group.
- Support for:
  - Temperature
  - Humidity
  - CO2
  - Pressure
  - Any numeric sensor using a common unit of measurement.

### Initial Detection Methods

- Absolute deviation.
- Percentage deviation.

### Created Entities

- Binary sensor for anomaly detection.