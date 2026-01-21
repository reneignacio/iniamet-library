# INIAMET Examples - Complete Guide

This directory contains working examples demonstrating various features of the INIAMET library.

## 📋 Example Index

### 🟢 Beginner Examples

#### 1. **[basic_usage.py](basic_usage.py)** ⭐ START HERE
**What it does:**
- Initialize INIAMET client
- List all stations and filter by region
- Get available variables for a station
- Download temperature data
- Basic statistical analysis

**Usage:**
```bash
python examples/basic_usage.py
```

**Learn:** Basic client initialization, station queries, simple data download, using variable constants (VAR_TEMPERATURA_MEDIA)

---

#### 2. **[using_variable_constants.py](using_variable_constants.py)** ⭐ NEW in v0.2.0
**What it does:**
- Demonstrates all new features in v0.2.0
- Show how to use named constants instead of magic numbers
- Examples of temporal aggregation (daily, weekly, monthly)
- Variable discovery functions

**Usage:**
```bash
python examples/using_variable_constants.py
```

**Learn:** Using VAR_* constants, `list_all_variables()`, `get_variable_info()`, `get_variable_id_by_name()`, temporal aggregation

---

### 🟡 Intermediate Examples

#### 3. **[regional_temperature.py](regional_temperature.py)**
**What it does:** Download temperature data for an entire region with quality control

**Usage:**
```bash
python examples/regional_temperature.py
```

**Learn:** RegionalDownloader class, quality control application, bulk data handling, CSV export

---

#### 4. **[multi_region_download.py](multi_region_download.py)**
**What it does:** Automated script for downloading data from multiple regions with command-line arguments

**Usage:**
```bash
# Default configuration
python examples/multi_region_download.py

# Specific region and dates
python examples/multi_region_download.py R16 2025-01-01 2025-01-31
```

**Learn:** Command-line argument parsing, multi-region batch processing, error handling for large downloads

---

### 🟠 Advanced Examples

#### 5. **[station_map.py](station_map.py)** (Requires viz extras)
**What it does:** Create interactive map of stations with folium

**Requirements:**
```bash
pip install iniamet[viz]
```

**Usage:**
```bash
python examples/station_map.py
```

---

## 🎯 Quick Navigation by Use Case

### I want to...

**...learn the basics** → [basic_usage.py](basic_usage.py)

**...see the new v0.2.0 features** → [using_variable_constants.py](using_variable_constants.py)

**...download data for one region** → [regional_temperature.py](regional_temperature.py)

**...download data for multiple regions** → [multi_region_download.py](multi_region_download.py)

**...create a map of stations** → [station_map.py](station_map.py)

**...apply quality control** → [regional_temperature.py](regional_temperature.py)

**...use temporal aggregation** → [using_variable_constants.py](using_variable_constants.py)

---

## 🔧 Prerequisites

1. **Install INIAMET:**
```bash
pip install iniamet
# Or for visualization examples:
pip install iniamet[viz]
```

2. **Configure API Key:**
```bash
python -m iniamet.config set-key YOUR-API-KEY
```

3. **Run any example:**
```bash
python examples/basic_usage.py
```

---

## 🆕 What's New in v0.2.0

The [using_variable_constants.py](using_variable_constants.py) example demonstrates:
- ✨ Named constants (VAR_TEMPERATURA_MEDIA, VAR_PRECIPITACION, etc.)
- ✨ Built-in aggregation (daily, weekly, monthly)
- ✨ Variable discovery functions
- ✨ Improved documentation

---

## 📚 Additional Resources

- **[Main Documentation](../README.md)**
- **[Documentation Index](../docs/INDEX.md)**
- **[Quick Reference](../docs/QUICK_REFERENCE.md)**
- **[Best Practices](../docs/BEST_PRACTICES.md)**

---

*For questions, please check the [main documentation](../README.md) or open an issue on GitHub.*
