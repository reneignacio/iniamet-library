Configuration
=============

API Key Management
------------------

INIAMET requires an API key to access INIA's agrometeorological data. There are three ways to configure it.

Method 1: Configuration File (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest method for permanent setup:

.. code-block:: bash

   # Set your API key
   python -m iniamet.config set-key YOUR-API-KEY-HERE
   
   # Verify it's saved
   python -m iniamet.config show
   
   # Remove it if needed
   python -m iniamet.config remove

The key is stored in ``~/.iniamet/config`` with restricted permissions (chmod 600 on Unix).

Method 2: Environment Variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set the ``INIA_API_KEY`` environment variable:

**Linux/macOS:**

.. code-block:: bash

   # Temporary (current session)
   export INIA_API_KEY='your-api-key-here'
   
   # Permanent (add to ~/.bashrc or ~/.zshrc)
   echo "export INIA_API_KEY='your-api-key-here'" >> ~/.bashrc
   source ~/.bashrc

**Windows CMD:**

.. code-block:: batch

   # Temporary
   set INIA_API_KEY=your-api-key-here
   
   # Permanent
   setx INIA_API_KEY "your-api-key-here"

**Windows PowerShell:**

.. code-block:: powershell

   # Temporary
   $env:INIA_API_KEY='your-api-key-here'
   
   # Permanent
   [Environment]::SetEnvironmentVariable('INIA_API_KEY', 'your-api-key', 'User')

Method 3: Direct in Code
~~~~~~~~~~~~~~~~~~~~~~~~~

Pass the API key when creating the client:

.. code-block:: python

   from iniamet import INIAClient
   
   client = INIAClient(api_key='your-api-key-here')

Priority Order
--------------

When multiple methods are configured, INIAMET uses this priority:

1. API key passed directly to ``INIAClient()``
2. ``INIA_API_KEY`` environment variable
3. Configuration file (``~/.iniamet/config``)

If no API key is found, you'll get:

.. code-block:: text

   RuntimeError: No API key configured. Please set via:
   1. python -m iniamet.config set-key YOUR_KEY
   2. Set INIA_API_KEY environment variable
   3. Pass api_key parameter to INIAClient

Getting an API Key
------------------

1. Visit https://agromet.inia.cl/api/v2/
2. Register or login to your account
3. Navigate to API keys section
4. Generate a new API key
5. Copy and configure it using one of the methods above

Caching Configuration
---------------------

INIAMET includes a built-in caching system to reduce API calls.

Enable/Disable Cache
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Enable caching (default)
   client = INIAClient(cache=True)
   
   # Disable caching
   client = INIAClient(cache=False)

Custom Cache Directory
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Custom cache location
   client = INIAClient(cache_dir="/path/to/cache")

Cache Location
~~~~~~~~~~~~~~

By default, cache is stored in:

* **Linux/macOS**: ``./iniamet_cache/``
* **Windows**: ``.\iniamet_cache\``

Cache Structure
~~~~~~~~~~~~~~~

.. code-block:: text

   iniamet_cache/
   ├── stations/
   │   └── all_stations.json
   ├── variables/
   │   ├── INIA-47.json
   │   └── INIA-139.json
   └── data/
       ├── INIA-47_2002_202409.parquet
       └── INIA-47_2001_202409.parquet

Clear Cache
~~~~~~~~~~~

To clear the cache:

.. code-block:: bash

   # Linux/macOS
   rm -rf iniamet_cache/
   
   # Windows
   Remove-Item -Recurse -Force iniamet_cache

Security Best Practices
-----------------------

1. **Never commit your API key** to version control
2. **Use configuration file** for local development
3. **Use environment variables** for production/CI
4. **Restrict file permissions** on config file
5. **Rotate keys periodically** for security

Example .gitignore
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   # API Keys
   .iniamet/
   config.ini
   secrets.yaml
   .env
   
   # Cache
   iniamet_cache/

Troubleshooting
---------------

"No API key configured" Error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you've configured your API key using one of the three methods above.

"Invalid API key" Error
~~~~~~~~~~~~~~~~~~~~~~~

1. Verify your API key at https://agromet.inia.cl/api/v2/
2. Check for extra spaces or characters
3. Regenerate a new key if needed

Cache Issues
~~~~~~~~~~~~

If you experience caching issues:

.. code-block:: python

   # Disable cache temporarily
   client = INIAClient(cache=False)
   
   # Or clear the cache directory
   # rm -rf iniamet_cache/
