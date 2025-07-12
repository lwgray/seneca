# Seneca Setup Guide

## Quick Start

Seneca is the open-source visualization platform for Marcus. It provides real-time visualization of agent conversations, decision-making processes, and system analytics.

### Prerequisites

- Python 3.8+
- Node.js 16+ (for UI development)
- Marcus installed and running
- Access to Marcus log directory

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/seneca.git
   cd seneca
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Marcus log directory**
   
   Seneca needs to know where Marcus stores its conversation logs. Set the `MARCUS_LOG_DIR` environment variable:
   
   ```bash
   # Option 1: Export in your shell
   export MARCUS_LOG_DIR="/path/to/marcus/logs/conversations"
   
   # Option 2: Create a .env file
   echo "MARCUS_LOG_DIR=/path/to/marcus/logs/conversations" > .env
   ```
   
   Default locations checked:
   - `~/dev/marcus/logs/conversations`
   - `../marcus/logs/conversations` (relative to Seneca)

4. **Start Seneca**
   ```bash
   python start_seneca.py
   ```
   
   Seneca will start on http://localhost:8080

### Configuration Options

All configuration can be set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MARCUS_LOG_DIR` | `~/dev/marcus/logs/conversations` | Path to Marcus conversation logs |
| `SENECA_HOST` | `0.0.0.0` | Server host address |
| `SENECA_PORT` | `8080` | Server port |
| `SENECA_DEBUG` | `false` | Enable debug mode |
| `UI_REFRESH_INTERVAL` | `1000` | UI refresh interval in milliseconds |
| `MAX_CONVERSATIONS_DISPLAY` | `100` | Maximum conversations to display |
| `ENABLE_WEBSOCKET` | `true` | Enable real-time updates |
| `ENABLE_ANALYTICS` | `true` | Enable analytics features |
| `ENABLE_EXPORT` | `true` | Enable data export |

### Verifying Setup

1. **Check Marcus logs exist**
   ```bash
   ls $MARCUS_LOG_DIR
   # Should show .jsonl files
   ```

2. **Test API endpoint**
   ```bash
   curl http://localhost:8080/api/conversations/recent
   ```

3. **Access UI**
   Open http://localhost:8080 in your browser

### Troubleshooting

**"Marcus log directory not found"**
- Ensure Marcus has been run at least once to create logs
- Check the MARCUS_LOG_DIR path is correct
- Make sure you have read permissions

**"No conversations found"**
- Run Marcus and perform some operations to generate logs
- Check log files are in JSONL format
- Verify file permissions

**Port already in use**
- Change port: `export SENECA_PORT=8081`
- Or stop the conflicting service

### Development Setup

For UI development with hot reload:

```bash
# Install UI dependencies
cd ui
npm install

# Run development server
npm run dev
```

### Docker Setup

```bash
# Build image
docker build -t seneca .

# Run container
docker run -p 8080:8080 \
  -v /path/to/marcus/logs:/logs:ro \
  -e MARCUS_LOG_DIR=/logs \
  seneca
```

### Next Steps

- Configure authentication (Enterprise feature in Zeno)
- Set up team collaboration (Enterprise feature in Zeno)
- Integrate with CI/CD pipelines
- Customize visualizations

For enterprise features including cloud deployment, ML insights, and team collaboration, consider upgrading to Zeno.