"""
Seneca MCP Client for connecting to Marcus

This module provides the core MCP client that connects to Marcus
to retrieve real-time data for visualization and analytics.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


logger = logging.getLogger(__name__)


class MarcusClient:
    """
    MCP client for connecting to Marcus server
    
    Provides methods to query Marcus for real-time data including
    agent status, project information, and conversations.
    """
    
    def __init__(self, server_path: Optional[str] = None):
        """
        Initialize Marcus MCP client
        
        Parameters
        ----------
        server_path : Optional[str]
            Path to Marcus MCP server script. If None, uses default.
        """
        self.server_path = server_path or "marcus"
        self.session: Optional[ClientSession] = None
        self.connected = False
        
    async def connect(self, auto_discover: bool = True) -> bool:
        """
        Connect to Marcus MCP server
        
        Parameters
        ----------
        auto_discover : bool
            If True, try to discover running Marcus instances first
        
        Returns
        -------
        bool
            True if connection successful
        """
        
        # Try auto-discovery first
        if auto_discover and not self.server_path:
            discovered_service = self._discover_marcus_service()
            if discovered_service:
                self.server_path = discovered_service["mcp_command"]
                logger.info(f"Discovered Marcus service: {discovered_service['instance_id']}")
        
        if not self.server_path:
            logger.error("No Marcus server path specified and no running instances found")
            return False
        
        try:
            # Parse command if it's a full command string
            if " " in self.server_path:
                command_parts = self.server_path.split()
                command = command_parts[0]
                args = command_parts[1:]
            else:
                command = self.server_path
                args = []
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=None
            )
            
            # Connect via stdio
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    self.connected = True
                    
                    # Initialize the connection
                    await session.initialize()
                    
                    # Send initial ping to identify as Seneca
                    await self.ping()
                    
                    logger.info("Connected to Marcus MCP server")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to connect to Marcus: {e}")
            self.connected = False
            return False
            
    def _discover_marcus_service(self) -> Optional[Dict[str, Any]]:
        """
        Discover running Marcus services
        
        Returns
        -------
        Optional[Dict[str, Any]]
            Service info for preferred Marcus instance, or None
        """
        try:
            from pathlib import Path
            import json
            import platform
            import psutil
            
            # Get registry directory
            if platform.system() == "Windows":
                import tempfile
                import os
                base_dir = Path(os.environ.get("APPDATA", tempfile.gettempdir()))
            else:
                base_dir = Path.home()
            
            registry_dir = base_dir / ".marcus" / "services"
            
            if not registry_dir.exists():
                return None
            
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
            
            # Return most recently started service
            if services:
                return sorted(services, key=lambda x: x.get("started_at", ""))[-1]
            
            return None
            
        except Exception as e:
            logger.warning(f"Service discovery failed: {e}")
            return None
            
    async def disconnect(self):
        """Disconnect from Marcus MCP server"""
        if self.session:
            self.connected = False
            self.session = None
            logger.info("Disconnected from Marcus MCP server")
            
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a tool on Marcus MCP server
        
        Parameters
        ----------
        tool_name : str
            Name of the tool to call
        arguments : Dict[str, Any], optional
            Arguments to pass to the tool
            
        Returns
        -------
        Dict[str, Any]
            Tool response
        """
        if not self.connected or not self.session:
            raise ConnectionError("Not connected to Marcus server")
            
        try:
            result = await self.session.call_tool(tool_name, arguments or {})
            return result.content[0].text if result.content else {}
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} - {e}")
            return {"error": str(e)}
    
    # Convenience methods for common Marcus operations
    
    async def get_project_status(self) -> Dict[str, Any]:
        """Get current project status from Marcus"""
        return await self.call_tool("get_project_status")
        
    async def list_registered_agents(self) -> List[Dict[str, Any]]:
        """Get list of registered agents"""
        result = await self.call_tool("list_registered_agents")
        return result.get("agents", [])
        
    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of specific agent"""
        return await self.call_tool("get_agent_status", {"agent_id": agent_id})
        
    async def get_conversations(self, limit: int = 100, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        args = {"limit": limit}
        if agent_id:
            args["agent_id"] = agent_id
        result = await self.call_tool("get_conversations", args)
        return result.get("conversations", [])
        
    async def ping(self) -> Dict[str, Any]:
        """Ping Marcus to check connectivity and identify as Seneca"""
        return await self.call_tool("ping", {"echo": "seneca_client"})


class MarcusLogReader:
    """
    Reader for Marcus log files
    
    Provides access to historical data from Marcus logs
    for analytics and trend analysis.
    """
    
    def __init__(self, log_dir: str = "logs/conversations"):
        """
        Initialize log reader
        
        Parameters
        ----------
        log_dir : str
            Directory containing Marcus log files
        """
        self.log_dir = Path(log_dir)
        
    def read_conversations(self, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]:
        """
        Read conversations from log files
        
        Parameters
        ----------
        start_time : datetime, optional
            Start time for filtering
        end_time : datetime, optional
            End time for filtering
            
        Returns
        -------
        List[Dict[str, Any]]
            List of conversation records
        """
        conversations = []
        
        # Find all conversation log files
        log_files = list(self.log_dir.glob("conversations_*.jsonl"))
        log_files.extend(list(self.log_dir.glob("realtime_*.jsonl")))
        
        for log_file in sorted(log_files):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                record = json.loads(line.strip())
                                
                                # Filter by time if specified
                                if start_time or end_time:
                                    record_time = datetime.fromisoformat(record.get('timestamp', ''))
                                    if start_time and record_time < start_time:
                                        continue
                                    if end_time and record_time > end_time:
                                        continue
                                
                                conversations.append(record)
                            except json.JSONDecodeError:
                                continue
            except FileNotFoundError:
                continue
                
        return conversations
        
    def get_recent_decisions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent PM decisions from logs"""
        conversations = self.read_conversations()
        decisions = [
            conv for conv in conversations 
            if conv.get('event') == 'pm_decision' or conv.get('type') == 'pm_decision'
        ]
        return decisions[-limit:] if decisions else []
        
    def get_agent_activity(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get agent activity from logs"""
        conversations = self.read_conversations()
        if agent_id:
            return [
                conv for conv in conversations
                if conv.get('worker_id') == agent_id or conv.get('source') == agent_id
            ]
        return conversations


# Global client instance
marcus_client = MarcusClient()
marcus_log_reader = MarcusLogReader()