INIAMET - Documentación
=======================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Versión Python

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: Licencia

.. image:: https://badge.fury.io/py/iniamet.svg
   :target: https://pypi.org/project/iniamet/
   :alt: Versión PyPI

.. image:: https://readthedocs.org/projects/iniamet/badge/?version=latest
   :target: https://iniamet.readthedocs.io/es/latest/?badge=latest
   :alt: Estado Documentación

**Librería Python de alto nivel para acceder a datos de estaciones agrometeorológicas de INIA (Instituto de Investigaciones Agropecuarias) de Chile.**

.. warning::
   **AVISO IMPORTANTE**: Esta es una **librería NO oficial, desarrollada por la comunidad**. 
   **NO está afiliada, respaldada ni mantenida oficialmente por INIA** 
   (Instituto de Investigaciones Agropecuarias). Esta librería accede a datos públicamente 
   disponibles desde la API agrometeorológica de INIA.

Accede a datos de más de 400 estaciones meteorológicas en todo Chile con una API simple e intuitiva. 
Descarga temperatura, precipitación, humedad, viento, radiación y más.

Características
---------------

* **API de Alto Nivel**: Funciones simples e intuitivas para consultar estaciones y descargar datos
* **Gestión Inteligente de Estaciones**: Maneja automáticamente diferentes formatos de códigos de estación
* **Filtrado Regional**: Filtra estaciones por regiones chilenas (R01-R16)
* **Sistema de Caché**: Sistema de almacenamiento en caché integrado para consultas repetidas más rápidas
* **Control de Calidad**: Validación de datos completa y verificaciones de calidad
* **Tipado Seguro**: Type hints completos para mejor soporte de IDE
* **Integración con pandas**: Retorna datos como DataFrames de pandas
* **Visualización**: Mapas interactivos con folium (opcional)

Inicio Rápido
-------------

Instalación
~~~~~~~~~~~

.. code-block:: bash

   pip install iniamet

Configuración de API Key
~~~~~~~~~~~~~~~~~~~~~~~~

Obtén tu API key desde https://agromet.inia.cl/api/v2/

**Opción 1: Archivo de configuración (Recomendado)**

.. code-block:: bash

   # Crear archivo .iniamet/config.ini en tu directorio home
   mkdir -p ~/.iniamet
   echo "[api]" > ~/.iniamet/config.ini
   echo "key = TU_API_KEY_AQUI" >> ~/.iniamet/config.ini

**Opción 2: Variable de entorno**

.. code-block:: bash

   # Linux/Mac
   export INIA_API_KEY="TU_API_KEY_AQUI"
   
   # Windows PowerShell
   $env:INIA_API_KEY="TU_API_KEY_AQUI"

**Opción 3: En código (no recomendado para producción)**

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient(api_key="TU_API_KEY_AQUI")

Ejemplo Básico
~~~~~~~~~~~~~~

.. code-block:: python

   from iniamet import INIAClient

   # Crear cliente
   client = INIAClient()

   # Obtener todas las estaciones de la región de Ñuble
   stations = client.get_stations(region="R16")
   print(f"Estaciones en Ñuble: {len(stations)}")

   # Descargar datos de temperatura
   data = client.get_data(
       station="INIA-47",  # Estación Chillán
       variable="temperature",
       start_date="2024-01-01",
       end_date="2024-12-31"
   )

   print(data.head())

Tabla de Contenidos
-------------------

.. toctree::
   :maxdepth: 2
   :caption: Guías del Usuario

   guias/instalacion
   guias/inicio_rapido
   guias/descarga_regional
   guias/control_calidad
   guias/recetas

.. toctree::
   :maxdepth: 2
   :caption: Referencia API

   api/client
   api/regional
   api/stations
   api/data
   api/qc
   api/utils
   api/visualization

.. toctree::
   :maxdepth: 1
   :caption: Ejemplos

   ejemplos/basico
   ejemplos/regional
   ejemplos/control_calidad
   ejemplos/automatizado

.. toctree::
   :maxdepth: 1
   :caption: Información Adicional

   acerca_de
   licencia
   changelog
   contribuir

Índices y Tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
