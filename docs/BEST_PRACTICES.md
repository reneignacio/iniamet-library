# Best Practices Guide for INIAMET Library

## Overview of Improvements

This guide explains the improvements made to the INIAMET library to make it more maintainable, readable, and LLM-friendly.

---

## Problem 1: Magic Numbers

### ❌ Before (Bad Practice)
```python
# What does 2002 mean? You have to look it up every time
data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
```

### ✅ After (Good Practice)
```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

# Self-documenting! Clear what variable you're downloading
data = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2024-09-01", "2024-09-30")
```

---

## Problem 2: Limited Aggregation Support

### ❌ Before (Bad Practice)
```python
# Only RegionalDownloader had aggregation
# INIAClient.get_data() didn't support it
downloader = RegionalDownloader("R16")
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature'],
    aggregation='daily'
)
```

### ✅ After (Good Practice)
```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

# Now INIAClient.get_data() supports aggregation directly!
client = INIAClient()
data = client.get_data(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA,
    start_date="2024-09-01",
    end_date="2024-09-30",
    aggregation='D'  # Daily aggregation
)
```

---

## Problem 3: No Variable Discovery

### ❌ Before (Bad Practice)
```python
# No way to programmatically list variables
# Had to check documentation or API manually
```

### ✅ After (Good Practice)
```python
from iniamet import list_all_variables, get_variable_info, get_variable_id_by_name

# List all available variables
all_vars = list_all_variables()
print(all_vars)

# Get detailed info about a variable
info = get_variable_info(2002)
print(info['nombre'])  # 'Temperatura del Aire Media'
print(info['unidad'])  # '°C'

# Find variable by name (fuzzy search)
var_id = get_variable_id_by_name("temperatura")
print(var_id)  # 2002
```

---

## Problem 4: Inconsistent Documentation

### ❌ Before (Bad Practice)
```python
def get_data(self, station, variable, start_date, end_date):
    """Download time series data."""
    # Minimal documentation, no examples
```

### ✅ After (Good Practice)
```python
def get_data(
    self,
    station: str,
    variable: Union[int, str],
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    use_cache: bool = True,
    aggregation: Optional[str] = None
) -> pd.DataFrame:
    """
    Download time series data with optional aggregation.
    
    Args:
        station: Station code (e.g., "INIA-47")
        variable: Variable ID (e.g., VAR_TEMPERATURA_MEDIA) or name
        start_date: Start date (YYYY-MM-DD or datetime)
        end_date: End date (YYYY-MM-DD or datetime)
        use_cache: Use cached data if available (default: True)
        aggregation: Optional temporal aggregation:
            - None or 'raw': Return raw data (default)
            - 'D' or 'daily': Daily aggregation
            - 'W': Weekly, 'M': Monthly
            - Any pandas resample rule
        
    Returns:
        DataFrame with columns: tiempo, valor
        (valor_min, valor_max for temperature with aggregation)
        
    Example:
        >>> from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
        >>> client = INIAClient()
        >>> # Daily aggregated temperature
        >>> data = client.get_data(
        ...     station="INIA-47",
        ...     variable=VAR_TEMPERATURA_MEDIA,
        ...     start_date="2024-09-01",
        ...     end_date="2024-09-30",
        ...     aggregation='D'
        ... )
    """
```

---

## Available Variable Constants

All variable IDs are now available as named constants:

```python
from iniamet import (
    VAR_PRECIPITACION,              # 2001
    VAR_TEMPERATURA_MEDIA,          # 2002
    VAR_HUMEDAD_RELATIVA,           # 2007
    VAR_VIENTO_DIRECCION,           # 2012
    VAR_VIENTO_VELOCIDAD_MEDIA,     # 2013
    VAR_VIENTO_VELOCIDAD_MAXIMA,    # 2014
    VAR_RADIACION_MEDIA,            # 2022
    VAR_BATERIA_VOLTAJE,            # 2024
    VAR_TEMPERATURA_SUELO_10CM,     # 2027
    VAR_TEMPERATURA_SUPERFICIE,     # 2077
    VAR_PRESION_ATMOSFERICA,        # 2125
)
```

---

## Aggregation Examples

### Raw Data (15-minute intervals)
```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

client = INIAClient()
raw_data = client.get_data(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA,
    start_date="2024-09-01",
    end_date="2024-09-30"
    # No aggregation = raw data
)
```

### Daily Aggregation
```python
# Temperature: includes min, max, mean
daily_temp = client.get_data(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA,
    start_date="2024-09-01",
    end_date="2024-09-30",
    aggregation='D'
)
# Returns: tiempo, valor, valor_min, valor_max, valor_media
```

### Weekly Aggregation
```python
weekly_precip = client.get_data(
    station="INIA-47",
    variable=VAR_PRECIPITACION,
    start_date="2024-01-01",
    end_date="2024-12-31",
    aggregation='W'  # Weekly totals
)
```

### Monthly Aggregation
```python
monthly_humidity = client.get_data(
    station="INIA-47",
    variable=VAR_HUMEDAD_RELATIVA,
    start_date="2023-01-01",
    end_date="2024-12-31",
    aggregation='M'  # Monthly averages
)
```

---

## Regional Downloader Improvements

The `RegionalDownloader` now uses the same constants and delegates to `INIAClient.get_data()`:

```python
from iniamet import RegionalDownloader, VAR_TEMPERATURA_MEDIA

# Using string names (old way still works)
downloader = RegionalDownloader("R16")
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],  # String names
    aggregation='daily'
)

# Or use constants directly
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=[VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION],  # Direct IDs
    aggregation='daily'
)
```

---

## Helper Functions for Variable Discovery

### List All Variables
```python
from iniamet import list_all_variables

# Get a DataFrame with all available variables
all_vars = list_all_variables()
print(all_vars)
#    variable_id                       nombre unidad
# 0         2001                Precipitación     mm
# 1         2002   Temperatura del Aire Media     °C
# ...
```

### Get Variable Information
```python
from iniamet import get_variable_info, VAR_TEMPERATURA_MEDIA

info = get_variable_info(VAR_TEMPERATURA_MEDIA)
print(info)
# {
#     'nombre': 'Temperatura del Aire Media',
#     'unidad': '°C',
#     'color': 'red',
#     'descripcion': 'Temperatura del aire media'
# }
```

### Search by Name (Fuzzy)
```python
from iniamet import get_variable_id_by_name

# Exact match
var_id = get_variable_id_by_name("temperatura")
print(var_id)  # 2002

# Partial match
var_id = get_variable_id_by_name("viento")
print(var_id)  # 2012 (Dirección del Viento)

# Also works with accents
var_id = get_variable_id_by_name("precipitación")
print(var_id)  # 2001
```

### Validate Variable IDs
```python
from iniamet import is_valid_variable_id, VAR_TEMPERATURA_MEDIA

# Check if a variable ID is valid
print(is_valid_variable_id(VAR_TEMPERATURA_MEDIA))  # True
print(is_valid_variable_id(9999))  # False
```

---

## Benefits for LLMs and Documentation

### 1. **Self-Documenting Code**
```python
# LLMs can understand this immediately
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION

client = INIAClient()
temp = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2024-09-01", "2024-09-30")
precip = client.get_data("INIA-47", VAR_PRECIPITACION, "2024-09-01", "2024-09-30")
```

### 2. **Type Hints and Docstrings**
All functions now have:
- Complete type hints
- Detailed docstrings with examples
- Clear parameter descriptions
- Return type documentation

### 3. **Constants in Source**
All constants are defined in `utils.py` and imported in `__init__.py`:
```python
# Easy to find and understand
from iniamet.utils import (
    VAR_TEMPERATURA_MEDIA,
    VAR_PRECIPITACION,
    # ... all constants defined here
)
```

### 4. **Consistent API**
- `INIAClient.get_data()` now has the same capabilities as `RegionalDownloader`
- All aggregation logic is centralized in one place
- Easier to maintain and extend

---

## 4. Backward Compatibility

**Zero Breaking Changes** - INIAMET v0.2.0+ maintains **full backward compatibility** with v0.1.x.

### Both Syntaxes Work Indefinitely

```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

client = INIAClient()

# ✅ OLD SYNTAX (v0.1.x) - Still works!
data_old = client.get_data(
    station='INIA-47',
    variable=2002,  # Magic number
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# ✅ NEW SYNTAX (v0.2.0+) - Recommended
data_new = client.get_data(
    station='INIA-47',
    variable=VAR_TEMPERATURA_MEDIA,  # Named constant
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# Both produce IDENTICAL results
assert data_old.equals(data_new)  # ✅ True
```

### Mixing Syntaxes

You can mix both syntaxes in the same project:

```python
# ✅ Old code (legacy) - no need to change
temp = client.get_data(station, 2002, start, end)

# ✅ New code (recommended) - use for new features
precip = client.get_data(station, VAR_PRECIPITACION, start, end)
```

### All Features Support Both Syntaxes

```python
# Aggregation works with both
daily_old = client.get_data(station, 2002, start, end, aggregation='daily')
daily_new = client.get_data(station, VAR_TEMPERATURA_MEDIA, start, end, aggregation='daily')

# Regional downloads work with both
downloader.download_climate_data('Ñuble', 2002, start, end)  # Old
downloader.download_climate_data('Ñuble', VAR_TEMPERATURA_MEDIA, start, end)  # New
```

### Future-Proof Guarantee

✅ **Your existing code will work for years without changes**
✅ **No forced migration required**
✅ **Both syntaxes perform identically**
✅ **All features support both syntaxes**

💡 **Recommendation:**
- Keep existing code as-is (no need to update)
- Use named constants for NEW code (more readable)
- Gradually migrate when convenient (not required)

📝 **See also:** `examples/backward_compatibility_demo.py`

---

## 5. Migration Guide

**⚠️ Important:** Migration is **OPTIONAL**. Your old code will continue working indefinitely.

### If you were using magic numbers:
```python
# ✅ OLD - Still works! No need to change
data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")

# ✅ NEW - Recommended for new code (more readable)
from iniamet import VAR_TEMPERATURA_MEDIA
data = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2024-09-01", "2024-09-30")

# Both produce IDENTICAL results
```

### If you were using RegionalDownloader for single station:
```python
# OLD (RegionalDownloader was overkill for single station)
downloader = RegionalDownloader("R16")
data = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature'],
    aggregation='daily',
    station_filter=["INIA-47"]
)

# NEW (much simpler!)
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA
client = INIAClient()
data = client.get_data(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA,
    start_date="2024-09-01",
    end_date="2024-09-30",
    aggregation='D'
)
```

---

## Summary

The improvements make the INIAMET library:
1. ✅ **More readable** - Named constants instead of magic numbers
2. ✅ **More flexible** - Aggregation support in `INIAClient.get_data()`
3. ✅ **More discoverable** - Helper functions to explore variables
4. ✅ **Better documented** - Complete docstrings with examples
5. ✅ **LLM-friendly** - Clear relationships and consistent API
6. ✅ **Maintainable** - Single source of truth for variable definitions

**See `examples/using_variable_constants.py` for a complete working example!**
