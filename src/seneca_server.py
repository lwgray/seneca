"""
Seneca - Marcus Visualization and Analytics Platform

Main server that provides web dashboard and API for Marcus insights.
"""

import asyncio
import logging
import os
from pathlib import Path

from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

# Import Seneca components (moved from Marcus)
from api.conversation_api import conversation_api
from api.agent_management_api import agent_api  
from api.project_management_api import project_api
from api.pipeline_enhancement_api import pipeline_api
from mcp_client import marcus_log_reader, get_marcus_client, initialize_marcus_client


def create_seneca_app():
    """Create and configure Seneca Flask application"""
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../../templates',
                static_folder='../../static')
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "seneca-secret-key")
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    
    # Register API blueprints
    app.register_blueprint(conversation_api)
    app.register_blueprint(agent_api)
    app.register_blueprint(project_api)
    app.register_blueprint(pipeline_api)
    
    # Main dashboard route
    @app.route("/")
    def dashboard():
        """Serve the main Seneca dashboard"""
        return render_template("seneca_dashboard.html")
    
    @app.route("/conversations")
    def conversations():
        """Serve the conversation visualization page"""
        return render_template("conversations.html")
    
    @app.route("/api/health")
    def health_check():
        """Health check endpoint"""
        client = get_marcus_client()
        return {
            "status": "healthy", 
            "service": "seneca",
            "marcus_connected": client.connected if client else False
        }
    
    # WebSocket events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print("Seneca client connected")
        
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print("Seneca client disconnected")
        
    return app, socketio


def run_seneca_server(host="0.0.0.0", port=8000, marcus_server=None, debug=False):
    """
    Run the Seneca server
    
    Parameters
    ----------
    host : str
        Host to bind to
    port : int
        Port to run on
    marcus_server : str, optional
        Path to Marcus MCP server
    debug : bool
        Enable debug mode
    """
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("🏛️  Seneca - Marcus Visualization Platform")
    print("=" * 60)
    print()
    
    # Create Flask app
    app, socketio = create_seneca_app()
    
    # Connect to Marcus if available
    async def connect_to_marcus():
        # Load config for transport settings
        from config import SenecaConfig
        config = SenecaConfig()
        
        success = await initialize_marcus_client(
            transport=config.marcus_transport,
            server_path=marcus_server,
            http_url=config.marcus_http_url,
            auto_discover=True
        )
        
        if success:
            client = get_marcus_client()
            logger.info(f"✓ Connected to Marcus via {type(client).__name__}")
            
            # Test the connection
            try:
                ping_result = await client.ping()
                logger.info(f"✓ Marcus responded: {ping_result.get('echo', 'pong')}")
            except Exception as e:
                logger.warning(f"Ping failed: {e}")
        else:
            logger.warning("✗ Failed to connect to Marcus MCP server")
            logger.info("  Seneca will run in log-only mode")
            logger.info("  Start Marcus first, then restart Seneca for live data")
    
    # Try to connect to Marcus
    try:
        asyncio.run(connect_to_marcus())
    except Exception as e:
        logger.warning(f"Marcus connection failed: {e}")
    
    print(f"📊 Dashboard: http://{host}:{port}")
    print(f"💬 Conversations: http://{host}:{port}/conversations")
    print(f"🔍 API: http://{host}:{port}/api/health")
    print()
    print("Features:")
    print("- Real-time Marcus monitoring")
    print("- Agent conversation visualization")
    print("- Historical analytics from logs")
    print("- Predictive insights")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run the server
    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Seneca...")
        client = get_marcus_client()
        if client and client.connected:
            asyncio.run(client.disconnect())


if __name__ == "__main__":
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