Examples
========

This page provides practical examples of using INIAMET.

Basic Operations
----------------

Initialize Client
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   
   # With default configuration
   client = INIAClient()
   
   # With custom API key
   client = INIAClient(api_key='your-key')
   
   # Without caching
   client = INIAClient(cache=False)

Get Stations
~~~~~~~~~~~~

.. code-block:: python

   # All stations
   all_stations = client.get_stations()
   
   # By region
   nuble = client.get_stations(region="R16")
   
   # By network
   inia = client.get_stations(network="INIA")
   
   # Combine filters
   inia_nuble = client.get_stations(region="R16", network="INIA")

Download Data
-------------

Single Variable
~~~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime
   
   # Temperature data
   temp = client.get_data(
       station="INIA-47",
       variable=2002,
       start_date=datetime(2024, 9, 1),
       end_date=datetime(2024, 9, 30)
   )
   
   print(temp.head())

Multiple Stations
~~~~~~~~~~~~~~~~~

.. code-block:: python

   stations = ["INIA-47", "INIA-139", "INIA-211"]
   
   all_data = []
   for station in stations:
       data = client.get_data(
           station=station,
           variable=2002,
           start_date="2024-09-01",
           end_date="2024-09-30"
       )
       data['station'] = station
       all_data.append(data)
   
   import pandas as pd
   combined = pd.concat(all_data, ignore_index=True)

Data Analysis
-------------

Basic Statistics
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Download data
   data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
   
   # Calculate statistics
   stats = {
       'mean': data['valor'].mean(),
       'min': data['valor'].min(),
       'max': data['valor'].max(),
       'std': data['valor'].std()
   }
   
   print(f"Temperature Statistics:")
   for key, value in stats.items():
       print(f"  {key}: {value:.2f}°C")

Time Series Resampling
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Set time as index
   data = data.set_index('tiempo')
   
   # Daily average
   daily = data.resample('D')['valor'].mean()
   
   # Weekly average
   weekly = data.resample('W')['valor'].mean()
   
   # Monthly statistics
   monthly = data.resample('M').agg({
       'valor': ['mean', 'min', 'max']
   })

Quality Control
---------------

Automatic QC
~~~~~~~~~~~~

.. code-block:: python

   from iniamet import apply_quality_control
   
   # Apply quality control
   clean = apply_quality_control(data, 'temperatura')
   
   print(f"Original: {len(data)}, Clean: {len(clean)}")

Custom QC
~~~~~~~~~

.. code-block:: python

   from iniamet import QualityControl
   
   qc = QualityControl()
   
   # Run specific checks
   extreme = qc.detect_extreme_values(data, 'temperatura')
   stuck = qc.detect_stuck_sensor(data)
   
   # Combine flags
   flagged = data[(extreme > 0) | (stuck > 0)]
   print(f"Flagged {len(flagged)} suspicious records")

Regional Analysis
-----------------

Download Regional Data
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import RegionalDownloader
   
   downloader = RegionalDownloader(region="R16")
   
   data = downloader.download_climate_data(
       start_date="2024-09-01",
       end_date="2024-09-30",
       variables=['temperature', 'precipitation'],
       aggregation='daily'
   )
   
   # Save to file
   data.to_csv("nuble_climate_data.csv")

Regional Statistics
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Calculate regional average
   regional_avg = data.groupby('tiempo')['valor'].mean()
   
   # Station comparison
   station_stats = data.groupby('station')['valor'].agg([
       'mean', 'min', 'max', 'count'
   ])

Visualization
-------------

Station Map
~~~~~~~~~~~

.. code-block:: python

   from iniamet.visualization import plot_station_map
   
   # Get stations
   stations = client.get_stations(region="R16")
   
   # Create map
   map_obj = plot_station_map(
       stations,
       output_file='stations_map.html'
   )

Temperature Map
~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet.visualization import quick_temp_map
   
   # Create temperature map for today
   map_obj = quick_temp_map(
       client,
       region='R16',
       date='2024-10-12'
   )

Export and Save
---------------

Save to CSV
~~~~~~~~~~~

.. code-block:: python

   # Download data
   data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
   
   # Save to CSV
   data.to_csv("temperature_data.csv", index=False)

Save to Excel
~~~~~~~~~~~~~

.. code-block:: python

   # Requires openpyxl: pip install openpyxl
   data.to_excel("temperature_data.xlsx", index=False)

Save to Parquet
~~~~~~~~~~~~~~~

.. code-block:: python

   # Efficient binary format
   data.to_parquet("temperature_data.parquet")

Complete Workflow
-----------------

Here's a complete analysis workflow:

.. code-block:: python

   from iniamet import INIAClient, apply_quality_control
   from datetime import datetime
   import pandas as pd
   
   # 1. Initialize
   client = INIAClient()
   
   # 2. Get stations
   stations = client.get_stations(region="R16")
   print(f"Found {len(stations)} stations")
   
   # 3. Download data for all stations
   all_data = []
   for idx, row in stations.iterrows():
       station = row['codigo']
       try:
           data = client.get_data(
               station=station,
               variable=2002,
               start_date=datetime(2024, 9, 1),
               end_date=datetime(2024, 9, 30)
           )
           data['station'] = station
           data['station_name'] = row['nombre']
           all_data.append(data)
       except Exception as e:
           print(f"Error with {station}: {e}")
   
   # 4. Combine data
   df = pd.concat(all_data, ignore_index=True)
   
   # 5. Quality control
   df_clean = apply_quality_control(df, 'temperatura')
   
   # 6. Analysis
   stats = df_clean.groupby('station_name')['valor'].agg([
       'mean', 'min', 'max', 'count'
   ]).round(2)
   
   # 7. Save results
   stats.to_csv("regional_temperature_stats.csv")
   df_clean.to_csv("clean_temperature_data.csv", index=False)
   
   print("Analysis complete!")
   print(stats)

More Examples
-------------

For more examples, see:

* `examples/ directory <https://github.com/reneignacio/iniamet-library/tree/main/examples>`_
* :doc:`quickstart` - Quick start guide
* :doc:`api/client` - API reference
