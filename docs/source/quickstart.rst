Quick Start
===========

This guide will help you get started with INIAMET in minutes.

Prerequisites
-------------

1. Python 3.8 or higher installed
2. INIAMET library installed (``pip install iniamet``)
3. API key from https://agromet.inia.cl/api/v2/

Step 1: Configure API Key
--------------------------

.. code-block:: bash

   python -m iniamet.config set-key YOUR-API-KEY-HERE

Verify it's saved:

.. code-block:: bash

   python -m iniamet.config show

Step 2: Get Station List
-------------------------

.. code-block:: python

   from iniamet import INIAClient
   
   # Initialize client
   client = INIAClient()
   
   # Get all stations
   stations = client.get_stations()
   print(f"Total stations: {len(stations)}")
   
   # View first few stations
   print(stations.head())

Output:

.. code-block:: text

   Total stations: 431
   
      codigo          nombre  latitud  longitud      region
   0  INIA-47        Chillán  -36.603   -71.912       Ñuble
   1  INIA-139         Talca  -35.432   -71.654       Maule
   ...

Step 3: Filter Stations
------------------------

By Region
~~~~~~~~~

.. code-block:: python

   # Get stations in Ñuble region
   nuble_stations = client.get_stations(region="R16")
   print(f"Ñuble stations: {len(nuble_stations)}")

By Network
~~~~~~~~~~

.. code-block:: python

   # Get only INIA stations
   inia_stations = client.get_stations(network="INIA")

Step 4: Get Available Variables
--------------------------------

.. code-block:: python

   # Get variables for a specific station
   variables = client.get_variables("INIA-47")
   
   # Display variables
   print(variables[['variable_id', 'nombre', 'unidad']].head(10))

Output:

.. code-block:: text

   variable_id                    nombre  unidad
   0         2001  Precipitación acumulada      mm
   1         2002      Temperatura del aire      °C
   2         2003      Humedad relativa (%)       %
   3         2004        Velocidad del viento    m/s
   ...

Step 5: Download Data
---------------------

Basic Download
~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime
   
   # Download temperature data
   data = client.get_data(
       station="INIA-47",
       variable=2002,  # Air temperature
       start_date=datetime(2024, 9, 1),
       end_date=datetime(2024, 9, 30)
   )
   
   print(f"Downloaded {len(data)} records")
   print(data.head())

Download Multiple Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Download temperature and precipitation
   temp_data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
   precip_data = client.get_data("INIA-47", 2001, "2024-09-01", "2024-09-30")

Step 6: Basic Analysis
-----------------------

.. code-block:: python

   # Calculate statistics
   print("Temperature Statistics:")
   print(f"Mean: {data['valor'].mean():.2f}°C")
   print(f"Min:  {data['valor'].min():.2f}°C")
   print(f"Max:  {data['valor'].max():.2f}°C")
   
   # Resample to daily average
   daily = data.set_index('tiempo').resample('D')['valor'].mean()
   print(daily)

Step 7: Quality Control
------------------------

.. code-block:: python

   from iniamet import apply_quality_control
   
   # Apply quality control
   clean_data = apply_quality_control(data, 'temperatura')
   
   # See removed records
   print(f"Original: {len(data)} records")
   print(f"Clean: {len(clean_data)} records")
   print(f"Removed: {len(data) - len(clean_data)} records")

Step 8: Regional Download
--------------------------

.. code-block:: python

   from iniamet import RegionalDownloader
   
   # Download all temperature data for a region
   downloader = RegionalDownloader(region="R16")
   
   result = downloader.download_climate_data(
       start_date="2024-09-01",
       end_date="2024-09-30",
       variables=['temperature'],
       aggregation='daily'
   )
   
   # Save to CSV
   result.to_csv("nuble_temperature_sept2024.csv")

Complete Example
----------------

Here's a complete workflow:

.. code-block:: python

   from iniamet import INIAClient, apply_quality_control
   from datetime import datetime
   import pandas as pd
   
   # Initialize
   client = INIAClient()
   
   # Get stations
   stations = client.get_stations(region="R16")
   print(f"Found {len(stations)} stations in Ñuble")
   
   # Download data for first station
   station_code = stations.iloc[0]['codigo']
   
   data = client.get_data(
       station=station_code,
       variable=2002,
       start_date=datetime(2024, 9, 1),
       end_date=datetime(2024, 9, 30)
   )
   
   # Quality control
   clean_data = apply_quality_control(data, 'temperatura')
   
   # Analysis
   stats = {
       'station': station_code,
       'mean_temp': clean_data['valor'].mean(),
       'min_temp': clean_data['valor'].min(),
       'max_temp': clean_data['valor'].max(),
       'records': len(clean_data)
   }
   
   print(pd.DataFrame([stats]))

Next Steps
----------

* :doc:`examples` - More detailed examples
* :doc:`api/client` - Full API reference
* :doc:`configuration` - Advanced configuration
* :doc:`regions` - Chilean region codes
* :doc:`variables` - Available meteorological variables
