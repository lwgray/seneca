# Seneca

> *"The willing, destiny guides them. The unwilling, destiny drags them."* - Seneca

Seneca is a visualization and analytics platform for Marcus, providing wisdom and insights into agent orchestration. Named after the Stoic philosopher and advisor, Seneca offers calm, focused visibility into what matters most.

## Overview

Seneca connects to Marcus as an MCP client, providing:

- **Real-time dashboard** showing agent activity and project status
- **Timeline view** of conversations and decisions
- **Focus mode** highlighting what needs attention
- **Analytics** for performance insights and predictions
- **Historical analysis** from Marcus log files

## Architecture

```
Marcus MCP Server ←── MCP Protocol ──→ Seneca MCP Client
        ↓                                      ↓
   Log Files (.jsonl) ←──── File System ──→ Log Processor
                                             ↓
                                      Seneca Web Dashboard
```

## Quick Start

### Using pip

```bash
# Install Seneca
pip install seneca-viz

# Start the server (requires Marcus logs)
seneca start

# Open dashboard
open http://localhost:8000
```

### Using Docker

```bash
# Run with docker-compose
docker-compose up -d

# Or run directly with Docker
docker run -p 8000:8000 -v ~/.marcus/logs:/logs marcusai/seneca:latest

# Open dashboard
open http://localhost:8000
```

### From Source

```bash
# Clone the repository
git clone https://github.com/marcus-ai/seneca.git
cd seneca

# Install in development mode
make dev-install

# Run the server
make run

# Open dashboard
open http://localhost:8000
```

## Features

### Core (Open Source)
- Agent status monitoring
- Conversation timeline
- Basic analytics
- Log file processing

### Enterprise (Paid)
- Advanced predictions
- Team performance analytics
- Custom dashboards
- Slack/Teams integration
- Cost tracking and ROI analysis

## Design Principles

- **Calm Technology**: Only interrupt when necessary
- **Progressive Disclosure**: Start simple, drill down for details
- **Context Over Data**: Show why something matters
- **Predictive Over Reactive**: Anticipate issues before they happen

## Requirements

- Python 3.8+
- Access to Marcus MCP server
- Marcus log files (for historical data)

## Configuration

### Environment Variables

```bash
# Path to Marcus conversation logs
export MARCUS_LOG_DIR=~/dev/marcus/logs/conversations

# Server configuration
export SENECA_HOST=localhost
export SENECA_PORT=8000

# Logging
export LOG_LEVEL=INFO
```

### Docker Configuration

The Docker setup includes:
- Multi-stage build for smaller images
- Non-root user for security
- Health checks
- Volume mounts for logs
- docker-compose for easy deployment

```bash
# Production deployment
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.dev.yml up

# With mock Marcus for testing
docker-compose -f docker-compose.dev.yml --profile testing up
```

## Development

```bash
# Install development dependencies
make dev-install

# Run tests
make test

# Run with coverage
make test-cov

# Format code
make format

# Run linters
make lint

# Build documentation
make docs
```

## Documentation

Full documentation is available at:
- [Online Documentation](https://seneca.marcus-ai.dev)
- Local: Run `make docs` then open `docs/_build/html/index.html`

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines.

## License

MIT License - See LICENSE file for details 
