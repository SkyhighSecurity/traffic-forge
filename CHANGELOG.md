# Changelog

All notable changes to this project will be documented in this file.

## [1.0.6] - 2025-01-06

### Changed
- Removed devTime field from LEEF formatter (replaced by separate date, time, and timestamp fields)
- Removed rt field from CEF formatter (replaced by separate date, time, and timestamp fields)

### Added
- Dockerfile now dynamically reads version from VERSION file
- Docker build script automatically tags images with version number
- Docker entrypoint displays version from VERSION file

## [1.0.5] - 2025-01-06

### Added
- Added separate date field (YYYY-MM-DD format) to LEEF formatter
- Added separate time field (HH:MM:SS.mmm format) to LEEF formatter  
- Added Unix timestamp field (epoch seconds) to LEEF formatter
- Added deviceCustomDate1 field for date in CEF formatter
- Added deviceCustomString1 field for time in CEF formatter
- Added deviceCustomNumber1 field for Unix timestamp in CEF formatter

### Changed
- Updated CEF formatter to use flexString2 for risk level (was flexString1)
- Adjusted CEF custom field indexing to accommodate new timestamp fields

## [1.0.4] - 2025-01-06

### Fixed
- Fixed LEEF formatting to include proper tab separator between header and first field (devTime)
- Corrected LEEF format examples in README documentation

### Changed
- Updated LEEF formatter to comply with LEEF 2.0 specification for field separation

## [1.0.3] - Previous releases

See git history for previous changes.