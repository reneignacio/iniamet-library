# INIAMET Examples

This directory contains practical examples demonstrating how to use the INIAMET library.

## 📋 Available Examples

### 1. `basic_usage.py`
**Basic operations with INIAMET**

Learn the fundamentals:
- Initialize the client
- Get station lists
- Filter by region
- Download data
- Basic statistics

```bash
python basic_usage.py
```

### 2. `regional_temperature.py`
**Regional temperature analysis**

Download and analyze temperature data for a specific region:
- Filter stations by region
- Download hourly temperature data
- Calculate regional statistics
- Export results

```bash
python regional_temperature.py
```

### 3. `multi_region_download.py`
**Multi-region data download**

Batch download data from multiple regions:
- Iterate over multiple regions
- Parallel data download
- Aggregate results
- Export to CSV

```bash
python multi_region_download.py
```

### 4. `station_map.py`
**Interactive station map**

Create an interactive map of all stations:
- Visualize station locations
- Filter by region
- Show current temperature
- Export to HTML

```bash
python station_map.py
```

**Note**: Requires visualization dependencies:
```bash
pip install iniamet[viz]
```

## 🔑 API Key Configuration

Before running any example, configure your API key:

```bash
# Option 1: Configuration file (recommended)
python -m iniamet.config set-key YOUR-API-KEY

# Option 2: Environment variable
export INIA_API_KEY='your-api-key'  # Linux/Mac
$env:INIA_API_KEY='your-api-key'    # Windows PowerShell
```

Get your API key from: https://agromet.inia.cl/api/v2/

## 📦 Requirements

Basic examples require only the core installation:
```bash
pip install iniamet
```

For visualization examples:
```bash
pip install iniamet[viz]
```

## 🎯 Quick Start

```bash
# 1. Install the library
pip install iniamet

# 2. Configure API key
python -m iniamet.config set-key YOUR-API-KEY

# 3. Run basic example
cd examples
python basic_usage.py
```

## 📚 Additional Resources

- [Documentation](../README.md)
- [Quick Reference](../docs/QUICK_REFERENCE.md)
- [Recipes](../docs/RECIPES.md)
- [API Reference](https://agromet.inia.cl/api/v2)

## 💡 Tips

- Examples create output files in the current directory
- Use `iniamet_cache/` is automatically created for caching
- All examples include error handling
- Check the source code for detailed comments

## 🆘 Troubleshooting

**API Key Error**:
```
RuntimeError: No API key configured
```
→ Configure your API key as shown above

**Import Error (visualization)**:
```
ModuleNotFoundError: No module named 'folium'
```
→ Install visualization dependencies: `pip install iniamet[viz]`

**No Data Found**:
- Check your internet connection
- Verify the station code is correct
- Try a different date range
