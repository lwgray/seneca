"""
Simple Marcus MCP Client for Seneca.

Direct MCP protocol implementation that we know works with Marcus analytics endpoint.
"""

import json
import logging
import asyncio
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SimpleMarcusClient:
    """
    Simple MCP client that connects directly to Marcus analytics endpoint.
    
    Uses the MCP protocol over HTTP that we tested and confirmed works.
    """
    
    def __init__(self, base_url: str = "http://localhost:4300"):
        """Initialize the simple Marcus client."""
        self.base_url = base_url
        self.session_id = None
        self.request_id = 1
        
    async def connect_and_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to Marcus and call a tool in one operation.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result or error information
        """
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Step 1: Initialize MCP session
                session_id = await self._initialize_session(client)
                if not session_id:
                    return {"success": False, "error": "Failed to initialize MCP session"}
                
                # Step 2: Send initialized notification
                await self._send_initialized(client, session_id)
                
                # Step 3: Call the tool
                return await self._call_tool(client, session_id, tool_name, arguments)
                
        except Exception as e:
            logger.error(f"Error in connect_and_call_tool: {e}")
            return {"success": False, "error": str(e)}
    
    async def _initialize_session(self, client) -> Optional[str]:
        """Initialize MCP session and return session ID."""
        init_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "seneca-analytics-client",
                    "version": "1.0.0"
                }
            }
        }
        self.request_id += 1
        
        try:
            response = await client.post(
                f"{self.base_url}/mcp/",
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                session_id = response.headers.get("mcp-session-id")
                if session_id:
                    logger.info(f"Initialized MCP session: {session_id}")
                    return session_id
                    
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            
        return None
    
    async def _send_initialized(self, client, session_id: str):
        """Send initialized notification to complete handshake."""
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        try:
            await client.post(
                f"{self.base_url}/mcp/",
                json=initialized_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=10.0
            )
        except Exception as e:
            logger.warning(f"Failed to send initialized notification: {e}")
    
    async def _call_tool(self, client, session_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a Marcus tool and return the result."""
        tool_request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self.request_id += 1
        
        try:
            response = await client.post(
                f"{self.base_url}/mcp/",
                json=tool_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                    "mcp-session-id": session_id
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                # Handle streaming response
                if response.headers.get('content-type') == 'text/event-stream':
                    response_text = response.text
                    lines = response_text.split('\n')
                    for line in lines:
                        if line.startswith('data: ') and line != 'data: ':
                            data_str = line[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(data_str)
                                if "result" in data:
                                    # Extract the actual result from MCP response
                                    result = data["result"]
                                    if "content" in result and len(result["content"]) > 0:
                                        # Parse the text content
                                        text_content = result["content"][0].get("text", "")
                                        try:
                                            parsed_result = json.loads(text_content)
                                            return parsed_result
                                        except json.JSONDecodeError:
                                            return {"success": True, "data": text_content}
                                    return {"success": True, "data": result}
                                break
                            except json.JSONDecodeError:
                                continue
                else:
                    data = response.json()
                    if "result" in data:
                        return {"success": True, "data": data["result"]}
            
            return {"success": False, "error": f"Tool call failed with status {response.status_code}"}
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"success": False, "error": str(e)}