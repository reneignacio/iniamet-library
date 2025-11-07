Chilean Regions
===============

INIAMET supports filtering stations by Chilean administrative regions.

Region Codes
------------

.. list-table::
   :header-rows: 1
   :widths: 10 30 20 20

   * - Code
     - Region Name
     - Stations
     - Capital
   * - R01
     - Tarapacá
     - ~15
     - Iquique
   * - R02
     - Antofagasta
     - ~20
     - Antofagasta
   * - R03
     - Atacama
     - ~18
     - Copiapó
   * - R04
     - Coquimbo
     - ~25
     - La Serena
   * - R05
     - Valparaíso
     - ~35
     - Valparaíso
   * - R06
     - O'Higgins
     - ~40
     - Rancagua
   * - R07
     - Maule
     - ~45
     - Talca
   * - R08
     - Biobío
     - ~50
     - Concepción
   * - R09
     - La Araucanía
     - ~40
     - Temuco
   * - R10
     - Los Lagos
     - ~35
     - Puerto Montt
   * - R11
     - Aysén
     - ~12
     - Coyhaique
   * - R12
     - Magallanes
     - ~10
     - Punta Arenas
   * - R13
     - Metropolitana
     - ~60
     - Santiago
   * - R14
     - Los Ríos
     - ~20
     - Valdivia
   * - R15
     - Arica y Parinacota
     - ~8
     - Arica
   * - R16
     - Ñuble
     - ~24
     - Chillán

Usage Examples
--------------

Filter by Region
~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient()
   
   # Get stations in Ñuble
   nuble = client.get_stations(region="R16")
   print(f"Ñuble has {len(nuble)} stations")
   
   # Get stations in Maule
   maule = client.get_stations(region="R07")

Using Region Names
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet.utils import get_region_code
   
   # Convert region name to code
   code = get_region_code("Ñuble")  # Returns "R16"
   
   stations = client.get_stations(region=code)

Regional Download
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import RegionalDownloader
   
   # Download all temperature data for a region
   downloader = RegionalDownloader(region="R16")
   
   data = downloader.download_climate_data(
       start_date="2024-09-01",
       end_date="2024-09-30",
       variables=['temperature'],
       aggregation='daily'
   )

Multiple Regions
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Download data from multiple regions
   regions = ["R07", "R08", "R16"]  # Maule, Biobío, Ñuble
   
   all_data = []
   for region in regions:
       downloader = RegionalDownloader(region=region)
       data = downloader.download_climate_data(
           start_date="2024-09-01",
           end_date="2024-09-30",
           variables=['temperature']
       )
       all_data.append(data)
   
   # Combine all regions
   import pandas as pd
   combined = pd.concat(all_data, ignore_index=True)

Region Statistics
-----------------

Get number of stations per region:

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient()
   stations = client.get_stations()
   
   # Count by region
   region_counts = stations.groupby('region').size()
   print(region_counts.sort_values(ascending=False))

Geographic Information
----------------------

Each station includes geographic coordinates:

.. code-block:: python

   # Get stations with coordinates
   stations = client.get_stations(region="R16")
   
   print(stations[['codigo', 'nombre', 'latitud', 'longitud']])

Example output:

.. code-block:: text

   codigo          nombre  latitud  longitud
   INIA-47        Chillán  -36.603   -71.912
   INIA-139         Talca  -35.432   -71.654

Creating Maps
~~~~~~~~~~~~~

.. code-block:: python

   from iniamet.visualization import plot_station_map
   
   # Create interactive map of region
   stations = client.get_stations(region="R16")
   map_obj = plot_station_map(stations, output_file='nuble_map.html')

Region Helper Functions
-----------------------

.. code-block:: python

   from iniamet.utils import get_region_name, REGION_MAP
   
   # Get region name from code
   name = get_region_name("R16")  # Returns "Ñuble"
   
   # Access all regions
   for code, name in REGION_MAP.items():
       print(f"{code}: {name}")
