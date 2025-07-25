WebSocket System
================

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

The WebSocket System is Seneca's real-time communication layer that enables bidirectional, low-latency data exchange between the backend and frontend. It provides instant updates to the visualization system, allowing users to see Marcus orchestration changes as they happen, creating a responsive and engaging observability experience.

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

1. **Flask-SocketIO Server**
   
   - WebSocket connection management
   - Event broadcasting and routing
   - Room-based message distribution
   - Connection state tracking

2. **Client Connection Manager**
   
   - Connection lifecycle management
   - Authentication and authorization
   - Reconnection handling
   - Load balancing support

3. **Event Bridge**
   
   - Event System → WebSocket transformation
   - Message filtering and routing
   - Rate limiting and throttling
   - Data serialization

4. **Frontend WebSocket Client**
   
   - Socket.IO client integration
   - Automatic reconnection
   - Event handler registration
   - State synchronization

Communication Flow
~~~~~~~~~~~~~~~~~

.. code-block:: text

   Marcus Events → Event System → WebSocket Bridge → Frontend
        ↓              ↓              ↓               ↓
   [Agent Status]  [Transform]    [Broadcast]     [Update UI]
   [Task Updates]  [Filter]       [Room-based]    [Animate]
   [Health Data]   [Serialize]    [Throttle]      [Notify]

How It Works
------------

Server-Side Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask_socketio import SocketIO, emit, join_room, leave_room
   
   class WebSocketManager:
       def __init__(self, app):
           self.socketio = SocketIO(app, cors_allowed_origins="*")
           self.connected_clients = {}
           self.setup_handlers()
           
       def setup_handlers(self):
           @self.socketio.on('connect')
           def handle_connect():
               client_id = request.sid
               self.connected_clients[client_id] = {
                   'connected_at': datetime.utcnow(),
                   'rooms': ['general'],
                   'user_type': 'observer'  # Default role
               }
               
               # Join default room
               join_room('general')
               
               # Send initial state
               emit('connection_established', {
                   'client_id': client_id,
                   'server_time': datetime.utcnow().isoformat()
               })
           
           @self.socketio.on('disconnect')
           def handle_disconnect():
               client_id = request.sid
               if client_id in self.connected_clients:
                   del self.connected_clients[client_id]

Event Broadcasting
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class EventBroadcaster:
       def __init__(self, socketio, event_system):
           self.socketio = socketio
           self.event_system = event_system
           self.setup_subscriptions()
           
       def setup_subscriptions(self):
           # Subscribe to Marcus events
           self.event_system.subscribe('agent.*', self.broadcast_agent_event)
           self.event_system.subscribe('project.*', self.broadcast_project_event)
           self.event_system.subscribe('system.*', self.broadcast_system_event)
           
       async def broadcast_agent_event(self, event):
           # Transform event for frontend consumption
           ui_event = {
               'type': 'agent_update',
               'timestamp': event['timestamp'],
               'data': {
                   'agent_id': event['data']['agent_id'],
                   'status': event['data']['status'],
                   'change_type': event['type'].split('.')[-1]
               }
           }
           
           # Broadcast to all observers
           self.socketio.emit('agent_update', ui_event, room='observers')

Client-Side Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   // Vue.js WebSocket integration
   import { io } from 'socket.io-client'
   import { useWorkflowStore } from '@/stores/workflow'
   
   class WebSocketClient {
     constructor() {
       this.socket = null
       this.reconnectAttempts = 0
       this.maxReconnectAttempts = 5
       this.workflowStore = useWorkflowStore()
     }
     
     connect() {
       this.socket = io('http://localhost:8000', {
         transports: ['websocket'],
         timeout: 20000
       })
       
       this.setupEventHandlers()
     }
     
     setupEventHandlers() {
       // Connection events
       this.socket.on('connect', () => {
         console.log('Connected to Seneca server')
         this.reconnectAttempts = 0
       })
       
       // Agent updates
       this.socket.on('agent_update', (event) => {
         this.workflowStore.updateAgent(event.data)
         this.animateChange('agent', event.data.agent_id)
       })
       
       // Project updates  
       this.socket.on('project_update', (event) => {
         this.workflowStore.updateProject(event.data)
         this.showNotification('Project status changed')
       })
       
       // System health updates
       this.socket.on('health_update', (event) => {
         this.workflowStore.updateSystemHealth(event.data)
         if (event.data.severity === 'critical') {
           this.showAlert(event.data.message)
         }
       })
     }
   }

Marcus Integration
------------------

Real-Time Data Pipeline
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Marcus MCP → Event Transform → WebSocket Emit → Frontend Update
        ↓            ↓               ↓               ↓
   [Tool Response] [Event Create] [Broadcast]    [React Update]
   [State Change]  [Filter/Map]   [Room-based]   [Animate]
   [Health Check]  [Serialize]    [Throttle]     [Display]

Event Transformation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class MarcusEventTransformer:
       def transform_for_websocket(self, marcus_event):
           """Transform Marcus events for WebSocket consumption"""
           
           transformations = {
               'agent.status.changed': self.transform_agent_status,
               'project.progress.updated': self.transform_project_progress,
               'task.assigned': self.transform_task_assignment,
               'system.health.changed': self.transform_health_update
           }
           
           event_type = marcus_event['type']
           if event_type in transformations:
               return transformations[event_type](marcus_event)
           
           # Default transformation
           return {
               'type': 'generic_update',
               'timestamp': marcus_event['timestamp'],
               'data': marcus_event['data']
           }
       
       def transform_agent_status(self, event):
           return {
               'type': 'agent_status_change',
               'agent_id': event['data']['agent_id'],
               'old_status': event['data']['old_status'],
               'new_status': event['data']['new_status'],
               'timestamp': event['timestamp'],
               'animation': 'pulse' if event['data']['new_status'] == 'active' else 'fade'
           }

Value Proposition
-----------------

Real-Time Responsiveness
~~~~~~~~~~~~~~~~~~~~~~~~

The WebSocket System provides:

- **Instant Updates**: Sub-second latency for state changes
- **Live Dashboards**: No page refresh needed for current data
- **Interactive Experience**: Responsive user interface
- **Situational Awareness**: Immediate awareness of system changes

Questions It Answers
~~~~~~~~~~~~~~~~~~~~

**Real-Time Monitoring**:

1. What just changed in the system?
2. Which agents are currently active?
3. Are there any urgent alerts or issues?
4. How is the current project progressing?

**System Responsiveness**:

1. How quickly does the UI reflect backend changes?
2. Are there any connection or performance issues?
3. Which clients are currently connected?
4. What's the current message throughput?

**User Experience**:

1. Are users seeing the most current data?
2. How engaging is the real-time experience?
3. Are notifications delivered promptly?
4. Is the system maintaining connection stability?

Analysis Capabilities
---------------------

Connection Analytics
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class ConnectionAnalytics:
       def analyze_connection_patterns(self):
           return {
               'total_connections': len(self.connected_clients),
               'connection_duration_avg': self.calculate_avg_duration(),
               'reconnection_rate': self.calculate_reconnection_rate(),
               'message_throughput': self.calculate_message_rate(),
               'peak_concurrent_users': self.get_peak_connections()
           }
       
       def analyze_user_engagement(self):
           return {
               'active_sessions': self.count_active_sessions(),
               'session_duration_distribution': self.get_session_durations(),
               'interaction_frequency': self.measure_interactions(),
               'feature_usage': self.track_feature_usage()
           }

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class WebSocketPerformance:
       def monitor_performance(self):
           metrics = {
               'message_latency': self.measure_message_latency(),
               'connection_time': self.measure_connection_time(),
               'memory_usage': self.get_memory_usage(),
               'cpu_usage': self.get_cpu_usage(),
               'network_throughput': self.measure_throughput()
           }
           
           # Alert on performance issues
           if metrics['message_latency'] > 1000:  # 1 second
               self.alert_high_latency()
           
           return metrics

Pattern Identification
----------------------

Connection Patterns
~~~~~~~~~~~~~~~~~~~

1. **Usage Patterns**
   
   - **Peak Hours**: When most users are connected
   - **Session Duration**: How long users stay connected
   - **Reconnection Behavior**: How users handle disconnections
   - **Feature Interaction**: Which real-time features are used most

2. **Performance Patterns**
   
   - **Latency Variations**: Message delivery time patterns
   - **Throughput Patterns**: Message volume over time
   - **Error Patterns**: Connection failures and causes
   - **Resource Usage**: CPU and memory consumption patterns

3. **User Behavior Patterns**
   
   - **Attention Patterns**: Which updates capture user focus
   - **Response Patterns**: How users react to different event types
   - **Navigation Patterns**: How real-time updates affect user flow
   - **Engagement Patterns**: What keeps users actively watching

System Health Patterns
~~~~~~~~~~~~~~~~~~~~~~~

1. **Connection Health**
   
   - **Stable Connections**: Long-duration, low-latency connections
   - **Flapping Connections**: Frequent connect/disconnect cycles
   - **Failed Connections**: Connection attempts that fail
   - **Degraded Connections**: High latency or packet loss

2. **Message Flow Patterns**
   
   - **Normal Flow**: Steady, predictable message rates
   - **Burst Patterns**: Sudden spikes in message volume
   - **Silence Patterns**: Unexpectedly quiet periods
   - **Error Cascades**: Multiple failed message deliveries

Interpretation Guidelines
-------------------------

Performance Metrics
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Metric
     - Excellent
     - Good
     - Needs Attention
   * - Message Latency
     - <100ms
     - 100-500ms
     - >500ms
   * - Connection Success
     - >99%
     - 95-99%
     - <95%
   * - Reconnection Rate
     - <5%
     - 5-15%
     - >15%
   * - Concurrent Users
     - <server limit
     - 80% of limit
     - >90% of limit

Connection Status Codes
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   CONNECTION_STATUS = {
       'connected': 'Client successfully connected',
       'connecting': 'Connection attempt in progress',
       'disconnected': 'Clean disconnection',
       'connect_error': 'Failed to establish connection',
       'reconnect_failed': 'Exhausted reconnection attempts',
       'timeout': 'Connection timed out'
   }

Message Priority Levels
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   MESSAGE_PRIORITIES = {
       'critical': 'Immediate delivery required',
       'high': 'Deliver within 100ms',
       'normal': 'Standard delivery timing',
       'low': 'Can be batched or delayed'
   }

Advantages
----------

1. **Low Latency**: Near-instantaneous data delivery
2. **Bidirectional**: Both client and server can initiate communication
3. **Efficient**: Lower overhead than HTTP polling
4. **Scalable**: Support for many concurrent connections
5. **Persistent**: Maintains connection for continuous updates

Product Tiers
-------------

**Open Source (Public)**:

Basic WebSocket Features:
- Standard WebSocket connections
- Basic event broadcasting
- Simple room management
- Connection state tracking
- Client reconnection handling
- Support for 100 concurrent connections

**Enterprise Add-ons**:

Advanced WebSocket Features:
- WebSocket clustering and load balancing
- Priority message queues
- Advanced routing and filtering
- Message persistence and replay
- Detailed connection analytics
- Custom authentication providers
- Rate limiting and throttling
- Message compression
- SSL/TLS termination
- Support for 10,000+ concurrent connections
- Custom WebSocket protocols
- Integration with message brokers

Configuration
-------------

WebSocket Settings
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config.py
   WEBSOCKET_CONFIG = {
       'server': {
           'cors_allowed_origins': ['http://localhost:3000'],
           'ping_timeout': 60,
           'ping_interval': 25,
           'max_http_buffer_size': 1000000
       },
       
       'rooms': {
           'default_room': 'general',
           'max_room_size': 1000,
           'room_cleanup_interval': 300
       },
       
       'performance': {
           'message_queue_size': 1000,
           'batch_messages': True,
           'compression': True,
           'heartbeat_interval': 30
       }
   }

Security Settings
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Security configuration
   SECURITY_CONFIG = {
       'authentication': {
           'required': True,
           'token_validation': True,
           'session_timeout': 3600
       },
       
       'rate_limiting': {
           'messages_per_minute': 100,
           'burst_limit': 10,
           'ban_duration': 300
       },
       
       'content_filtering': {
           'validate_message_format': True,
           'max_message_size': 64000,
           'sanitize_content': True
       }
   }

Best Practices
--------------

1. **Connection Management**
   
   - Implement exponential backoff for reconnections
   - Handle connection state gracefully
   - Provide visual feedback for connection status

2. **Performance**
   
   - Batch messages when possible
   - Use message compression
   - Implement connection pooling

3. **Security**
   
   - Validate all incoming messages
   - Implement rate limiting
   - Use secure WebSocket (WSS) in production

Future Enhancements
-------------------

- WebRTC integration for peer-to-peer communication
- Binary message support for large data transfers
- Advanced routing with message brokers
- WebSocket API gateway integration
- Custom protocol extensions
- Mobile WebSocket optimization
- Edge computing support for global deployment