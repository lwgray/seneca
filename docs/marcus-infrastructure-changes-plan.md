# Marcus Infrastructure Changes Plan

## Executive Summary

Marcus has a well-architected storage system that can be extended without breaking existing functionality. The JSONL logging should remain as-is for compatibility, while we add new capabilities through the Events system and custom persistence backends.

## Current Marcus Architecture

### Storage Layers
1. **JSONL Files** - Human-readable logs for debugging and analysis
2. **SQLite Database** - Structured persistence for state
3. **JSON Files** - Configuration and assignment tracking
4. **Events System** - Real-time pub/sub with optional persistence

### Key Finding
The Events system is the **best integration point** - it's designed for extension and won't break existing functionality.

## Proposed Changes to Marcus

### Phase 1: Expose Analytics Data (No Breaking Changes)

#### 1.1 Add Analytics Event Publisher
```python
# File: marcus/src/core/analytics_events.py
class AnalyticsEventPublisher:
    """Publishes high-level analytics events without breaking existing logging"""
    
    def __init__(self, events: Events):
        self.events = events
        
        # Subscribe to raw events and publish analytics events
        events.subscribe("task_assignment", self._on_task_assignment)
        events.subscribe("progress_update", self._on_progress_update)
        events.subscribe("worker_registration", self._on_worker_registration)
    
    async def _on_task_assignment(self, event):
        # Publish analytics-specific event
        await self.events.publish("analytics.task_assigned", {
            "timestamp": event["timestamp"],
            "agent_id": event["metadata"]["agent_id"],
            "task_id": event["metadata"]["task_id"],
            "score": event["metadata"]["assignment_score"],
            "skills_match": event["metadata"]["skills_match_percentage"]
        })
```

**Why**: This adds analytics without touching existing code.

#### 1.2 Add Metrics Collection Points
```python
# File: marcus/src/core/metrics_collector.py
class MetricsCollector:
    """Collects metrics at key points without modifying core logic"""
    
    def __init__(self, events: Events):
        self.events = events
        self.metrics = {}
        
        # Collect metrics from events
        events.subscribe("*", self._collect_metrics)
    
    async def _collect_metrics(self, event):
        # Extract metrics from events
        if event["type"] == "task_assignment":
            await self._update_metric("tasks_assigned_total", 1)
            await self._update_metric("assignment_score_avg", event["metadata"]["score"])
```

### Phase 2: Add External Storage Support (Backwards Compatible)

#### 2.1 Create TimeSeries Persistence Backend
```python
# File: marcus/src/core/persistence/timeseries_backend.py
class TimeSeriesPersistence(PersistenceBackend):
    """Writes to both files (for compatibility) and TimescaleDB (for analytics)"""
    
    def __init__(self, file_backend: FilePersistence, db_config: dict):
        self.file_backend = file_backend  # Keep existing file storage
        self.db = await self._connect_timescale(db_config)
    
    async def store(self, collection: str, key: str, data: Any) -> None:
        # Store in files for compatibility
        await self.file_backend.store(collection, key, data)
        
        # Also store metrics in TimescaleDB
        if collection == "events" and self._is_metric_event(data):
            await self._store_metric(data)
```

#### 2.2 Configuration for Dual Storage
```python
# File: marcus/config.py
PERSISTENCE_CONFIG = {
    "backend": "dual",  # New option
    "dual_config": {
        "primary": "file",  # Keep files as primary
        "secondary": "timeseries",  # Add TimescaleDB
        "timeseries_config": {
            "host": "localhost",
            "port": 5432,
            "database": "marcus_metrics"
        }
    }
}
```

### Phase 3: JSONL Logging Enhancement (Preserve Format)

#### 3.1 Add Log Multiplexer
```python
# File: marcus/src/logging/log_multiplexer.py
class LogMultiplexer:
    """Sends logs to multiple destinations without changing format"""
    
    def __init__(self, primary_logger):
        self.primary = primary_logger
        self.secondary_handlers = []
    
    def add_handler(self, handler):
        """Add additional log destinations (Kafka, S3, etc.)"""
        self.secondary_handlers.append(handler)
    
    def log(self, event):
        # Always log to primary (JSONL files)
        self.primary.log(event)
        
        # Send to additional handlers asynchronously
        for handler in self.secondary_handlers:
            asyncio.create_task(handler.handle(event))
```

### Phase 4: Event Stream Export (New Capability)

#### 4.1 Add Event Export API
```python
# File: marcus/src/marcus_mcp/tools/analytics.py
async def stream_events(
    event_types: List[str],
    start_time: Optional[str],
    end_time: Optional[str],
    state: Any
) -> Dict[str, Any]:
    """Stream events for external analytics systems"""
    
    # This is a new tool that Seneca can use
    events = []
    
    # From in-memory history (last 1000 events)
    for event in state.events.history:
        if event["type"] in event_types:
            if _in_time_range(event, start_time, end_time):
                events.append(event)
    
    return {
        "events": events,
        "count": len(events),
        "has_more": len(events) == 1000
    }
```

## Implementation Strategy

### Keep Working (No Changes Needed)
1. **JSONL Logging** - Continue as-is for debugging and compatibility
2. **SQLite Persistence** - Keep for state management
3. **Events System** - Already perfect for extension
4. **Assignment Tracking** - No changes needed

### Add Without Breaking
1. **Analytics Events** - New event types for metrics
2. **Dual Persistence** - Write to both files and TimescaleDB
3. **Log Multiplexing** - Send logs to multiple destinations
4. **Export APIs** - New tools for data access

### Migration Path

#### Stage 1: Parallel Operation (Month 1)
```
Current: Events → JSONL Files → Manual Analysis
Add:     Events → Analytics Publisher → TimescaleDB → Seneca
Result:  Both systems work independently
```

#### Stage 2: Enhanced Logging (Month 2)
```
Current: Logger → JSONL Files
Add:     Logger → Multiplexer → JSONL Files + Kafka/S3
Result:  Logs available in multiple formats
```

#### Stage 3: Unified Analytics (Month 3)
```
Final:   Events → Multi-Backend → JSONL + TimescaleDB + Stream
         ↓         ↓              ↓        ↓            ↓
         Legacy    Analytics     Debug    Metrics      Real-time
```

## Code Changes Summary

### Minimal Risk Changes
1. **Add new files** - No modification to existing code
   - `analytics_events.py`
   - `metrics_collector.py`
   - `timeseries_backend.py`

2. **Configuration additions** - Optional new settings
   - Add `dual` backend option
   - Add analytics configuration

3. **New MCP tools** - Additional capabilities
   - `stream_events`
   - `get_metrics`
   - `export_analytics`

### Zero Risk Changes
1. **Event subscriptions** - Use existing system
2. **Log parsing** - Read JSONL files externally
3. **Database queries** - Direct SQLite access

## Benefits of This Approach

1. **No Breaking Changes** - Marcus continues working exactly as before
2. **Gradual Migration** - Add capabilities incrementally
3. **Fallback Options** - Can disable new features instantly
4. **Multiple Consumers** - JSONL for debugging, TimescaleDB for analytics
5. **Future Proof** - Easy to add more backends later

## Testing Strategy

1. **Parallel Testing** - Run old and new systems together
2. **Output Comparison** - Verify JSONL files unchanged
3. **Performance Testing** - Ensure no impact on core operations
4. **Fallback Testing** - Verify system works with analytics disabled

## Rollback Plan

If issues arise:
1. Set `PERSISTENCE_CONFIG["backend"] = "file"`
2. Disable analytics event publisher
3. Remove log multiplexer handlers
4. System returns to original state instantly

## Conclusion

This plan preserves Marcus's existing functionality while adding powerful analytics capabilities. The JSONL logging remains unchanged for compatibility, while new systems provide the data needed for advanced analytics and visualization.

The key insight is that Marcus's Events system is already designed for this type of extension - we just need to use it properly.