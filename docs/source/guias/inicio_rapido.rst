Guía de Inicio Rápido
=====================

Esta guía te ayudará a comenzar a usar INIAMET en minutos.

Instalación
-----------

Instalar desde PyPI:

.. code-block:: bash

   pip install iniamet

O instalar desde el código fuente:

.. code-block:: bash

   git clone https://github.com/reneignacio/iniamet-library.git
   cd iniamet-library
   pip install -e .

Configuración de API Key
-------------------------

Necesitas una API key de INIA Agromet. Obtén una en: https://agromet.inia.cl/api/v2/

Opción 1: Archivo de Configuración (Recomendado)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Crear directorio de configuración
   mkdir -p ~/.iniamet

   # Crear archivo de configuración
   cat > ~/.iniamet/config.ini << EOF
   [api]
   key = TU_API_KEY_AQUI
   EOF

Opción 2: Variable de Entorno
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Linux/Mac:

.. code-block:: bash

   export INIA_API_KEY="TU_API_KEY_AQUI"

Windows PowerShell:

.. code-block:: powershell

   $env:INIA_API_KEY="TU_API_KEY_AQUI"

Opción 3: En Código
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient(api_key="TU_API_KEY_AQUI")

.. warning::
   No recomendado para código en producción o código compartido públicamente.

Primer Ejemplo
--------------

Obtener Estaciones de una Región
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient

   # Crear cliente
   client = INIAClient()

   # Obtener estaciones de la región de Ñuble
   stations = client.get_stations(region="R16")

   print(f"Estaciones encontradas: {len(stations)}")
   
   # Ver detalles de las primeras 3 estaciones
   for station in stations[:3]:
       print(f"{station['codigo']}: {station['nombre']} - {station['comuna']}")

Salida esperada:

.. code-block:: text

   Estaciones encontradas: 24
   INIA-47: Chillán - Chillán
   INIA-48: San Carlos - San Carlos
   INIA-49: Bulnes - Bulnes

Descargar Datos de Temperatura
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient
   from datetime import datetime, timedelta

   client = INIAClient()

   # Último mes de datos
   end_date = datetime.now()
   start_date = end_date - timedelta(days=30)

   # Descargar datos
   data = client.get_data(
       station="INIA-47",  # Chillán
       variable="temperature",
       start_date=start_date.strftime('%Y-%m-%d'),
       end_date=end_date.strftime('%Y-%m-%d')
   )

   print(f"Registros descargados: {len(data)}")
   print("\nPrimeros 5 registros:")
   print(data.head())

Salida esperada:

.. code-block:: text

   Registros descargados: 2880
   
   Primeros 5 registros:
                  tiempo  valor
   0 2024-10-08 00:00:00   12.3
   1 2024-10-08 01:00:00   11.8
   2 2024-10-08 02:00:00   11.2
   3 2024-10-08 03:00:00   10.9
   4 2024-10-08 04:00:00   10.5

Guardar Datos a CSV
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Guardar a CSV
   data.to_csv('temperatura_chillan.csv', index=False, encoding='utf-8')
   print("Datos guardados en temperatura_chillan.csv")

Próximos Pasos
--------------

- :doc:`descarga_regional` - Descargar datos de múltiples estaciones
- :doc:`control_calidad` - Aplicar control de calidad a los datos
- :doc:`recetas` - Recetas y ejemplos avanzados

Variables Disponibles
---------------------

La librería soporta múltiples variables meteorológicas:

Temperatura
~~~~~~~~~~~

- ``temperature`` - Temperatura del aire (°C)
- ``temperature_max`` - Temperatura máxima
- ``temperature_min`` - Temperatura mínima

Precipitación
~~~~~~~~~~~~~

- ``precipitation`` - Precipitación acumulada (mm)

Humedad
~~~~~~~

- ``humidity`` - Humedad relativa (%)

Viento
~~~~~~

- ``wind_speed`` - Velocidad del viento (m/s)
- ``wind_direction`` - Dirección del viento (grados)

Radiación
~~~~~~~~~

- ``solar_radiation`` - Radiación solar (W/m²)

Otras
~~~~~

- ``atmospheric_pressure`` - Presión atmosférica (hPa)
- ``soil_temperature`` - Temperatura del suelo (°C)

Regiones de Chile
-----------------

Códigos de región disponibles:

.. code-block:: python

   from iniamet.utils import REGION_MAP
   
   # Ver todas las regiones
   for codigo, nombre in REGION_MAP.items():
       print(f"{codigo}: {nombre}")

Salida:

.. code-block:: text

   R01: Tarapacá
   R02: Antofagasta
   R03: Atacama
   R04: Coquimbo
   R05: Valparaíso
   R06: O'Higgins
   R07: Maule
   R08: BioBío
   R09: Araucanía
   R10: Los Lagos
   R11: Aysén
   R12: Magallanes
   R13: Metropolitana
   R14: Los Ríos
   R15: Arica y Parinacota
   R16: Ñuble

Solución de Problemas
---------------------

Error de API Key
~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: API key not configured

**Solución**: Configura tu API key usando uno de los métodos descritos arriba.

Error de Conexión
~~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: Connection timeout

**Solución**: Verifica tu conexión a internet y que la API de INIA esté disponible.

No se Encuentran Datos
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Warning: No data found for the specified period

**Solución**: Verifica que:

1. El código de estación sea correcto
2. El rango de fechas tenga datos disponibles
3. La variable solicitada exista para esa estación
