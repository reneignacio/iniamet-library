# INIAMET - Quick Reference Guide

## Installation

```bash
# From PyPI (when published)
pip install iniamet

# From source (development)
git clone <repository>
cd iniamet-library
pip install -e .
```

## Quick Start

```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

# Initialize
client = INIAClient()

# Get stations
stations = client.get_stations(region="R16")  # Ñuble

# Download data (v0.2.0+: use constants for readability)
data = client.get_data(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA,  # Recommended: named constant
    start_date="2024-09-01",
    end_date="2024-09-30"
)
```

## Common Variable IDs

| ID | Variable | Unit |
|----|----------|------|
| 2001 | Precipitación | mm |
| 2002 | Temperatura del Aire Media | °C |
| 2007 | Humedad Relativa Media | % |
| 2012 | Dirección del Viento | ° |
| 2013 | Velocidad Viento Media | m/s |
| 2014 | Velocidad Viento Máxima | m/s |
| 2022 | Radiación Media | W/m² |
| 2024 | Batería Voltaje Mínima | V |
| 2027 | Temperatura Suelo 10cm Media | °C |
| 2077 | Temperatura Superficie Media | °C |
| 2125 | Presión Atmosférica | mbar |

## Region Codes

| Code | Region |
|------|--------|
| R01 | Tarapacá |
| R02 | Antofagasta |
| R03 | Atacama |
| R04 | Coquimbo |
| R05 | Valparaíso |
| R06 | O'Higgins |
| R07 | Maule |
| R08 | Biobío |
| R09 | La Araucanía |
| R10 | Los Lagos |
| R11 | Aysén |
| R12 | Magallanes |
| R13 | Metropolitana |
| R14 | Los Ríos |
| R15 | Arica y Parinacota |
| R16 | Ñuble |

## Regional Download

```python
from iniamet import RegionalDownloader

# Download all data for a region
downloader = RegionalDownloader(region="R16")

df = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],
    aggregation='daily'
)

# Save to CSV
downloader.save_to_csv(df, "nuble_climate.csv")
```

## Advanced Features

### Caching

```python
# Enable caching (default)
client = INIAClient(cache=True, cache_dir="./cache")

# Disable caching
client = INIAClient(cache=False)

# Force update (bypass cache)
stations = client.get_stations(force_update=True)
```

### Bulk Downloads

```python
# Download multiple stations/variables
data = client.bulk_download(
    stations=["INIA-47", "INIA-139"],
    variables=[2002, 2001],
    start_date="2024-09-01",
    end_date="2024-09-30",
    delay=0.5  # seconds between requests
)

# Returns: {'INIA-47_2002': DataFrame, 'INIA-47_2001': DataFrame, ...}
```

### Data Aggregation

```python
from iniamet.data import DataDownloader

downloader = client.data_downloader

# Daily mean
df_daily = downloader.aggregate_daily(df, agg_func='mean')

# Daily temperature stats (min/max/mean)
df_temp = downloader.aggregate_temperature_daily(df)
```

### Station Filtering

```python
# By region
stations = client.get_stations(region="R16")

# By station type
inia_stations = client.get_stations(station_type="INIA")

# Combined
stations = client.get_stations(region="R16", station_type="INIA")
```

### Variable Validation

```python
from iniamet import VAR_TEMPERATURA_MEDIA, get_variable_info, is_valid_variable_id

# Check if variable exists for station
is_valid = client.validate_station_variable(
    station="INIA-47",
    variable=VAR_TEMPERATURA_MEDIA  # Or use: 2002 (both work!)
)

# Get variable info
info = get_variable_info(VAR_TEMPERATURA_MEDIA)
print(f"{info['nombre']}: {info['unidad']}")

# Validate variable ID
if is_valid_variable_id(2002):
    print("Valid variable!")

# ⚠️ BACKWARD COMPATIBILITY: Both forms work identically
var_id = 2002  # Old syntax
var_id = VAR_TEMPERATURA_MEDIA  # New syntax (recommended)
```

## Context Manager Usage

```python
from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

# Automatic cleanup
with INIAClient() as client:
    stations = client.get_stations()
    
    # Both syntaxes work!
    data = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA, "2024-09-01", "2024-09-30")
    # Or: data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
# Client automatically closed
```

## Error Handling

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

try:
    data = client.get_data("INVALID-STATION", 9999, "2024-01-01", "2024-01-31")
except Exception as e:
    print(f"Error: {e}")
```

## Performance Tips

1. **Use caching** for repeated queries
2. **Batch downloads** instead of individual requests
3. **Filter stations** before downloading to reduce API calls
4. **Use daily aggregation** when sub-daily data not needed
5. **Set appusing_variable_constants.py` - New v0.2.0 features demo
- `examples/backward_compatibility_demo.py` - Backward compatibility demonstration
- `examples/ropriate delays** in bulk downloads to avoid rate limiting

## Examples Directory

- `examples/basic_usage.py` - Basic client usage
- `examples/regional_download.py` - Regional bulk download

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=iniamet --cov-report=html

# Run specific test
pytest tests/test_api_client.py -v
```

## Troubleshooting

### Import errors
```bash
# Reinstall in development mode
pip install -e .
```

### No data returned
- Check if station code is correct
- Verify variable ID exists for station
- Confirm date range has available data
- Check API key is valid

### Slow performance
- Enable caching
- Reduce date range
- Use daily aggregation
- Check internet connection

## API Documentation

Official INIA API: https://agromet.inia.cl/api/v2

## Support

- GitHub Issues: [repository]/issues
- Email: data@inia.cl
- Documentation: https://iniamet.readthedocs.io
