# MCP Protocol Fix - 2025-06-18 Streamable HTTP

## Problem Identified

Your server implements the **OLD 2024-11-05 HTTP+SSE protocol**, but MCP Inspector uses the **NEW 2025-06-18 Streamable HTTP protocol**.

### Key Differences

| Aspect | OLD (2024-11-05) | NEW (2025-06-18) |
|--------|------------------|------------------|
| Connection | GET `/sse` → separate POST endpoint | POST `/sse` with initialize → SSE response |
| Initialization | Client connects, then sends initialize | Client POST initialize, server streams response |
| Endpoint Discovery | `event: endpoint` with separate URL | No separate endpoint - same URL for all |
| Message Flow | SSE (server→client) + POST (client→server) | POST for all client requests + SSE for responses |

## Required Changes

### Current Implementation (WRONG)
```python
@app.get("/sse")  # ❌ Only accepts GET
async def sse_endpoint(request: Request):
    # Sends: event: endpoint
    # Expects: Client to POST to /mcp/messages/
```

### Correct Implementation (Streamable HTTP)
```python
@app.post("/sse")  # ✅ POST for initialize
@app.api_route("/sse", methods=["POST", "GET"])  # ✅ Both methods
async def sse_endpoint(request: Request):
    # If POST with InitializeRequest:
    #   - Return SSE stream with InitializeResult
    # If GET:
    #   - Return SSE stream for notifications (optional)
```

## Step-by-Step Fix

### 1. Make `/sse` Accept POST

```python
from fastapi import Request, Response
from starlette.responses import StreamingResponse

@app.api_route("/sse", methods=["POST", "GET"])
async def sse_endpoint(request: Request):
    """Streamable HTTP endpoint (MCP 2025-06-18)"""
    
    if request.method == "POST":
        # Client is sending InitializeRequest
        body = await request.json()
        
        # Validate it's an initialize request
        if body.get("method") != "initialize":
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Expected initialize request"
                    }
                }),
                media_type="application/json",
                status_code=400
            )
        
        # Return SSE stream with InitializeResult
        async def init_stream():
            # Send InitializeResult as first message
            init_result = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "mtr-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            # CRITICAL: Send as SSE message event (NOT endpoint event)
            yield f"event: message\ndata: {json.dumps(init_result)}\n\n"
            
            # Keep connection alive with heartbeats
            while True:
                await asyncio.sleep(30)
                
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Send heartbeat notification
                heartbeat = {
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {
                        "level": "info",
                        "logger": "mcp-server",
                        "data": {"type": "heartbeat", "status": "running"}
                    }
                }
                yield f"event: message\ndata: {json.dumps(heartbeat)}\n\n"
        
        return StreamingResponse(
            init_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    elif request.method == "GET":
        # Optional: Support GET for server-initiated notifications
        # (Inspector might use this for optional notification stream)
        async def notification_stream():
            while True:
                await asyncio.sleep(60)
                if await request.is_disconnected():
                    break
                
                # Send periodic updates
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {
                        "level": "info",
                        "logger": "mcp-server",
                        "data": {"type": "status", "message": "Server active"}
                    }
                }
                yield f"event: message\ndata: {json.dumps(notification)}\n\n"
        
        return StreamingResponse(
            notification_stream(),
            media_type="text/event-stream"
        )
```

### 2. Remove Separate `/messages/` Endpoint

The new protocol doesn't use a separate POST endpoint. All client requests should go to the **same** endpoint (`/sse`).

However, for backwards compatibility, you can keep it but it won't be used by modern MCP Inspector.

### 3. Handle Subsequent Requests

After initialization, Inspector will send **new POST requests** to the same `/sse` endpoint:

```python
@app.api_route("/sse", methods=["POST", "GET"])
async def sse_endpoint(request: Request):
    if request.method == "POST":
        body = await request.json()
        method = body.get("method")
        
        if method == "initialize":
            # Return SSE stream with InitializeResult (as above)
            return StreamingResponse(init_stream(), ...)
        
        elif method == "tools/list":
            # Return JSON response (NOT SSE)
            tools = [...] # Your tools
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {"tools": tools}
                }),
                media_type="application/json"
            )
        
        elif method == "tools/call":
            # Can return either JSON or SSE stream
            # For simple responses: JSON
            # For streaming/progress: SSE
            result = execute_tool(body["params"])
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": result
                }),
                media_type="application/json"
            )
```

## Testing

After applying the fix:

```bash
# 1. Initialize with POST (Inspector does this)
curl -X POST https://project-1-04.eduhk.hk/mcp/sse \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'

# Expected: SSE stream starting with InitializeResult
# event: message
# data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18",...}}

# 2. Call tools/list
curl -X POST https://project-1-04.eduhk.hk/mcp/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'

# Expected: JSON response (NOT SSE)
# {"jsonrpc":"2.0","id":2,"result":{"tools":[...]}}
```

## References

- New Protocol: https://spec.modelcontextprotocol.io/specification/2025-06-18/basic/transports/
- Old Protocol: https://modelcontextprotocol.io/specification/2024-11-05/basic/transports
- Backwards Compatibility: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports/#backwards-compatibility
