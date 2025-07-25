#!/usr/bin/env python3
"""
Seneca CLI - Command line interface for Marcus visualization

Usage:
    seneca status          # Check for running Marcus instances
    seneca start           # Start dashboard with auto-discovery
    seneca start --port 8080  # Start on custom port
    seneca logs            # Show recent Marcus logs
"""

import sys
import json
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def discover_marcus_services():
    """Discover running Marcus services"""
    try:
        from pathlib import Path
        import json
        import platform
        import psutil
        import os
        import tempfile
        
        # Get registry directory
        if platform.system() == "Windows":
            base_dir = Path(os.environ.get("APPDATA", tempfile.gettempdir()))
        else:
            base_dir = Path.home()
        
        registry_dir = base_dir / ".marcus" / "services"
        
        if not registry_dir.exists():
            return []
        
        services = []
        
        # Read all service files
        for service_file in registry_dir.glob("marcus_*.json"):
            try:
                with open(service_file, 'r') as f:
                    service_info = json.load(f)
                
                # Check if process is still running
                pid = service_info.get("pid")
                if pid and psutil.pid_exists(pid):
                    services.append(service_info)
                else:
                    # Clean up stale service file
                    service_file.unlink()
                    
            except (json.JSONDecodeError, FileNotFoundError):
                # Clean up invalid service files
                try:
                    service_file.unlink()
                except:
                    pass
        
        return sorted(services, key=lambda x: x.get("started_at", ""))
        
    except Exception as e:
        print(f"Discovery failed: {e}")
        return []


def cmd_status():
    """Show status of Marcus instances"""
    print("🏛️  Seneca Status")
    print("=" * 40)
    
    services = discover_marcus_services()
    
    if not services:
        print("❌ No running Marcus instances found")
        print("\nTo start Marcus:")
        print("  cd ~/dev/marcus")
        print("  python -m src.marcus_mcp.server")
        return
    
    print(f"✅ Found {len(services)} running Marcus instance(s):")
    print()
    
    for i, service in enumerate(services, 1):
        print(f"{i}. Instance: {service['instance_id']}")
        print(f"   PID: {service['pid']}")
        print(f"   Project: {service.get('project_name', 'None')}")
        print(f"   Provider: {service.get('provider', 'Unknown')}")
        print(f"   Logs: {service['log_dir']}")
        print(f"   Started: {service['started_at']}")
        print()


def cmd_start():
    """Start Seneca dashboard"""
    from start_seneca import run_seneca_server
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Seneca dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--marcus-server", help="Specific Marcus server path")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Parse remaining args
    args = parser.parse_args(sys.argv[2:])
    
    run_seneca_server(
        host=args.host,
        port=args.port,
        marcus_server=args.marcus_server,
        debug=args.debug
    )


def cmd_logs():
    """Show recent Marcus logs"""
    from mcp_client.marcus_client import MarcusLogReader
    
    print("📜 Recent Marcus Conversations")
    print("=" * 50)
    
    # Try to find log directory from discovered services
    services = discover_marcus_services()
    log_dir = None
    
    if services:
        log_dir = services[-1]["log_dir"]  # Use most recent
        print(f"Reading from: {log_dir}")
    else:
        # Fallback to default location
        log_dir = "logs/conversations"
        print(f"No running Marcus found, trying: {log_dir}")
    
    print()
    
    try:
        reader = MarcusLogReader(log_dir)
        conversations = reader.read_conversations()
        
        if not conversations:
            print("No conversations found")
            return
        
        # Show last 20 conversations
        recent = conversations[-20:] if len(conversations) > 20 else conversations
        
        for conv in recent:
            timestamp = conv.get('timestamp', '')[:19]  # Just date/time
            source = conv.get('source', conv.get('worker_id', '?'))
            target = conv.get('target', 'marcus')
            message = conv.get('message', conv.get('thought', ''))
            
            # Truncate long messages
            if len(message) > 80:
                message = message[:77] + "..."
            
            # Format nicely
            print(f"{timestamp} {source} → {target}")
            if message:
                print(f"  {message}")
            print()
            
    except Exception as e:
        print(f"Failed to read logs: {e}")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("🏛️  Seneca - Marcus Visualization Platform")
        print()
        print("Usage:")
        print("  seneca status     # Check Marcus instances")
        print("  seneca start      # Start dashboard")
        print("  seneca logs       # Show recent logs")
        print()
        print("Examples:")
        print("  seneca start --port 8080")
        print("  seneca start --marcus-server /path/to/marcus")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        cmd_status()
    elif command == "start":
        cmd_start()
    elif command == "logs":
        cmd_logs()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: status, start, logs")


if __name__ == "__main__":
    main()