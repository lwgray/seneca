#!/usr/bin/env python3
"""
Test Marcus analytics endpoint connectivity and tools
"""
import json
import asyncio
import httpx
from datetime import datetime

# Test Marcus analytics endpoint (port 4300)
ANALYTICS_ENDPOINT = "http://localhost:4300"

async def test_marcus_analytics():
    """Test Marcus analytics MCP connection and tools"""
    
    print("🔍 Testing Marcus Analytics connection (port 4300)...")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # Initialize MCP session
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {
                            "listChanged": True
                        },
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "seneca-analytics-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print(f"Initializing MCP session at {ANALYTICS_ENDPOINT}/mcp")
            response = await client.post(
                f"{ANALYTICS_ENDPOINT}/mcp",
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=10.0
            )
            
            print(f"Response status: {response.status_code}")
            session_id = response.headers.get("mcp-session-id")
            if session_id:
                print(f"Got session ID: {session_id}")
            
            if response.status_code == 200:
                # Handle streaming response (Server-Sent Events)
                if response.headers.get('content-type') == 'text/event-stream':
                    print("Handling streaming response...")
                    response_text = response.text
                    
                    # Parse SSE format
                    lines = response_text.split('\n')
                    for line in lines:
                        if line.startswith('data: ') and line != 'data: ':
                            data_str = line[6:]  # Remove 'data: ' prefix
                            try:
                                data = json.loads(data_str)
                                print(f"✅ MCP initialization response received")
                                break
                            except json.JSONDecodeError:
                                continue
                else:
                    data = response.json()
                    print(f"✅ MCP initialization response received")
                
                # Send initialized notification
                await send_initialized_notification(client, session_id)
                
                # Now request tools list  
                await test_tools_list(client, session_id)
            else:
                print(f"❌ MCP initialization failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

async def send_initialized_notification(client, session_id):
    """Send initialized notification to complete MCP handshake"""
    print("\n📢 Sending initialized notification...")
    
    initialized_request = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    
    try:
        response = await client.post(
            f"{ANALYTICS_ENDPOINT}/mcp",
            json=initialized_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            },
            timeout=10.0
        )
        
        print(f"Initialized notification status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Initialized notification error: {e}")

async def test_tools_list(client, session_id):
    """Test getting tools list from analytics endpoint"""
    print("\n🔧 Testing tools list...")
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = await client.post(
            f"{ANALYTICS_ENDPOINT}/mcp",
            json=tools_request,
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
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if "result" in data and "tools" in data["result"]:
                                tools = data["result"]["tools"]
                                print(f"✅ Found {len(tools)} tools in analytics endpoint:")
                                for i, tool in enumerate(tools[:5], 1):  # Show first 5
                                    print(f"  {i}. {tool['name']} - {tool['description']}")
                                if len(tools) > 5:
                                    print(f"  ... and {len(tools) - 5} more tools")
                                return tools
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"✅ Found {len(tools)} tools in analytics endpoint")
                    return tools
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    return []

if __name__ == "__main__":
    asyncio.run(test_marcus_analytics())