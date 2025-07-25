MCP Client System
==================

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

The MCP (Model Context Protocol) Client System is Seneca's primary interface for communicating with Marcus. It provides a robust, transport-agnostic connection layer that enables real-time data retrieval and observability of the Marcus orchestration system.

Architecture
------------

Components
~~~~~~~~~~

1. **MarcusClient** (``marcus_client.py``)
   
   - Main client class handling MCP connections
   - Supports multiple transport protocols (stdio, HTTP)
   - Implements auto-discovery of running Marcus instances
   - Manages session lifecycle and connection pooling

2. **Transport Layer**
   
   - **STDIO Transport**: Direct process communication via pipes
   - **HTTP Transport**: RESTful API with session management
   - Automatic fallback and retry mechanisms

3. **Session Management**
   
   - Client registration with role-based access
   - Persistent session tracking
   - Automatic reconnection on failure

How It Works
------------

Connection Flow
~~~~~~~~~~~~~~~

1. **Discovery Phase**
   
   - Scans ``~/.marcus/services/`` for active Marcus instances
   - Validates running processes using PID checks
   - Selects most recent instance or uses configured endpoint

2. **Authentication Phase**
   
   - Registers as "observer" client type
   - Receives filtered tool list based on role
   - Establishes session for subsequent operations

3. **Communication Phase**
   
   - Sends tool calls via MCP protocol
   - Receives structured responses
   - Handles errors and reconnection

Code Example
~~~~~~~~~~~~

.. code-block:: python

   # Initialize and connect
   client = MarcusClient()
   await client.connect(auto_discover=True)
   
   # Register as observer
   await client.call_tool("register_client", {
       "client_id": "seneca-001",
       "client_type": "observer",
       "role": "analytics"
   })
   
   # Query project status
   status = await client.get_project_status()

Marcus Integration
------------------

Available Tools
~~~~~~~~~~~~~~~

As an "observer" client, Seneca has access to:

**Monitoring Tools**:

- ``ping`` - Health checks and diagnostics
- ``get_project_status`` - Current project metrics
- ``list_registered_agents`` - Active agent inventory
- ``get_agent_status`` - Individual agent details
- ``check_board_health`` - Board health analysis
- ``check_task_dependencies`` - Dependency graphs

**Analytics Tools**:

- ``pipeline_monitor_dashboard`` - Live dashboard data
- ``pipeline_monitor_flow`` - Flow tracking
- ``pipeline_predict_risk`` - Risk predictions
- ``pipeline_find_similar`` - Pattern matching
- ``pipeline_report`` - Report generation

Value Proposition
-----------------

Real-Time Observability
~~~~~~~~~~~~~~~~~~~~~~~

The MCP Client enables:

- **Live Agent Monitoring**: Track agent status, workload, and performance
- **Project Health Metrics**: Real-time project progress and bottlenecks
- **System Diagnostics**: Health checks and performance monitoring

Questions It Answers
~~~~~~~~~~~~~~~~~~~~

1. **System Health**
   
   - Is Marcus running and responsive?
   - What's the current system load?
   - Are there any stuck assignments?

2. **Agent Performance**
   
   - Which agents are active?
   - What tasks are they working on?
   - What's their completion rate?

3. **Project Status**
   
   - What's the overall project progress?
   - Are there any blockers?
   - What's the task completion velocity?

Analysis Capabilities
---------------------

Performance Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Analyze agent utilization
   agents = await client.list_registered_agents()
   utilization = {
       agent['id']: agent['current_task'] is not None 
       for agent in agents
   }

Risk Assessment
~~~~~~~~~~~~~~~

.. code-block:: python

   # Predict pipeline failures
   risk = await client.call_tool("pipeline_predict_risk", {
       "flow_id": current_flow
   })
   if risk['probability'] > 0.7:
       alert("High failure risk detected")

Pattern Identification
----------------------

Key Patterns to Detect
~~~~~~~~~~~~~~~~~~~~~~

1. **Connection Patterns**
   
   - Frequent disconnections (network issues)
   - Slow response times (performance degradation)
   - Failed tool calls (permission issues)

2. **Usage Patterns**
   
   - Peak activity times
   - Most frequently called tools
   - Error rate trends

3. **Performance Patterns**
   
   - Response time distributions
   - Throughput variations
   - Resource utilization cycles

Interpretation Guidelines
-------------------------

Response Codes
~~~~~~~~~~~~~~

- **Success**: Normal operation, data retrieved
- **503 Service Unavailable**: Marcus not running
- **401 Unauthorized**: Client not registered
- **429 Rate Limited**: Too many requests

Metrics Interpretation
~~~~~~~~~~~~~~~~~~~~~~

- **Latency < 100ms**: Excellent performance
- **Latency 100-500ms**: Normal operation
- **Latency > 500ms**: Potential issues
- **Connection failures**: Check Marcus health

Advantages
----------

1. **Protocol Abstraction**: Works with any MCP transport
2. **Automatic Discovery**: Finds Marcus instances automatically
3. **Role-Based Access**: Only sees appropriate tools
4. **Resilient Connection**: Auto-reconnect and retry
5. **Type Safety**: Structured tool calls and responses

Product Tiers
-------------

**Open Source (Public)**:

- Basic connection and authentication
- Read-only tool access
- Manual configuration
- STDIO transport only

**Enterprise Add-ons**:

- HTTP/WebSocket transport
- Connection pooling and load balancing
- Advanced retry strategies
- Custom authentication providers
- Priority queue for tool calls
- Connection analytics and monitoring
- SLA guarantees on response times

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Transport selection
   MARCUS_TRANSPORT=http  # or stdio, auto
   
   # HTTP transport settings
   MARCUS_HTTP_URL=http://marcus-server:4298/mcp
   
   # Connection settings
   MARCUS_CONNECT_TIMEOUT=30
   MARCUS_RETRY_ATTEMPTS=3

Best Practices
--------------

1. **Connection Management**
   
   - Always use ``async with`` for session management
   - Implement connection pooling for high-frequency queries
   - Set appropriate timeouts

2. **Error Handling**
   
   - Catch ``ConnectionError`` for network issues
   - Implement exponential backoff for retries
   - Log all failures for debugging

3. **Performance**
   
   - Batch related queries when possible
   - Cache frequently accessed data
   - Use appropriate polling intervals

Future Enhancements
-------------------

- WebSocket support for real-time updates
- GraphQL interface for complex queries
- Distributed tracing integration
- Multi-instance load balancing
- Custom transport plugins