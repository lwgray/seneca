.. Seneca documentation master file

Seneca - Open Source Conversation Visualization
===============================================

Seneca is an open-source conversation visualization platform for Marcus AI systems.
It provides real-time insights, analytics, and visual representations of agent
conversations, task progress, and system health.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   quickstart
   api/index
   architecture
   development
   changelog

Key Features
------------

* **Real-time Visualization** - Monitor agent conversations as they happen
* **Statistical Analysis** - Get insights into conversation patterns and agent behavior
* **Task Tracking** - Visualize task progress and dependencies
* **Performance Metrics** - Track system health and performance indicators
* **Local Deployment** - Run on your own infrastructure with full control

Getting Started
---------------

To get started with Seneca:

1. :doc:`Install Seneca <installation>` on your local machine
2. Follow the :doc:`quickstart` guide to connect to Marcus
3. Explore the :doc:`API documentation <api/index>` for integration

Architecture Overview
--------------------

Seneca is built with a modular architecture:

* **ConversationProcessor** - Reads and processes Marcus log files
* **Analyzers** - Provide statistical and temporal analysis
* **Visualization Server** - Serves the web-based UI
* **API Layer** - RESTful API for integration

For more details, see the :doc:`architecture` documentation.

API Reference
-------------

The complete API reference is available at :doc:`api/index`.

Key modules include:

* :mod:`processors.conversation_processor` - Core conversation processing
* :mod:`processors.ui_server` - Visualization server
* :mod:`processors.health_monitor` - System health monitoring

Contributing
------------

Seneca is open source and welcomes contributions! See our :doc:`development`
guide for information on:

* Setting up a development environment
* Running tests
* Submitting pull requests
* Code style guidelines

License
-------

Seneca is released under the MIT License. See the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`