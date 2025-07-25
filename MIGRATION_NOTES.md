# Seneca CLI Migration Notes

## Old vs New Commands

### Previous (Deprecated)
```bash
python start_seneca.py --port 8080
python seneca_cli.py
```

### New (Recommended)
```bash
seneca start --port 8080
seneca open
seneca status
seneca logs
seneca stop
```

## Migrated Files

The following files have been moved to `.old` extensions and are no longer used:

- `start_seneca.py` → `start_seneca.py.old`  
- `seneca_cli.py` → `seneca_cli.py.old`

## Installation

Run the installation script to set up the new CLI:

```bash
./install.sh
```

This installs the `seneca` command to your PATH.

## Benefits of New CLI

1. **Standard Commands**: Follows Unix conventions (`start`, `stop`, `status`)
2. **Process Management**: Proper daemon mode with PID tracking
3. **Browser Integration**: `seneca open` command
4. **Transport Configuration**: Easy HTTP/stdio switching
5. **Marcus Health Checking**: Shows connection status
6. **Better Logging**: Structured log files with timestamps

## HTTP Transport Support

The new CLI fully supports the HTTP transport migration:

```bash
# Connect to Marcus HTTP endpoint
seneca start --marcus-http http://localhost:4298

# Or use environment variables
export MARCUS_TRANSPORT=http
export MARCUS_HTTP_URL=http://localhost:4298
seneca start
```

## Backward Compatibility

The old scripts are preserved as `.old` files in case you need them for reference or emergency use.