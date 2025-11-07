INIAClient
==========

.. automodule:: iniamet.client
   :members:
   :undoc-members:
   :show-inheritance:

Overview
--------

``INIAClient`` is the main high-level interface for accessing INIA agrometeorological data.

Basic Usage
-----------

.. code-block:: python

   from iniamet import INIAClient
   
   # Initialize with default settings
   client = INIAClient()
   
   # Or with custom API key
   client = INIAClient(api_key='your-key')
   
   # Disable caching
   client = INIAClient(cache=False)

Methods
-------

.. autoclass:: iniamet.client.INIAClient
   :members:
   :undoc-members:
   :special-members: __init__

Examples
--------

Get Stations
~~~~~~~~~~~~

.. code-block:: python

   # Get all stations
   stations = client.get_stations()
   
   # Filter by region
   nuble = client.get_stations(region="R16")
   
   # Filter by network
   inia = client.get_stations(network="INIA")

Get Variables
~~~~~~~~~~~~~

.. code-block:: python

   # Get all variables for a station
   variables = client.get_variables("INIA-47")
   
   # Display variable information
   print(variables[['variable_id', 'nombre', 'unidad']])

Download Data
~~~~~~~~~~~~~

.. code-block:: python

   from datetime import datetime
   
   # Download temperature data
   data = client.get_data(
       station="INIA-47",
       variable=2002,
       start_date=datetime(2024, 9, 1),
       end_date=datetime(2024, 9, 30)
   )
   
   # With string dates
   data = client.get_data(
       station="INIA-47",
       variable=2002,
       start_date="2024-09-01",
       end_date="2024-09-30"
   )
