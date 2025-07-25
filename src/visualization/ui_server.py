"""
Visualization UI Server for Marcus monitoring.

This provides a web-based UI for monitoring Marcus operations with 
real-time agent conversations, task progress, and system metrics.
"""

import asyncio
import json
import logging
import aiohttp
import aiohttp_cors
import socketio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VisualizationServer:
    """
    Web UI server for Marcus monitoring and visualization.
    
    Provides real-time monitoring of:
    - Agent conversations
    - Task progress 
    - System metrics
    - Pipeline flows
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize the visualization server."""
        self.host = host
        self.port = port
        self.app = None
        self.sio = None
        self.runner = None
        self.site = None
        
        # Server state
        self.connected_clients = set()
        self.marcus_client = None
        
        # Setup templates
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None
        )
        
    async def setup(self):
        """Setup the aiohttp application and socket.io server."""
        # Create Socket.IO server
        self.sio = socketio.AsyncServer(
            async_mode='aiohttp',
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False
        )
        
        # Create aiohttp application
        self.app = aiohttp.web.Application()
        
        # Attach Socket.IO to the app
        self.sio.attach(self.app)
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Setup routes
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/dashboard', self.dashboard_handler)
        self.app.router.add_get('/api/status', self.status_handler)
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
            
        # Setup Socket.IO event handlers
        self.setup_socketio_handlers()
        
    def setup_socketio_handlers(self):
        """Setup Socket.IO event handlers."""
        
        @self.sio.event
        async def connect(sid, environ):
            """Handle client connection."""
            self.connected_clients.add(sid)
            logger.info(f"Client {sid} connected. Total clients: {len(self.connected_clients)}")
            
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection."""
            self.connected_clients.discard(sid)
            logger.info(f"Client {sid} disconnected. Total clients: {len(self.connected_clients)}")
            
        @self.sio.event
        async def subscribe_conversations(sid, data):
            """Subscribe client to conversation updates."""
            try:
                await self.sio.enter_room(sid, 'conversations')
                await self.sio.emit('subscription_confirmed', {'type': 'conversations'}, room=sid)
            except Exception as e:
                logger.error(f"Error subscribing to conversations: {e}")
                
        @self.sio.event
        async def subscribe_metrics(sid, data):
            """Subscribe client to metrics updates."""
            try:
                await self.sio.enter_room(sid, 'metrics')
                await self.sio.emit('subscription_confirmed', {'type': 'metrics'}, room=sid)
            except Exception as e:
                logger.error(f"Error subscribing to metrics: {e}")
    
    async def index_handler(self, request):
        """Handle index page request."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Marcus Visualization Server</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 20px; background: #f0f8ff; border-radius: 5px; margin: 20px 0; }
                .nav { margin: 20px 0; }
                .nav a { margin-right: 20px; text-decoration: none; color: #0066cc; }
                .nav a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Marcus Visualization Server</h1>
                <div class="status">
                    <p><strong>Status:</strong> Running on {host}:{port}</p>
                    <p><strong>Connected clients:</strong> {clients}</p>
                </div>
                <div class="nav">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/api/status">API Status</a>
                </div>
                <h2>Features</h2>
                <ul>
                    <li>Real-time agent conversation monitoring</li>
                    <li>Task progress visualization</li>
                    <li>System metrics dashboard</li>
                    <li>Pipeline flow tracking</li>
                </ul>
            </div>
        </body>
        </html>
        """.format(host=self.host, port=self.port, clients=len(self.connected_clients))
        
        return aiohttp.web.Response(text=html_content, content_type='text/html')
    
    async def dashboard_handler(self, request):
        """Handle dashboard page request."""
        # For now, return a simple dashboard
        # In production, this would render a full React/Vue dashboard
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Marcus Dashboard</title>
            <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
        </head>
        <body>
            <h1>Marcus Analytics Dashboard</h1>
            <div id="status">Connecting...</div>
            <div id="metrics"></div>
            <script>
                const socket = io();
                socket.on('connect', () => {
                    document.getElementById('status').textContent = 'Connected';
                    socket.emit('subscribe_metrics', {});
                });
                socket.on('metrics_update', (data) => {
                    document.getElementById('metrics').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                });
            </script>
        </body>
        </html>
        """
        return aiohttp.web.Response(text=html_content, content_type='text/html')
    
    async def status_handler(self, request):
        """Handle status API request."""
        status = {
            "server": "running",
            "host": self.host,
            "port": self.port,
            "connected_clients": len(self.connected_clients),
            "uptime": "unknown"  # Could track actual uptime
        }
        return aiohttp.web.json_response(status)
    
    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """Broadcast metrics to all connected clients."""
        if self.connected_clients:
            await self.sio.emit('metrics_update', metrics, room='metrics')
    
    async def broadcast_conversation(self, conversation: Dict[str, Any]):
        """Broadcast conversation update to subscribed clients."""
        if self.connected_clients:
            await self.sio.emit('conversation_update', conversation, room='conversations')
    
    async def start(self):
        """Start the visualization server."""
        await self.setup()
        
        self.runner = aiohttp.web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = aiohttp.web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        logger.info(f"Visualization server started on http://{self.host}:{self.port}")
        print(f"Access the dashboard at: http://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the visualization server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Visualization server stopped")