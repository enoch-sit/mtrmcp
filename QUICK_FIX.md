# Quick Fix for MCP Inspector Connection

## The Problem

Your `/mcp/sse` endpoint sends:
```
data: {"type": "connection", ...}    ← Custom format ❌
data: {"type": "heartbeat", ...}     ← Custom format ❌
```

MCP Inspector expects:
```
event: endpoint                      ← MCP standard ✅
data: /mcp/messages/?session_id=123

event: message                       ← MCP standard ✅  
data: {"jsonrpc":"2.0",...}
```

## The Fix

Replace your SSE endpoint in `fastapi_mcp_integration.py`:

### BEFORE (Lines 199-239):

```python
@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for MCP Inspector"""
    
    async def event_stream():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected', 'server': 'mtr_next_train'})}\n\n"
        
        # Keep connection alive and send periodic heartbeats
        while True:
            try:
                # Check if client is still connected
                if await request.is_disconnected():
                    break
                
                # Send heartbeat
                heartbeat = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running" if mcp_manager.is_running else "stopped"
                }
                yield f"data: {json.dumps(heartbeat)}\n\n"
                
                # Wait before next heartbeat
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
```

### AFTER (MCP-Compatible):

```python
import uuid

# Add this at the top of the file (after imports)
active_sessions = {}  # Store active SSE sessions

@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for MCP Inspector - MCP Protocol Compatible"""
    
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {"created": datetime.now(), "active": True}
    
    async def event_stream():
        try:
            # MCP REQUIRED: Send endpoint event first
            endpoint_path = f"/mcp/messages/?session_id={session_id}"
            yield f"event: endpoint\ndata: {endpoint_path}\n\n"
            logger.info(f"SSE session {session_id}: sent endpoint event")
            
            # Keep connection alive with heartbeats as JSON-RPC notifications
            heartbeat_count = 0
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    logger.info(f"SSE session {session_id}: client disconnected")
                    break
                
                # Send heartbeat as MCP notification (optional)
                heartbeat_count += 1
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {
                        "level": "info",
                        "logger": "mcp-server",
                        "data": {
                            "type": "heartbeat",
                            "count": heartbeat_count,
                            "timestamp": datetime.now().isoformat(),
                            "status": "running" if mcp_manager.is_running else "stopped"
                        }
                    }
                }
                
                # MCP FORMAT: Send as 'message' event with JSON-RPC data
                yield f"event: message\ndata: {json.dumps(notification)}\n\n"
                
                # Wait before next heartbeat
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE stream error for session {session_id}: {e}")
        finally:
            # Cleanup session
            active_sessions.pop(session_id, None)
            logger.info(f"SSE session {session_id}: cleaned up")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control, Last-Event-ID"
        }
    )
```

### Add Missing POST Endpoint

Add this after the SSE endpoint:

```python
@app.post("/messages/")
async def handle_mcp_messages(
    request: Request,
    session_id: str = None
):
    """Handle MCP JSON-RPC messages via POST (required for MCP protocol)"""
    
    # Validate session
    if not session_id:
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "session_id required"}},
            status_code=400
        )
    
    if session_id not in active_sessions:
        logger.warning(f"Unknown session_id: {session_id}")
        # Continue anyway - session might have been created earlier
    
    try:
        # Parse JSON-RPC request
        json_rpc_request = await request.json()
        logger.info(f"Received MCP message for session {session_id}: {json_rpc_request}")
        
        # Validate JSON-RPC format
        if json_rpc_request.get("jsonrpc") != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": json_rpc_request.get("id"),
                "error": {"code": -32600, "message": "Invalid JSON-RPC version"}
            })
        
        method = json_rpc_request.get("method")
        request_id = json_rpc_request.get("id")
        params = json_rpc_request.get("params", {})
        
        # Handle MCP methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "mtr_next_train",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_next_train_schedule",
                            "description": "Get next train schedule for MTR stations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "station": {
                                        "type": "string",
                                        "description": "MTR station code (e.g., 'CEN', 'TST')"
                                    },
                                    "line": {
                                        "type": "string",
                                        "description": "MTR line name (optional)"
                                    }
                                },
                                "required": ["station"]
                            }
                        },
                        {
                            "name": "get_next_train_structured",
                            "description": "Get structured next train information with details",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "station": {"type": "string"},
                                    "direction": {"type": "string", "enum": ["UP", "DOWN"]}
                                },
                                "required": ["station"]
                            }
                        }
                    ]
                }
            })
        
        elif method == "resources/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": [
                        {
                            "uri": "mtr://stations/list",
                            "name": "MTR Stations List",
                            "description": "List of all MTR stations",
                            "mimeType": "application/json"
                        },
                        {
                            "uri": "mtr://lines/map",
                            "name": "MTR Lines Map",
                            "description": "MTR system lines and connections",
                            "mimeType": "application/json"
                        }
                    ]
                }
            })
        
        elif method == "prompts/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": [
                        {
                            "name": "check_next_train",
                            "description": "Check next train for a specific station",
                            "arguments": [
                                {"name": "station", "description": "Station code", "required": True}
                            ]
                        },
                        {
                            "name": "plan_mtr_journey",
                            "description": "Plan a journey using MTR",
                            "arguments": [
                                {"name": "from", "description": "Starting station", "required": True},
                                {"name": "to", "description": "Destination station", "required": True}
                            ]
                        }
                    ]
                }
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Mock tool execution
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tool '{tool_name}' executed with arguments: {json.dumps(arguments)}\n\nResult: Mock data - integrate with actual MTR API"
                        }
                    ]
                }
            })
        
        else:
            # Unknown method
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except Exception as e:
        logger.error(f"Error handling MCP message: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": json_rpc_request.get("id") if 'json_rpc_request' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }, status_code=500)
```

## Apply the Fix

1. **Backup your current file:**
   ```bash
   # On your Windows dev machine
   copy fastapi_mcp_integration.py fastapi_mcp_integration.py.backup
   ```

2. **Update the SSE endpoint** (lines 199-239) with the new code

3. **Add the `/messages/` POST endpoint** after the SSE endpoint

4. **Commit and push to GitHub:**
   ```bash
   git add fastapi_mcp_integration.py
   git commit -m "Fix: Make SSE endpoint MCP-protocol compatible"
   git push
   ```

5. **Deploy on Ubuntu server:**
   ```bash
   # SSH to Ubuntu server
   cd ~/mtrmcp
   git pull
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

6. **Test the fix:**
   ```bash
   # Should now show MCP format
   curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse | head -10
   
   # Expected output:
   # event: endpoint
   # data: /mcp/messages/?session_id=abc-123-def
   #
   # event: message
   # data: {"jsonrpc":"2.0","method":"notifications/message",...}
   ```

7. **Connect MCP Inspector:**
   - URL: `https://project-1-04.eduhk.hk/mcp/sse`
   - Connection Type: Direct
   - Should now connect successfully! ✅

## What Changed

| Before | After |
|--------|-------|
| `data: {"type": "connection"}` | `event: endpoint` + `data: /mcp/messages/?session_id=...` |
| `data: {"type": "heartbeat"}` | `event: message` + `data: {"jsonrpc":"2.0",...}` |
| No `/messages/` endpoint | POST `/mcp/messages/` handles JSON-RPC |
| Custom format | MCP Protocol standard |

## Why This Fixes the Issue

1. **MCP Inspector expects** specific SSE event types (`endpoint`, `message`)
2. **Your server was sending** plain `data:` without event types
3. **MCP protocol requires** JSON-RPC 2.0 format for all messages
4. **POST endpoint** is needed for bidirectional communication (client→server)

Once fixed, MCP Inspector will:
1. ✅ Connect to `/mcp/sse`
2. ✅ Receive `event: endpoint` and extract session ID
3. ✅ Send `initialize` request to `/mcp/messages/?session_id=...`
4. ✅ List your tools and allow testing
5. ✅ Execute tools and show results

Good luck! 🚀
