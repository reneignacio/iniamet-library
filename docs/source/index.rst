==========================
INIAMET — Documentación
==========================

Librería Python para acceder a datos de estaciones agrometeorológicas de
`INIA Chile <https://agromet.inia.cl>`_.

.. note::

   Esta librería **no** es un producto oficial de INIA. Accede a datos
   públicos disponibles a través de la API de Agromet.

Características
---------------

- Cliente de alto nivel con una sola clase: ``INIAClient``
- Filtrado de estaciones por región, tipo o nombre
- Descarga de datos cada 15 min, horario, diario, semanal o mensual
- Descarga masiva de múltiples estaciones y variables
- Caché automático en disco (Parquet)
- Control de calidad (QC) con tests WMO/IPCC
- Constantes con nombre para todas las variables (sin números mágicos)
- Integración nativa con pandas

Ejemplo rápido
--------------

.. code-block:: python

   from iniamet import INIAClient, VAR_TEMPERATURA_MEDIA

   client = INIAClient(api_key="TU_API_KEY")

   # Estaciones de Ñuble
   estaciones = client.get_stations(region="Ñuble")

   # Temperatura diaria de enero 2025
   temp = client.get_data(
       "INIA-47", VAR_TEMPERATURA_MEDIA,
       "2025-01-01", "2025-01-31",
       aggregation="diario"
   )

   # Exportar
   temp.to_csv("temperatura_ninhue.csv", index=False)


Contenido
---------

.. toctree::
   :maxdepth: 2

   instalacion
   uso
   referencia
   changelog

Índices
-------

* :ref:`genindex`
* :ref:`modindex`
