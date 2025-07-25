# Seneca Implementation Plan

## Executive Summary

This plan outlines how to leverage Marcus's existing capabilities while building scalable analytics infrastructure for Seneca. The approach prioritizes using Marcus's existing tools first, then adding visualization and analytics layers in Seneca.

## Phase 1: Expose Marcus Prediction Tools (Week 1-2)

### A. Access Marcus's Existing Prediction Tools

**Feature**: Project completion predictions, task assignment intelligence  
**Implementation Location**: Marcus  
**Resources Needed**: 1 developer, 1 week

#### Tasks:

1. **Add prediction tools to observer role** (Marcus)
   ```python
   # In marcus/src/marcus_mcp/tools/auth.py
   ROLE_TOOLS = {
       "observer": [
           # ... existing tools ...
           # Add prediction tools
           "predict_completion_time",
           "predict_task_outcome", 
           "predict_blockage_probability",
           "predict_cascade_effects",
           "get_task_assignment_score",
       ]
   }
   ```

2. **Create prediction API endpoints** (Seneca)
   ```python
   # In seneca/src/api/prediction_api.py
   @prediction_api.route('/project/<project_id>/completion')
   async def predict_project_completion(project_id):
       client = get_marcus_client()
       return await client.call_tool('predict_completion_time', {
           'project_id': project_id
       })
   ```

3. **Add prediction visualizations** (Seneca)
   - Gantt chart with predicted completion dates
   - Confidence interval visualization
   - Risk indicator components

## Phase 2: Enhanced Analytics Infrastructure (Week 3-4)

### B. Implement Scalable Analytics Storage

**Feature**: Time-series metrics storage  
**Implementation Location**: Seneca (with Marcus events)  
**Resources Needed**: 1 developer, 1 week

#### Option 1: Lightweight (Recommended to Start)

1. **Add TimescaleDB extension to PostgreSQL** (Seneca)
   ```sql
   CREATE EXTENSION IF NOT EXISTS timescaledb;
   
   CREATE TABLE metrics (
       time TIMESTAMPTZ NOT NULL,
       metric_name TEXT NOT NULL,
       value DOUBLE PRECISION,
       tags JSONB,
       PRIMARY KEY (time, metric_name)
   );
   
   SELECT create_hypertable('metrics', 'time');
   ```

2. **Create metrics collector service** (Seneca)
   ```python
   # seneca/src/services/metrics_collector.py
   class MetricsCollector:
       async def collect_metrics(self):
           # Poll Marcus every 60 seconds
           while True:
               agents = await marcus_client.list_registered_agents()
               for agent in agents:
                   await self.store_metric(
                       'agent.utilization',
                       agent['utilization'],
                       tags={'agent_id': agent['id']}
                   )
               await asyncio.sleep(60)
   ```

#### Option 2: Full Scale (If Needed Later)

- Add Kafka for event streaming
- Use InfluxDB for dedicated time-series
- Implement Apache Flink for stream processing

## Phase 3: Code Production Metrics (Week 5-6)

### C. Extend Marcus GitHub Integration

**Feature**: Code production metrics  
**Implementation Location**: Marcus  
**Resources Needed**: 1 developer, 1 week

1. **Add code metrics tools** (Marcus)
   ```python
   # marcus/src/marcus_mcp/tools/github.py
   async def get_code_metrics(
       agent_id: str,
       start_date: str,
       end_date: str,
       state: Any
   ) -> Dict[str, Any]:
       commits = await github_client.get_commits(
           author=agent_id,
           since=start_date,
           until=end_date
       )
       
       return {
           'commits': len(commits),
           'lines_added': sum(c.stats.additions for c in commits),
           'lines_deleted': sum(c.stats.deletions for c in commits),
           'files_changed': sum(len(c.files) for c in commits),
           'review_comments': await count_review_comments(agent_id)
       }
   ```

2. **Create code metrics API** (Seneca)
   ```python
   @code_api.route('/agent/<agent_id>/code-metrics')
   async def get_agent_code_metrics(agent_id):
       return await marcus_client.call_tool('get_code_metrics', {
           'agent_id': agent_id,
           'start_date': request.args.get('start_date'),
           'end_date': request.args.get('end_date')
       })
   ```

## Phase 4: Advanced Visualizations (Week 7-8)

### D. Multi-Agent Development Visualizations

**Feature**: Collaboration graphs, parallel work views  
**Implementation Location**: Seneca  
**Resources Needed**: 1 frontend developer, 2 weeks

1. **Collaboration Network Graph** (Seneca)
   ```javascript
   // seneca/src/ui/components/CollaborationGraph.vue
   // Use D3.js force-directed graph
   // Nodes: agents
   // Edges: shared tasks, code reviews, blockers resolved
   ```

2. **Parallel Work Timeline** (Seneca)
   ```javascript
   // seneca/src/ui/components/ParallelTimeline.vue
   // Swimlane visualization showing concurrent work
   // Each lane = one agent
   // Bars = task duration with overlaps visible
   ```

3. **Code Activity Heatmap** (Seneca)
   - Git activity by hour/day
   - Commit frequency patterns
   - Review turnaround times

## Phase 5: Anomaly Detection & ML (Week 9-10)

### E. Implement Anomaly Detection

**Feature**: Performance anomaly detection  
**Implementation Location**: Seneca  
**Resources Needed**: 1 ML developer, 2 weeks

1. **Simple Statistical Anomaly Detection** (Seneca)
   ```python
   # seneca/src/analytics/anomaly_detector.py
   from scipy import stats
   
   class AnomalyDetector:
       def detect_outliers(self, metric_name, window='7d'):
           data = self.fetch_metrics(metric_name, window)
           z_scores = stats.zscore(data)
           return [d for d, z in zip(data, z_scores) if abs(z) > 3]
   ```

2. **ML-Based Prediction Enhancement** (Optional)
   - Use Prophet for time-series forecasting
   - Implement isolation forests for anomaly detection
   - Add LSTM for sequence prediction

## Implementation Roadmap

### Immediate (Week 1-2)
- [ ] Expose Marcus prediction tools to observer role
- [ ] Create prediction API endpoints in Seneca
- [ ] Basic prediction visualizations

### Short Term (Week 3-6)
- [ ] Set up TimescaleDB for metrics
- [ ] Implement metrics collector service
- [ ] Extend Marcus GitHub integration for code metrics
- [ ] Create code metrics dashboard

### Medium Term (Week 7-10)
- [ ] Build collaboration network visualization
- [ ] Implement parallel work timeline
- [ ] Add statistical anomaly detection
- [ ] Create alert system for anomalies

### Long Term (Month 3+)
- [ ] Evaluate need for Kafka/InfluxDB
- [ ] Implement ML-based predictions
- [ ] Build custom dashboard builder
- [ ] Add natural language insights

## Resource Requirements

### Development Team
- 1 Full-stack developer (primary)
- 1 Frontend developer (visualizations)
- 1 ML engineer (anomaly detection)

### Infrastructure
- PostgreSQL with TimescaleDB (minimum)
- Redis for caching
- Additional 8GB RAM for analytics workloads

### Third-Party Services
- None required initially
- Optional: Grafana for advanced dashboards

## Success Metrics

1. **Phase 1**: Prediction accuracy within 20% of actual
2. **Phase 2**: Query response time <100ms for 30-day metrics
3. **Phase 3**: Code metrics available for all agents
4. **Phase 4**: User engagement with new visualizations >80%
5. **Phase 5**: Anomaly detection catches 90% of performance issues

## Risk Mitigation

1. **Marcus API Changes**: Version lock MCP protocol
2. **Performance Issues**: Start with sampling, scale up gradually
3. **Data Volume**: Implement data retention policies early
4. **User Adoption**: Include users in design process

## Conclusion

This plan leverages Marcus's existing intelligence while adding the visualization and analytics layers that make Seneca valuable. By starting simple and scaling based on actual needs, we can deliver value quickly while maintaining flexibility for future growth.