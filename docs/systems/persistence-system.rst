Persistence System
==================

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

The Persistence System is Seneca's data storage and retrieval layer that manages both historical Marcus data and Seneca-specific analytics data. It provides reliable, scalable storage for conversation logs, system metrics, user preferences, and analytical insights, enabling long-term trend analysis and system recovery capabilities.

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

1. **Log File Management**
   
   - **MarcusLogReader**: JSONL log file processing
   - **Conversation Archive**: Historical conversation storage
   - **Audit Trail**: System activity logging
   - **Backup Management**: Data protection and recovery

2. **Database Systems**
   
   - **Time Series Database**: Metrics and performance data
   - **Document Store**: Flexible schema for events and logs
   - **Relational Database**: Structured configuration data
   - **Cache Layer**: High-performance data access

3. **Data Processing Pipeline**
   
   - **Ingestion**: Raw data import and validation
   - **Transformation**: Data cleaning and normalization
   - **Indexing**: Search and query optimization
   - **Archival**: Long-term storage management

4. **Query Interface**
   
   - **Query Engine**: Flexible data retrieval
   - **Aggregation**: Statistical computations
   - **Search**: Full-text and semantic search
   - **Export**: Data extraction for external tools

Storage Architecture
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Data Sources → Ingestion → Processing → Storage → Query Interface
        ↓            ↓          ↓           ↓           ↓
   [Marcus Logs]  [Validate] [Transform] [Database]  [API Queries]
   [MCP Events]   [Parse]    [Enrich]    [Files]     [Analytics]
   [UI Actions]   [Filter]   [Index]     [Cache]     [Reports]
   [System Data]  [Route]    [Archive]   [Backup]    [Exports]

How It Works
------------

Log File Processing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class MarcusLogReader:
       def __init__(self, log_dir: str):
           self.log_dir = Path(log_dir)
           self.conversation_cache = {}
           
       def read_conversations(self, start_time=None, end_time=None):
           """Read conversation logs with time filtering"""
           conversations = []
           
           # Find all conversation log files
           log_files = list(self.log_dir.glob("conversations_*.jsonl"))
           log_files.extend(list(self.log_dir.glob("realtime_*.jsonl")))
           
           for log_file in sorted(log_files):
               try:
                   with open(log_file, 'r') as f:
                       for line in f:
                           if line.strip():
                               try:
                                   record = json.loads(line.strip())
                                   
                                   # Apply time filtering
                                   if self._within_time_range(record, start_time, end_time):
                                       conversations.append(
                                           self._enrich_conversation_record(record)
                                       )
                                       
                               except json.JSONDecodeError:
                                   continue
               except FileNotFoundError:
                   continue
                   
           return sorted(conversations, key=lambda x: x.get('timestamp', ''))

Database Storage
~~~~~~~~~~~~~~~~

.. code-block:: python

   class PersistenceManager:
       def __init__(self, config):
           self.config = config
           self.time_series_db = self._init_time_series_db()
           self.document_store = self._init_document_store()
           self.relational_db = self._init_relational_db()
           self.cache = self._init_cache()
           
       async def store_event(self, event):
           """Store event in appropriate storage backend"""
           
           # Route to appropriate storage
           if event['type'] == 'metric':
               await self._store_metric(event)
           elif event['type'] == 'conversation':
               await self._store_conversation(event)
           elif event['type'] == 'system_event':
               await self._store_system_event(event)
           
           # Update cache
           await self._update_cache(event)
           
       async def _store_metric(self, event):
           """Store metric in time series database"""
           metric_data = {
               'timestamp': event['timestamp'],
               'metric_name': event['data']['name'],
               'value': event['data']['value'],
               'tags': event['data'].get('tags', {}),
               'source': event['source']
           }
           
           await self.time_series_db.write_point(metric_data)

Marcus Integration
------------------

Data Source Integration
~~~~~~~~~~~~~~~~~~~~~~~

1. **Live MCP Data**
   
   - Real-time agent status
   - Task execution metrics
   - System health indicators
   - Performance measurements

2. **Historical Log Files**
   
   - Conversation transcripts (JSONL format)
   - Decision logs and context
   - Error reports and diagnostics
   - Audit trails and compliance data

3. **Derived Analytics**
   
   - Computed metrics and KPIs
   - Pattern analysis results
   - Predictive model outputs
   - Trend analysis data

Data Schema Design
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Conversation record schema
   CONVERSATION_SCHEMA = {
       'id': str,                    # Unique conversation ID
       'timestamp': datetime,        # When the conversation occurred
       'participants': List[str],    # Agent IDs involved
       'messages': List[dict],       # Message sequence
       'context': dict,             # Environmental context
       'outcomes': List[str],       # Results or decisions
       'metadata': dict             # Additional properties
   }
   
   # Metric record schema
   METRIC_SCHEMA = {
       'timestamp': datetime,        # Measurement time
       'name': str,                 # Metric name (e.g., 'agent.utilization')
       'value': Union[float, int],  # Metric value
       'unit': str,                 # Value unit (e.g., 'percent', 'seconds')
       'tags': dict,                # Dimensional data
       'source': str                # Data source identifier
   }

Value Proposition
-----------------

Data Continuity
~~~~~~~~~~~~~~~

The Persistence System provides:

- **Historical Context**: Access to complete system history
- **Trend Analysis**: Long-term pattern identification
- **Audit Compliance**: Complete activity trails
- **Disaster Recovery**: System state restoration capabilities

Questions It Answers
~~~~~~~~~~~~~~~~~~~~

**Historical Analysis**:

1. How has system performance changed over time?
2. What patterns led to successful vs. failed projects?
3. Which agents have shown consistent improvement?
4. How do seasonal patterns affect productivity?

**Compliance & Audit**:

1. What actions were taken and when?
2. Who made specific decisions and why?
3. How was sensitive data handled?
4. What was the system state at any point in time?

**Capacity Planning**:

1. What are our storage growth patterns?
2. How much historical data do we need to retain?
3. What backup and recovery capabilities do we need?
4. How should we optimize query performance?

Analysis Capabilities
---------------------

Historical Trend Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class TrendAnalyzer:
       def analyze_long_term_trends(self, metric_name, period='1y'):
           """Analyze long-term trends in system metrics"""
           
           # Query historical data
           data = self.persistence.query_metrics(
               metric=metric_name,
               start_time=datetime.now() - timedelta(days=365),
               aggregation='daily'
           )
           
           # Statistical analysis
           trends = {
               'overall_trend': self.calculate_trend_direction(data),
               'seasonal_patterns': self.detect_seasonal_patterns(data),
               'anomalies': self.identify_anomalies(data),
               'forecast': self.predict_future_values(data)
           }
           
           return trends

Data Mining Capabilities
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class DataMiner:
       def mine_conversation_patterns(self, time_range='6m'):
           """Extract patterns from conversation history"""
           
           conversations = self.persistence.query_conversations(
               start_time=datetime.now() - timedelta(days=180)
           )
           
           patterns = {
               'common_topics': self.extract_topics(conversations),
               'communication_flows': self.analyze_flows(conversations),
               'success_indicators': self.find_success_patterns(conversations),
               'collaboration_networks': self.build_networks(conversations)
           }
           
           return patterns

Pattern Identification
----------------------

Storage Patterns
~~~~~~~~~~~~~~~~

1. **Growth Patterns**
   
   - **Linear Growth**: Steady, predictable data accumulation
   - **Exponential Growth**: Rapid data volume increases
   - **Seasonal Growth**: Periodic spikes in data creation
   - **Event-Driven Growth**: Growth correlated with system activity

2. **Access Patterns**
   
   - **Hot Data**: Frequently accessed recent data
   - **Warm Data**: Occasionally accessed recent data
   - **Cold Data**: Rarely accessed historical data
   - **Archive Data**: Long-term retention for compliance

3. **Performance Patterns**
   
   - **Query Performance**: Response time trends
   - **Storage Efficiency**: Compression and deduplication
   - **Index Effectiveness**: Search performance optimization
   - **Cache Hit Rates**: Memory utilization patterns

Data Quality Patterns
~~~~~~~~~~~~~~~~~~~~~

1. **Completeness Patterns**
   
   - **Missing Data**: Gaps in data collection
   - **Partial Records**: Incomplete data entries
   - **Schema Evolution**: Changes in data structure
   - **Source Reliability**: Data source consistency

2. **Consistency Patterns**
   
   - **Data Conflicts**: Contradictory information
   - **Format Variations**: Inconsistent data formats
   - **Temporal Alignment**: Time synchronization issues
   - **Cross-Source Validation**: Data verification across sources

Interpretation Guidelines
-------------------------

Storage Metrics
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 25 30

   * - Metric
     - Healthy Range
     - Warning Range
     - Action Required
   * - Storage Growth
     - <10% monthly
     - 10-25% monthly
     - >25% monthly
   * - Query Response
     - <100ms
     - 100ms-1s
     - >1s
   * - Cache Hit Rate
     - >90%
     - 70-90%
     - <70%
   * - Backup Success
     - 100%
     - 95-99%
     - <95%

Data Retention Policies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Data lifecycle management
   RETENTION_POLICIES = {
       'conversations': {
           'hot': '30d',      # Full-text searchable
           'warm': '1y',      # Compressed storage
           'cold': '7y',      # Archive storage
           'delete': '10y'    # Compliance requirement
       },
       
       'metrics': {
           'raw': '30d',      # High-resolution data
           'hourly_agg': '1y', # Hourly aggregations
           'daily_agg': '5y',  # Daily aggregations
           'monthly_agg': 'forever' # Long-term trends
       },
       
       'system_logs': {
           'error_logs': '2y',
           'audit_logs': '7y',
           'debug_logs': '7d',
           'performance_logs': '90d'
       }
   }

Backup and Recovery
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Backup strategy
   BACKUP_STRATEGY = {
       'frequency': {
           'incremental': 'hourly',   # Changed data only
           'differential': 'daily',   # Changes since last full
           'full': 'weekly'          # Complete backup
       },
       
       'retention': {
           'daily': 30,    # Keep 30 daily backups
           'weekly': 12,   # Keep 12 weekly backups
           'monthly': 12,  # Keep 12 monthly backups
           'yearly': 7     # Keep 7 yearly backups
       },
       
       'storage': {
           'local': True,      # On-site backup
           'cloud': True,      # Off-site backup
           'encryption': True, # Encrypted backups
           'compression': True # Compressed storage
       }
   }

Advantages
----------

1. **Data Durability**: Reliable long-term data preservation
2. **Query Flexibility**: Support for diverse query patterns
3. **Scalability**: Growth accommodation without performance loss
4. **Recovery Capability**: System restoration from backups
5. **Compliance Support**: Audit trail and data governance

Product Tiers
-------------

**Open Source (Public)**:

Basic Persistence:
- File-based storage (JSONL, CSV)
- SQLite database support
- Basic backup utilities
- 30-day data retention
- Simple query interface
- Manual data export

**Enterprise Add-ons**:

Advanced Persistence:
- Multi-database support (PostgreSQL, MongoDB, InfluxDB)
- Automated backup and recovery
- Data replication and clustering
- Unlimited data retention
- Advanced query engine
- Real-time data streaming
- Data warehouse integration
- Compliance reporting
- Data encryption at rest
- Performance monitoring
- Custom data pipelines
- API-based data access

Configuration
-------------

Storage Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # config.py
   PERSISTENCE_CONFIG = {
       'storage': {
           'backend': 'hybrid',  # file, sqlite, postgresql, mongodb
           'data_dir': '/data/seneca',
           'max_file_size': '100MB',
           'compression': True
       },
       
       'databases': {
           'time_series': {
               'type': 'influxdb',
               'host': 'localhost',
               'port': 8086,
               'database': 'seneca_metrics'
           },
           
           'document': {
               'type': 'mongodb',
               'host': 'localhost', 
               'port': 27017,
               'database': 'seneca_events'
           }
       },
       
       'retention': {
           'default_retention': '1y',
           'auto_cleanup': True,
           'cleanup_interval': '24h'
       }
   }

Performance Tuning
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Performance optimization
   PERFORMANCE_CONFIG = {
       'indexing': {
           'auto_index': True,
           'index_threshold': 1000,  # records
           'rebuild_interval': '7d'
       },
       
       'caching': {
           'query_cache_size': '256MB',
           'cache_ttl': 3600,  # seconds
           'cache_strategy': 'lru'
       },
       
       'query': {
           'max_result_size': 10000,
           'query_timeout': 30,  # seconds
           'parallel_queries': True
       }
   }

Best Practices
--------------

1. **Data Modeling**
   
   - Design schemas for query patterns
   - Normalize where appropriate
   - Use appropriate data types

2. **Performance**
   
   - Index frequently queried fields
   - Partition large datasets
   - Implement query optimization

3. **Reliability**
   
   - Test backup and recovery procedures
   - Monitor storage health
   - Implement data validation

Future Enhancements
-------------------

- Distributed storage for horizontal scaling
- Machine learning for query optimization
- Real-time data streaming pipelines
- Advanced data compression algorithms
- Automated data lifecycle management
- Graph database integration for relationships
- Blockchain for immutable audit trails