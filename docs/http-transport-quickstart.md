# Seneca HTTP Transport Quickstart

## Overview

Seneca now supports connecting to Marcus via HTTP transport, providing better reliability and network flexibility compared to stdio transport.

## Quick Start

### 1. Start Marcus with HTTP Transport

```bash
# In Marcus directory
cd /path/to/marcus

# Start with HTTP transport on default port 4298
python run_marcus.py --http

# Or specify custom port
python run_marcus.py --http --port 5000
```

### 2. Configure Seneca

Set environment variables before starting Seneca:

```bash
# Use HTTP transport
export MARCUS_TRANSPORT=http
export MARCUS_HTTP_URL=http://localhost:4298

# Start Seneca
cd /path/to/seneca
python start_seneca.py
```

### 3. Auto Mode (Default)

If you don't set any environment variables, Seneca will:
1. Try HTTP if `MARCUS_HTTP_URL` is set
2. Fall back to stdio if HTTP fails
3. Use auto-discovery for stdio

## Configuration Options

### Environment Variables

```bash
# Transport mode: "http", "stdio", or "auto" (default)
export MARCUS_TRANSPORT=http

# HTTP endpoint URL (required for HTTP mode)
export MARCUS_HTTP_URL=http://localhost:4298

# Other Seneca settings
export MARCUS_LOG_DIR=/path/to/marcus/logs/conversations
export SENECA_PORT=8080
```

### Testing the Connection

1. Start Marcus with HTTP:
   ```bash
   python run_marcus.py --http
   ```
   
   You should see:
   ```
   ====================================================================
       Marcus MCP Server (HTTP Mode)
   ====================================================================
   
   [I] Server URL:    http://127.0.0.1:4298/mcp
   [I] Transport:     HTTP (Streamable)
   [I] Started:       2024-XX-XX XX:XX:XX
   
   [I] Ready to accept connections...
   ```

2. Start Seneca:
   ```bash
   export MARCUS_TRANSPORT=http
   python start_seneca.py
   ```
   
   You should see:
   ```
   ✓ Connected to Marcus via MarcusHttpClient
   ✓ Marcus responded: seneca-2024-XX-XXTXX:XX:XX
   Registered as observer: Client 'seneca-XXXXXXXX' registered as observer
   ```

3. Check health endpoint:
   ```bash
   curl http://localhost:8080/api/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "service": "seneca",
     "marcus_connected": true
   }
   ```

## Benefits of HTTP Transport

1. **Network Flexibility**: Connect across machines
2. **Better Reliability**: Handles interruptions gracefully
3. **Scalability**: Multiple Seneca instances can connect
4. **Security**: Can add HTTPS, authentication headers
5. **Monitoring**: Standard HTTP metrics and logging

## Role-Based Access

Seneca now registers as an "observer" role with Marcus, giving it access to:
- All read-only tools
- Analytics and monitoring tools
- Pipeline visualization tools
- Usage reports

## Troubleshooting

### Connection Failed

1. Check Marcus is running with HTTP:
   ```bash
   ps aux | grep marcus
   # Should show: python run_marcus.py --http
   ```

2. Check port is accessible:
   ```bash
   curl http://localhost:4298/mcp
   # Should return JSON-RPC error (method not allowed)
   ```

3. Check environment variables:
   ```bash
   echo $MARCUS_TRANSPORT
   echo $MARCUS_HTTP_URL
   ```

### Fallback to Stdio

If HTTP connection fails and `MARCUS_TRANSPORT=auto`, Seneca will try stdio. Check logs:
```
Auto mode: HTTP failed, trying stdio transport
```

### Port Conflicts

If port 4298 is in use:
1. Start Marcus on different port:
   ```bash
   python run_marcus.py --http --port 5000
   ```

2. Update Seneca config:
   ```bash
   export MARCUS_HTTP_URL=http://localhost:5000
   ```

## Migration from Stdio

Existing Seneca installations can migrate gradually:

1. **Test**: Set `MARCUS_TRANSPORT=auto` to test both
2. **Verify**: Ensure all features work with HTTP
3. **Switch**: Set `MARCUS_TRANSPORT=http` for HTTP-only
4. **Monitor**: Check for any issues

## Advanced Configuration

### Custom Headers

For authentication or tracking:
```python
# In marcus_http_client.py
headers={
    "Content-Type": "application/json",
    "X-Client-ID": self._client_id,
    "Authorization": "Bearer YOUR_TOKEN"  # If needed
}
```

### Timeout Settings

Adjust in `marcus_http_client.py`:
```python
timeout = ClientTimeout(
    total=30,      # Total timeout
    connect=5,     # Connection timeout
    sock_read=25   # Read timeout
)
```

### Multiple Marcus Instances

Connect to different Marcus instances:
```bash
# Development
export MARCUS_HTTP_URL=http://dev.example.com:4298

# Production
export MARCUS_HTTP_URL=https://prod.example.com/marcus
```

## Next Steps

1. Monitor connection stability
2. Set up HTTPS for production
3. Add authentication if needed
4. Configure reverse proxy for load balancing