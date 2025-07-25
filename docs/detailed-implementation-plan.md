# Seneca Detailed Implementation Plan for Engineers

## Why We're Building This

Seneca provides observability for Marcus AI orchestration. While Marcus has the intelligence to predict and assign tasks, it lacks:
1. Visual dashboards for human operators
2. Historical trend analysis at scale
3. Code production metrics from GitHub
4. Anomaly detection for performance issues
5. Multi-agent collaboration insights

This plan details exactly what we're building, why, and how.

## Phase 1: Expose Marcus's Hidden Intelligence (Week 1-2)

### What We're Adding
Marcus already predicts project completion and task outcomes, but these tools aren't available to Seneca's "observer" role.

### Why We're Adding It
Teams need to see:
- "When will this project actually finish?" (with confidence intervals)
- "Which tasks are likely to fail?" (with probability scores)
- "How will delays cascade through the project?" (impact analysis)

### How We're Adding It

#### 1.1 Marcus Changes
```python
# File: marcus/src/marcus_mcp/tools/auth.py
# Add these tools to observer role
ROLE_TOOLS = {
    "observer": [
        # ... existing tools ...
        "predict_completion_time",      # Returns: {completion_date, confidence_low, confidence_high}
        "predict_task_outcome",         # Returns: {success_probability, estimated_duration, blockage_risk}
        "predict_blockage_probability", # Returns: {probability, likely_causes, suggested_mitigations}
        "predict_cascade_effects",      # Returns: {affected_tasks, delay_impact, critical_path_changes}
        "get_task_assignment_score",    # Returns: {agent_scores, selected_agent, reasoning}
    ]
}
```

#### 1.2 Seneca API Implementation
```python
# File: seneca/src/api/prediction_api.py
@prediction_api.route('/project/<project_id>/completion')
async def predict_project_completion(project_id):
    """
    Returns: {
        "predicted_completion": "2024-02-15T10:00:00Z",
        "confidence_interval": {
            "low": "2024-02-10T10:00:00Z",   # Best case
            "high": "2024-02-20T10:00:00Z"   # Worst case
        },
        "current_velocity": 3.5,  # tasks/day
        "required_velocity": 4.2, # tasks/day to meet deadline
        "risk_factors": [
            {"task_id": "task-123", "risk": "high", "reason": "blocking 5 other tasks"}
        ]
    }
    """
    client = get_marcus_client()
    return await client.call_tool('predict_completion_time', {
        'project_id': project_id
    })
```

#### 1.3 Frontend Visualization
```javascript
// File: seneca/src/ui/components/ProjectTimeline.vue
// Gantt chart with confidence intervals
// Visual elements:
// - Tasks as horizontal bars
// - Predicted completion with shaded confidence interval
// - Critical path highlighted in red
// - Risk indicators (⚠️) on high-risk tasks
```

### What We're Measuring
- Project completion dates with confidence intervals
- Task success probabilities (0-100%)
- Blockage risks for each task
- Cascade effects of delays

### Data Needs
- No new data storage needed
- Direct API calls to Marcus for predictions
- Cache predictions for 5 minutes to avoid overload

## Phase 2: Time-Series Analytics Infrastructure (Week 3-4)

### What We're Adding
A scalable metrics storage system using PostgreSQL + TimescaleDB for historical analysis.

### Why We're Adding It
Currently, analyzing "how has velocity changed over the past month?" requires parsing hundreds of JSONL files. This doesn't scale beyond ~100MB of logs.

### How We're Adding It

#### 2.1 Database Schema
```sql
-- File: seneca/migrations/001_create_metrics_tables.sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Core metrics table
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    value DOUBLE PRECISION,
    tags JSONB,
    PRIMARY KEY (time, metric_name, tags)
);
SELECT create_hypertable('metrics', 'time');

-- Pre-aggregated daily metrics for fast queries
CREATE TABLE daily_metrics (
    date DATE NOT NULL,
    metric_name TEXT NOT NULL,
    avg_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    count INTEGER,
    tags JSONB,
    PRIMARY KEY (date, metric_name, tags)
);
```

#### 2.2 Metrics Collector Service
```python
# File: seneca/src/services/metrics_collector.py
class MetricsCollector:
    """Polls Marcus every 60 seconds and stores time-series metrics"""
    
    METRICS_TO_COLLECT = [
        # Agent metrics
        ('agent.utilization', lambda a: a['utilization']),
        ('agent.tasks_active', lambda a: len(a['active_tasks'])),
        ('agent.success_rate', lambda a: a['performance']['success_rate']),
        
        # Project metrics
        ('project.velocity', lambda p: p['velocity']),
        ('project.tasks_completed', lambda p: p['completed_count']),
        ('project.tasks_blocked', lambda p: p['blocked_count']),
        ('project.health_score', lambda p: p['health_score']),
        
        # System metrics
        ('system.active_agents', lambda s: s['active_agent_count']),
        ('system.total_throughput', lambda s: s['tasks_per_hour']),
    ]
    
    async def collect_metrics(self):
        while True:
            # Collect agent metrics
            agents = await marcus_client.list_registered_agents()
            for agent in agents:
                for metric_name, extractor in self.AGENT_METRICS:
                    await self.store_metric(
                        metric_name,
                        extractor(agent),
                        tags={'agent_id': agent['id'], 'role': agent['role']}
                    )
            
            # Collect project metrics
            project = await marcus_client.get_project_status()
            for metric_name, extractor in self.PROJECT_METRICS:
                await self.store_metric(
                    metric_name,
                    extractor(project),
                    tags={'project_id': project['id']}
                )
            
            await asyncio.sleep(60)
```

### What We're Measuring
**Agent Performance Metrics:**
- Utilization percentage (0-100%)
- Active task count
- Success rate over time
- Average task completion time

**Project Health Metrics:**
- Velocity (tasks completed per day)
- Blocked task count trends
- Health score (0-100)
- Progress percentage

**System Performance:**
- Total active agents
- System throughput (tasks/hour)
- API response times
- Error rates

### Why TimescaleDB Instead of InfluxDB/Kafka
1. **Simplicity**: It's just PostgreSQL with superpowers
2. **SQL Queries**: Engineers already know SQL
3. **Built-in Aggregations**: Automatic rollups for performance
4. **Scaling**: Handles billions of rows efficiently
5. **Migration Path**: Can add Kafka later if needed

## Phase 3: Code Production Metrics (Week 5-6)

### What We're Adding
GitHub integration to measure actual code output per agent, not just task completion.

### Why We're Adding It
"Task completed" doesn't tell us:
- How much code was written?
- What's the code quality?
- How long do reviews take?
- Who's actually producing vs. reviewing?

### How We're Adding It

#### 3.1 Marcus GitHub Metrics Tool
```python
# File: marcus/src/marcus_mcp/tools/github_metrics.py
async def get_code_metrics(
    agent_id: str,
    start_date: str,
    end_date: str,
    state: Any
) -> Dict[str, Any]:
    """
    Calculate code production metrics for an agent
    """
    # Map agent_id to GitHub username
    github_username = state.get_github_username(agent_id)
    
    # Fetch commits
    commits = await github_client.get_commits(
        author=github_username,
        since=start_date,
        until=end_date
    )
    
    # Calculate metrics
    metrics = {
        'commits': len(commits),
        'lines_added': 0,
        'lines_deleted': 0,
        'files_changed': set(),
        'languages': {},
        'review_comments_made': 0,
        'review_comments_received': 0,
        'prs_opened': 0,
        'prs_merged': 0,
        'average_pr_merge_time': 0,
        'code_churn': 0  # Lines changed that were changed again within 2 weeks
    }
    
    for commit in commits:
        metrics['lines_added'] += commit.stats.additions
        metrics['lines_deleted'] += commit.stats.deletions
        
        for file in commit.files:
            metrics['files_changed'].add(file.filename)
            ext = file.filename.split('.')[-1]
            metrics['languages'][ext] = metrics['languages'].get(ext, 0) + 1
    
    # Fetch PR metrics
    prs = await github_client.get_pull_requests(author=github_username)
    metrics['prs_opened'] = len(prs)
    metrics['prs_merged'] = len([pr for pr in prs if pr.merged])
    
    # Calculate average merge time
    merge_times = []
    for pr in prs:
        if pr.merged:
            merge_time = (pr.merged_at - pr.created_at).total_seconds() / 3600
            merge_times.append(merge_time)
    
    if merge_times:
        metrics['average_pr_merge_time'] = sum(merge_times) / len(merge_times)
    
    return metrics
```

#### 3.2 Seneca Code Metrics Dashboard
```javascript
// File: seneca/src/ui/components/CodeMetricsDashboard.vue
// Displays:
// 1. Lines of Code chart (stacked bar: additions/deletions)
// 2. Language breakdown (pie chart)
// 3. PR merge time trends (line chart)
// 4. Code review participation (network graph)
// 5. Productivity heatmap (commits by day/hour)
```

### What We're Measuring
- **Volume**: Lines added/deleted, files changed
- **Quality**: Code churn rate, review comments
- **Velocity**: PR merge times, commit frequency
- **Collaboration**: Review participation, co-authored commits

### Data Storage
```sql
-- Store code metrics in time-series
INSERT INTO metrics (time, metric_name, value, tags) VALUES
    (NOW(), 'code.lines_added', 150, '{"agent_id": "agent1", "language": "python"}'),
    (NOW(), 'code.pr_merge_time', 4.5, '{"agent_id": "agent1", "pr_size": "medium"}');
```

## Phase 4: Multi-Agent Visualizations (Week 7-8)

### What We're Adding
Advanced visualizations specifically for multi-agent software development teams.

### Why We're Adding It
Current node-and-edge diagram doesn't show:
- Who's working together effectively?
- Where are the collaboration bottlenecks?
- How does parallel work actually flow?

### How We're Adding It

#### 4.1 Collaboration Network Graph
```javascript
// File: seneca/src/ui/components/CollaborationNetwork.vue
<template>
  <div class="collaboration-network">
    <!-- D3.js Force-Directed Graph -->
    <!-- Nodes: Agents (size = productivity) -->
    <!-- Edges: Collaboration strength -->
    <!-- Edge width: Number of shared tasks -->
    <!-- Edge color: Success rate when working together -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      collaborationData: {
        nodes: [
          { id: 'agent1', name: 'Backend Dev', productivity: 85 },
          { id: 'agent2', name: 'Frontend Dev', productivity: 92 }
        ],
        edges: [
          { 
            source: 'agent1', 
            target: 'agent2', 
            weight: 15,  // Number of shared tasks
            success_rate: 0.93  // 93% success when working together
          }
        ]
      }
    }
  },
  
  methods: {
    calculateCollaborationStrength(agent1, agent2) {
      // Factors:
      // 1. Number of shared tasks
      // 2. Success rate of shared tasks
      // 3. Communication frequency (blockers resolved for each other)
      // 4. Code review interactions
    }
  }
}
</script>
```

#### 4.2 Parallel Work Timeline
```javascript
// File: seneca/src/ui/components/ParallelTimeline.vue
// Swimlane visualization showing:
// - Each agent gets a horizontal lane
// - Tasks shown as bars with actual start/end times
// - Overlapping tasks clearly visible
// - Dependencies shown as arrows between lanes
// - Blocked periods shown in red
// - Idle time visible as gaps
```

### Vue.js Display Adequacy
Your current Vue.js setup is good! You'll need to add:
1. **D3.js** for force-directed graphs and complex visualizations
2. **Vue Flow** enhancement for parallel timeline
3. **ApexCharts** or **Chart.js** for time-series charts
4. **Heatmap.js** for productivity heatmaps

## Phase 5: Anomaly Detection (Week 9-10)

### What We're Adding
Statistical anomaly detection to catch performance issues early.

### Why We're Adding It
Need to automatically detect:
- Agent performing 50% below normal
- Sudden spike in blocked tasks
- Unusual error patterns
- System performance degradation

### What Outliers We're Measuring

#### 5.1 Agent Performance Outliers
```python
# File: seneca/src/analytics/anomaly_detector.py
class AgentAnomalyDetector:
    def detect_performance_anomalies(self, agent_id: str, metric: str):
        """
        Detect when an agent's performance deviates significantly
        
        Metrics monitored:
        - task_completion_rate: Usually 3-5 tasks/day, alert if <1 or >10
        - success_rate: Usually 85-95%, alert if <70%
        - response_time: Usually <5min, alert if >30min
        - code_production: Usually 100-500 lines/day, alert if 0 or >2000
        """
        
        # Get last 30 days of data
        historical_data = self.get_metrics(
            f"agent.{metric}",
            agent_id=agent_id,
            days=30
        )
        
        # Calculate statistics
        mean = np.mean(historical_data)
        std = np.std(historical_data)
        
        # Get current value
        current = self.get_current_value(f"agent.{metric}", agent_id)
        
        # Z-score method: >3 standard deviations = anomaly
        z_score = (current - mean) / std
        
        if abs(z_score) > 3:
            return {
                'anomaly': True,
                'severity': 'high' if abs(z_score) > 4 else 'medium',
                'current_value': current,
                'expected_range': (mean - 2*std, mean + 2*std),
                'deviation': f"{z_score:.1f} standard deviations",
                'recommendation': self.get_recommendation(metric, z_score)
            }
```

#### 5.2 Project Health Anomalies
```python
def detect_project_anomalies(self, project_id: str):
    """
    Moving averages we're comparing:
    
    1. Velocity Moving Average (7-day vs 30-day)
       - If 7-day MA < 50% of 30-day MA = declining velocity
       
    2. Blocker Rate Moving Average  
       - If blockers/day increases >2x normal = problem
       
    3. Task Completion Time MA
       - If tasks taking 2x longer than historical average
    """
    
    anomalies = []
    
    # Velocity comparison
    velocity_7d = self.get_moving_average('project.velocity', days=7)
    velocity_30d = self.get_moving_average('project.velocity', days=30)
    
    if velocity_7d < 0.5 * velocity_30d:
        anomalies.append({
            'type': 'velocity_decline',
            'severity': 'high',
            'message': f'Velocity dropped from {velocity_30d:.1f} to {velocity_7d:.1f} tasks/day',
            'recommendation': 'Check for blockers or agent availability issues'
        })
```

### What Moving Averages We're Comparing

1. **Short vs Long Term Performance**
   - 7-day MA vs 30-day MA for velocity
   - Detects recent performance drops

2. **Baseline vs Current**
   - 30-day baseline vs last 24 hours
   - Catches sudden changes

3. **Individual vs Team**
   - Agent performance vs team average
   - Identifies struggling agents

4. **Expected vs Actual**
   - Predicted completion vs actual progress
   - Early warning for delays

### Alert Configuration
```python
ANOMALY_THRESHOLDS = {
    'agent.task_completion_rate': {
        'method': 'z_score',
        'threshold': 3,
        'window': '30d'
    },
    'project.velocity': {
        'method': 'moving_average_ratio',
        'short_window': '7d',
        'long_window': '30d',
        'threshold': 0.5  # Alert if 7d MA < 50% of 30d MA
    },
    'system.error_rate': {
        'method': 'absolute_threshold',
        'threshold': 0.05  # Alert if >5% error rate
    }
}
```

## Data Flow Summary

```
Marcus (Source) → Seneca Collector → TimescaleDB → Analytics → Visualizations
       ↓                    ↓              ↓           ↓            ↓
  [Live APIs]         [60s polling]   [Time-series] [Anomaly]   [Vue.js]
  [Predictions]       [Metrics]       [Storage]     [Detection]  [D3.js]
  [GitHub API]        [Transform]     [Aggregate]   [Alerts]     [Charts]
```

## Success Metrics

1. **Performance**: Dashboard loads in <2 seconds
2. **Accuracy**: Predictions within 20% of actual
3. **Detection**: Catch 90% of performance anomalies
4. **Usability**: 80% of users check dashboard daily
5. **Scalability**: Handle 1M metrics/day without degradation

## Final Notes for Engineers

1. **Start Simple**: Get basic metrics flowing before adding ML
2. **Use What Exists**: Marcus has the intelligence, just expose it
3. **Measure Everything**: Storage is cheap, insights are valuable
4. **Alert Sparingly**: Too many alerts = ignored alerts
5. **Visualize Clearly**: If it takes >5 seconds to understand, redesign it

This plan gives you a complete observability platform that leverages Marcus's intelligence while adding the visualization and analytics layers that make the data actionable for human operators.