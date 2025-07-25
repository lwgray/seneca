#!/usr/bin/env python3
"""
Start Seneca - Marcus Visualization Platform
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    from seneca_server import run_seneca_server
    import argparse
    
    parser = argparse.ArgumentParser(description="Seneca - Marcus Visualization Platform")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")  
    parser.add_argument("--marcus-server", help="Path to Marcus MCP server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    run_seneca_server(
        host=args.host,
        port=args.port,
        marcus_server=args.marcus_server,
        debug=args.debug
    )