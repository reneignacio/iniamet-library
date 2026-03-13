============
Instalación
============

Requisitos
----------

- Python 3.8 o superior
- pip

Desde código fuente
-------------------

.. code-block:: bash

   git clone <URL-del-repositorio>
   cd iniamet-library
   pip install -e .

Desde PyPI (cuando esté publicado)
-----------------------------------

.. code-block:: bash

   pip install iniamet

Verificar instalación
---------------------

.. code-block:: python

   from iniamet import INIAClient
   print("OK")


Configuración de la API key
----------------------------

Necesitas una API key de `agromet.inia.cl <https://agromet.inia.cl/api/v2/>`_.
Hay tres formas de configurarla (en orden de prioridad):

**1. Directamente en el código**

.. code-block:: python

   client = INIAClient(api_key="tu_api_key_aqui")

**2. Variable de entorno**

.. code-block:: bash

   # Linux/Mac
   export INIA_API_KEY="tu_api_key_aqui"

   # Windows PowerShell
   $env:INIA_API_KEY = "tu_api_key_aqui"

.. code-block:: python

   client = INIAClient()  # Lee INIA_API_KEY automáticamente

**3. Archivo de configuración**

Crear ``~/.iniamet/config`` con el contenido:

.. code-block:: text

   [api]
   key = tu_api_key_aqui

.. code-block:: python

   client = INIAClient()  # Lee ~/.iniamet/config automáticamente
