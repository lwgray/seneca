"""
Seneca HTTP Client for connecting to Marcus

This module provides an HTTP-based MCP client that connects to Marcus
when it's running in HTTP transport mode.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import aiohttp
from aiohttp import ClientTimeout

logger = logging.getLogger(__name__)


class MCPError(Exception):
    """MCP protocol error"""
    pass


class MarcusHTTPClient:
    """
    HTTP-based MCP client for connecting to Marcus server
    
    Provides methods to query Marcus for real-time data including
    agent status, project information, and conversations via HTTP.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Marcus HTTP client
        
        Parameters
        ----------
        base_url : Optional[str]
            Base URL for Marcus HTTP endpoint. If None, uses discovery.
        """
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self._client_id = f"seneca-{uuid.uuid4().hex[:8]}"
        self._registered = False
        
    async def connect(self, auto_discover: bool = True) -> bool:
        """
        Connect to Marcus HTTP server
        
        Parameters
        ----------
        auto_discover : bool
            If True, try to discover Marcus HTTP endpoint
        
        Returns
        -------
        bool
            True if connection successful
        """
        # Use provided URL or try discovery
        if not self.base_url:
            if auto_discover:
                discovered = self._discover_http_endpoint()
                if discovered:
                    self.base_url = discovered
                    logger.info(f"Discovered Marcus HTTP endpoint: {self.base_url}")
                else:
                    # Default to localhost
                    self.base_url = "http://localhost:4298"
                    logger.info(f"Using default Marcus HTTP endpoint: {self.base_url}")
            else:
                logger.error("No Marcus HTTP URL provided")
                return False
        
        try:
            # Create session with timeout
            timeout = ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection with ping
            result = await self.ping()
            if result:
                self.connected = True
                logger.info(f"Connected to Marcus HTTP server at {self.base_url}")
                
                # Register as observer
                await self._register_as_observer()
                
                return True
            else:
                logger.error("Failed to ping Marcus HTTP server")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Marcus HTTP: {e}")
            if self.session:
                await self.session.close()
            return False
    
    async def authenticate(self, client_id: str, client_type: str, role: str) -> Dict[str, Any]:
        """
        Authenticate with Marcus server.
        
        Parameters
        ----------
        client_id : str
            Client identifier
        client_type : str
            Type of client (observer, agent, etc.)
        role : str
            Role for the client
            
        Returns
        -------
        Dict[str, Any]
            Authentication result
        """
        try:
            result = await self.call_tool("authenticate", {
                "client_id": client_id,
                "client_type": client_type,
                "role": role,
                "metadata": {
                    "tool": "seneca",
                    "version": "2.0",
                    "transport": "http"
                }
            })
            
            if result and result.get("success"):
                self._registered = True
                logger.info(f"Authenticated as {client_type}: {result.get('message')}")
                logger.debug(f"Available tools: {result.get('available_tools', [])}")
            
            return result or {}
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {"success": False, "error": str(e)}

    async def _register_as_observer(self) -> None:
        """Register Seneca as an observer client with Marcus"""
        try:
            result = await self.authenticate(self._client_id, "observer", "analytics")
            
            if not result.get("success"):
                logger.warning("Failed to register as observer, continuing with limited access")
                
        except Exception as e:
            logger.warning(f"Failed to register with Marcus: {e}")
    
    def _discover_http_endpoint(self) -> Optional[str]:
        """
        Discover Marcus HTTP endpoint from service registry
        
        Returns
        -------
        Optional[str]
            HTTP endpoint URL if found
        """
        service_dir = Path.home() / ".marcus" / "services"
        if not service_dir.exists():
            return None
        
        # Look for service files
        for service_file in service_dir.glob("marcus_*.json"):
            try:
                with open(service_file, 'r') as f:
                    service_info = json.load(f)
                    
                # Check for HTTP endpoint
                if "http_endpoint" in service_info:
                    return service_info["http_endpoint"]
                    
            except Exception as e:
                logger.debug(f"Failed to read service file {service_file}: {e}")
                
        return None
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict] = None) -> Any:
        """
        Call an MCP tool via HTTP
        
        Parameters
        ----------
        tool_name : str
            Name of the tool to call
        arguments : Optional[Dict]
            Tool arguments
        
        Returns
        -------
        Any
            Tool result
        """
        if not self.session:
            raise RuntimeError("Not connected to Marcus")
        
        # Prepare JSON-RPC request
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            },
            "id": str(uuid.uuid4())
        }
        
        try:
            # Make HTTP request
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Client-ID": self._client_id
                }
            ) as response:
                # Check HTTP status
                response.raise_for_status()
                
                # Parse JSON-RPC response
                result = await response.json()
                
                # Check for JSON-RPC error
                if "error" in result:
                    error = result["error"]
                    raise MCPError(f"{error.get('message', 'Unknown error')} (code: {error.get('code')})")
                
                # Extract result
                if "result" in result:
                    # MCP tools return content array
                    content = result["result"].get("content", [])
                    if content and len(content) > 0:
                        # Return the text content
                        text_content = content[0].get("text", "{}")
                        # Try to parse as JSON
                        try:
                            return json.loads(text_content)
                        except json.JSONDecodeError:
                            return text_content
                    
                return None
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            raise MCPError(f"HTTP error: {e}")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def ping(self) -> Dict[str, Any]:
        """Test connection to Marcus"""
        try:
            return await self.call_tool("ping", {"echo": f"seneca-{datetime.now().isoformat()}"})
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return {}
    
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of registered agents"""
        result = await self.call_tool("list_registered_agents")
        return result.get("agents", []) if result else []
    
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        return await self.call_tool("get_agent_status", {"agent_id": agent_id}) or {}
    
    async def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        return await self.call_tool("get_project_status") or {}
    
    async def register_agent(self, agent_id: str, name: str, role: str, skills: List[str] = None) -> Dict[str, Any]:
        """Register a new agent"""
        return await self.call_tool("register_agent", {
            "agent_id": agent_id,
            "name": name,
            "role": role,
            "skills": skills or []
        }) or {}
    
    async def request_next_task(self, agent_id: str) -> Dict[str, Any]:
        """Request next task for an agent"""
        return await self.call_tool("request_next_task", {"agent_id": agent_id}) or {}
    
    async def report_task_progress(self, agent_id: str, task_id: str, status: str, progress: int = 0, message: str = "") -> Dict[str, Any]:
        """Report task progress"""
        return await self.call_tool("report_task_progress", {
            "agent_id": agent_id,
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message
        }) or {}
    
    async def report_blocker(self, agent_id: str, task_id: str, blocker_description: str, severity: str = "medium") -> Dict[str, Any]:
        """Report a task blocker"""
        return await self.call_tool("report_blocker", {
            "agent_id": agent_id,
            "task_id": task_id,
            "blocker_description": blocker_description,
            "severity": severity
        }) or {}
    
    async def create_project(self, description: str, project_name: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new project"""
        return await self.call_tool("create_project", {
            "description": description,
            "project_name": project_name,
            "options": options
        }) or {}
    
    async def get_usage_report(self, days: int = 7) -> Dict[str, Any]:
        """Get usage analytics report (observer role required)"""
        return await self.call_tool("get_usage_report", {"days": days}) or {}
    
    async def disconnect(self):
        """Disconnect from Marcus"""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
        logger.info("Disconnected from Marcus HTTP server")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()