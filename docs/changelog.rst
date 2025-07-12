Changelog
=========

All notable changes to Seneca will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/>`_.

[Unreleased]
------------

Added
~~~~~

* Initial open source release
* Core conversation processor for reading Marcus logs
* Real-time streaming capabilities
* Web-based visualization UI
* RESTful API for integration
* WebSocket support for live updates
* Statistical analysis engine
* Health monitoring system
* Comprehensive documentation
* Unit test suite

[1.0.0] - 2025-01-15
--------------------

Initial Release
~~~~~~~~~~~~~~~

**Core Features:**

* ConversationProcessor for reading JSONL logs
* ConversationStreamProcessor for real-time monitoring
* Web UI with dashboard and analytics
* REST API with full documentation
* Docker support for easy deployment

**Analysis Capabilities:**

* Statistical analysis (counts, averages, distributions)
* Temporal analysis (time-based patterns)
* Agent behavior analysis
* Task tracking and metrics
* Performance monitoring

**Developer Features:**

* Comprehensive API documentation
* Type hints throughout codebase
* Extensive test coverage
* Plugin architecture for extensions
* NumPy-style docstrings

Known Issues
~~~~~~~~~~~~

* Large log files (>1GB) may cause slower initial load times
* WebSocket reconnection needs manual refresh
* Time zone handling assumes UTC for naive timestamps

Future Plans
------------

[1.1.0] - Planned
~~~~~~~~~~~~~~~~~

**Planned Features:**

* Distributed mode for multi-node deployments
* S3/GCS/Azure blob storage support
* Prometheus metrics export
* Advanced filtering UI
* Custom dashboard layouts
* Alert system for anomalies

[1.2.0] - Planned
~~~~~~~~~~~~~~~~~

**Planned Features:**

* Machine learning insights
* Predictive analytics
* Natural language search
* Mobile-responsive UI
* Export to CSV/Excel
* Integration with Jupyter notebooks

[2.0.0] - Future
~~~~~~~~~~~~~~~~

**Major Version Plans:**

* GraphQL API alongside REST
* Kubernetes operator
* Multi-tenancy support
* Enterprise features (as Zeno)
* Advanced security features
* Compliance reporting

Migration Guides
----------------

Migrating from Marcus Built-in UI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're currently using Marcus's built-in visualization:

1. Install Seneca alongside Marcus
2. Configure ``MARCUS_LOG_DIR`` to point to Marcus logs
3. Start Seneca server
4. Access familiar visualizations with enhanced features

No changes to Marcus configuration required!

Upgrading Seneca
~~~~~~~~~~~~~~~~

To upgrade between Seneca versions:

.. code-block:: bash

    # Backup your configuration
    cp config.yaml config.yaml.backup
    
    # Upgrade Seneca
    pip install --upgrade seneca-viz
    
    # Check for configuration changes
    seneca check-config
    
    # Restart server
    seneca restart

Breaking Changes
----------------

None yet - we strive to maintain backward compatibility.

When breaking changes are necessary, they will be:

1. Announced in advance
2. Documented with migration guides
3. Supported with compatibility layers
4. Released in major versions only

Deprecation Policy
------------------

* Deprecated features will be marked in documentation
* Deprecation warnings will be shown in logs
* Deprecated features maintained for 2 minor versions
* Removal only in major version releases

Support Policy
--------------

* Latest version: Full support
* Previous minor version: Security fixes
* Older versions: Community support only

See `SECURITY.md` for security policy details.