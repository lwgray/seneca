Installation
============

This guide will help you install Seneca on your local machine.

Requirements
------------

* Python 3.8 or higher
* Marcus AI system (for conversation logs)
* Modern web browser (Chrome, Firefox, Safari, or Edge)

Installation Methods
--------------------

Using pip (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

Install Seneca directly from PyPI::

    pip install seneca-viz

From Source
~~~~~~~~~~~

Clone the repository and install in development mode::

    git clone https://github.com/marcus-ai/seneca.git
    cd seneca
    pip install -e .

Using Docker
~~~~~~~~~~~~

Pull and run the official Docker image::

    docker pull marcusai/seneca:latest
    docker run -p 8000:8000 -v ~/.marcus/logs:/logs marcusai/seneca

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Seneca uses the following environment variables:

* ``MARCUS_LOG_DIR`` - Path to Marcus conversation logs (default: ``~/dev/marcus/logs/conversations``)
* ``SENECA_PORT`` - Port for the web server (default: ``8000``)
* ``SENECA_HOST`` - Host to bind to (default: ``localhost``)

Configuration File
~~~~~~~~~~~~~~~~~~

Create a ``config.yaml`` file in your Seneca directory::

    marcus:
      log_dir: /path/to/marcus/logs
      
    server:
      host: localhost
      port: 8000
      
    analysis:
      cache_enabled: true
      cache_ttl: 300

Verifying Installation
----------------------

After installation, verify that Seneca is working::

    # Check version
    seneca --version
    
    # Start the server
    seneca start
    
    # Open http://localhost:8000 in your browser

Troubleshooting
---------------

Log Directory Not Found
~~~~~~~~~~~~~~~~~~~~~~~

If you see "Log directory does not exist", ensure:

1. Marcus is installed and has generated logs
2. The ``MARCUS_LOG_DIR`` environment variable is set correctly
3. You have read permissions for the log directory

Port Already in Use
~~~~~~~~~~~~~~~~~~~

If port 8000 is already in use::

    seneca start --port 8080

Or set the ``SENECA_PORT`` environment variable.

Next Steps
----------

* Follow the :doc:`quickstart` guide
* Read about the :doc:`architecture`
* Explore the :doc:`api/index`