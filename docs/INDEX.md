# INIAMET Documentation Index

This is the master index for all INIAMET library documentation. Use this to quickly find information about any aspect of the library.

---

## 📚 Quick Access Links

### For Getting Started
- **[README.md](../README.md)** - Main documentation with installation and basic usage
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference guide with common operations
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** - Best practices and code patterns (NEW in v0.2.0)
- **[BACKWARD_COMPATIBILITY.md](BACKWARD_COMPATIBILITY.md)** - **Your old code keeps working forever!**

### For Development
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute to the project
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes

### For Recipes and Examples
- **[RECIPES.md](RECIPES.md)** - Code recipes for common tasks (English)
- **[RECETAS.md](RECETAS.md)** - Recetas de código para tareas comunes (Español)
- **[Examples Directory](../examples/)** - Working code examples

### Language-Specific
- **[README_ES.md](README_ES.md)** - Documentación en español
- **[MULTILANGUAGE.md](MULTILANGUAGE.md)** - Multi-language support information

### Security
- **[SECURITY.md](../SECURITY.md)** - Security policy and vulnerability reporting

---

## 🎯 Quick Navigation by Topic

### Variables and Constants

**Where to find variable information:**
- **Variable ID Constants**: [`src/iniamet/utils.py`](../src/iniamet/utils.py#L28-L55)
- **Variable Metadata**: [`src/iniamet/utils.py`](../src/iniamet/utils.py#L60-L126)
- **Quick Reference Table**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md#common-variable-ids)

**Key Constants:**
```python
from iniamet import (
    VAR_PRECIPITACION,           # 2001
    VAR_TEMPERATURA_MEDIA,       # 2002
    VAR_HUMEDAD_RELATIVA,        # 2007
    VAR_VIENTO_DIRECCION,        # 2012
    VAR_VIENTO_VELOCIDAD_MEDIA,  # 2013
    VAR_VIENTO_VELOCIDAD_MAXIMA, # 2014
    VAR_RADIACION_MEDIA,         # 2022
    VAR_BATERIA_VOLTAJE,         # 2024
    VAR_TEMPERATURA_SUELO_10CM,  # 2027
    VAR_TEMPERATURA_SUPERFICIE,  # 2077
    VAR_PRESION_ATMOSFERICA,     # 2125
)
```

**Helper Functions:**
```python
from iniamet import (
    list_all_variables,      # List all available variables
    get_variable_info,       # Get detailed info about a variable
    get_variable_id_by_name, # Search variable by name
    is_valid_variable_id,    # Validate variable ID
)
```

### Core Classes and Functions

#### INIAClient (Main API)
- **Source**: [`src/iniamet/client.py`](../src/iniamet/client.py)
- **Documentation**: [QUICK_REFERENCE.md - Basic Usage](QUICK_REFERENCE.md#basic-usage)
- **Example**: [`examples/basic_usage.py`](../examples/basic_usage.py)

**Key Methods:**
- `get_stations(region=None)` - Get station list
- `get_variables(station)` - Get available variables for a station
- `get_data(station, variable, start_date, end_date, aggregation=None)` - Download data
- `bulk_download()` - Download multiple stations/variables

#### DataDownloader
- **Source**: [`src/iniamet/data.py`](../src/iniamet/data.py)
- **Used by**: INIAClient (internal)
- **Features**: Caching, aggregation, bulk downloads

#### RegionalDownloader
- **Source**: [`src/iniamet/regional.py`](../src/iniamet/regional.py)
- **Documentation**: [RECIPES.md - Regional Downloads](RECIPES.md#regional-data-downloads)
- **Examples**: 
  - [`examples/regional_temperature.py`](../examples/regional_temperature.py)
  - [`examples/multi_region_download.py`](../examples/multi_region_download.py)

**Usage:**
```python
from iniamet import RegionalDownloader

downloader = RegionalDownloader("R16")  # Ñuble region
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],
    aggregation='daily'
)
```

#### Quality Control (QC)
- **Source**: [`src/iniamet/qc.py`](../src/iniamet/qc.py)
- **Documentation**: [RECIPES.md - Quality Control](RECIPES.md#quality-control)
- **Example**: [`examples/regional_temperature.py`](../examples/regional_temperature.py#L60-L70)

**Usage:**
```python
from iniamet import apply_quality_control, get_qc_report

# Apply QC
clean_data = apply_quality_control(data, 'temperatura')

# Get detailed report
report = get_qc_report(data, 'temperatura')
print(f"Valid records: {report['valid_percentage']:.1f}%")
```

#### Visualization
- **Source**: [`src/iniamet/visualization.py`](../src/iniamet/visualization.py)
- **Requirements**: Install with `pip install iniamet[viz]`
- **Example**: [`examples/station_map.py`](../examples/station_map.py)

**Functions:**
- `plot_station_map()` - Create interactive station map
- `plot_temperature_map()` - Temperature heatmap
- `quick_temp_map()` - One-line temperature map creation

### Regions

**Region Codes:**
- **Constant**: `REGION_MAP` in [`src/iniamet/utils.py`](../src/iniamet/utils.py#L9-L26)
- **Quick Reference**: [QUICK_REFERENCE.md - Region Codes](QUICK_REFERENCE.md#region-codes)

**Helper Functions:**
```python
from iniamet import get_region_name, get_region_code

name = get_region_name("R16")  # "Ñuble"
code = get_region_code("Ñuble")  # "R16"
```

---

## 📖 Documentation for Different Audiences

### For Beginners
1. Start with [README.md](../README.md) for installation
2. Follow [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for basic operations
3. Try [examples/basic_usage.py](../examples/basic_usage.py)
4. Read [BEST_PRACTICES.md](BEST_PRACTICES.md) to learn proper patterns

### For Researchers
1. Read [RECIPES.md](RECIPES.md) for common analysis patterns
2. Check [Quality Control documentation](RECIPES.md#quality-control)
3. Use [regional_temperature.py](../examples/regional_temperature.py) as template
4. Review [aggregation options](BEST_PRACTICES.md#aggregation-examples)

### For Data Scientists
1. Review [pandas integration](RECIPES.md#working-with-data)
2. Check [bulk download patterns](RECIPES.md#bulk-downloads)
3. Use [multi_region_download.py](../examples/multi_region_download.py) for large-scale downloads
4. Review [visualization options](RECIPES.md#visualization)

### For LLMs/AI Assistants
1. **Primary Reference**: [BEST_PRACTICES.md](BEST_PRACTICES.md) - Shows correct patterns
2. **Constants Definition**: [`src/iniamet/utils.py`](../src/iniamet/utils.py#L28-L126)
3. **Type Hints**: All functions have complete type annotations
4. **Docstrings**: All public functions have detailed docstrings with examples
5. **Examples**: [`examples/using_variable_constants.py`](../examples/using_variable_constants.py) shows all new features

**Key Patterns for LLMs:**
```python
# ✅ CORRECT: Use named constants
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
data = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2024-09-01", "2024-09-30")

# ❌ AVOID: Magic numbers (but still works for backward compatibility)
data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")

# ✅ CORRECT: Use aggregation parameter
daily_data = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, 
                             "2024-09-01", "2024-09-30", aggregation='D')

# ✅ CORRECT: Discover variables programmatically
from iniamet import list_all_variables, get_variable_id_by_name
all_vars = list_all_variables()
temp_id = get_variable_id_by_name("temperatura")  # Returns 2002
```

### For Contributors
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Check [project structure](../README.md#project-structure)
3. Review [CHANGELOG.md](../CHANGELOG.md) for version history
4. Follow [BEST_PRACTICES.md](BEST_PRACTICES.md) patterns

---

## 🗂️ Complete File Structure

```
iniamet-library/
├── README.md                    # Main documentation
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guide
├── SECURITY.md                  # Security policy
├── LICENSE                      # MIT License
├── pyproject.toml              # Package configuration
├── setup.py                     # Setup script
├── requirements.txt             # Dependencies
│
├── docs/                        # Documentation
│   ├── INDEX.md                # THIS FILE - Documentation index
│   ├── QUICK_REFERENCE.md      # Quick reference guide
│   ├── BEST_PRACTICES.md       # Best practices (NEW v0.2.0)
│   ├── RECIPES.md              # Code recipes (English)
│   ├── RECETAS.md              # Recetas (Español)
│   ├── README_ES.md            # Documentación en español
│   └── MULTILANGUAGE.md        # Multi-language support
│
├── src/iniamet/                # Main package
│   ├── __init__.py             # Package exports (includes constants)
│   ├── client.py               # INIAClient (main API)
│   ├── api_client.py           # Low-level API client
│   ├── data.py                 # DataDownloader (with aggregation)
│   ├── stations.py             # StationManager
│   ├── regional.py             # RegionalDownloader
│   ├── cache.py                # CacheManager
│   ├── qc.py                   # Quality Control
│   ├── utils.py                # Utilities (CONSTANTS, helpers)
│   ├── config.py               # Configuration management
│   └── visualization.py        # Visualization functions
│
├── examples/                    # Working examples
│   ├── basic_usage.py          # Basic example
│   ├── using_variable_constants.py  # NEW: Best practices demo
│   ├── regional_temperature.py # Regional download
│   ├── multi_region_download.py # Multi-region download
│   ├── station_map.py          # Visualization example
│   └── ...                     # More examples
│
└── tests/                       # Test suite
    ├── test_client.py
    ├── test_data.py
    ├── test_stations.py
    ├── test_qc.py
    └── test_utils.py
```

---

## 🔍 Search by Keyword

### Data Download
- Single station: [`INIAClient.get_data()`](QUICK_REFERENCE.md#downloading-data)
- Multiple stations: [`INIAClient.bulk_download()`](RECIPES.md#bulk-downloads)
- Regional: [`RegionalDownloader`](RECIPES.md#regional-data-downloads)
- With aggregation: [Aggregation Examples](BEST_PRACTICES.md#aggregation-examples)

### Stations
- List all: [`client.get_stations()`](QUICK_REFERENCE.md#getting-stations)
- By region: [`client.get_stations(region="R16")`](QUICK_REFERENCE.md#getting-stations)
- Variables for station: [`client.get_variables()`](QUICK_REFERENCE.md#getting-variables)

### Variables
- List all: [`list_all_variables()`](BEST_PRACTICES.md#list-all-variables)
- Get info: [`get_variable_info()`](BEST_PRACTICES.md#get-variable-information)
- Find by name: [`get_variable_id_by_name()`](BEST_PRACTICES.md#search-by-name-fuzzy)
- Constants: [Variable Constants](QUICK_REFERENCE.md#common-variable-ids)

### Quality Control
- Apply QC: [`apply_quality_control()`](RECIPES.md#quality-control)
- Get report: [`get_qc_report()`](RECIPES.md#quality-control)
- QC class: [`QualityControl`](../src/iniamet/qc.py)

### Visualization
- Station map: [`plot_station_map()`](RECIPES.md#visualization)
- Temperature map: [`plot_temperature_map()`](RECIPES.md#visualization)
- Quick map: [`quick_temp_map()`](RECIPES.md#visualization)

### Aggregation
- Daily: `aggregation='D'` or `aggregation='daily'`
- Weekly: `aggregation='W'`
- Monthly: `aggregation='M'`
- Hourly: `aggregation='H'`
- See [Aggregation Guide](BEST_PRACTICES.md#aggregation-examples)

### Configuration
- Set API key: [`python -m iniamet.config set-key`](README.md#api-key-configuration)
- Config file location: `~/.iniamet/config`
- Environment variable: `INIA_API_KEY`

---

## 📝 Version Information

- **Current Version**: 0.2.0 (January 21, 2026)
- **Changes**: See [CHANGELOG.md](../CHANGELOG.md)
- **Migration Guide**: See [BEST_PRACTICES.md - Migration Guide](BEST_PRACTICES.md#migration-guide)

---

## 🆘 Getting Help

- **Issues**: Report bugs at GitHub Issues
- **Questions**: Check [RECIPES.md](RECIPES.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Examples**: See [examples/](../examples/) directory
- **API Reference**: See docstrings in source code

---

## 🔄 Quick Links to Common Tasks

| Task | Documentation | Example Code |
|------|---------------|--------------|
| Install library | [README.md](../README.md#installation) | `pip install iniamet` |
| Configure API key | [README.md](../README.md#api-key-configuration) | `python -m iniamet.config set-key YOUR-KEY` |
| Download temperature | [QUICK_REFERENCE.md](QUICK_REFERENCE.md#downloading-data) | [basic_usage.py](../examples/basic_usage.py) |
| Use constants | [BEST_PRACTICES.md](BEST_PRACTICES.md) | [using_variable_constants.py](../examples/using_variable_constants.py) |
| Regional download | [RECIPES.md](RECIPES.md#regional-data-downloads) | [regional_temperature.py](../examples/regional_temperature.py) |
| Apply QC | [RECIPES.md](RECIPES.md#quality-control) | [regional_temperature.py](../examples/regional_temperature.py#L60) |
| Create map | [RECIPES.md](RECIPES.md#visualization) | [station_map.py](../examples/station_map.py) |
| Aggregate data | [BEST_PRACTICES.md](BEST_PRACTICES.md#aggregation-examples) | [using_variable_constants.py](../examples/using_variable_constants.py) |

---

*Last updated: January 21, 2026 (v0.2.0)*
