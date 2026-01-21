# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-21

### Added ✨
- **Variable ID Constants**: Named constants for all variables (e.g., `VAR_TEMPERATURA_MEDIA`, `VAR_PRECIPITACION`)
- **Aggregation Support in INIAClient**: `get_data()` now supports temporal aggregation (daily, weekly, monthly)
- **Helper Functions for Variable Discovery**:
  - `list_all_variables()`: Get DataFrame with all available variables
  - `get_variable_id_by_name()`: Find variable ID by name (fuzzy search)
  - `is_valid_variable_id()`: Validate if a variable ID exists
  - `get_variable_info()`: Get metadata for a specific variable
- **Enhanced Documentation**: Complete docstrings with examples for all public functions
- **Best Practices Guide**: New documentation file explaining improvements ([docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md))
- **Example Scripts**: 
  - `examples/using_variable_constants.py` - Comprehensive v0.2.0 features demo
  - `examples/backward_compatibility_demo.py` - Demonstrates backward compatibility
- **Test Suite**: `tests/test_backward_compatibility.py` - Automated compatibility tests

### ✅ Backward Compatibility

**ZERO BREAKING CHANGES** - All v0.1.x code continues working indefinitely:

- ✅ Old syntax (magic numbers like `2002`) still works
- ✅ New syntax (constants like `VAR_TEMPERATURA_MEDIA`) works identically
- ✅ Both syntaxes can be mixed in the same project
- ✅ All features support both syntaxes (aggregation, caching, regional downloads, etc.)
- ✅ **No migration required** - Use constants for new code, keep existing code as-is

```python
# ✅ OLD (v0.1.x) - Still works forever!
client.get_data('INIA-47', 2002, '2024-01-01', '2024-01-31')

# ✅ NEW (v0.2.0+) - More readable (recommended)
client.get_data('INIA-47', VAR_TEMPERATURA_MEDIA, '2024-01-01', '2024-01-31')
```

### Changed 🔄
- **Corrected Variable IDs**: Fixed mapping to match INIA API v2 response
  - 2001: Precipitación (was incorrectly Humedad Relativa)
  - 2007: Humedad Relativa Media (was incorrectly Presión Atmosférica)
  - 2125: Presión Atmosférica (was not mapped)
- **Updated VARIABLE_INFO**: Expanded to include all 11 variables from API
- **RegionalDownloader**: Now uses constants and delegates aggregation to `INIAClient`
- **Improved Type Hints**: More complete and accurate type annotations
- **Better Examples**: Updated all examples to use new constants and best practices

### Fixed 🐛
- Variable ID mappings now match actual INIA API v2 response structure
- Temperature aggregation now properly returns `valor_min`, `valor_max`, `valor_media`
- Precipitation aggregation uses sum instead of mean
- Cache now only stores raw data (not aggregated data)

### Documentation 📚
- Added comprehensive variable constant documentation
- Improved docstrings with clear parameter descriptions
- Added migration guide for existing code
- Examples now demonstrate self-documenting code practices

## [Unreleased]

### Fixed
- Made IPython and folium optional dependencies for visualization
- Visualization module now imports gracefully if dependencies not installed
- Fixed test failures in CI/CD by adding API key environment variable
- Updated all GitHub URLs to point to correct repository (reneignacio/iniamet-library)
- Added conftest.py to automatically set test API key for CI

### Changed
- Moved visualization dependencies to optional `[viz]` extra
- Install with `pip install iniamet[viz]` to use visualization features
- Updated installation instructions in README

### Security
- **BREAKING CHANGE**: Removed hardcoded API key for security
- Users must now configure their own API key (see README)
- Added three methods for API key configuration:
  1. Config file (easiest): `python -m iniamet.config set-key YOUR-KEY`
  2. Environment variable: `INIA_API_KEY`
  3. Direct in code: `INIAClient(api_key='YOUR-KEY')`
- Added helpful error messages when API key is not configured
- Config file stored with restrictive permissions

## [0.1.0] - 2025-11-07

### Added
- Initial release of INIAMET library
- `INIAClient` high-level API for station data access
- `RegionalDownloader` for bulk regional data downloads
- `QualityControl` module with comprehensive data validation
  - Extreme value checks (WMO standards)
  - Stuck sensor detection (persistence test)
  - Temporal consistency validation
  - Suspicious zero detection
- `Visualization` module with Folium-based mapping
  - Station location maps
  - Temperature heatmaps
  - Interactive popup information
- Smart station code handling (10 different network types)
- Regional filtering by Chilean regions (R01-R16)
- Built-in caching system for faster repeated queries
- Type hints throughout the codebase
- pandas DataFrame integration
- Automated temperature download examples
  - Regional multi-station downloader
  - Configurable date ranges
  - Hourly vs 15-minute data options
  - Automatic quality control integration
  - CSV export with 2-decimal precision

### Supported Features
- **Station Management**: Query 400+ stations across Chile
- **Variables**: Temperature, precipitation, humidity, wind, radiation, pressure
- **Regions**: All 16 Chilean regions supported
- **Data Formats**: pandas DataFrames, CSV export
- **Quality Control**: 4-level validation system
- **Caching**: Local file-based cache for offline access
- **Visualization**: Interactive HTML maps with Folium

### Dependencies
- requests >= 2.28.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- folium >= 0.14.0

### Known Issues
- Folium HeatMap temporarily disabled due to compatibility issue
- API key hardcoded (will be moved to environment variable in 0.2.0)

### Documentation
- Complete README with examples
- Quick Reference guide
- Recipe collection for common tasks
- Function reference documentation

[Unreleased]: https://github.com/yourusername/iniamet/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/iniamet/releases/tag/v0.1.0
