#!/usr/bin/env python3
"""
Test Marcus analytics endpoint tools - exact copy of working approach
"""
import json
import asyncio
import httpx

ANALYTICS_ENDPOINT = "http://localhost:4300"

async def test_marcus_analytics():
    """Test Marcus analytics endpoint exactly like the working test"""
    
    print("🔍 Testing Marcus Analytics connection (port 4300)...")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # Initialize MCP session - exact format from working test
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
                        "name": "seneca-analytics-test",
                        "version": "1.0.0"
                    }
                }
            }
            
            print(f"Initializing MCP session at {ANALYTICS_ENDPOINT}/mcp")
            response = await client.post(
                f"{ANALYTICS_ENDPOINT}/mcp",  # No trailing slash like working test
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                },
                timeout=10.0
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            # Extract session ID from headers
            session_id = response.headers.get("mcp-session-id")
            if session_id:
                print(f"Got session ID: {session_id}")
            
            if response.status_code == 200:
                # Parse response exactly like working test
                if response.headers.get('content-type') == 'text/event-stream':
                    print("Handling streaming response...")
                    response_text = response.text
                    print(f"Raw response: {response_text[:200]}...")
                    
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
                
                # Send initialization complete notification - exact format
                await send_initialized_notification(client, session_id)
                
                # Authenticate as observer to get observer tools
                await authenticate_as_observer(client, session_id)
                
                # Now request tools list
                await test_tools_list(client, session_id)
            else:
                print(f"❌ MCP initialization failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

async def send_initialized_notification(client, session_id):
    """Send initialized notification - exact format from working test"""
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
    """Test getting tools list - exact format from working test"""
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
        
        print(f"Tools response status: {response.status_code}")
        print(f"Tools response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Handle streaming response exactly like working test
            if response.headers.get('content-type') == 'text/event-stream':
                response_text = response.text
                print(f"Raw tools response: {response_text[:200]}...")
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('data: ') and line != 'data: ':
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            print(f"✅ Tools list response: {json.dumps(data, indent=2)}")
                            
                            # Count and list tools
                            if "result" in data and "tools" in data["result"]:
                                tools = data["result"]["tools"]
                                print(f"\n🔧 Found {len(tools)} tools:")
                                for i, tool in enumerate(tools, 1):
                                    print(f"  {i:2d}. {tool['name']} - {tool['description']}")
                            break
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                print(f"✅ Tools list response: {json.dumps(data, indent=2)}")
                
                # Count and list tools
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"\n🔧 Found {len(tools)} tools:")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i:2d}. {tool['name']} - {tool['description']}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Tools list error: {e}")

async def authenticate_as_observer(client, session_id):
    """Authenticate as observer to get full tool list"""
    print("\n🔐 Authenticating as observer...")
    
    auth_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "authenticate",
            "arguments": {
                "client_id": "seneca-analytics-test",
                "client_type": "observer",
                "role": "analytics",
                "metadata": {
                    "version": "2.0",
                    "environment": "test"
                }
            }
        }
    }
    
    try:
        response = await client.post(
            f"{ANALYTICS_ENDPOINT}/mcp",
            json=auth_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": session_id
            },
            timeout=10.0
        )
        
        print(f"Authentication status: {response.status_code}")
        if response.status_code == 200:
            if response.headers.get('content-type') == 'text/event-stream':
                response_text = response.text
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('data: ') and line != 'data: ':
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if "result" in data:
                                available_tools = data['result'].get('available_tools', [])
                                print(f"✅ Authenticated as observer with {len(available_tools)} tools")
                                return
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                print(f"✅ Authentication response: {data}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    asyncio.run(test_marcus_analytics())