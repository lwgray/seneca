API System
==========

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

The API System is Seneca's RESTful interface layer that exposes Marcus orchestration data through well-defined endpoints. It serves as the bridge between the frontend visualization components and the backend data sources, providing both real-time and historical analytics capabilities.

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

The API System consists of six specialized API modules:

1. **Conversation API** (``conversation_api.py``)
   
   - Agent communication visualization
   - Real-time conversation streaming
   - Decision-making process insights

2. **Agent Management API** (``agent_management_api.py``)
   
   - Agent registration and status
   - Task assignment monitoring
   - Workload distribution analytics

3. **Project Management API** (``project_management_api.py``)
   
   - Project lifecycle tracking
   - Board configuration management
   - Multi-project orchestration

4. **Pipeline Enhancement API** (``pipeline_enhancement_api.py``)
   
   - Pipeline execution monitoring
   - Flow visualization and replay
   - What-if analysis scenarios

5. **Memory Insights API** (``memory_insights_api.py``)
   
   - Historical pattern analysis
   - Learning system insights
   - Performance predictions

6. **Pattern Learning API** (``pattern_learning_api.py``)
   
   - Project similarity detection
   - Quality assessment metrics
   - Recommendation engine interface

Design Principles
~~~~~~~~~~~~~~~~~

- **RESTful Architecture**: Standard HTTP methods and status codes
- **Async Operations**: Non-blocking request handling
- **Role-Based Access**: Different endpoints for different user types
- **Real-Time Support**: WebSocket integration for live updates

How It Works
------------

Request Flow
~~~~~~~~~~~~

.. code-block:: text

   Client Request → Flask Router → Async Wrapper → API Handler
        ↓                                              ↓
   Response ← JSON Serialization ← Data Processing ← MCP Client

Example: Agent Status Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # 1. Client requests agent status
   GET /api/agents/agent-001/status
   
   # 2. Route handler processes request
   @agent_api.route('/<agent_id>/status')
   @async_route
   async def get_status(agent_id):
       # 3. Call Marcus via MCP client
       client = get_marcus_client()
       result = await client.get_agent_status(agent_id)
       
       # 4. Return JSON response
       return jsonify(result)

Marcus Integration
------------------

Communication Patterns
~~~~~~~~~~~~~~~~~~~~~~

1. **Direct MCP Calls**
   
   - Real-time data queries
   - System status checks
   - Live metrics retrieval

2. **Log File Analysis**
   
   - Historical data processing
   - Trend analysis
   - Pattern detection

3. **Event Subscription**
   
   - WebSocket notifications
   - State change alerts
   - Progress updates

API Endpoints
-------------

Conversation API
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Endpoint
     - Method
     - Description
   * - /api/conversations
     - GET
     - List all conversations with filtering
   * - /api/conversations/stream
     - WS
     - Real-time conversation updates
   * - /api/conversations/analytics
     - GET
     - Communication pattern analysis

Agent Management API
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Endpoint
     - Method
     - Description
   * - /api/agents/register
     - POST
     - Register new agent (simulation)
   * - /api/agents/list
     - GET
     - List all registered agents
   * - /api/agents/{id}/status
     - GET
     - Get specific agent status
   * - /api/agents/{id}/request-task
     - POST
     - Simulate task request
   * - /api/agents/report-progress
     - POST
     - Update task progress

Project Management API
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Endpoint
     - Method
     - Description
   * - /api/projects
     - GET
     - List all projects
   * - /api/projects/current
     - GET
     - Get active project
   * - /api/projects/switch
     - POST
     - Change active project
   * - /api/projects/{id}/health
     - GET
     - Project health metrics

Value Proposition
-----------------

Unified Interface
~~~~~~~~~~~~~~~~~

The API System provides:

- **Single Access Point**: All Marcus data through one interface
- **Consistent Format**: Standardized JSON responses
- **Error Handling**: Graceful degradation when Marcus is offline
- **Data Aggregation**: Combines multiple data sources

Questions It Answers
~~~~~~~~~~~~~~~~~~~~

**Operational Questions**:

1. What are my agents currently working on?
2. Which projects have the most blockers?
3. What's the task completion rate?
4. Where are the bottlenecks?

**Strategic Questions**:

1. Which agent skills are underutilized?
2. What project patterns lead to success?
3. How accurate are our estimates?
4. What causes project delays?

Analysis Capabilities
---------------------

Real-Time Analytics
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Agent utilization analysis
   agents = await api.get('/api/agents/list')
   utilization = calculate_utilization(agents)
   
   # Bottleneck detection
   health = await api.get('/api/projects/current/health')
   bottlenecks = identify_critical_paths(health)

Historical Analysis
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Performance trending
   conversations = await api.get('/api/conversations', {
       'start_date': '2024-01-01',
       'end_date': '2024-12-31'
   })
   trends = analyze_performance_trends(conversations)

Predictive Analytics
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Success prediction
   patterns = await api.get('/api/patterns/recommendations', {
       'project_type': 'web_app',
       'team_size': 5
   })
   success_probability = patterns['prediction']['success_rate']

Pattern Identification
----------------------

Communication Patterns
~~~~~~~~~~~~~~~~~~~~~~

1. **Request-Response Cycles**: Agent query patterns
2. **Decision Chains**: PM decision sequences
3. **Collaboration Networks**: Agent interaction graphs
4. **Error Cascades**: Failure propagation patterns

Performance Patterns
~~~~~~~~~~~~~~~~~~~~

1. **Peak Load Times**: When system is busiest
2. **Response Time Variations**: API latency patterns
3. **Resource Utilization**: Memory and CPU trends
4. **Cache Hit Rates**: Data access patterns

Interpretation Guidelines
-------------------------

Response Formats
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "success": true,
     "data": {
       "agents": [...],
       "total": 25,
       "active": 18
     },
     "metadata": {
       "timestamp": "2024-01-15T10:30:00Z",
       "source": "marcus_mcp",
       "cached": false
     }
   }

Status Codes
~~~~~~~~~~~~

- **200 OK**: Successful data retrieval
- **202 Accepted**: Async operation initiated
- **404 Not Found**: Resource doesn't exist
- **503 Service Unavailable**: Marcus offline

Advantages
----------

1. **Abstraction Layer**: Hides MCP complexity
2. **Caching**: Improves response times
3. **Aggregation**: Combines multiple data sources
4. **Filtering**: Client-side data reduction
5. **Versioning**: API evolution support

Product Tiers
-------------

**Open Source (Public)**:

Core APIs:
- Basic agent and project endpoints
- Read-only operations
- Simple filtering and pagination
- JSON response format
- Rate limiting (100 req/min)

**Enterprise Add-ons**:

Advanced Features:
- GraphQL interface
- Batch operations API
- Webhook subscriptions
- Custom aggregations
- Priority queuing
- Response caching
- API key management
- SLA monitoring
- Custom endpoints
- Data export APIs

Configuration
-------------

API Settings
~~~~~~~~~~~~

.. code-block:: python

   # config.py
   API_CONFIG = {
       'rate_limit': 100,  # requests per minute
       'cache_ttl': 300,   # seconds
       'page_size': 50,    # default pagination
       'timeout': 30,      # request timeout
       'cors_origins': ['http://localhost:3000']
   }

Security
~~~~~~~~

.. code-block:: python

   # Authentication middleware
   @app.before_request
   def check_auth():
       if not is_authenticated(request):
           return jsonify({'error': 'Unauthorized'}), 401

Best Practices
--------------

1. **Error Handling**
   
   - Always return consistent error formats
   - Include helpful error messages
   - Log all errors for debugging

2. **Performance**
   
   - Implement response caching
   - Use pagination for large datasets
   - Optimize database queries

3. **Documentation**
   
   - Keep OpenAPI specs updated
   - Provide example requests/responses
   - Version APIs properly

API Documentation
-----------------

OpenAPI Specification
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   openapi: 3.0.0
   info:
     title: Seneca API
     version: 1.0.0
   paths:
     /api/agents/list:
       get:
         summary: List all agents
         responses:
           200:
             description: Agent list
             content:
               application/json:
                 schema:
                   $ref: '#/components/schemas/AgentList'

Future Enhancements
-------------------

- GraphQL support for flexible queries
- Real-time subscriptions via WebSocket
- API versioning strategy
- OAuth2 authentication
- Request batching
- Response compression
- API analytics dashboard
- Developer portal