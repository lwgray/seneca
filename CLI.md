# Seneca CLI Commands

Seneca provides a simple command-line interface for visualization and analytics.

## Installation

```bash
# Install system-wide
./install.sh

# Or add to PATH manually
export PATH="$PWD:$PATH"
```

## Usage

### Start Seneca

```bash
# Start with auto-discovery
seneca start

# Connect to specific Marcus HTTP endpoint
seneca start --marcus-http http://localhost:4298

# Start on custom port
seneca start --port 8090

# Force stdio transport
seneca start --marcus-stdio

# Run in foreground (see output)
seneca start --foreground
```

### Open in Browser

```bash
# Open dashboard in browser
seneca open
```

### Check Status

```bash
seneca status
```

Output:
```
✅ Seneca is running
   PID: 12346
   CPU: 1.5%
   Memory: 98.7 MB
   Uptime: 0:03:15
   Dashboard: http://localhost:8080
   API Health: http://localhost:8080/api/health
   Marcus: ✅ Connected
```

### View Logs

```bash
# View recent logs (last 50 lines)
seneca logs

# Follow logs in real-time
seneca logs --follow

# Show last 20 lines
seneca logs --tail 20
```

### Stop Seneca

```bash
seneca stop
```

### Configuration

```bash
# View current config
seneca config

# Edit config file
seneca config --edit
```

## Workflow Examples

### Standard Workflow

```bash
# 1. Start Marcus
marcus start --http

# 2. Start Seneca
seneca start

# 3. Open dashboard
seneca open

# 4. When done
seneca stop
marcus stop
```

### Development Workflow

```bash
# Start both in foreground for debugging
marcus start --http --foreground &
seneca start --foreground
```

### Multiple Environments

```bash
# Development
seneca start --marcus-http http://dev.example.com:4298 --port 8080

# Staging
seneca start --marcus-http http://staging.example.com:4298 --port 8081
```

## Environment Variables

Seneca respects these environment variables:

- `MARCUS_TRANSPORT`: Transport mode ("auto", "http", "stdio")
- `MARCUS_HTTP_URL`: Marcus HTTP endpoint
- `SENECA_PORT`: Server port
- `SENECA_HOST`: Server host

## Features

- **Auto-discovery**: Finds running Marcus instances automatically
- **HTTP Transport**: Better reliability than stdio
- **Role-based Access**: Registers as "observer" with Marcus
- **Browser Integration**: Automatically opens dashboard
- **Process Management**: Runs as daemon by default

## Comparison with Other Tools

Similar to popular tools:

- `jupyter lab` - Data science notebooks
- `grafana-server` - Monitoring dashboards  
- `streamlit run` - Data apps
- `flask run` - Web development

Seneca follows standard patterns for visualization platforms.