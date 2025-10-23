# 🚀 Deploy Streamable HTTP

## What Was Fixed

Implemented **NEW Streamable HTTP protocol (2025-06-18)** to fix MCP Inspector v0.15.0 connection issues.

### Changes Made

1. **Dual Protocol Support**: `/mcp/sse` now accepts both GET and POST
2. **Streamable HTTP**: POST with `initialize` returns SSE stream with `InitializeResult`
3. **Helper Function**: Added `handle_json_rpc_request()` for non-initialize methods
4. **Protocol Version Negotiation**: Echoes back client's requested version

## Deploy to Ubuntu Server

SSH to your server and run:

```bash
cd ~/mtrmcp
git pull
docker-compose down
docker-compose up -d --build
```

## Verify Deployment

### 1. Check Container Status
```bash
docker ps
# Should show: mtr-mcp-server (healthy)
```

### 2. Check Logs
```bash
docker logs mtr-mcp-server --tail 50
# Should show: "Starting FastAPI application with MCP under /mcp"
```

### 3. Test SSE Endpoint (GET - old protocol)
```bash
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse | head -5
# Should see: event: endpoint
```

### 4. Test Streamable HTTP (POST - new protocol)
```bash
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
  }' | head -10

# Expected output:
# event: message
# data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18",...}}
```

## Connect MCP Inspector

1. **Open MCP Inspector**: https://inspector.mcp.run (or run locally)
2. **Transport Type**: Select **"SSE"** (Inspector will auto-detect Streamable HTTP)
3. **Server URL**: `https://project-1-04.eduhk.hk/mcp/sse`
4. **Click "Connect"** ✅

### Expected Results

After connection:
- ✅ **Tools Tab**: Shows 2 tools (`get_next_train_schedule`, `get_next_train_structured`)
- ✅ **Resources Tab**: Shows 2 resources (`stations/list`, `lines/map`)
- ✅ **Prompts Tab**: Shows 2 prompts (`check_next_train`, `plan_mtr_journey`)
- ✅ **History Tab**: Shows `initialize` request/response

## Troubleshooting

### Issue: Still getting "Connection Error"

**Check logs for POST requests:**
```bash
docker logs mtr-mcp-server | grep "POST.*sse"
# Should see: "Streamable HTTP POST: method=initialize"
```

**If you see only GET requests**, MCP Inspector might be cached:
1. Clear browser cache
2. Open in incognito/private window
3. Try again

### Issue: Tools/Resources not showing

**Check initialize response:**
```bash
docker logs mtr-mcp-server | grep "initialize result"
# Should see: "SSE session <uuid>: sent initialize result"
```

**Check protocol version:**
```bash
docker logs mtr-mcp-server | grep "protocolVersion"
# Should see: '2025-06-18' (matching Inspector's request)
```

### Issue: NGINX 502 Bad Gateway

**Check container is running:**
```bash
docker ps | grep mtr-mcp
# Must show "Up" and "(healthy)"
```

**Check port binding:**
```bash
sudo netstat -tulpn | grep 8080
# Should show: docker-proxy ... 0.0.0.0:8080
```

## How It Works Now

### Old Protocol (2024-11-05) - Still Supported
```
Client: GET /mcp/sse
Server: event: endpoint → data: /mcp/messages/?session_id=<uuid>
Client: POST /mcp/messages/?session_id=<uuid> (initialize)
Server: JSON response
```

### New Protocol (2025-06-18) - Inspector Uses This
```
Client: POST /mcp/sse (with initialize in body)
Server: SSE stream → event: message → data: InitializeResult
Client: POST /mcp/sse (with tools/list in body)
Server: JSON response (NOT SSE)
```

## Success Indicators

In MCP Inspector logs you should see:
```
Created client transport
Created server transport
Received POST message for sessionId <uuid>
```

In your server logs you should see:
```
INFO: POST /mcp/sse HTTP/1.1" 200 OK
INFO: Streamable HTTP POST: method=initialize, id=0
INFO: SSE session <uuid>: sent initialize result
```

## Next Steps

After successful connection:
1. **Test a tool**: Click on a tool → Fill parameters → Execute
2. **View resources**: Browse available resources
3. **Try prompts**: Test prompt templates

---

🎉 **Your MCP server is now compatible with MCP Inspector v0.15.0!**
