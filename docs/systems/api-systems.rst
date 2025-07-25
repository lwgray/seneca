===========
API Systems
===========

The API layer provides RESTful endpoints and WebSocket services for data exchange between the frontend, external clients, and Marcus AI instances.

.. contents:: Table of Contents
   :local:
   :depth: 3

API Architecture Overview
========================

.. graphviz::

   digraph api_architecture {
       rankdir=TB;
       node [shape=box, style="rounded,filled"];
       
       subgraph cluster_clients {
           label="API Clients";
           style=filled;
           fillcolor=lightblue;
           "Vue Frontend" [fillcolor=lightblue];
           "External Tools" [fillcolor=lightblue];
           "CLI Tools" [fillcolor=lightblue];
       }
       
       subgraph cluster_gateway {
           label="API Gateway (Flask)";
           style=filled;
           fillcolor=lightyellow;
           "Request Router" [fillcolor=lightyellow];
           "Authentication" [fillcolor=lightyellow];
           "Rate Limiting" [fillcolor=lightyellow];
           "Response Cache" [fillcolor=lightyellow];
       }
       
       subgraph cluster_apis {
           label="API Modules";
           style=filled;
           fillcolor=lightgreen;
           "Conversation API" [fillcolor=lightgreen];
           "Agent Management" [fillcolor=lightgreen];
           "Project Management" [fillcolor=lightgreen];
           "Pipeline Enhancement" [fillcolor=lightgreen];
           "Cost Tracking" [fillcolor=lightgreen];
           "Memory Insights" [fillcolor=lightgreen];
           "Pattern Learning" [fillcolor=lightgreen];
           "Context Visualization" [fillcolor=lightgreen];
       }
       
       subgraph cluster_realtime {
           label="Real-time Services";
           style=filled;
           fillcolor=pink;
           "WebSocket Server" [fillcolor=pink];
           "Event Broadcasting" [fillcolor=pink];
           "Connection Management" [fillcolor=pink];
       }
       
       subgraph cluster_backend {
           label="Backend Services";
           style=filled;
           fillcolor=lightcyan;
           "MCP Client" [fillcolor=lightcyan];
           "Data Processors" [fillcolor=lightcyan];
           "Analytics Engine" [fillcolor=lightcyan];
       }
       
       "Vue Frontend" -> "Request Router";
       "External Tools" -> "Request Router";
       "CLI Tools" -> "Request Router";
       
       "Request Router" -> "Authentication";
       "Authentication" -> "Rate Limiting";
       "Rate Limiting" -> "Response Cache";
       
       "Response Cache" -> "Conversation API";
       "Response Cache" -> "Agent Management";
       "Response Cache" -> "Project Management";
       "Response Cache" -> "Pipeline Enhancement";
       "Response Cache" -> "Cost Tracking";
       "Response Cache" -> "Memory Insights";
       "Response Cache" -> "Pattern Learning";
       "Response Cache" -> "Context Visualization";
       
       "Vue Frontend" -> "WebSocket Server";
       "WebSocket Server" -> "Event Broadcasting";
       "Event Broadcasting" -> "Connection Management";
       
       "Conversation API" -> "MCP Client";
       "Agent Management" -> "Data Processors";
       "Project Management" -> "Analytics Engine";
   }

Core API Modules
===============

Conversation API
===============

**Location**: :file:`src/api/conversation_api.py`

Provides endpoints for agent communication visualization and real-time conversation monitoring.

Endpoints
--------

.. tab-set::

    .. tab-item:: GET /api/conversations
        
        **Purpose**: Retrieve conversation history and metadata
        
        **Parameters**:
        
        * ``limit`` (int, optional): Maximum conversations to return (default: 50)
        * ``offset`` (int, optional): Pagination offset (default: 0)
        * ``agent_id`` (str, optional): Filter by specific agent
        * ``project_id`` (str, optional): Filter by project
        * ``since`` (datetime, optional): Return conversations after timestamp
        
        **Response**:
        
        .. code-block:: json
        
           {
             "conversations": [
               {
                 "id": "conv_123",
                 "agent_id": "agent_456",
                 "project_id": "proj_789",
                 "started_at": "2025-07-14T10:30:00Z",
                 "status": "active",
                 "message_count": 42,
                 "last_activity": "2025-07-14T11:15:30Z"
               }
             ],
             "total": 150,
             "has_more": true
           }

    .. tab-item:: GET /api/conversations/{id}/messages
        
        **Purpose**: Retrieve messages for a specific conversation
        
        **Parameters**:
        
        * ``id`` (str): Conversation identifier
        * ``limit`` (int, optional): Messages per page (default: 100)
        * ``before`` (str, optional): Message ID for pagination
        
        **Response**:
        
        .. code-block:: json
        
           {
             "messages": [
               {
                 "id": "msg_123",
                 "conversation_id": "conv_123",
                 "sender": "agent_456",
                 "recipient": "user",
                 "content": "Analysis complete. Found 3 issues.",
                 "timestamp": "2025-07-14T11:15:30Z",
                 "message_type": "response",
                 "metadata": {
                   "tool_calls": ["analyze_code"],
                   "execution_time": 1.25
                 }
               }
             ],
             "has_more": false
           }

    .. tab-item:: POST /api/conversations/{id}/stream
        
        **Purpose**: Start real-time conversation streaming
        
        **Request Body**:
        
        .. code-block:: json
        
           {
             "include_metadata": true,
             "filter_types": ["request", "response", "error"],
             "real_time": true
           }
        
        **Response**: Establishes WebSocket connection for real-time updates

    .. tab-item:: GET /api/conversations/analytics
        
        **Purpose**: Conversation analytics and insights
        
        **Response**:
        
        .. code-block:: json
        
           {
             "total_conversations": 1250,
             "active_conversations": 15,
             "avg_response_time": 2.3,
             "peak_hours": ["09:00-11:00", "14:00-16:00"],
             "top_agents": [
               {"agent_id": "agent_456", "conversation_count": 89},
               {"agent_id": "agent_789", "conversation_count": 67}
             ],
             "error_rate": 0.03
           }

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Real-time Conversation Monitoring
        :class-card: sd-border-success
        
        **Condition**: Marcus instance connected, active conversations
        
        **Flow**:
        
        1. Frontend requests conversation stream via WebSocket
        2. API establishes connection to MCP client
        3. Real-time messages flow from Marcus to frontend
        4. Conversation analytics updated continuously
        
        **Data Flow**:
        
        * Marcus → MCP Client → WebSocket → Frontend
        * Message latency: < 100ms
        * Analytics refresh: Every 5 seconds
        
        **Features Available**:
        
        * ✅ Live message streaming
        * ✅ Real-time participant tracking
        * ✅ Interactive conversation threads
        * ✅ Instant search and filtering

    .. grid-item-card:: 🟡 Historical Analysis Mode
        :class-card: sd-border-warning
        
        **Condition**: No Marcus connection, historical data available
        
        **Flow**:
        
        1. Frontend requests conversation history
        2. API reads from cached/logged conversation data
        3. Static analytics generated from historical patterns
        4. Limited to read-only operations
        
        **Data Sources**:
        
        * Cached conversation database
        * Log file parsing
        * Previous session recordings
        
        **Features Available**:
        
        * ✅ Historical conversation browsing
        * ✅ Static analytics and trends
        * ⚠️  No real-time updates
        * ❌ Cannot initiate new conversations

    .. grid-item-card:: 🔴 High Load Management
        :class-card: sd-border-danger
        
        **Condition**: Many concurrent conversations, system under stress
        
        **Load Management**:
        
        1. Rate limiting activated (100 requests/minute/client)
        2. Response caching enabled for repeated queries
        3. WebSocket connection pooling
        4. Priority queuing for critical updates
        
        **Performance Optimizations**:
        
        * Message batching for high-frequency updates
        * Selective streaming based on user filters
        * Background processing for analytics
        * Circuit breaker for overloaded endpoints
        
        **Degradation Strategy**:
        
        * Reduce update frequency
        * Limit conversation history depth
        * Disable non-essential features
        * Inform users of reduced functionality

    .. grid-item-card:: 🔵 Multi-Project Filtering
        :class-card: sd-border-primary
        
        **Condition**: Multiple Marcus projects with cross-project analysis
        
        **Project Isolation**:
        
        1. API enforces project-based access control
        2. Conversations tagged with project identifiers
        3. Cross-project analytics available to admins
        4. Project-specific rate limits and quotas
        
        **Data Organization**:
        
        * Project-scoped conversation threads
        * Cross-project agent activity tracking
        * Aggregated analytics with project breakdown
        
        **Access Patterns**:
        
        * Users see only their project conversations
        * Admins access cross-project insights
        * API keys scoped to specific projects
        * Audit logging for access patterns

Agent Management API
===================

**Location**: :file:`src/api/agent_management_api.py`

Manages agent lifecycle, status monitoring, and performance metrics.

Endpoints
--------

.. tab-set::

    .. tab-item:: GET /api/agents
        
        **Purpose**: List all agents with current status
        
        **Response**:
        
        .. code-block:: json
        
           {
             "agents": [
               {
                 "id": "agent_456",
                 "name": "CodeAnalyzer",
                 "type": "specialist",
                 "status": "active",
                 "current_task": "task_789",
                 "performance": {
                   "tasks_completed": 127,
                   "avg_response_time": 1.8,
                   "success_rate": 0.94,
                   "last_active": "2025-07-14T11:15:30Z"
                 },
                 "capabilities": ["code_analysis", "bug_detection", "refactoring"],
                 "load": 0.7
               }
             ]
           }

    .. tab-item:: GET /api/agents/{id}/status
        
        **Purpose**: Detailed status for specific agent
        
        **Response**:
        
        .. code-block:: json
        
           {
             "agent_id": "agent_456",
             "status": "active",
             "current_task": {
               "id": "task_789",
               "description": "Analyze repository structure",
               "started_at": "2025-07-14T11:10:00Z",
               "progress": 0.65,
               "estimated_completion": "2025-07-14T11:20:00Z"
             },
             "queue": {
               "pending_tasks": 3,
               "estimated_wait_time": 180
             },
             "resources": {
               "cpu_usage": 0.45,
               "memory_usage": 0.62,
               "active_connections": 2
             },
             "health": {
               "status": "healthy",
               "last_heartbeat": "2025-07-14T11:15:25Z",
               "error_count": 0,
               "warnings": []
             }
           }

    .. tab-item:: POST /api/agents/{id}/commands
        
        **Purpose**: Send commands to specific agent
        
        **Request Body**:
        
        .. code-block:: json
        
           {
             "command": "pause_processing",
             "parameters": {
               "reason": "maintenance",
               "duration": 300
             }
           }
        
        **Available Commands**:
        
        * ``pause_processing`` - Temporarily halt task processing
        * ``resume_processing`` - Resume normal operations
        * ``clear_queue`` - Remove pending tasks
        * ``update_capabilities`` - Modify agent capabilities
        * ``request_status_report`` - Force immediate status update

    .. tab-item:: GET /api/agents/analytics
        
        **Purpose**: Agent performance analytics
        
        **Response**:
        
        .. code-block:: json
        
           {
             "overview": {
               "total_agents": 8,
               "active_agents": 6,
               "idle_agents": 2,
               "overloaded_agents": 0
             },
             "performance": {
               "avg_response_time": 2.1,
               "total_tasks_completed": 1847,
               "current_throughput": 12.5,
               "peak_throughput": 28.3
             },
             "efficiency": {
               "resource_utilization": 0.73,
               "load_distribution": "balanced",
               "bottlenecks": []
             }
           }

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Normal Agent Operations
        :class-card: sd-border-success
        
        **Condition**: All agents healthy and processing normally
        
        **Monitoring**:
        
        * Real-time status updates every 5 seconds
        * Performance metrics collected continuously
        * Health checks passed consistently
        * Load balancing effective
        
        **Admin Capabilities**:
        
        * View agent performance dashboards
        * Monitor task queue depths
        * Track resource utilization
        * Receive proactive alerts for issues
        
        **System Behavior**:
        
        * Automatic load balancing across agents
        * Predictive scaling recommendations
        * Performance trend analysis
        * Optimization suggestions

    .. grid-item-card:: 🟡 Agent Performance Issues
        :class-card: sd-border-warning
        
        **Condition**: Some agents experiencing degraded performance
        
        **Detection**:
        
        * Response times exceeding thresholds
        * Error rates above acceptable limits
        * Resource usage at critical levels
        * Queue backup indicators
        
        **Management Actions**:
        
        1. Automatic performance alerts generated
        2. Load redistribution to healthy agents
        3. Diagnostic data collection initiated
        4. Performance tuning recommendations provided
        
        **Recovery Strategies**:
        
        * Task queue rebalancing
        * Agent restart coordination
        * Resource limit adjustments
        * Capability-based task routing

    .. grid-item-card:: 🔴 Agent Failure Scenarios
        :class-card: sd-border-danger
        
        **Condition**: Agent crashes or becomes unresponsive
        
        **Failure Detection**:
        
        * Heartbeat timeouts (30 seconds)
        * Connection drops detected
        * Error thresholds exceeded
        * Resource exhaustion indicators
        
        **Automatic Recovery**:
        
        1. Failed agent marked as unavailable
        2. Active tasks redistributed to healthy agents
        3. Queue tasks rerouted automatically
        4. Client connections gracefully transferred
        5. Recovery attempt initiated after cooldown
        
        **Fallback Mechanisms**:
        
        * Task persistence during agent failures
        * Graceful degradation of dependent services
        * Client notification of service impacts
        * Manual intervention capabilities

    .. grid-item-card:: 🔵 Multi-Agent Coordination
        :class-card: sd-border-primary
        
        **Condition**: Complex tasks requiring multiple agent collaboration
        
        **Coordination Features**:
        
        * Cross-agent communication monitoring
        * Dependency tracking between agents
        * Collaborative task decomposition
        * Result aggregation and synthesis
        
        **Visualization**:
        
        * Agent interaction diagrams
        * Task dependency graphs
        * Communication flow analysis
        * Collaboration efficiency metrics
        
        **Management**:
        
        * Orchestrated task distribution
        * Conflict resolution mechanisms
        * Performance optimization for teams
        * Resource allocation coordination

Project Management API
======================

**Location**: :file:`src/api/project_management_api.py`

Handles project lifecycle, feature management, and workflow orchestration.

Endpoints
--------

.. tab-set::

    .. tab-item:: GET /api/projects
        
        **Purpose**: List all projects with status and metadata
        
        **Response**:
        
        .. code-block:: json
        
           {
             "projects": [
               {
                 "id": "proj_123",
                 "name": "E-commerce Platform",
                 "status": "active",
                 "created_at": "2025-07-01T00:00:00Z",
                 "updated_at": "2025-07-14T11:15:30Z",
                 "progress": {
                   "total_tasks": 45,
                   "completed_tasks": 28,
                   "in_progress_tasks": 8,
                   "blocked_tasks": 2,
                   "completion_percentage": 0.62
                 },
                 "team": {
                   "total_agents": 5,
                   "active_agents": 4,
                   "agent_types": ["frontend", "backend", "database", "testing"]
                 },
                 "health": {
                   "status": "healthy",
                   "risk_level": "low",
                   "issues": []
                 }
               }
             ]
           }

    .. tab-item:: POST /api/projects
        
        **Purpose**: Create new project
        
        **Request Body**:
        
        .. code-block:: json
        
           {
             "name": "Mobile App Development",
             "description": "Cross-platform mobile application",
             "template": "mobile_app",
             "configuration": {
               "target_platforms": ["ios", "android"],
               "framework": "react_native",
               "backend_integration": true
             },
             "team_requirements": {
               "frontend_agents": 2,
               "backend_agents": 1,
               "testing_agents": 1
             }
           }

    .. tab-item:: GET /api/projects/{id}/workflow
        
        **Purpose**: Project workflow visualization data
        
        **Response**:
        
        .. code-block:: json
        
           {
             "workflow_id": "workflow_456",
             "stages": [
               {
                 "id": "planning",
                 "name": "Planning & Design",
                 "status": "completed",
                 "tasks": 8,
                 "duration": 5
               },
               {
                 "id": "development",
                 "name": "Development",
                 "status": "in_progress",
                 "tasks": 25,
                 "progress": 0.68
               }
             ],
             "dependencies": [
               {"from": "planning", "to": "development", "type": "finish_to_start"}
             ],
             "critical_path": ["planning", "development", "testing", "deployment"],
             "estimated_completion": "2025-08-15T00:00:00Z"
           }

    .. tab-item:: PUT /api/projects/{id}/features
        
        **Purpose**: Manage project features and capabilities
        
        **Request Body**:
        
        .. code-block:: json
        
           {
             "features": {
               "enable_ai_analysis": true,
               "enable_auto_testing": true,
               "enable_performance_monitoring": true,
               "code_quality_gates": {
                 "coverage_threshold": 0.8,
                 "complexity_limit": 10,
                 "security_scan": true
               }
             }
           }

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 Active Project Development
        :class-card: sd-border-success
        
        **Condition**: Project in active development with team collaboration
        
        **Workflow Management**:
        
        * Automated task distribution to appropriate agents
        * Real-time progress tracking and reporting
        * Dynamic resource allocation based on priorities
        * Continuous integration and deployment pipeline
        
        **Team Coordination**:
        
        * Agent specialization and task routing
        * Cross-agent communication facilitation
        * Conflict resolution and dependency management
        * Performance monitoring and optimization
        
        **Project Health**:
        
        * ✅ All agents productive and engaged
        * ✅ Tasks progressing according to schedule
        * ✅ Quality gates being met consistently
        * ✅ No critical blockers or risks

    .. grid-item-card:: 🟡 Project Risk Management
        :class-card: sd-border-warning
        
        **Condition**: Project experiencing delays or quality issues
        
        **Risk Detection**:
        
        * Schedule slippage beyond acceptable thresholds
        * Quality metrics below standards
        * Resource constraints affecting progress
        * Dependencies causing bottlenecks
        
        **Mitigation Strategies**:
        
        1. Automatic escalation to project managers
        2. Resource reallocation recommendations
        3. Scope adjustment proposals
        4. Alternative approach suggestions
        
        **Monitoring Enhancements**:
        
        * Increased reporting frequency
        * Detailed performance analytics
        * Stakeholder notification systems
        * Recovery plan activation

    .. grid-item-card:: 🔴 Project Crisis Response
        :class-card: sd-border-danger
        
        **Condition**: Critical project issues requiring immediate intervention
        
        **Crisis Scenarios**:
        
        * Multiple agent failures affecting deliverables
        * Critical security vulnerabilities discovered
        * Major scope changes from stakeholders
        * Technical blockers preventing progress
        
        **Emergency Protocols**:
        
        1. Immediate stakeholder notification
        2. Crisis response team activation
        3. Emergency resource provisioning
        4. Alternative delivery strategies
        5. Recovery timeline establishment
        
        **Communication**:
        
        * Real-time status dashboards
        * Automated alert systems
        * Executive reporting
        * Client communication protocols

    .. grid-item-card:: 🔵 Project Completion & Handover
        :class-card: sd-border-primary
        
        **Condition**: Project nearing completion with handover preparation
        
        **Completion Activities**:
        
        * Final quality assurance and testing
        * Documentation generation and review
        * Knowledge transfer preparation
        * Deployment and go-live planning
        
        **Handover Process**:
        
        1. Comprehensive project documentation
        2. Agent knowledge extraction and preservation
        3. Maintenance team onboarding
        4. Performance baseline establishment
        5. Support transition planning
        
        **Success Metrics**:
        
        * Delivery against original requirements
        * Quality standards achievement
        * Timeline adherence
        * Stakeholder satisfaction

WebSocket Services
=================

**Location**: :file:`src/api/conversation_websocket.py`

Real-time bidirectional communication for live updates and interactive features.

WebSocket Events
---------------

.. tab-set::

    .. tab-item:: Connection Events
        
        **Client Connection**:
        
        .. code-block:: javascript
        
           // Client initiates connection
           const socket = io('/api/ws', {
             auth: {
               token: 'user_auth_token',
               project_id: 'proj_123'
             }
           });
           
           // Server responds with connection confirmation
           {
             "event": "connection_established",
             "data": {
               "session_id": "sess_456",
               "server_time": "2025-07-14T11:15:30Z",
               "available_channels": ["conversations", "agents", "projects"]
             }
           }

    .. tab-item:: Subscription Management
        
        **Channel Subscription**:
        
        .. code-block:: javascript
        
           // Subscribe to specific data streams
           socket.emit('subscribe', {
             channels: ['conversations', 'agent_status'],
             filters: {
               project_id: 'proj_123',
               agent_types: ['frontend', 'backend']
             }
           });
           
           // Subscription confirmation
           {
             "event": "subscription_confirmed",
             "data": {
               "channels": ["conversations", "agent_status"],
               "active_subscriptions": 2,
               "estimated_message_rate": 5.2
             }
           }

    .. tab-item:: Real-time Data Streams
        
        **Conversation Updates**:
        
        .. code-block:: javascript
        
           // New message in conversation
           {
             "event": "conversation_message",
             "channel": "conversations",
             "data": {
               "conversation_id": "conv_123",
               "message": {
                 "id": "msg_789",
                 "sender": "agent_456",
                 "content": "Task completed successfully",
                 "timestamp": "2025-07-14T11:15:30Z"
               }
             }
           }
           
           // Agent status change
           {
             "event": "agent_status_update",
             "channel": "agent_status",
             "data": {
               "agent_id": "agent_456",
               "status": "idle",
               "previous_status": "busy",
               "task_completed": "task_789"
             }
           }

    .. tab-item:: Interactive Commands
        
        **Client Commands**:
        
        .. code-block:: javascript
        
           // Request specific data
           socket.emit('request_data', {
             type: 'conversation_history',
             parameters: {
               conversation_id: 'conv_123',
               limit: 50
             }
           });
           
           // Send agent command
           socket.emit('agent_command', {
             agent_id: 'agent_456',
             command: 'pause_processing',
             reason: 'user_requested'
           });

Scenario Cards
--------------

.. grid:: 1 1 2 2

    .. grid-item-card:: 🟢 High-Frequency Real-time Updates
        :class-card: sd-border-success
        
        **Condition**: Multiple active conversations with frequent message exchanges
        
        **Performance Optimization**:
        
        * Message batching for high-frequency updates (100ms windows)
        * Selective subscription based on user interests
        * Connection pooling and load balancing
        * Compression for large message payloads
        
        **Client Experience**:
        
        * Smooth, responsive UI updates
        * No message loss or duplication
        * Minimal latency (< 100ms end-to-end)
        * Graceful handling of connection interruptions
        
        **Server Management**:
        
        * Automatic connection health monitoring
        * Circuit breakers for overloaded connections
        * Priority queuing for critical updates
        * Memory-efficient message routing

    .. grid-item-card:: 🟡 Connection Resilience
        :class-card: sd-border-warning
        
        **Condition**: Network interruptions or server maintenance
        
        **Resilience Features**:
        
        * Automatic reconnection with exponential backoff
        * Message queue persistence during disconnections
        * State synchronization on reconnection
        * Graceful degradation to polling mode
        
        **Recovery Process**:
        
        1. Detect connection loss within 5 seconds
        2. Attempt immediate reconnection
        3. Queue outbound messages locally
        4. Request state synchronization on reconnect
        5. Replay missed messages in order
        
        **User Experience**:
        
        * Visual connection status indicators
        * Offline mode with limited functionality
        * Automatic background reconnection
        * Seamless transition back to real-time mode

    .. grid-item-card:: 🔴 High Load Management
        :class-card: sd-border-danger
        
        **Condition**: Server under extreme load with many concurrent connections
        
        **Load Management Strategies**:
        
        * Connection rate limiting (max 1000 concurrent per server)
        * Message rate limiting (max 100 messages/second per client)
        * Priority-based message delivery
        * Connection dropping for inactive clients
        
        **Performance Optimization**:
        
        1. Horizontal scaling with load balancers
        2. Message aggregation and compression
        3. Selective feature disabling under load
        4. Client notification of reduced service levels
        
        **Recovery Actions**:
        
        * Automatic server capacity scaling
        * Client reconnection throttling
        * Emergency mode with essential features only
        * Performance monitoring and alerting

    .. grid-item-card:: 🔵 Multi-Client Synchronization
        :class-card: sd-border-primary
        
        **Condition**: Multiple clients viewing same project/conversation
        
        **Synchronization Features**:
        
        * Real-time cursor and selection sharing
        * Collaborative editing capabilities
        * Conflict resolution for simultaneous actions
        * Presence indicators for active users
        
        **State Management**:
        
        * Centralized state broadcasting
        * Optimistic updates with rollback capability
        * Version control for collaborative changes
        * User action attribution and history
        
        **Coordination**:
        
        * User awareness and presence system
        * Permission-based action filtering
        * Cross-client notification system
        * Session management and handover

Pipeline Enhancement API
=======================

**Location**: :file:`src/api/pipeline_enhancement_api.py`

Provides pipeline flow visualization, execution tracking, and performance optimization.

Endpoints
--------

.. tab-set::

    .. tab-item:: GET /api/pipelines
        
        **Purpose**: List all pipelines with execution status
        
        **Response**:
        
        .. code-block:: json
        
           {
             "pipelines": [
               {
                 "id": "pipe_123",
                 "name": "Code Review Pipeline",
                 "project_id": "proj_456",
                 "status": "running",
                 "stages": [
                   {
                     "id": "lint",
                     "name": "Code Linting",
                     "status": "completed",
                     "duration": 45,
                     "agent": "agent_linter"
                   },
                   {
                     "id": "test",
                     "name": "Unit Testing",
                     "status": "running",
                     "progress": 0.7,
                     "agent": "agent_tester"
                   }
                 ],
                 "metrics": {
                   "total_duration": 180,
                   "success_rate": 0.94,
                   "avg_stage_time": 22.5
                 }
               }
             ]
           }

    .. tab-item:: POST /api/pipelines/{id}/execute
        
        **Purpose**: Trigger pipeline execution
        
        **Request Body**:
        
        .. code-block:: json
        
           {
             "trigger": "manual",
             "parameters": {
               "branch": "feature/new-component",
               "environment": "staging",
               "run_full_suite": true
             },
             "notifications": {
               "on_completion": ["email", "webhook"],
               "on_failure": ["email", "slack"]
             }
           }

    .. tab-item:: GET /api/pipelines/{id}/visualization
        
        **Purpose**: Pipeline flow diagram data
        
        **Response**:
        
        .. code-block:: json
        
           {
             "nodes": [
               {
                 "id": "stage_lint",
                 "type": "process",
                 "label": "Code Linting",
                 "position": {"x": 100, "y": 50},
                 "status": "completed",
                 "agent": "agent_linter"
               }
             ],
             "edges": [
               {
                 "id": "edge_1",
                 "source": "stage_lint",
                 "target": "stage_test",
                 "type": "dependency"
               }
             ],
             "layout": "dagre",
             "execution_path": ["stage_lint", "stage_test", "stage_deploy"]
           }

Additional API Systems
=====================

Cost Tracking API
-----------------

**Location**: :file:`src/api/cost_tracking_api.py`

Tracks resource usage, cost estimation, and budget monitoring.

**Key Features**:
* Resource consumption tracking per agent/task
* Cost estimation based on usage patterns
* Budget alerts and recommendations
* Cross-project cost analysis

Memory Insights API
------------------

**Location**: :file:`src/api/memory_insights_api.py`

Provides memory usage analysis and knowledge graph insights.

**Key Features**:
* Memory usage visualization per agent
* Knowledge graph relationship mapping
* Context retention analysis
* Memory optimization recommendations

Pattern Learning API
-------------------

**Location**: :file:`src/api/pattern_learning_api.py`

Detects patterns in agent behavior and provides learning insights.

**Key Features**:
* Behavioral pattern detection
* Learning algorithm management
* Insight generation and recommendations
* Performance prediction based on patterns

Context Visualization API
-------------------------

**Location**: :file:`src/api/context_visualization_api.py`

Maps context relationships and dependencies across the system.

**Key Features**:
* Context relationship visualization
* Dependency impact analysis
* Cross-system context tracking
* Context optimization suggestions

API Integration Patterns
========================

Authentication and Authorization
-------------------------------

.. tab-set::

    .. tab-item:: Token-Based Authentication
        
        **Implementation**:
        
        .. code-block:: python
        
           # JWT token validation
           @api.before_request
           def validate_token():
               token = request.headers.get('Authorization', '').replace('Bearer ', '')
               try:
                   payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                   g.user_id = payload['user_id']
                   g.project_access = payload['projects']
               except jwt.InvalidTokenError:
                   return jsonify({'error': 'Invalid token'}), 401

    .. tab-item:: Project-Scoped Access
        
        **Authorization Checks**:
        
        .. code-block:: python
        
           def require_project_access(project_id):
               if project_id not in g.project_access:
                   abort(403, 'Insufficient project permissions')
           
           @api.route('/api/projects/<project_id>/conversations')
           def get_project_conversations(project_id):
               require_project_access(project_id)
               # ... rest of endpoint logic

    .. tab-item:: Rate Limiting
        
        **Implementation**:
        
        .. code-block:: python
        
           from flask_limiter import Limiter
           
           limiter = Limiter(
               app,
               key_func=lambda: g.user_id,
               default_limits=["1000 per hour", "100 per minute"]
           )
           
           @api.route('/api/conversations')
           @limiter.limit("10 per minute")
           def get_conversations():
               # Endpoint with stricter rate limiting

Error Handling and Resilience
-----------------------------

.. tab-set::

    .. tab-item:: Standardized Error Responses
        
        **Error Format**:
        
        .. code-block:: json
        
           {
             "error": {
               "code": "CONVERSATION_NOT_FOUND",
               "message": "Conversation with ID 'conv_123' does not exist",
               "details": {
                 "conversation_id": "conv_123",
                 "available_conversations": 45
               },
               "timestamp": "2025-07-14T11:15:30Z",
               "request_id": "req_789"
             }
           }

    .. tab-item:: Circuit Breaker Pattern
        
        **Implementation**:
        
        .. code-block:: python
        
           class CircuitBreaker:
               def __init__(self, failure_threshold=5, timeout=60):
                   self.failure_count = 0
                   self.failure_threshold = failure_threshold
                   self.timeout = timeout
                   self.last_failure_time = None
                   self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
               
               def call(self, func, *args, **kwargs):
                   if self.state == 'OPEN':
                       if time.time() - self.last_failure_time > self.timeout:
                           self.state = 'HALF_OPEN'
                       else:
                           raise CircuitBreakerError("Service unavailable")
                   
                   try:
                       result = func(*args, **kwargs)
                       if self.state == 'HALF_OPEN':
                           self.state = 'CLOSED'
                           self.failure_count = 0
                       return result
                   except Exception as e:
                       self.failure_count += 1
                       self.last_failure_time = time.time()
                       if self.failure_count >= self.failure_threshold:
                           self.state = 'OPEN'
                       raise e

    .. tab-item:: Graceful Degradation
        
        **Fallback Strategies**:
        
        .. code-block:: python
        
           def get_conversation_with_fallback(conversation_id):
               try:
                   # Try real-time data from MCP client
                   return mcp_client.get_conversation(conversation_id)
               except ConnectionError:
                   # Fall back to cached data
                   return cache.get_conversation(conversation_id)
               except Exception:
                   # Last resort: basic conversation structure
                   return {
                       'id': conversation_id,
                       'status': 'unknown',
                       'messages': [],
                       'note': 'Limited data available due to service issues'
                   }

Performance Optimization
-----------------------

.. tab-set::

    .. tab-item:: Response Caching
        
        **Implementation**:
        
        .. code-block:: python
        
           from functools import wraps
           import redis
           
           redis_client = redis.Redis(host='localhost', port=6379, db=0)
           
           def cache_response(expiry=300):
               def decorator(func):
                   @wraps(func)
                   def wrapper(*args, **kwargs):
                       cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                       cached_result = redis_client.get(cache_key)
                       
                       if cached_result:
                           return json.loads(cached_result)
                       
                       result = func(*args, **kwargs)
                       redis_client.setex(cache_key, expiry, json.dumps(result))
                       return result
                   return wrapper
               return decorator
           
           @api.route('/api/agents/analytics')
           @cache_response(expiry=60)  # Cache for 1 minute
           def get_agent_analytics():
               # Expensive analytics computation
               return compute_agent_analytics()

    .. tab-item:: Request Batching
        
        **Batch Processing**:
        
        .. code-block:: python
        
           @api.route('/api/conversations/batch', methods=['POST'])
           def get_conversations_batch():
               conversation_ids = request.json.get('conversation_ids', [])
               
               if len(conversation_ids) > 50:
                   return jsonify({'error': 'Too many conversations requested'}), 400
               
               # Process in parallel
               with ThreadPoolExecutor(max_workers=10) as executor:
                   futures = {
                       executor.submit(get_conversation, conv_id): conv_id 
                       for conv_id in conversation_ids
                   }
                   
                   results = {}
                   for future in as_completed(futures):
                       conv_id = futures[future]
                       try:
                           results[conv_id] = future.result()
                       except Exception as e:
                           results[conv_id] = {'error': str(e)}
               
               return jsonify({'conversations': results})

    .. tab-item:: Database Optimization
        
        **Query Optimization**:
        
        .. code-block:: python
        
           # Efficient pagination with cursor-based approach
           @api.route('/api/conversations')
           def get_conversations():
               limit = min(int(request.args.get('limit', 50)), 100)
               cursor = request.args.get('cursor')
               
               query = db.session.query(Conversation)
               
               if cursor:
                   # Decode cursor to get timestamp and ID
                   timestamp, last_id = decode_cursor(cursor)
                   query = query.filter(
                       or_(
                           Conversation.updated_at < timestamp,
                           and_(
                               Conversation.updated_at == timestamp,
                               Conversation.id < last_id
                           )
                       )
                   )
               
               conversations = query.order_by(
                   Conversation.updated_at.desc(),
                   Conversation.id.desc()
               ).limit(limit + 1).all()
               
               has_more = len(conversations) > limit
               if has_more:
                   conversations = conversations[:-1]
               
               next_cursor = None
               if has_more and conversations:
                   last_conv = conversations[-1]
                   next_cursor = encode_cursor(last_conv.updated_at, last_conv.id)
               
               return jsonify({
                   'conversations': [conv.to_dict() for conv in conversations],
                   'has_more': has_more,
                   'next_cursor': next_cursor
               })

Monitoring and Observability
===========================

API Metrics and Logging
-----------------------

.. tab-set::

    .. tab-item:: Request Metrics
        
        **Metric Collection**:
        
        .. code-block:: python
        
           import time
           from prometheus_client import Counter, Histogram, generate_latest
           
           REQUEST_COUNT = Counter(
               'api_requests_total',
               'Total API requests',
               ['method', 'endpoint', 'status']
           )
           
           REQUEST_DURATION = Histogram(
               'api_request_duration_seconds',
               'API request duration',
               ['method', 'endpoint']
           )
           
           @api.before_request
           def before_request():
               g.start_time = time.time()
           
           @api.after_request
           def after_request(response):
               duration = time.time() - g.start_time
               
               REQUEST_COUNT.labels(
                   method=request.method,
                   endpoint=request.endpoint or 'unknown',
                   status=response.status_code
               ).inc()
               
               REQUEST_DURATION.labels(
                   method=request.method,
                   endpoint=request.endpoint or 'unknown'
               ).observe(duration)
               
               return response
           
           @api.route('/metrics')
           def metrics():
               return generate_latest(), 200, {'Content-Type': 'text/plain'}

    .. tab-item:: Structured Logging
        
        **Log Format**:
        
        .. code-block:: python
        
           import structlog
           
           logger = structlog.get_logger()
           
           @api.route('/api/conversations/<conversation_id>')
           def get_conversation(conversation_id):
               logger.info(
                   "conversation_request",
                   conversation_id=conversation_id,
                   user_id=g.user_id,
                   request_id=g.request_id
               )
               
               try:
                   conversation = conversation_service.get(conversation_id)
                   logger.info(
                       "conversation_retrieved",
                       conversation_id=conversation_id,
                       message_count=len(conversation.messages),
                       response_time=time.time() - g.start_time
                   )
                   return jsonify(conversation.to_dict())
                   
               except ConversationNotFound:
                   logger.warning(
                       "conversation_not_found",
                       conversation_id=conversation_id,
                       user_id=g.user_id
                   )
                   return jsonify({'error': 'Conversation not found'}), 404

    .. tab-item:: Health Checks
        
        **Health Endpoint**:
        
        .. code-block:: python
        
           @api.route('/health')
           def health_check():
               health_status = {
                   'status': 'healthy',
                   'timestamp': datetime.utcnow().isoformat(),
                   'version': app.config['VERSION'],
                   'services': {}
               }
               
               # Check database connectivity
               try:
                   db.session.execute('SELECT 1')
                   health_status['services']['database'] = 'healthy'
               except Exception as e:
                   health_status['services']['database'] = f'unhealthy: {str(e)}'
                   health_status['status'] = 'degraded'
               
               # Check MCP client connection
               try:
                   if mcp_client.is_connected():
                       health_status['services']['marcus'] = 'connected'
                   else:
                       health_status['services']['marcus'] = 'disconnected'
                       health_status['status'] = 'degraded'
               except Exception as e:
                   health_status['services']['marcus'] = f'error: {str(e)}'
                   health_status['status'] = 'unhealthy'
               
               # Check Redis cache
               try:
                   redis_client.ping()
                   health_status['services']['cache'] = 'healthy'
               except Exception as e:
                   health_status['services']['cache'] = f'unhealthy: {str(e)}'
                   # Cache is optional, don't change overall status
               
               status_code = 200 if health_status['status'] == 'healthy' else 503
               return jsonify(health_status), status_code

Next Steps
==========

* :doc:`processing-systems` - Learn about data processing and analysis engines
* :doc:`frontend-systems` - Understand the Vue.js frontend and visualization
* :doc:`integration-flow` - See complete end-to-end system interactions