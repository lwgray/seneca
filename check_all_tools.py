#!/usr/bin/env python3
"""
Check all available tools from Marcus analytics endpoint
"""
import json
import asyncio
import httpx

ANALYTICS_ENDPOINT = "http://localhost:4300"

async def get_all_tools():
    """Get complete list of tools from Marcus analytics endpoint"""
    
    print("🔍 Getting complete tools list from Marcus analytics endpoint...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Initialize MCP session
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                    "clientInfo": {"name": "seneca-tools-checker", "version": "1.0.0"}
                }
            }
            
            response = await client.post(
                f"{ANALYTICS_ENDPOINT}/mcp/",
                json=init_request,
                headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
                timeout=10.0
            )
            
            session_id = response.headers.get("mcp-session-id")
            if not session_id:
                print("❌ No session ID received")
                return
            
            print(f"✅ Session ID: {session_id}")
            
            # Send initialized notification
            await client.post(
                f"{ANALYTICS_ENDPOINT}/mcp/",
                json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                headers={"Content-Type": "application/json", "mcp-session-id": session_id},
                timeout=10.0
            )
            
            # Get tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                f"{ANALYTICS_ENDPOINT}/mcp/",
                json=tools_request,
                headers={"Content-Type": "application/json", "mcp-session-id": session_id},
                timeout=10.0
            )
            
            if response.status_code == 200:
                if response.headers.get('content-type') == 'text/event-stream':
                    lines = response.text.split('\n')
                    for line in lines:
                        if line.startswith('data: ') and line != 'data: ':
                            try:
                                data = json.loads(line[6:])
                                if "result" in data and "tools" in data["result"]:
                                    tools = data["result"]["tools"]
                                    print(f"\n🔧 Found {len(tools)} tools:")
                                    for i, tool in enumerate(tools, 1):
                                        print(f"  {i:2d}. {tool['name']} - {tool['description']}")
                                    return len(tools)
                            except json.JSONDecodeError:
                                continue
                else:
                    data = response.json()
                    if "result" in data and "tools" in data["result"]:
                        tools = data["result"]["tools"] 
                        print(f"\n🔧 Found {len(tools)} tools:")
                        for i, tool in enumerate(tools, 1):
                            print(f"  {i:2d}. {tool['name']} - {tool['description']}")
                        return len(tools)
            
            print(f"❌ Failed to get tools: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_all_tools())