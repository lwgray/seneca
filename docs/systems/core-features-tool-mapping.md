# Core Features to Marcus Tools Mapping

This document maps Seneca's core features to the specific Marcus MCP tools available to "observer" role clients, identifying gaps and implementation status.

## Available Marcus Tools for Seneca (Observer Role)

Based on the role-based access control in Marcus, Seneca as an "observer" client has access to these tools:

### Basic Connectivity
- `ping` - Health checks and diagnostics
- `register_client` - Client authentication

### Project Visibility (Read-Only)
- `get_project_status` - Current project metrics and status
- `get_current_project` - Active project information
- `list_projects` - All available projects
- `remove_project` - Project deletion (needed for PMs)

### Agent Monitoring
- `list_registered_agents` - Agent roster with current status
- `get_agent_status` - Individual agent details and current task

### Board Health Analysis
- `check_board_health` - Overall board health metrics and issues
- `check_task_dependencies` - Task relationships and bottlenecks
- `check_assignment_health` - Assignment system health

### Analytics and Monitoring Tools
- `pipeline_monitor_dashboard` - Live dashboard data
- `pipeline_monitor_flow` - Specific flow tracking
- `pipeline_report` - Report generation (HTML/markdown/JSON)
- `pipeline_predict_risk` - Failure risk predictions
- `pipeline_find_similar` - Pattern matching for similar flows
- `pipeline_compare` - Compare multiple pipeline flows

### Pipeline Replay Tools
- `pipeline_replay_start` - Start replay session
- `pipeline_replay_forward` - Step forward in replay
- `pipeline_replay_backward` - Step backward in replay
- `pipeline_replay_jump` - Jump to specific position

### Audit and Usage
- `get_usage_report` - Usage statistics and analytics

## Core Features Implementation Mapping

### 1. Real-Time Marcus Monitoring ✅

**Feature: Live Agent Status**
- Tool: `list_registered_agents` + `get_agent_status`
- Implementation: API endpoint + WebSocket updates
- Status: ✅ Implemented in `agent_management_api.py`

**Feature: Task Progress Tracking**
- Tool: `get_agent_status` (includes current_task)
- Implementation: Polling + WebSocket for real-time updates
- Status: ✅ Can be extracted from agent status

**Feature: Project Health Dashboard**
- Tool: `get_project_status` + `check_board_health`
- Implementation: Combined metrics from both tools
- Status: ✅ Implemented in `project_management_api.py`

**Feature: System Connectivity**
- Tool: `ping`
- Implementation: Regular health checks
- Status: ✅ Implemented in `seneca_server.py`

### 2. Historical Data Analysis ⚠️

**Feature: Conversation Timeline**
- Tool: None directly available
- Alternative: `MarcusLogReader` reads JSONL files
- Implementation: `conversation_processor.py`
- Status: ⚠️ Requires file system access to Marcus logs

**Feature: Task Completion Trends**
- Tool: `pipeline_monitor_dashboard` (some data)
- Alternative: Parse from historical logs
- Implementation: Analytics processing of log data
- Status: ⚠️ Limited real-time data, needs historical processing

**Feature: Agent Performance History**
- Tool: None directly available
- Alternative: Accumulate from periodic `get_agent_status` calls
- Implementation: Time-series storage in Persistence system
- Status: ❌ Need to build historical tracking

**Feature: Project Retrospectives**
- Tool: `pipeline_report` + historical logs
- Implementation: Combine report generation with log analysis
- Status: ⚠️ Partially available

### 3. Interactive Visualizations ✅

**Feature: Workflow Canvas**
- Data Source: `list_registered_agents` + `get_project_status`
- Implementation: Vue Flow components in `WorkflowCanvas.vue`
- Status: ✅ Implemented

**Feature: Status Indicators**
- Data Source: All status-related tools
- Implementation: Color-coded nodes in visualization
- Status: ✅ Implemented

**Feature: Progress Charts**
- Data Source: `pipeline_monitor_dashboard`
- Implementation: D3.js charts in frontend
- Status: ✅ Basic implementation exists

**Feature: Filtering Controls**
- Data Source: Client-side filtering of received data
- Implementation: `FilterPanel.vue`
- Status: ✅ Implemented

### 4. Basic Analytics ⚠️

**Feature: Simple Statistics**
- Tool: `get_usage_report` + data processing
- Implementation: Analytics system calculations
- Status: ⚠️ Basic stats from usage report

**Feature: Trend Detection**
- Tool: Historical data accumulation needed
- Implementation: Time-series analysis in Analytics
- Status: ❌ Requires historical data collection

**Feature: Health Scoring**
- Tool: `check_board_health` provides health scores
- Implementation: Direct from tool response
- Status: ✅ Available from Marcus

**Feature: Export Capability**
- Tool: `pipeline_report` (multiple formats)
- Implementation: API endpoints for data export
- Status: ✅ Partially implemented

### 5. Core APIs ✅

**Feature: Read-Only REST APIs**
- Implementation: Flask API endpoints
- Status: ✅ Implemented for all data types

**Feature: WebSocket Streaming**
- Implementation: Flask-SocketIO
- Status: ✅ Implemented

**Feature: Basic Authentication**
- Implementation: Token-based auth in API
- Status: ⚠️ Basic implementation needed

**Feature: Rate Limiting**
- Implementation: Flask middleware
- Status: ❌ Not yet implemented

### 6. Essential Infrastructure ✅

**Feature: File-Based Storage**
- Implementation: `MarcusLogReader` + file system
- Status: ✅ Implemented

**Feature: In-Memory Events**
- Implementation: Event System with Python async
- Status: ✅ Implemented

**Feature: SQLite Database**
- Implementation: For config and cache
- Status: ⚠️ Using file system currently

**Feature: Basic Backup**
- Implementation: Export/import functionality
- Status: ❌ Not yet implemented

## What We Have vs What We Need

### Already Have (Systems)
1. **MCP Client System** - Connects to Marcus, calls tools
2. **API System** - REST endpoints for all features
3. **Processor System** - Data transformation
4. **Event System** - Real-time pub/sub
5. **WebSocket System** - Real-time frontend updates
6. **Visualization System** - Vue.js frontend
7. **Persistence System** - Log file reading

### Gaps to Address

#### Missing Tools/Features:
1. **Historical Data Collection**
   - Need: Periodic polling and storage of agent/project status
   - Solution: Background task to collect and store time-series data

2. **Authentication System**
   - Need: Basic token auth for API access
   - Solution: Simple JWT implementation

3. **Rate Limiting**
   - Need: Prevent API abuse
   - Solution: Flask-Limiter middleware

4. **Database Storage**
   - Need: SQLite for configuration and cache
   - Solution: Add SQLAlchemy models

5. **Backup/Export**
   - Need: Data export functionality
   - Solution: API endpoints for bulk data export

#### Missing Marcus Tools (Would Be Helpful):
1. **Historical Metrics API** - Get metrics over time ranges
2. **Conversation History API** - Direct access to conversation data
3. **Aggregated Statistics API** - Pre-computed analytics

## Implementation Priority

### High Priority (Core Functionality)
1. ✅ Real-time monitoring (DONE)
2. ⚠️ Historical data collection system
3. ⚠️ Basic authentication

### Medium Priority (Enhanced Features)
1. ❌ Rate limiting
2. ❌ SQLite database integration
3. ❌ Backup/export functionality

### Low Priority (Nice to Have)
1. ❌ Advanced analytics
2. ❌ Custom dashboards
3. ❌ Alert system

## Systems That Make Up the Observability Platform

### Core Observability Stack:
1. **MCP Client** (Data Source) → 
2. **Processor** (Transform) → 
3. **Event System** (Distribute) → 
4. **WebSocket** (Real-time) → 
5. **Visualization** (Display)

### Supporting Systems:
- **API System**: Data access interface
- **Persistence**: Historical data
- **Analytics**: Insights generation

This mapping shows that Seneca has most of the infrastructure needed for the core features, but needs to implement:
- Historical data collection and storage
- Basic authentication and rate limiting
- Better integration between real-time and historical data