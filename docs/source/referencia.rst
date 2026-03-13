====================
Referencia de la API
====================

.. contents:: Clases y módulos
   :local:
   :depth: 2


INIAClient
----------

Clase principal. Punto de entrada para toda la funcionalidad.

.. autoclass:: iniamet.client.INIAClient
   :members:
   :undoc-members:
   :show-inheritance:


StationManager
--------------

Gestión de estaciones. Se accede internamente desde ``INIAClient``.

.. autoclass:: iniamet.stations.StationManager
   :members:
   :undoc-members:
   :show-inheritance:


DataDownloader
--------------

Descarga y agregación de datos. Se accede internamente desde ``INIAClient``.

.. autoclass:: iniamet.data.DataDownloader
   :members:
   :undoc-members:
   :show-inheritance:


RegionalDownloader
------------------

Descarga consolidada de datos para una región completa.

.. autoclass:: iniamet.regional.RegionalDownloader
   :members:
   :undoc-members:
   :show-inheritance:


CacheManager
------------

Sistema de caché en disco (JSON para metadatos, Parquet para datos).

.. autoclass:: iniamet.cache.CacheManager
   :members:
   :undoc-members:
   :show-inheritance:


QualityControl
--------------

Control de calidad basado en estándares WMO.

.. autoclass:: iniamet.qc.QualityControl
   :members:
   :undoc-members:
   :show-inheritance:

Funciones de conveniencia
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: iniamet.qc.apply_quality_control

.. autofunction:: iniamet.qc.get_qc_report


Utilidades
----------

Constantes
~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 10 35

   * - Constante
     - Valor
     - Descripción
   * - ``VAR_PRECIPITACION``
     - 2001
     - Precipitación (mm)
   * - ``VAR_TEMPERATURA_MEDIA``
     - 2002
     - Temperatura del aire media (°C)
   * - ``VAR_HUMEDAD_RELATIVA``
     - 2007
     - Humedad relativa media (%)
   * - ``VAR_VIENTO_DIRECCION``
     - 2012
     - Dirección del viento (°)
   * - ``VAR_VIENTO_VELOCIDAD_MEDIA``
     - 2013
     - Velocidad viento media (m/s)
   * - ``VAR_VIENTO_VELOCIDAD_MAXIMA``
     - 2014
     - Velocidad viento máxima (m/s)
   * - ``VAR_RADIACION_MEDIA``
     - 2022
     - Radiación solar media (W/m²)
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

Regiones
~~~~~~~~

.. data:: iniamet.utils.REGION_MAP

   Diccionario ``{código: nombre}`` de las 16 regiones de Chile.

Funciones auxiliares
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: iniamet.utils.normalize_region

.. autofunction:: iniamet.utils.normalize_regions

.. autofunction:: iniamet.utils.get_region_name

.. autofunction:: iniamet.utils.get_region_code

.. autofunction:: iniamet.utils.get_variable_info

.. autofunction:: iniamet.utils.list_all_variables

.. autofunction:: iniamet.utils.get_variable_id_by_name

.. autofunction:: iniamet.utils.is_valid_variable_id

.. autofunction:: iniamet.utils.parse_date

.. autofunction:: iniamet.utils.format_station_code

.. autofunction:: iniamet.utils.normalize_text
