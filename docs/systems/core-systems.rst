============
Core Systems
============

The core systems provide the essential foundation for Seneca's operation, including command-line interface, service discovery, configuration management, and the main web server.

.. contents:: Table of Contents
   :local:
   :depth: 3

CLI System
==========

**Location**: :file:`seneca_cli.py:1-300`

The Command-Line Interface provides user-friendly commands for managing Seneca operations.

Architecture
-----------

.. code-block:: python

   # Core CLI commands
   seneca status    # Check Marcus instances
   seneca start     # Start dashboard
   seneca logs      # View Marcus logs

Components
----------

.. py:function:: discover_marcus_services()
   :module: seneca_cli
   
   Discovers active Marcus instances from the service registry.
   
   :returns: List of active Marcus service information
   :rtype: List[Dict[str, Any]]

.. py:function:: start_dashboard(marcus_server=None, port=5000)
   :module: seneca_cli
   
   Starts the Seneca dashboard with optional Marcus server specification.

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Normal Startup
        :class-card: sd-border-success
        
        **Condition**: Marcus instance running, auto-discovery enabled
        
        **Flow**:
        
        1. User runs ``seneca start``
        2. CLI calls ``discover_marcus_services()``
        3. Service registry scanned for active instances
        4. Latest Marcus instance selected
        5. Dashboard starts with real-time connection
        
        **Result**: Full visualization capabilities with live data
        
        **Indicators**:
        
        * ✅ Connection status: Connected
        * ✅ Real-time updates flowing
        * ✅ All features available

    .. grid-item-card:: 🟡 Manual Server Selection
        :class-card: sd-border-warning
        
        **Condition**: Multiple Marcus instances, specific server needed
        
        **Flow**:
        
        1. User runs ``seneca start --marcus-server /path/to/marcus``
        2. CLI bypasses auto-discovery
        3. Direct connection attempt to specified server
        4. Dashboard starts with targeted connection
        
        **Result**: Connected to specific Marcus instance
        
        **Indicators**:
        
        * ✅ Connection status: Connected (Manual)
        * ⚠️  Auto-discovery disabled
        * ✅ Targeted monitoring active

    .. grid-item-card:: 🔴 No Marcus Found
        :class-card: sd-border-danger
        
        **Condition**: No running Marcus instances detected
        
        **Flow**:
        
        1. User runs ``seneca start``
        2. CLI calls ``discover_marcus_services()``
        3. Service registry empty or stale entries
        4. Dashboard starts in log-only mode
        
        **Result**: Historical data visualization only
        
        **Indicators**:
        
        * ❌ Connection status: Disconnected
        * ⚠️  Log-only mode active
        * 📁 Historical data available

    .. grid-item-card:: 🔵 Status Check
        :class-card: sd-border-primary
        
        **Condition**: User wants to check system status
        
        **Flow**:
        
        1. User runs ``seneca status``
        2. CLI scans service registry
        3. Process verification with ``psutil.pid_exists()``
        4. Display active instances with details
        
        **Result**: Comprehensive system status report
        
        **Indicators**:
        
        * 📊 Instance count and details
        * ⏱️  Startup timestamps
        * 🔄 Process health status

Marcus Service Detection System
==============================

**Purpose**: Automatically discover and connect to running Marcus instances through a file-based service registry.

Architecture
-----------

.. graphviz::

   digraph service_detection {
       rankdir=LR;
       node [shape=box, style="rounded,filled"];
       
       "Marcus Instance" [fillcolor=lightblue];
       "Service Registry\n(~/.marcus/services/)" [fillcolor=lightyellow, shape=cylinder];
       "Service Detection" [fillcolor=lightgreen];
       "Process Verification" [fillcolor=lightcyan];
       "MCP Connection" [fillcolor=pink];
       
       "Marcus Instance" -> "Service Registry\n(~/.marcus/services/)" [label="registers\nmarcus_*.json"];
       "Service Detection" -> "Service Registry\n(~/.marcus/services/)" [label="scans for\nactive services"];
       "Service Detection" -> "Process Verification" [label="verify PIDs"];
       "Process Verification" -> "Service Detection" [label="cleanup stale\nentries"];
       "Service Detection" -> "MCP Connection" [label="latest instance\ninfo"];
   }

Service Registry Format
----------------------

Marcus instances register themselves by creating JSON files in the service registry:

.. code-block:: json

   {
     "instance_id": "marcus_20250714_142335_abc123",
     "pid": 12345,
     "project_name": "my-ai-project",
     "provider": "github",
     "log_dir": "/Users/user/.marcus/logs/my-ai-project",
     "started_at": "2025-07-14T14:23:35Z",
     "mcp_command": "python -m marcus.mcp_server --project /path/to/project"
   }

Discovery Process
----------------

.. mermaid::

   flowchart TD
       A[Start Discovery] --> B[Scan ~/.marcus/services/]
       B --> C{JSON files found?}
       C -->|No| D[Return empty list]
       C -->|Yes| E[Parse each marcus_*.json]
       
       E --> F[Extract PID from JSON]
       F --> G{Process exists?}
       G -->|No| H[Delete stale file]
       G -->|Yes| I[Add to active list]
       
       H --> J{More files?}
       I --> J
       J -->|Yes| E
       J -->|No| K[Sort by started_at]
       K --> L[Return active services]

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Single Marcus Instance
        :class-card: sd-border-success
        
        **Condition**: One Marcus instance running
        
        **Detection Flow**:
        
        1. Scan ``~/.marcus/services/`` directory
        2. Find ``marcus_abc123.json`` file
        3. Verify PID 12345 exists with ``psutil.pid_exists()``
        4. Return instance information
        
        **Connection**:
        
        * Extract MCP command from service file
        * Establish direct connection
        * Begin real-time data streaming
        
        **Behavior**:
        
        * Auto-selection of the single instance
        * Immediate connection attempt
        * Full functionality available

    .. grid-item-card:: 🟡 Multiple Marcus Instances
        :class-card: sd-border-warning
        
        **Condition**: Multiple Marcus instances running
        
        **Detection Flow**:
        
        1. Scan finds multiple ``marcus_*.json`` files
        2. Verify all PIDs are active
        3. Sort by ``started_at`` timestamp
        4. Select most recent instance
        
        **Connection**:
        
        * Connect to latest started instance
        * Other instances remain available for manual selection
        * User can override with ``--marcus-server`` flag
        
        **Behavior**:
        
        * Automatic selection of newest instance
        * Clear indication of selection criteria
        * Manual override capability preserved

    .. grid-item-card:: 🔴 Stale Registry Entries
        :class-card: sd-border-danger
        
        **Condition**: Service files exist but processes terminated
        
        **Detection Flow**:
        
        1. Scan finds ``marcus_*.json`` files
        2. Process verification fails for PIDs
        3. Auto-cleanup removes stale files
        4. Continue scanning remaining entries
        
        **Connection**:
        
        * No connection possible to terminated processes
        * Clean registry for future discoveries
        * Fallback to log-only mode if no active instances
        
        **Behavior**:
        
        * Automatic cleanup of stale entries
        * Graceful degradation to available modes
        * User notification of cleanup actions

    .. grid-item-card:: 🔵 Cross-Platform Discovery
        :class-card: sd-border-primary
        
        **Condition**: Different operating systems and paths
        
        **Registry Locations**:
        
        * **Unix/Linux/macOS**: ``~/.marcus/services/``
        * **Windows**: ``%APPDATA%/.marcus/services/``
        * **Fallback**: Temp directory if home unavailable
        
        **Process Verification**:
        
        * Uses ``psutil`` for cross-platform PID checking
        * Handles platform-specific process behaviors
        * Graceful fallback for permission issues
        
        **Behavior**:
        
        * Consistent discovery across platforms
        * Platform-specific optimizations
        * Robust error handling

Configuration System
====================

**Location**: :file:`config.py:1-150`

Centralized configuration management with environment variable support and validation.

Configuration Categories
-----------------------

.. tab-set::

    .. tab-item:: Server Configuration
        
        .. code-block:: python
        
           # Flask server settings
           SENECA_HOST = "127.0.0.1"
           SENECA_PORT = 5000
           SENECA_DEBUG = False
           
           # WebSocket settings
           WEBSOCKET_TIMEOUT = 30
           WEBSOCKET_PING_INTERVAL = 10

    .. tab-item:: Path Configuration
        
        .. code-block:: python
        
           # Directory paths
           SENECA_LOG_DIR = "~/.seneca/logs"
           SENECA_DATA_DIR = "~/.seneca/data"
           SENECA_CACHE_DIR = "~/.seneca/cache"
           
           # Marcus integration paths
           MARCUS_SERVICE_REGISTRY = "~/.marcus/services"
           MARCUS_LOG_FALLBACK = "~/.marcus/logs"

    .. tab-item:: UI Configuration
        
        .. code-block:: python
        
           # Theme settings
           SENECA_THEME = "dark"  # dark, light, auto
           
           # Feature flags
           ENABLE_REAL_TIME_UPDATES = True
           ENABLE_AI_ANALYSIS = True
           ENABLE_PATTERN_LEARNING = True
           
           # Performance settings
           MAX_CONVERSATION_HISTORY = 1000
           REFRESH_INTERVAL = 1000  # milliseconds

    .. tab-item:: Caching Configuration
        
        .. code-block:: python
        
           # Cache settings
           CACHE_ENABLED = True
           CACHE_TTL = 300  # seconds
           CACHE_MAX_SIZE = 100  # MB
           
           # Redis configuration (optional)
           REDIS_URL = None
           REDIS_PASSWORD = None

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Default Configuration
        :class-card: sd-border-success
        
        **Condition**: No environment variables set
        
        **Behavior**:
        
        * Uses built-in defaults from ``config.py``
        * Server starts on ``127.0.0.1:5000``
        * Dark theme enabled
        * All features enabled with conservative limits
        
        **Suitable For**:
        
        * Development environments
        * Quick testing and demonstrations
        * First-time users

    .. grid-item-card:: 🟡 Environment Override
        :class-card: sd-border-warning
        
        **Condition**: Environment variables provided
        
        **Example**:
        
        .. code-block:: bash
        
           export SENECA_PORT=8080
           export SENECA_THEME=light
           export ENABLE_AI_ANALYSIS=false
           seneca start
        
        **Behavior**:
        
        * Environment variables override defaults
        * Validation ensures type safety
        * Invalid values fall back to defaults with warnings
        
        **Suitable For**:
        
        * Production deployments
        * Custom enterprise configurations
        * Performance tuning

    .. grid-item-card:: 🔴 Configuration Validation
        :class-card: sd-border-danger
        
        **Condition**: Invalid configuration values
        
        **Validation Checks**:
        
        * Port numbers in valid range (1024-65535)
        * Directory paths are writable
        * Boolean values properly converted
        * Numeric limits within reasonable bounds
        
        **Error Handling**:
        
        * Log warnings for invalid values
        * Fall back to safe defaults
        * Continue operation with corrected config
        
        **Prevention**:
        
        * Schema validation on startup
        * Type checking and conversion
        * Range validation for numeric values

    .. grid-item-card:: 🔵 Dynamic Reconfiguration
        :class-card: sd-border-primary
        
        **Condition**: Configuration changes during runtime
        
        **Hot-Reloadable Settings**:
        
        * Theme preferences
        * Feature flags
        * Cache settings
        * Refresh intervals
        
        **Non-Reloadable Settings**:
        
        * Server host and port
        * Core directory paths
        * Security settings
        
        **Implementation**:
        
        * WebSocket broadcasts for UI updates
        * Configuration file watchers
        * API endpoints for admin changes

Flask Server System
==================

**Location**: :file:`src/seneca_server.py:1-200`

The main web server provides REST API endpoints, WebSocket support, and static file serving.

Server Architecture
------------------

.. graphviz::

   digraph flask_server {
       rankdir=TB;
       node [shape=box, style="rounded,filled"];
       
       subgraph cluster_server {
           label="Flask Server";
           style=filled;
           fillcolor=lightblue;
           
           "Flask App" [fillcolor=lightblue];
           "Blueprint Registry" [fillcolor=lightblue];
           "Middleware Stack" [fillcolor=lightblue];
           "Static File Handler" [fillcolor=lightblue];
       }
       
       subgraph cluster_apis {
           label="API Blueprints";
           style=filled;
           fillcolor=lightyellow;
           
           "Conversation API" [fillcolor=lightyellow];
           "Agent Management API" [fillcolor=lightyellow];
           "Project API" [fillcolor=lightyellow];
           "WebSocket Handler" [fillcolor=lightyellow];
       }
       
       subgraph cluster_clients {
           label="Clients";
           style=filled;
           fillcolor=lightgreen;
           
           "Vue Frontend" [fillcolor=lightgreen];
           "REST Clients" [fillcolor=lightgreen];
           "WebSocket Clients" [fillcolor=lightgreen];
       }
       
       "Flask App" -> "Blueprint Registry";
       "Flask App" -> "Middleware Stack";
       "Flask App" -> "Static File Handler";
       
       "Blueprint Registry" -> "Conversation API";
       "Blueprint Registry" -> "Agent Management API";
       "Blueprint Registry" -> "Project API";
       "Blueprint Registry" -> "WebSocket Handler";
       
       "Vue Frontend" -> "Static File Handler";
       "REST Clients" -> "Conversation API";
       "REST Clients" -> "Agent Management API";
       "REST Clients" -> "Project API";
       "WebSocket Clients" -> "WebSocket Handler";
   }

Server Startup Process
---------------------

.. mermaid::

   sequenceDiagram
       participant Main as Main Process
       participant Config as Configuration
       participant Flask as Flask App
       participant MCP as MCP Client
       participant WS as WebSocket
       participant APIs as API Blueprints
       
       Main->>Config: load_configuration()
       Config-->>Main: config object
       
       Main->>Flask: create_app(config)
       Flask->>APIs: register_blueprints()
       APIs-->>Flask: blueprints registered
       
       Main->>MCP: initialize_client()
       MCP->>MCP: attempt auto-discovery
       MCP-->>Main: connection status
       
       Main->>WS: setup_websocket(app)
       WS-->>Main: websocket ready
       
       Main->>Flask: app.run(host, port)
       Flask-->>Main: server running

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Successful Startup
        :class-card: sd-border-success
        
        **Condition**: All systems operational
        
        **Startup Sequence**:
        
        1. Configuration loaded successfully
        2. Marcus instance discovered and connected
        3. All API blueprints registered
        4. WebSocket server initialized
        5. Static file serving configured
        6. Server starts on configured port
        
        **Health Indicators**:
        
        * ✅ Configuration validation passed
        * ✅ MCP connection established
        * ✅ All endpoints responding
        * ✅ WebSocket connections accepted
        
        **Available Features**:
        
        * Full REST API functionality
        * Real-time WebSocket updates
        * Static frontend serving
        * Live agent monitoring

    .. grid-item-card:: 🟡 Degraded Mode Startup
        :class-card: sd-border-warning
        
        **Condition**: Marcus connection failed, server operational
        
        **Startup Sequence**:
        
        1. Configuration loaded successfully
        2. Marcus discovery fails or connection timeout
        3. Server starts in log-only mode
        4. APIs available but with limited data
        5. WebSocket functional for cached data
        
        **Health Indicators**:
        
        * ✅ Server started successfully
        * ⚠️  MCP connection failed
        * ✅ Static content serving
        * 📁 Historical data available
        
        **Available Features**:
        
        * Limited REST API (cached/historical data)
        * WebSocket for UI updates
        * Static visualizations
        * Log file analysis

    .. grid-item-card:: 🔴 Startup Failure
        :class-card: sd-border-danger
        
        **Condition**: Critical system failure preventing startup
        
        **Failure Scenarios**:
        
        * Port already in use
        * Configuration file errors
        * Missing dependencies
        * Insufficient permissions
        * Database connection failures
        
        **Error Handling**:
        
        1. Log detailed error information
        2. Attempt automatic resolution where possible
        3. Provide clear user guidance
        4. Graceful shutdown if unrecoverable
        
        **Recovery Actions**:
        
        * Port conflict: Suggest alternative ports
        * Permissions: Guide user to fix permissions
        * Dependencies: List missing requirements
        * Config errors: Show validation details

    .. grid-item-card:: 🔵 Hot Reload Development
        :class-card: sd-border-primary
        
        **Condition**: Development mode with code changes
        
        **Development Features**:
        
        * Flask debug mode enabled
        * Automatic code reload on changes
        * Detailed error tracebacks
        * Vue.js hot module replacement
        * Development proxy configuration
        
        **Behavior**:
        
        1. File system watchers detect changes
        2. Server automatically restarts
        3. Frontend updates without page refresh
        4. Development tools integration
        5. Enhanced logging and debugging
        
        **Performance**:
        
        * Faster development cycles
        * Immediate feedback on changes
        * Preserved application state where possible
        * Debugging tools integration

Integration Patterns
===================

The core systems work together through well-defined integration patterns.

System Initialization Order
---------------------------

.. mermaid::

   graph TD
       A[CLI Command] --> B[Configuration Loading]
       B --> C[Service Discovery]
       C --> D{Marcus Found?}
       D -->|Yes| E[MCP Connection]
       D -->|No| F[Log-Only Mode]
       E --> G[Flask Server Start]
       F --> G
       G --> H[API Registration]
       H --> I[WebSocket Setup]
       I --> J[Frontend Serving]
       J --> K[System Ready]

Cross-System Communication
-------------------------

.. tab-set::

    .. tab-item:: Service Discovery → MCP Client
        
        **Data Flow**: Service registry information to connection parameters
        
        .. code-block:: python
        
           # Service discovery provides
           service_info = {
               "mcp_command": "python -m marcus.mcp_server --project /path",
               "instance_id": "marcus_abc123",
               "log_dir": "/Users/user/.marcus/logs"
           }
           
           # MCP client uses for connection
           await mcp_client.connect(
               command=service_info["mcp_command"],
               auto_discover=True
           )

    .. tab-item:: Configuration → All Systems
        
        **Data Flow**: Centralized configuration to system-specific settings
        
        .. code-block:: python
        
           # Configuration provides
           config = {
               "server": {"host": "127.0.0.1", "port": 5000},
               "paths": {"log_dir": "~/.seneca/logs"},
               "features": {"enable_ai_analysis": True}
           }
           
           # Systems consume
           flask_app.run(host=config.server.host, port=config.server.port)
           logger.setup(log_dir=config.paths.log_dir)
           ai_engine.enabled = config.features.enable_ai_analysis

    .. tab-item:: CLI → Flask Server
        
        **Data Flow**: Command-line parameters to server configuration
        
        .. code-block:: python
        
           # CLI processes arguments
           args = parse_args()  # --marcus-server, --port, --debug
           
           # Flask server receives configuration
           server_config = {
               "marcus_server": args.marcus_server,
               "port": args.port,
               "debug": args.debug
           }
           
           # Server adapts behavior
           if server_config.marcus_server:
               # Manual Marcus server specification
               mcp_client.server_path = server_config.marcus_server

    .. tab-item:: All Systems → Error Handling
        
        **Data Flow**: System errors to centralized error handling
        
        .. code-block:: python
        
           # Systems report errors to central handler
           error_handler.report_error(
               system="service_discovery",
               error_type="connection_failed",
               details={"marcus_server": "/path/to/server"},
               recovery_suggestions=["Check Marcus is running", "Verify path"]
           )
           
           # Error handler coordinates response
           if error_handler.can_recover():
               error_handler.attempt_recovery()
           else:
               error_handler.graceful_degradation()

Performance Considerations
=========================

.. tab-set::

    .. tab-item:: Service Discovery
        
        **Optimization Strategies**:
        
        * Cache discovery results for short periods
        * Use file system watchers instead of polling
        * Implement concurrent PID verification
        * Lazy cleanup of stale entries
        
        **Performance Metrics**:
        
        * Discovery time: < 100ms for typical setups
        * Registry scan: < 50ms for 10 instances
        * PID verification: < 10ms per process

    .. tab-item:: Configuration Loading
        
        **Optimization Strategies**:
        
        * Parse configuration once at startup
        * Cache environment variable lookups
        * Validate configuration in background
        * Use immutable configuration objects
        
        **Performance Metrics**:
        
        * Load time: < 50ms for full configuration
        * Validation: < 20ms for complete schema
        * Memory usage: < 5MB for configuration data

    .. tab-item:: Flask Server
        
        **Optimization Strategies**:
        
        * Use production WSGI server (Gunicorn, uWSGI)
        * Enable response compression
        * Implement request/response caching
        * Optimize static file serving
        
        **Performance Metrics**:
        
        * Startup time: < 2 seconds in production
        * Response time: < 100ms for API endpoints
        * Concurrent connections: 100+ WebSocket clients
        * Memory usage: Base 50MB + 1MB per client

Troubleshooting Guide
====================

Common Issues and Solutions
--------------------------

.. dropdown:: Service Discovery Issues
   :class-title: sd-text-danger
   
   **Problem**: No Marcus instances found
   
   **Diagnostic Steps**:
   
   1. Check service registry: ``ls ~/.marcus/services/``
   2. Verify Marcus is running: ``ps aux | grep marcus``
   3. Check permissions: ``ls -la ~/.marcus/``
   
   **Solutions**:
   
   * Start Marcus instance
   * Fix registry permissions
   * Use manual server specification
   * Check for path configuration issues

.. dropdown:: Configuration Problems
   :class-title: sd-text-warning
   
   **Problem**: Server won't start due to configuration
   
   **Diagnostic Steps**:
   
   1. Check configuration file syntax
   2. Verify environment variables
   3. Test port availability: ``netstat -ln | grep :5000``
   4. Check directory permissions
   
   **Solutions**:
   
   * Fix configuration syntax errors
   * Clear conflicting environment variables
   * Use alternative port
   * Fix directory permissions

.. dropdown:: Server Startup Issues
   :class-title: sd-text-danger
   
   **Problem**: Flask server fails to start
   
   **Diagnostic Steps**:
   
   1. Check port conflicts
   2. Verify Python environment
   3. Check dependency installation
   4. Review startup logs
   
   **Solutions**:
   
   * Kill conflicting processes
   * Reinstall dependencies
   * Use virtual environment
   * Check system resources

.. dropdown:: Connection Problems
   :class-title: sd-text-warning
   
   **Problem**: Cannot connect to Marcus
   
   **Diagnostic Steps**:
   
   1. Verify Marcus instance is running
   2. Check MCP command in service registry
   3. Test manual connection
   4. Review connection logs
   
   **Solutions**:
   
   * Restart Marcus instance
   * Update service registry
   * Fix MCP command syntax
   * Check network connectivity

Next Steps
==========

* :doc:`api-systems` - Learn about the API layer and WebSocket services
* :doc:`processing-systems` - Understand data processing and analysis
* :doc:`integration-flow` - See how systems work together end-to-end