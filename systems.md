# Seneca Systems Documentation

This document provides a comprehensive overview of all systems, modules, and components in the Seneca codebase.

## Overview

Seneca is a comprehensive visualization and monitoring platform for Marcus AI systems, providing real-time insights into agent communication, project management, and system health through a modern web interface with advanced visualization capabilities.

## Core Systems

### 1. CLI System
- **Location**: `seneca_cli.py:1-300`
- **Purpose**: Command-line interface for managing Seneca
- **Commands**:
  - `status` - Check for running Marcus instances
  - `start` - Start dashboard with auto-discovery
  - `logs` - Show recent Marcus logs

### 2. Flask Server System
- **Location**: `src/seneca_server.py:1-200`
- **Purpose**: Main web server application
- **Features**: REST API endpoints, WebSocket support, static file serving

### 3. Configuration System
- **Location**: `config.py:1-150`
- **Purpose**: Centralized configuration management
- **Features**:
  - Environment variable handling
  - Default settings for paths, server, UI, features, caching, and themes
  - Configuration validation

### 4. Marcus Service Detection System
- **Purpose**: Automatically discover and connect to running Marcus instances
- **Components**:
  - **Service Registry**: File-based registry at `~/.marcus/services/` (Unix/macOS) or `%APPDATA%/.marcus/services/` (Windows)
  - **Discovery Functions**:
    - `discover_marcus_services()` (seneca_cli.py:150-200) - Scans registry for active instances
    - `_discover_marcus_service()` (src/mcp_client/marcus_client.py:100-150) - Client-side discovery
  - **Features**:
    - Process verification using `psutil.pid_exists()`
    - Automatic selection of most recent Marcus instance
    - MCP command extraction from service registry
    - Fallback to log-only mode if no Marcus found
  - **Connection Modes**:
    - Auto-discovery (default): Finds and connects to latest Marcus
    - Manual: Connects to specific instance via `--marcus-server` flag
    - Log-only: Reads historical data when no Marcus is running
  - **No Active Scanning**: Uses passive file-based discovery instead of port scanning

## API Systems

All API modules are located in `src/api/`:

### Core APIs

1. **Conversation API** (`conversation_api.py`)
   - Agent communication visualization endpoints
   - Real-time message streaming
   - Conversation history retrieval

2. **Agent Management API** (`agent_management_api.py`)
   - Agent status monitoring
   - Agent lifecycle management
   - Performance metrics

3. **Project Management API** (`project_management_api.py`)
   - Project creation and configuration
   - Feature management
   - Workflow orchestration

4. **Pipeline Enhancement API** (`pipeline_enhancement_api.py`)
   - Pipeline flow visualization
   - Execution tracking
   - Performance optimization

5. **Cost Tracking API** (`cost_tracking_api.py`)
   - Resource usage analytics
   - Cost estimation and tracking
   - Budget monitoring

6. **Memory Insights API** (`memory_insights_api.py`)
   - Memory usage visualization
   - Knowledge graph insights
   - Context retention analysis

7. **Pattern Learning API** (`pattern_learning_api.py`)
   - Pattern detection in agent behavior
   - Learning algorithm management
   - Insight generation

8. **Context Visualization API** (`context_visualization_api.py`)
   - Context relationship mapping
   - Dependency visualization
   - Impact analysis

### Infrastructure APIs

1. **WebSocket System** (`conversation_websocket.py`)
   - Real-time bidirectional communication
   - Event broadcasting
   - Connection management

2. **Application Setup** (`app.py`)
   - Flask application initialization
   - Middleware configuration
   - Route registration

3. **Async Support** (`async_wrapper.py`)
   - Async/await support for Flask
   - Non-blocking operations
   - Performance optimization

4. **Server Management** (`integrated_server.py`, `marcus_server_singleton.py`)
   - Marcus server connection singleton
   - Connection pooling
   - Failover handling

## Processing Systems

All processors are located in `src/processors/`:

### Core Processors

1. **Conversation Processing**
   - `conversation_processor.py` - Process and analyze conversations
   - `conversation_stream.py` - Real-time conversation streaming
   - `conversation_adapter.py` - Adapt conversation formats

2. **AI Analysis Engine** (`ai_analysis_engine.py`)
   - AI-powered analysis of agent behavior
   - Decision pattern recognition
   - Performance prediction

3. **Decision Visualizer** (`decision_visualizer.py`)
   - Visualize decision-making processes
   - Decision tree generation
   - Impact analysis

4. **Health Monitor** (`health_monitor.py`)
   - System health tracking
   - Project health metrics
   - Alert generation

5. **Knowledge Graph** (`knowledge_graph.py`)
   - Build and manage knowledge graphs
   - Relationship mapping
   - Query optimization

### Pipeline System

1. **Pipeline Manager** (`pipeline_manager.py`)
   - Pipeline flow management
   - Execution orchestration
   - Resource allocation

2. **Pipeline Components**
   - `pipeline_flow.py` - Pipeline execution flows
   - `pipeline_bridge.py` - Bridge between pipeline components
   - `pipeline_conversation_bridge.py` - Connect conversations to pipeline
   - `pipeline_replay.py` - Replay pipeline executions
   - `shared_pipeline_events.py` - Shared event system

### Visualization Systems

1. **Event Visualizer** (`event_integrated_visualizer.py`)
   - Integrated event visualization
   - Timeline generation
   - Event correlation

2. **UI Server** (`ui_server.py`)
   - UI server management
   - Static asset serving
   - Client state synchronization

### Data Models

**Location**: `src/processors/models.py`
- **Enums**: `TaskStatus`, `WorkerStatus`, `RiskLevel`
- **Dataclasses**: `Task`, `Worker`, `ProjectState`

## MCP Client System

**Location**: `src/mcp_client/`

### Marcus Client (`marcus_client.py`)
- MCP (Model Context Protocol) client for Marcus communication
- Features:
  - Service discovery
  - Connection management
  - Real-time data retrieval
  - Session handling
  - Error recovery

## Frontend Systems

**Location**: `src/ui/`

### Technology Stack
- **Framework**: Vue 3 with Vite
- **State Management**: Pinia stores
- **WebSocket**: Socket.io client
- **Visualization**: Vue Flow, D3.js
- **Build System**: Vite with hot module replacement

### Main Components (`src/ui/src/components/`)

1. **Core Components**
   - `ConnectionStatus.vue` - WebSocket connection indicator
   - `EventLog.vue` - Real-time event display
   - `ExecutionControls.vue` - Workflow execution controls
   - `HealthAnalysisPanel.vue` - System health visualization

2. **Canvas Components** (`canvas/`)
   - `WorkflowCanvas.vue` - Main workflow visualization
   - **Node Types**:
     - `DecisionNode.vue` - Decision points in workflow
     - `KanbanNode.vue` - Task board nodes
     - `KnowledgeNode.vue` - Knowledge graph nodes
     - `PMAgentNode.vue` - Project manager nodes
     - `WorkerNode.vue` - Worker agent nodes

3. **Sidebar Components** (`sidebar/`)
   - `FilterPanel.vue` - Event and node filtering
   - `MetricsPanel.vue` - Performance metrics dashboard
   - `NodeDetailsPanel.vue` - Detailed node information
   - `NodePalette.vue` - Draggable node palette for canvas

### State Management (`src/ui/src/stores/`)
- `events.js` - Event management and history
- `websocket.js` - WebSocket connection state
- `workflow.js` - Workflow canvas state and operations

## Template System

**Location**: `templates/`
- `seneca_dashboard.html` - Main dashboard layout
- `conversations.html` - Conversation viewer interface
- `patterns.html` - Pattern analysis interface
- `index.html` - Landing page
- `test.html` - Testing and debugging interface

## Static Assets

**Location**: `static/`
- `css/styles.css` - Global styles and themes
- `js/app.js` - Legacy JavaScript functionality
- `js/conversations.js` - Conversation handling logic

## Infrastructure & Deployment Systems

### Docker Containerization
- `Dockerfile` - Production container configuration
- `Dockerfile.dev` - Development container with hot reload
- `docker-compose.yml` - Production orchestration
- `docker-compose.dev.yml` - Development orchestration

### Build Automation
**Location**: `Makefile`
- Installation targets
- Testing and linting
- Documentation generation
- Docker build and deployment
- CI/CD helper targets

### Package Management
- `setup.py` - Python package configuration
- `requirements.txt` - Python dependencies
- `package.json` - Frontend dependencies

## Documentation System

**Location**: `docs/`
- Sphinx-based documentation
- API documentation generation
- Architecture guides
- Installation and setup guides
- Developer documentation

## Testing Framework

**Location**: `tests/`

### Unit Tests (`unit/`)
- `test_conversation_processor.py` - Conversation processing tests
- `HealthAnalysisPanel.spec.js` - Vue component tests

### Integration Tests (`integration/`)
- End-to-end workflow tests
- API integration tests
- WebSocket communication tests

## Key Features & Capabilities

### Real-time Monitoring
- WebSocket-based live updates
- Agent status tracking
- Task progress visualization
- Decision flow visualization
- Event streaming

### Analytics & Insights
- Conversation analysis
- Pattern detection
- Cost tracking
- Performance metrics
- Health monitoring
- Predictive analytics

### Marcus Integration
- MCP client for direct communication
- Log file reading for historical data
- Service discovery for running instances
- Real-time event streaming
- Bidirectional data flow

### Visualization Capabilities
- Interactive workflow canvas
- Node-based agent representation
- Real-time event logs
- Metrics dashboards
- Knowledge graph visualization
- Decision tree display

### Configuration & Environment
- Environment variable support
- Theme management (dark/light modes)
- Caching configuration
- Feature flags for component control
- Multi-environment support

## Security Features
- Authentication support
- Session management
- Secure WebSocket connections
- Input validation
- Rate limiting

## Performance Optimization
- Caching system
- Lazy loading
- Connection pooling
- Resource management
- Background task processing

## Extensibility
- Plugin architecture
- Custom node types
- API extensions
- Theme customization
- Component modularity