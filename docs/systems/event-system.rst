Event System
============

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

The Event System is Seneca's real-time communication backbone that enables loosely coupled, asynchronous communication between system components. It provides a publish-subscribe architecture that allows different parts of Seneca to react to Marcus orchestration events without tight coupling, enabling scalable and maintainable real-time observability.

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

1. **Event Bus**
   
   - Central message routing system
   - Topic-based message distribution
   - Async message handling
   - Event persistence and replay

2. **Event Publishers**
   
   - MCP Client events (connection status, tool responses)
   - Processor events (analysis completion, insights generated)
   - API events (request handling, error conditions)
   - System events (health changes, alerts)

3. **Event Subscribers**
   
   - WebSocket handlers (real-time UI updates)
   - Analytics processors (metric calculation)
   - Alert managers (notification triggers)
   - Log aggregators (audit trails)

4. **Event Store**
   
   - Event persistence for replay
   - Audit trail maintenance
   - Pattern analysis data
   - System recovery support

Event Flow Architecture
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Marcus → MCP Client → Event Bus → Subscribers → Actions
     ↓         ↓           ↓           ↓           ↓
   [Status]  [Events]   [Routing]   [Process]   [Update UI]
   [Tasks]   [Publish]  [Filter]    [Analyze]   [Send Alert]
   [Health]  [Format]   [Persist]   [Store]     [Log Audit]

How It Works
------------

Event Publishing
~~~~~~~~~~~~~~~~

.. code-block:: python

   class EventPublisher:
       def __init__(self, event_bus):
           self.event_bus = event_bus
           
       async def publish_agent_status_change(self, agent_id, old_status, new_status):
           event = {
               'type': 'agent.status.changed',
               'source': 'mcp_client',
               'timestamp': datetime.utcnow().isoformat(),
               'data': {
                   'agent_id': agent_id,
                   'old_status': old_status,
                   'new_status': new_status,
                   'transition_time': datetime.utcnow().isoformat()
               },
               'metadata': {
                   'severity': 'info',
                   'category': 'agent_management'
               }
           }
           
           await self.event_bus.publish('agent.status', event)

Event Subscription
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class WebSocketEventHandler:
       def __init__(self, event_bus, socketio):
           self.event_bus = event_bus
           self.socketio = socketio
           
       async def setup_subscriptions(self):
           # Subscribe to agent events
           await self.event_bus.subscribe(
               'agent.*', 
               self.handle_agent_event
           )
           
           # Subscribe to project events  
           await self.event_bus.subscribe(
               'project.*',
               self.handle_project_event
           )
           
       async def handle_agent_event(self, event):
           # Forward to connected WebSocket clients
           await self.socketio.emit('agent_update', {
               'type': event['type'],
               'data': event['data'],
               'timestamp': event['timestamp']
           })

Marcus Integration
------------------

Event Sources from Marcus
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Agent Lifecycle Events**
   
   - Agent registration/deregistration
   - Status changes (active, idle, offline)
   - Task assignments and completions
   - Skill updates and certifications

2. **Project Events**
   
   - Project creation and configuration
   - Status updates and milestone completion
   - Resource allocation changes
   - Health metric updates

3. **Task Execution Events**
   
   - Task creation and assignment
   - Progress updates and state changes
   - Blocker reports and resolutions
   - Completion and quality assessments

4. **System Events**
   
   - Health checks and diagnostics
   - Performance metrics updates
   - Error conditions and alerts
   - Configuration changes

Event Transformation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class MarcusEventTransformer:
       def transform_mcp_response(self, tool_name, response):
           """Transform MCP tool responses into Seneca events"""
           
           if tool_name == 'get_agent_status':
               return {
                   'type': 'agent.status.updated',
                   'source': 'marcus_mcp',
                   'data': {
                       'agent_id': response['agent_id'],
                       'status': response['status'],
                       'current_task': response.get('current_task'),
                       'utilization': response.get('utilization', 0)
                   }
               }
           
           elif tool_name == 'get_project_status':
               return {
                   'type': 'project.status.updated',
                   'source': 'marcus_mcp', 
                   'data': {
                       'project_id': response['project_id'],
                       'progress': response['progress'],
                       'health_score': response['health_score'],
                       'active_tasks': response['active_tasks']
                   }
               }

Value Proposition
-----------------

Real-Time Responsiveness
~~~~~~~~~~~~~~~~~~~~~~~~

The Event System enables:

- **Immediate Updates**: UI updates as soon as Marcus state changes
- **Proactive Alerts**: Instant notifications on critical conditions
- **Live Dashboards**: Real-time metrics without polling
- **Audit Trails**: Complete system activity logging

Questions It Answers
~~~~~~~~~~~~~~~~~~~~

**Real-Time Monitoring**:

1. What's happening in the system right now?
2. Which agents just changed status?
3. Are there any new blockers or alerts?
4. How is the current project progressing?

**System Behavior**:

1. What sequence of events led to this situation?
2. How frequently do certain events occur?
3. What patterns exist in event timing?
4. Which events tend to cluster together?

**Performance Analysis**:

1. How quickly does the system respond to changes?
2. What's the latency between Marcus events and UI updates?
3. Are there any event processing bottlenecks?
4. Which event types have the highest volume?

Analysis Capabilities
---------------------

Event Stream Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Real-time event pattern analysis
   class EventStreamAnalyzer:
       def analyze_event_patterns(self, time_window='1h'):
           events = self.get_events_in_window(time_window)
           
           # Calculate event frequencies
           frequencies = self.calculate_frequencies(events)
           
           # Detect event sequences
           sequences = self.find_common_sequences(events)
           
           # Identify anomalies
           anomalies = self.detect_anomalies(events)
           
           return {
               'total_events': len(events),
               'event_types': frequencies,
               'common_sequences': sequences,
               'anomalies': anomalies
           }

Correlation Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Event correlation detection
   def analyze_event_correlations(self, event_types, time_window='5m'):
       correlations = {}
       
       for event_type_a in event_types:
           for event_type_b in event_types:
               if event_type_a != event_type_b:
                   correlation = self.calculate_temporal_correlation(
                       event_type_a, event_type_b, time_window
                   )
                   
                   if correlation > 0.7:  # Strong correlation
                       correlations[f"{event_type_a} → {event_type_b}"] = correlation
       
       return correlations

Pattern Identification
----------------------

Temporal Patterns
~~~~~~~~~~~~~~~~~

1. **Event Cascades**
   
   - Agent status change → Task reassignment → Project update
   - Blocker reported → PM decision → Resource reallocation
   - Health degradation → Alert → Intervention

2. **Rhythmic Patterns**
   
   - Daily activity cycles (9am spike, lunch lull, 5pm wind-down)
   - Weekly patterns (Monday ramp-up, Friday completion push)
   - Project phase patterns (planning bursts, execution steady state)

3. **Anomaly Patterns**
   
   - Unusual event volumes (traffic spikes, dead periods)
   - Out-of-sequence events (completion before assignment)
   - Missing expected events (no status updates, silent agents)

Behavioral Patterns
~~~~~~~~~~~~~~~~~~~

1. **Agent Patterns**
   
   - Work rhythm identification
   - Communication style patterns
   - Collaboration network effects

2. **Project Patterns**
   
   - Success trajectory indicators
   - Risk accumulation patterns
   - Quality degradation signals

Interpretation Guidelines
-------------------------

Event Volume Interpretation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Volume Level
     - Events/Hour
     - Interpretation
   * - Low
     - <50
     - System quiet, possible issues
   * - Normal
     - 50-500
     - Healthy activity levels
   * - High
     - 500-2000
     - Busy but manageable
   * - Critical
     - >2000
     - Potential system stress

Event Latency Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Latency interpretation
   LATENCY_BENCHMARKS = {
       'excellent': '<100ms',    # Real-time feel
       'good': '100-500ms',      # Responsive
       'acceptable': '500ms-2s', # Noticeable but okay  
       'poor': '2s-10s',         # Sluggish response
       'critical': '>10s'        # System issues
   }

Alert Patterns
~~~~~~~~~~~~~~

.. code-block:: python

   # Alert pattern recognition
   def classify_alert_pattern(events):
       if is_storm_pattern(events):
           return 'alert_storm'  # Many alerts in short time
       elif is_cascade_pattern(events):
           return 'failure_cascade'  # Related system failures
       elif is_flapping_pattern(events):
           return 'unstable_system'  # Rapid state changes
       else:
           return 'normal_alert'

Advantages
----------

1. **Loose Coupling**: Components don't need direct knowledge of each other
2. **Scalability**: Easy to add new event handlers without system changes
3. **Resilience**: Failure in one subscriber doesn't affect others
4. **Auditability**: Complete event history for debugging and compliance
5. **Real-Time Capability**: Immediate response to system changes

Product Tiers
-------------

**Open Source (Public)**:

Basic Event System:
- In-memory event bus
- Simple pub/sub functionality
- Basic event persistence (24h)
- Standard event types
- File-based event storage

**Enterprise Add-ons**:

Advanced Event Features:
- Distributed event bus with clustering
- Event sourcing and replay capabilities
- Custom event types and schemas
- Advanced event filtering and routing
- Real-time event analytics
- Event stream processing
- Dead letter queue handling
- Event versioning and migration
- Integration with external event systems
- Compliance and audit features
- High availability and failover
- Performance monitoring and SLA tracking

Configuration
-------------

Event System Settings
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config.py
   EVENT_CONFIG = {
       'event_store': {
           'type': 'memory',  # or 'redis', 'postgres'
           'retention_hours': 24,
           'max_events': 100000
       },
       'bus': {
           'async_processing': True,
           'batch_size': 100,
           'flush_interval': 1000  # ms
       },
       'subscriptions': {
           'max_retries': 3,
           'retry_delay': 1000,  # ms
           'dead_letter_queue': True
       }
   }

Performance Tuning
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Performance optimization
   PERFORMANCE_CONFIG = {
       'event_processing': {
           'worker_pool_size': 4,
           'queue_size': 10000,
           'batch_processing': True
       },
       'persistence': {
           'async_writes': True,
           'write_batch_size': 1000,
           'compression': True
       }
   }

Best Practices
--------------

1. **Event Design**
   
   - Use consistent event schemas
   - Include sufficient context in events
   - Version events for backward compatibility

2. **Performance**
   
   - Avoid blocking operations in event handlers
   - Use event batching for high-volume scenarios
   - Implement circuit breakers for failing subscribers

3. **Reliability**
   
   - Handle subscriber failures gracefully
   - Implement event replay for recovery
   - Monitor event processing metrics

Future Enhancements
-------------------

- Event sourcing for complete system state reconstruction
- Complex event processing (CEP) for advanced pattern detection
- Integration with external messaging systems (Kafka, RabbitMQ)
- Event schema registry and evolution
- Distributed event tracing
- Machine learning for event pattern prediction
- GraphQL subscriptions for real-time queries