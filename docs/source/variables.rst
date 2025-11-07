Variables
=========

Available Meteorological Variables
-----------------------------------

INIAMET provides access to numerous meteorological variables from INIA stations.

Common Variables
----------------

Temperature
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 35

   * - Variable ID
     - Name
     - Unit
     - Description
   * - 2002
     - Air Temperature
     - °C
     - Temperature at 1.5-2m height
   * - 2021
     - Maximum Temperature
     - °C
     - Daily maximum temperature
   * - 2022
     - Minimum Temperature
     - °C
     - Daily minimum temperature
   * - 2023
     - Soil Temperature
     - °C
     - Temperature at various depths

Precipitation
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 35

   * - Variable ID
     - Name
     - Unit
     - Description
   * - 2001
     - Precipitation
     - mm
     - Accumulated precipitation
   * - 2024
     - Snow Depth
     - cm
     - Snow accumulation

Humidity
~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 35

   * - Variable ID
     - Name
     - Unit
     - Description
   * - 2003
     - Relative Humidity
     - %
     - Relative humidity percentage
   * - 2025
     - Dew Point
     - °C
     - Dew point temperature

Wind
~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 35

   * - Variable ID
     - Name
     - Unit
     - Description
   * - 2004
     - Wind Speed
     - m/s
     - Average wind speed
   * - 2005
     - Wind Direction
     - degrees
     - Wind direction (0-360)
   * - 2026
     - Wind Gust
     - m/s
     - Maximum wind gust

Radiation
~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 15 35 15 35

   * - Variable ID
     - Name
     - Unit
     - Description
   * - 2006
     - Solar Radiation
     - W/m²
     - Global solar radiation
   * - 2027
     - PAR
     - µmol/m²/s
     - Photosynthetically active radiation

Usage Examples
--------------

Get Variable Information
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient()
   
   # Get all variables for a station
   variables = client.get_variables("INIA-47")
   
   # Display variable details
   print(variables[['variable_id', 'nombre', 'unidad', 'descripcion']])

Filter Variables
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Filter by name
   temp_vars = variables[variables['nombre'].str.contains('Temperatura', case=False)]
   
   # Filter by unit
   celsius_vars = variables[variables['unidad'] == '°C']

Download Specific Variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Download air temperature
   temp_data = client.get_data(
       station="INIA-47",
       variable=2002,  # Air temperature
       start_date="2024-09-01",
       end_date="2024-09-30"
   )
   
   # Download precipitation
   precip_data = client.get_data(
       station="INIA-47",
       variable=2001,  # Precipitation
       start_date="2024-09-01",
       end_date="2024-09-30"
   )

Download Multiple Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   variables_to_download = [2002, 2001, 2003]  # Temp, Precip, Humidity
   
   all_data = {}
   for var_id in variables_to_download:
       data = client.get_data(
           station="INIA-47",
           variable=var_id,
           start_date="2024-09-01",
           end_date="2024-09-30"
       )
       all_data[var_id] = data

Variable Helper Functions
-------------------------

.. code-block:: python

   from iniamet.utils import get_variable_info, VARIABLE_INFO
   
   # Get information about a variable
   info = get_variable_info(2002)
   print(f"Variable: {info['nombre']}")
   print(f"Unit: {info['unidad']}")
   
   # List all available variables
   for var_id, info in VARIABLE_INFO.items():
       print(f"{var_id}: {info['nombre']} ({info['unidad']})")

Data Temporal Resolution
-------------------------

Variables are available at different temporal resolutions:

* **Hourly**: Most meteorological variables
* **Daily**: Aggregated daily statistics
* **Monthly**: Long-term climate data

The resolution depends on the station and variable configuration.

Missing Data
------------

Some variables may not be available at all stations. Always check:

.. code-block:: python

   # Get variables for specific station
   available = client.get_variables("INIA-47")
   
   # Check if variable exists
   var_id = 2002
   if var_id in available['variable_id'].values:
       print(f"Variable {var_id} is available")
   else:
       print(f"Variable {var_id} not available at this station")

Quality and Validation
-----------------------

Apply quality control based on variable type:

.. code-block:: python

   from iniamet import apply_quality_control
   
   # Temperature data
   temp_clean = apply_quality_control(temp_data, 'temperatura')
   
   # Precipitation data
   precip_clean = apply_quality_control(precip_data, 'precipitacion')

For more information on specific variables, consult the `INIA API documentation <https://agromet.inia.cl/api/v2>`_.
