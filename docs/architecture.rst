Architecture
============

This document describes the architecture of Seneca and how it integrates with Marcus.

System Overview
---------------

.. code-block:: text

    ┌─────────────┐     ┌──────────────┐     ┌────────────┐
    │   Marcus    │────▶│ Log Files    │◀────│   Seneca   │
    │   System    │     │  (JSONL)     │     │  Processor │
    └─────────────┘     └──────────────┘     └────────────┘
                                                    │
                                                    ▼
                        ┌───────────────────────────┴────────────────┐
                        │                                            │
                  ┌─────▼──────┐                          ┌─────────▼────────┐
                  │  Analyzer   │                          │  Visualization   │
                  │   Engine    │                          │     Server       │
                  └─────────────┘                          └──────────────────┘
                                                                    │
                                                                    ▼
                                                           ┌────────────────┐
                                                           │   Web UI       │
                                                           │  (Browser)     │
                                                           └────────────────┘

Core Components
---------------

ConversationProcessor
~~~~~~~~~~~~~~~~~~~~~

The heart of Seneca, responsible for:

* Reading Marcus log files from disk
* Parsing JSONL formatted conversations
* Filtering and sorting conversations
* Providing query interfaces

**Key Features:**

* Efficient file reading with caching
* Support for large log files
* Real-time streaming capabilities
* Timezone-aware timestamp handling

.. code-block:: python

    processor = ConversationProcessor(log_dir)
    conversations = processor.get_recent_conversations(limit=100)

ConversationStreamProcessor
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extends ConversationProcessor with streaming capabilities:

* Tracks file positions for incremental reading
* Detects new log entries in real-time
* Handles log file rotation
* Provides WebSocket support

Analyzer Engine
~~~~~~~~~~~~~~~

Modular analysis system with pluggable analyzers:

* **StatisticalAnalyzer** - Basic metrics and counts
* **TemporalAnalyzer** - Time-based patterns
* **BehavioralAnalyzer** - Agent activity analysis
* **PerformanceAnalyzer** - System efficiency metrics

Each analyzer implements the ``BaseAnalyzer`` interface from the core package.

Visualization Server
~~~~~~~~~~~~~~~~~~~~

FastAPI-based web server providing:

* RESTful API endpoints
* WebSocket connections for real-time updates
* Static file serving for the web UI
* Integration with the analyzer engine

Data Flow
---------

1. **Log Generation**
   
   Marcus writes conversations to JSONL files::
   
       {"timestamp": "2024-01-15T10:00:00Z", "type": "worker_to_pm", ...}

2. **File Monitoring**
   
   Seneca monitors log directory for changes:
   
   * New files detected via filesystem watching
   * Existing files checked for new entries
   * File rotation handled automatically

3. **Data Processing**
   
   Raw logs are processed into structured data:
   
   * JSON parsing and validation
   * Timestamp normalization
   * Agent/task extraction
   * Metadata enrichment

4. **Analysis**
   
   Processed data flows through analyzers:
   
   * Real-time analysis for dashboards
   * Batch analysis for reports
   * Cached results for performance

5. **Visualization**
   
   Results delivered to users via:
   
   * REST API for programmatic access
   * WebSocket for real-time updates
   * Web UI for interactive exploration

File Structure
--------------

Log File Format
~~~~~~~~~~~~~~~

Marcus logs are stored as JSONL (JSON Lines)::

    /path/to/marcus/logs/conversations/
    ├── conversations_2024_01_15.jsonl
    ├── conversations_2024_01_16.jsonl
    └── conversations_2024_01_17.jsonl

Each line is a complete JSON object representing one conversation.

Conversation Schema
~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
      "timestamp": "ISO 8601 timestamp with timezone",
      "type": "conversation type enum value",
      "agent_id": "agent identifier (optional)",
      "worker_id": "worker identifier (optional)",
      "task_id": "associated task ID (optional)",
      "message": "conversation content",
      "metadata": {
        "additional": "fields as needed"
      }
    }

Performance Considerations
--------------------------

File Reading Strategy
~~~~~~~~~~~~~~~~~~~~~

* Files read in chunks to minimize memory usage
* Most recent files prioritized
* Configurable read-ahead buffer
* Automatic cache invalidation

Caching Architecture
~~~~~~~~~~~~~~~~~~~~

* In-memory LRU cache for recent conversations
* Analysis results cached with TTL
* File position tracking for streaming
* Configurable cache sizes

Scalability
~~~~~~~~~~~

Seneca scales through:

* **Horizontal** - Multiple Seneca instances can read same logs
* **Vertical** - Efficient algorithms handle large log volumes
* **Temporal** - Old logs can be archived/compressed

Security Model
--------------

* **Local Only** - No external network calls
* **Read Only** - Never modifies Marcus logs
* **File Permissions** - Respects OS file permissions
* **No Authentication** - Relies on OS-level access control

For production deployments, consider:

* Running behind a reverse proxy (nginx, Apache)
* Adding authentication middleware
* Implementing rate limiting
* Enabling HTTPS

Extension Points
----------------

Custom Analyzers
~~~~~~~~~~~~~~~~

Create custom analyzers by extending ``BaseAnalyzer``:

.. code-block:: python

    from base_analyzer import BaseAnalyzer
    
    class CustomAnalyzer(BaseAnalyzer):
        async def analyze_conversations(self, conversations, filters):
            # Custom analysis logic
            return results

Visualization Plugins
~~~~~~~~~~~~~~~~~~~~~

Add custom visualizations by:

1. Creating new API endpoints
2. Adding frontend components
3. Registering with the UI router

Data Exporters
~~~~~~~~~~~~~~

Export data to external systems:

* Prometheus metrics
* Elasticsearch indexes
* Custom databases
* CSV/Excel reports

Future Architecture
-------------------

Planned enhancements include:

* **Distributed Mode** - Cluster support for large deployments
* **Storage Backends** - S3, GCS, Azure Blob support
* **Stream Processing** - Apache Kafka integration
* **ML Pipeline** - Real-time anomaly detection