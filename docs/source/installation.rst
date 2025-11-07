Installation
============

Basic Installation
------------------

Install INIAMET using pip:

.. code-block:: bash

   pip install iniamet

This installs the core library with basic dependencies:

* requests
* pandas
* numpy

From Source
-----------

To install from source:

.. code-block:: bash

   git clone https://github.com/reneignacio/iniamet-library
   cd iniamet-library
   pip install -e .

Optional Dependencies
---------------------

Visualization Features
~~~~~~~~~~~~~~~~~~~~~~

For interactive maps and visualization:

.. code-block:: bash

   pip install iniamet[viz]

This installs:

* folium (interactive maps)
* IPython (notebook integration)

Development Tools
~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

   pip install iniamet[dev]

This installs:

* pytest (testing)
* pytest-cov (coverage)
* black (code formatting)
* flake8 (linting)
* mypy (type checking)

All Features
~~~~~~~~~~~~

To install everything:

.. code-block:: bash

   pip install iniamet[all]

Requirements
------------

* Python 3.8 or higher
* Operating System: Windows, Linux, macOS
* Internet connection (to access INIA API)

Verification
------------

Verify the installation:

.. code-block:: python

   import iniamet
   print(iniamet.__version__)

You should see: ``0.1.0``

API Key Setup
-------------

After installation, configure your API key:

.. code-block:: bash

   python -m iniamet.config set-key YOUR-API-KEY

Get your API key from: https://agromet.inia.cl/api/v2/

Next Steps
----------

* :doc:`configuration` - Configure API key and settings
* :doc:`quickstart` - Start using INIAMET
* :doc:`examples` - See usage examples
