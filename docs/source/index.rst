INIAMET Documentation
====================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://readthedocs.org/projects/iniamet/badge/?version=latest
   :target: https://iniamet.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**High-level Python library for accessing Chilean INIA (Instituto de Investigaciones Agropecuarias) agrometeorological station data.**

.. warning::
   **DISCLAIMER**: This is an **unofficial, community-developed library**. 
   It is **NOT officially affiliated with, endorsed by, or maintained by INIA** 
   (Instituto de Investigaciones Agropecuarias). This library accesses publicly 
   available data from INIA's agrometeorological API.

Access data from 400+ weather stations across Chile with a simple, intuitive API. Download temperature, precipitation, humidity, wind, radiation data and more.

Features
--------

* **High-Level API**: Simple, intuitive functions to query stations and download data
* **Smart Station Management**: Automatically handles different station code formats
* **Regional Filtering**: Filter stations by Chilean regions (R01-R16)
* **Data Caching**: Built-in caching system for faster repeated queries
* **Quality Control**: Comprehensive data validation and quality checks
* **Type Safety**: Full type hints for better IDE support
* **pandas Integration**: Returns data as pandas DataFrames
* **Visualization**: Interactive maps with folium (optional)

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install iniamet

API Key Configuration
~~~~~~~~~~~~~~~~~~~~~

Get your API key from https://agromet.inia.cl/api/v2/

**Option 1: Configuration file (Recommended)**

.. code-block:: bash

   python -m iniamet.config set-key YOUR-API-KEY-HERE

**Option 2: Environment variable**

.. code-block:: bash

   # Linux/Mac
   export INIA_API_KEY='your-api-key-here'
   
   # Windows PowerShell
   $env:INIA_API_KEY='your-api-key-here'

**Option 3: Direct in code**

.. code-block:: python

   from iniamet import INIAClient
   client = INIAClient(api_key='your-api-key-here')

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   
   # Initialize client
   client = INIAClient()
   
   # Get all stations
   stations = client.get_stations()
   print(f"Total stations: {len(stations)}")
   
   # Filter by region (Ñuble)
   nuble_stations = client.get_stations(region="R16")
   
   # Get available variables for a station
   variables = client.get_variables("INIA-47")
   
   # Download data
   from datetime import datetime
   
   data = client.get_data(
       station="INIA-47",
       variable=2002,  # Air temperature
       start_date=datetime(2024, 9, 1),
       end_date=datetime(2024, 9, 30)
   )
   
   print(data.head())

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   installation
   quickstart
   configuration
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/client
   api/stations
   api/data
   api/qc
   api/regional
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Additional Information
   
   regions
   variables
   changelog
   contributing
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
