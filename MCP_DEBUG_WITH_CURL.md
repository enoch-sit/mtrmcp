# Debugging MCP Server with curl

## Your Current Status

✅ **WORKING:** Your SSE endpoint is connected and receiving heartbeats!

```bash
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Output:
data: {"type": "connection", "status": "connected", "server": "mtr_next_train"}
data: {"type": "heartbeat", "timestamp": "2025-10-23T04:15:39.981209", "status": "running"}
```

This is **exactly correct** behavior! The connection stays open (hangs) to receive real-time events.

## Why MCP Inspector Cannot Connect

Based on MCP protocol documentation, your server needs to send **specific SSE messages** for MCP Inspector to recognize it as an MCP server.

### What's Missing

Your server sends:
```
data: {"type": "connection", "status": "connected", ...}  ❌ Custom format
```

MCP Inspector expects:
```
event: endpoint                                           ✅ MCP standard
data: /messages/?session_id=abc123

event: message                                            ✅ MCP standard
data: {"jsonrpc":"2.0","method":"..."}
```

## MCP Protocol SSE Requirements

According to MCP Python SDK documentation, an MCP-compatible SSE server must:

### 1. **First Event: Endpoint Announcement**

```
event: endpoint
data: /messages/?session_id={session_id}
```

This tells the client WHERE to POST JSON-RPC requests.

### 2. **Subsequent Events: JSON-RPC Messages**

```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{...}}
```

All MCP communication uses JSON-RPC 2.0 format.

## Testing MCP Protocol with curl

### Test 1: Check Current SSE Output

```bash
# On Ubuntu server
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse
```

**What to look for:**
- `event: endpoint` (REQUIRED for MCP)
- `event: message` (REQUIRED for MCP)
- If you only see `data: {...}` without `event:`, it's not MCP-compatible

### Test 2: Send JSON-RPC Initialize Request

MCP clients send an `initialize` request first:

```bash
# Save this as test_mcp_init.json
cat > test_mcp_init.json << 'EOF'
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    },
    "capabilities": {}
  }
}
EOF

# Try to POST to your server (this will likely fail currently)
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d @test_mcp_init.json \
  https://project-1-04.eduhk.hk/mcp/sse
```

**Expected Response (MCP-compatible):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {}
    },
    "serverInfo": {
      "name": "mtr-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

### Test 3: List Tools (After Initialize)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  https://project-1-04.eduhk.hk/mcp/messages/?session_id=YOUR_SESSION_ID
```

## Analyzing Your FastAPI Server

Let's check if your `fastapi_mcp_integration.py` implements MCP protocol correctly:

### Required Components

1. **SSE Endpoint** (`/mcp/sse`):
   - Must send `event: endpoint` first
   - Must send `event: message` for JSON-RPC responses
   - Must support long-lived connections

2. **Message POST Endpoint** (`/mcp/messages/`):
   - Must accept JSON-RPC 2.0 requests
   - Must parse `session_id` from query params
   - Must route to appropriate handlers

3. **MCP Methods** (JSON-RPC):
   - `initialize` - Server capabilities
   - `tools/list` - Available tools
   - `tools/call` - Execute a tool
   - `resources/list` - Available resources (optional)
   - `prompts/list` - Available prompts (optional)

## Debug Commands

### Check SSE Event Format

```bash
# Verbose curl to see all details
curl -v -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse 2>&1 | head -50
```

Look for:
```
< HTTP/1.1 200 OK
< Content-Type: text/event-stream

event: endpoint          ← REQUIRED
data: /messages/?session_id=...

event: message           ← For JSON-RPC
data: {"jsonrpc":"2.0"...}
```

### Check POST Endpoint Exists

```bash
# Test if /messages/ endpoint exists
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  https://project-1-04.eduhk.hk/mcp/messages/

# Expected: 400 (bad request) or error about session_id
# Not expected: 404 (endpoint missing)
```

### Check Health vs SSE Difference

```bash
# Health endpoint (your custom format)
curl https://project-1-04.eduhk.hk/mcp/health
# Returns: {"status":"healthy",...}

# SSE endpoint (should be MCP format)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse
# Should return: event: endpoint + event: message
```

## Common Issues & Solutions

### Issue 1: Custom SSE Format (Not MCP-Compatible)

**Symptom:**
```
data: {"type": "connection", ...}  ← Custom format
```

**Solution:**
Update your FastAPI SSE endpoint to send MCP-format events:

```python
@app.get("/mcp/sse")
async def sse_endpoint(request: Request):
    async def event_generator():
        session_id = str(uuid.uuid4())
        
        # MCP REQUIRED: Send endpoint event
        yield {
            "event": "endpoint",
            "data": f"/mcp/messages/?session_id={session_id}"
        }
        
        # MCP REQUIRED: Send JSON-RPC messages
        while True:
            # Heartbeat as JSON-RPC notification
            yield {
                "event": "message",
                "data": json.dumps({
                    "jsonrpc": "2.0",
                    "method": "notifications/heartbeat",
                    "params": {"timestamp": datetime.now().isoformat()}
                })
            }
            await asyncio.sleep(30)
    
    return EventSourceResponse(event_generator())
```

### Issue 2: Missing Message POST Endpoint

**Symptom:**
```
POST /mcp/messages/?session_id=123
404 Not Found
```

**Solution:**
Add POST endpoint to handle JSON-RPC requests:

```python
@app.post("/mcp/messages/")
async def handle_message(
    session_id: str = Query(...),
    request: Request
):
    body = await request.json()
    
    # Validate JSON-RPC format
    if body.get("jsonrpc") != "2.0":
        return {"error": "Invalid JSON-RPC version"}
    
    method = body.get("method")
    request_id = body.get("id")
    params = body.get("params", {})
    
    # Route to appropriate handler
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mtr-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "aws_bedrock_invoke_model",
                        "description": "Invoke AWS Bedrock model",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "model_id": {"type": "string"},
                                "prompt": {"type": "string"}
                            },
                            "required": ["model_id", "prompt"]
                        }
                    }
                ]
            }
        }
```

### Issue 3: FastMCP Not Configured for SSE

**Symptom:**
Your code uses FastMCP but SSE endpoint doesn't work correctly.

**Solution:**
Check if FastMCP is running with SSE transport:

```python
from fastmcp import FastMCP

mcp = FastMCP("mtr-mcp-server")

# Add tools
@mcp.tool()
def my_tool(arg: str) -> str:
    return f"Result: {arg}"

# Run with SSE transport
if __name__ == "__main__":
    mcp.run(transport="sse", port=8080)
```

## Verification Checklist

Run these commands in order to verify your MCP server:

```bash
# 1. Health check (custom endpoint)
curl https://project-1-04.eduhk.hk/mcp/health
# ✅ Should return: {"status":"healthy",...}

# 2. SSE connection (MCP protocol)
timeout 5 curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse
# ✅ Should show: event: endpoint
# ✅ Should show: event: message

# 3. Extract session_id from SSE
SESSION_ID=$(curl -s -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse | \
  grep "data: /mcp/messages" | head -1 | \
  sed -n 's/.*session_id=\([^"]*\).*/\1/p')

echo "Session ID: $SESSION_ID"

# 4. Send initialize request
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"curl-test","version":"1.0"},"capabilities":{}}}' \
  "https://project-1-04.eduhk.hk/mcp/messages/?session_id=$SESSION_ID"
# ✅ Should return: JSON-RPC response with serverInfo

# 5. List tools
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  "https://project-1-04.eduhk.hk/mcp/messages/?session_id=$SESSION_ID"
# ✅ Should return: Array of tools
```

## Next Steps

### If SSE doesn't show `event: endpoint`:

1. **Check your FastAPI code:**
   ```bash
   # Read your current implementation
   cat fastapi_mcp_integration.py | grep -A 20 "def.*sse"
   ```

2. **Update to MCP format:**
   - SSE must send `event: endpoint` first
   - SSE must send `event: message` for JSON-RPC

3. **Restart Docker container:**
   ```bash
   docker restart mtr-mcp-server
   ```

### If POST endpoint returns 404:

1. **Verify endpoint exists:**
   ```bash
   # Check FastAPI logs
   docker logs mtr-mcp-server | grep -i "post\|messages"
   ```

2. **Add missing endpoint** if needed

3. **Restart and test** again

### If JSON-RPC format is wrong:

1. **Validate JSON-RPC structure:**
   - Must have `jsonrpc: "2.0"`
   - Must have `id` (for requests)
   - Must have `method` and `params`

2. **Check response format:**
   - Must have `jsonrpc: "2.0"`
   - Must have `id` (matching request)
   - Must have `result` or `error`

## Reference: MCP Python SDK Example

Here's how MCP Python SDK implements SSE (from official examples):

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount

# Create SSE transport
sse = SseServerTransport("/messages/")

# SSE handler
async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())
    return Response()

# Create Starlette app
starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)
```

Key points:
- SSE transport automatically sends `event: endpoint`
- SSE transport automatically formats messages as `event: message`
- POST endpoint at `/messages/` handles JSON-RPC

## Summary

**Your Issue:**
Your SSE endpoint is working at the transport level (connection established, heartbeats received), but it's not sending MCP-compatible event format.

**Quick Fix:**
1. Update SSE endpoint to send `event: endpoint` first
2. Send subsequent messages as `event: message` with JSON-RPC data
3. Ensure POST endpoint exists at `/mcp/messages/`
4. Implement JSON-RPC handlers for `initialize`, `tools/list`, etc.

**Test After Fix:**
```bash
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse | head -5
```

Should output:
```
event: endpoint
data: /mcp/messages/?session_id=abc123

event: message
data: {"jsonrpc":"2.0",...}
```

Then MCP Inspector will successfully connect! 🎉
