=============
Guía de uso
=============

.. contents:: En esta página
   :local:
   :depth: 2

Conexión
--------

.. code-block:: python

   from iniamet import INIAClient

   client = INIAClient(api_key="TU_API_KEY")

   # También funciona como context manager
   with INIAClient(api_key="TU_API_KEY") as client:
       estaciones = client.get_stations()


Estaciones
----------

Listar todas las estaciones
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   todas = client.get_stations()
   print(f"Total: {len(todas)}")
   todas.head()

El DataFrame incluye: ``codigo``, ``nombre``, ``region``, ``comuna``,
``latitud``, ``longitud``, ``elevacion``, ``tipo``, ``primera_lectura``.

Filtrar por región
~~~~~~~~~~~~~~~~~~

Se acepta código (``R16``), nombre (``Ñuble``) o número (``16``):

.. code-block:: python

   # Cualquiera de estas formas funciona
   nuble = client.get_stations(region="R16")
   nuble = client.get_stations(region="Ñuble")
   nuble = client.get_stations(region="16")

   # Varias regiones a la vez
   centro = client.get_stations(region=["R16", "R08", "R07"])

Filtrar por tipo de estación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   inia = client.get_stations(region="R16", station_type="INIA")

Códigos de región
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 40

   * - Código
     - Región
   * - R15
     - Arica y Parinacota
   * - R01
     - Tarapacá
   * - R02
     - Antofagasta
   * - R03
     - Atacama
   * - R04
     - Coquimbo
   * - R05
     - Valparaíso
   * - R13
     - Metropolitana
   * - R06
     - O'Higgins
   * - R07
     - Maule
   * - R16
     - Ñuble
   * - R08
     - Biobío
   * - R09
     - La Araucanía
   * - R14
     - Los Ríos
   * - R10
     - Los Lagos
   * - R11
     - Aysén
   * - R12
     - Magallanes


Variables
---------

Cada estación mide distintas variables. La librería incluye constantes
para no usar números mágicos:

.. list-table::
   :header-rows: 1
   :widths: 35 10 30

   * - Constante
     - ID
     - Variable
   * - ``VAR_PRECIPITACION``
     - 2001
     - Precipitación (mm)
   * - ``VAR_TEMPERATURA_MEDIA``
     - 2002
     - Temperatura del aire (°C)
   * - ``VAR_HUMEDAD_RELATIVA``
     - 2007
     - Humedad relativa (%)
   * - ``VAR_VIENTO_DIRECCION``
     - 2012
     - Dirección del viento (°)
   * - ``VAR_VIENTO_VELOCIDAD_MEDIA``
     - 2013
     - Velocidad viento media (m/s)
   * - ``VAR_VIENTO_VELOCIDAD_MAXIMA``
     - 2014
     - Ráfaga máxima (m/s)
   * - ``VAR_RADIACION_MEDIA``
     - 2022
     - Radiación solar (W/m²)
   * - ``VAR_BATERIA_VOLTAJE``
     - 2024
     - Voltaje batería (V)
   * - ``VAR_TEMPERATURA_SUELO_10CM``
     - 2027
     - Temperatura suelo 10 cm (°C)
   * - ``VAR_TEMPERATURA_SUPERFICIE``
     - 2077
     - Temperatura superficie (°C)
   * - ``VAR_PRESION_ATMOSFERICA``
     - 2125
     - Presión atmosférica (mbar)

Consultar variables de una estación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   variables = client.get_variables("INIA-47")
   variables

Listar todas las variables conocidas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import list_all_variables
   list_all_variables()


Descarga de datos
-----------------

Datos crudos (cada 15 minutos)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import VAR_TEMPERATURA_MEDIA

   temp = client.get_data(
       station="INIA-47",
       variable=VAR_TEMPERATURA_MEDIA,
       start_date="2025-01-01",
       end_date="2025-01-31"
   )
   print(f"Registros: {len(temp)}")
   temp.head()

Agregación temporal
~~~~~~~~~~~~~~~~~~~

Se puede agregar los datos a distintas resoluciones. Los alias aceptados
son:

.. list-table::
   :header-rows: 1
   :widths: 25 25 25

   * - Español
     - Inglés
     - Resolución
   * - *(nada)* / ``"raw"`` / ``"crudo"``
     -
     - Cada 15 minutos
   * - ``"horario"``
     - ``"hourly"`` / ``"H"``
     - Horario
   * - ``"diario"``
     - ``"daily"`` / ``"D"``
     - Diario
   * - ``"semanal"``
     - ``"weekly"`` / ``"W"``
     - Semanal
   * - ``"mensual"``
     - ``"monthly"`` / ``"M"``
     - Mensual

**Temperatura** se agrega con min, max y media automáticamente.
**Precipitación** se suma (no se promedia).
**Otras variables** se promedian.

.. code-block:: python

   # Horario
   temp_h = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
                            "2025-01-01", "2025-01-31",
                            aggregation="horario")

   # Diario (temperatura incluye valor_min, valor_max, valor_media)
   temp_d = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
                            "2025-01-01", "2025-01-31",
                            aggregation="diario")

   # Precipitación diaria (se suma)
   from iniamet import VAR_PRECIPITACION
   pp = client.get_data("INIA-47", VAR_PRECIPITACION,
                        "2025-06-01", "2025-06-30",
                        aggregation="diario")

   # Mensual
   temp_m = client.get_data("INIA-47", VAR_TEMPERATURA_MEDIA,
                            "2025-01-01", "2025-12-31",
                            aggregation="mensual")


Descarga masiva
---------------

Varias estaciones y variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import VAR_HUMEDAD_RELATIVA

   datos = client.bulk_download(
       stations=["INIA-47", "INIA-139", "INIA-351"],
       variables=[VAR_TEMPERATURA_MEDIA, VAR_HUMEDAD_RELATIVA],
       start_date="2025-01-01",
       end_date="2025-01-31"
   )

   # Resultado: diccionario {"estacion_variable": DataFrame}
   for key, df in datos.items():
       print(f"{key}: {len(df)} registros")

Todas las estaciones de una región
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   estaciones = client.get_stations(region="Ñuble")
   codigos = estaciones['codigo'].tolist()

   datos = client.bulk_download(
       stations=codigos,
       variables=[VAR_TEMPERATURA_MEDIA],
       start_date="2025-01-01",
       end_date="2025-01-07"
   )

Descarga regional con ``RegionalDownloader``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import RegionalDownloader

   rd = RegionalDownloader(region="Ñuble")
   df = rd.download_climate_data(
       start_date="2025-01-01",
       end_date="2025-01-31",
       variables=["temperature", "precipitation"],
       aggregation="daily"
   )
   rd.save_to_csv(df, "nuble_enero_2025.csv")


Exportar datos
--------------

.. code-block:: python

   # CSV
   df.to_csv("datos.csv", index=False)

   # Excel (requiere openpyxl)
   df.to_excel("datos.xlsx", index=False)

   # Parquet
   df.to_parquet("datos.parquet", index=False)


Gráfico rápido
--------------

.. code-block:: python

   import matplotlib.pyplot as plt

   td = client.get_data(
       "INIA-47", VAR_TEMPERATURA_MEDIA,
       "2025-01-01", "2025-03-31",
       aggregation="diario"
   )

   plt.figure(figsize=(12, 4))
   plt.fill_between(td['tiempo'], td['valor_min'], td['valor_max'],
                     alpha=0.3, label='Min-Max')
   plt.plot(td['tiempo'], td['valor'], 'r-', lw=1, label='Media')
   plt.ylabel('Temperatura (°C)')
   plt.title('INIA-47 Ninhue — Temperatura diaria')
   plt.legend()
   plt.grid(alpha=0.3)
   plt.tight_layout()
   plt.show()


Caché
-----

La librería guarda automáticamente los datos en ``iniamet_cache/``.
La segunda consulta es instantánea.

.. code-block:: python

   # Desactivar caché
   client = INIAClient(api_key="...", cache=False)

   # Cambiar directorio
   client = INIAClient(api_key="...", cache_dir="mi_cache")

   # Limpiar todo el caché
   client.cache_manager.clear_cache()


Control de calidad
------------------

La librería incluye un módulo de QC basado en estándares WMO:

.. code-block:: python

   from iniamet import apply_quality_control, get_qc_report

   # Aplicar QC y obtener solo datos limpios
   datos_limpios = apply_quality_control(df, variable_name="temperatura")

   # Obtener reporte detallado
   print(get_qc_report(df))

Tests disponibles:

- **Valores imposibles**: fuera de rangos físicamente posibles
- **Valores extremos**: detección por rango fijo (WMO) o IQR
- **Sensor atascado**: valores repetidos consecutivos
- **Cambios bruscos**: variación temporal excesiva
- **Ceros consecutivos**: posible falla de sensor

.. code-block:: python

   from iniamet.qc import QualityControl

   qc = QualityControl()

   # Tests individuales
   df = qc.detect_impossible_values(df, variable_name="temperatura")
   df = qc.detect_extreme_values(df, variable_name="temperatura")
   df = qc.detect_stuck_sensor(df)
   df = qc.detect_sudden_changes(df, variable_name="temperatura")

   # Todos los tests a la vez
   df = qc.apply_all_checks(df, variable_name="temperatura")
   print(qc.get_qc_summary(df))
