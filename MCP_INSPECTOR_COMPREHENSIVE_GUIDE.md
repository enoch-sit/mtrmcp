# MCP Inspector: Comprehensive Guide for Beginners

## Table of Contents
1. [What is MCP?](#what-is-mcp)
2. [Understanding MCP Architecture](#understanding-mcp-architecture)
3. [What is MCP Inspector?](#what-is-mcp-inspector)
4. [Connection Types Explained](#connection-types-explained)
5. [How to Use MCP Inspector](#how-to-use-mcp-inspector)
6. [Debugging SSE Connection Issues](#debugging-sse-connection-issues)
7. [Common Problems and Solutions](#common-problems-and-solutions)
8. [Real-World Example: Your MCP Server](#real-world-example)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol that enables AI applications (like Claude, ChatGPT, or custom LLM applications) to connect to external data sources and tools securely.

### Why MCP Exists

Imagine you're building an AI assistant that needs to:
- Access your company's database
- Call APIs to get real-time data
- Execute tools (search, calculations, file operations)
- Maintain context across multiple interactions

**Without MCP**: You'd have to build custom integrations for each data source and tool, creating security risks and maintenance nightmares.

**With MCP**: You build ONE MCP server that exposes:
- **Resources** (data like files, database records)
- **Prompts** (pre-configured AI prompts)
- **Tools** (functions the AI can execute)

### Key Concepts

```
┌─────────────────┐           ┌──────────────────┐           ┌─────────────────┐
│   AI Client     │◄─────────►│   MCP Server     │◄─────────►│  Your Systems   │
│ (Claude, etc)   │    MCP    │  (Your FastAPI)  │           │ (DB, APIs, etc) │
└─────────────────┘  Protocol └──────────────────┘           └─────────────────┘
```

**MCP Client** → The AI application requesting data/tools
**MCP Server** → Your FastAPI service exposing resources/tools
**MCP Protocol** → Standardized communication format between them

---

## Understanding MCP Architecture

### 1. Transport Layer: SSE (Server-Sent Events)

MCP uses **SSE** for real-time, bidirectional communication:

- **What is SSE?** A web standard for pushing updates from server to client over HTTP
- **Why SSE?** Simpler than WebSockets, works with standard HTTP, firewall-friendly
- **How it works**: Client opens connection → Server keeps it alive → Streams data as events

```
Client Request:
GET /mcp/sse HTTP/1.1
Accept: text/event-stream

Server Response:
HTTP/1.1 200 OK
Content-Type: text/event-stream

event: message
data: {"jsonrpc":"2.0","method":"tools/list",...}

event: message
data: {"jsonrpc":"2.0","result":[...],...}
```

### 2. Message Format: JSON-RPC 2.0

MCP messages follow JSON-RPC 2.0 standard:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Key Fields:**
- `jsonrpc`: Always "2.0"
- `id`: Request ID for matching responses
- `method`: The operation (e.g., "tools/list", "resources/read")
- `params`: Operation parameters
- `result`: Response data (in response messages)
- `error`: Error details (if something failed)

### 3. MCP Server Capabilities

Your MCP server can expose:

#### **Resources** (Data Access)
```json
{
  "uri": "file:///data/customers.json",
  "name": "Customer Database",
  "description": "Access customer records",
  "mimeType": "application/json"
}
```

#### **Prompts** (Pre-configured AI Instructions)
```json
{
  "name": "analyze_customer",
  "description": "Analyze customer behavior",
  "arguments": [
    {"name": "customer_id", "required": true}
  ]
}
```

#### **Tools** (Functions AI Can Execute)
```json
{
  "name": "search_customers",
  "description": "Search customer database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"}
    }
  }
}
```

---

## What is MCP Inspector?

**MCP Inspector** is a web-based debugging tool for MCP servers. Think of it as:
- **Browser DevTools** for MCP protocol
- **Postman** for MCP APIs
- **Debug Console** for testing MCP capabilities

### What You Can Do With Inspector

1. **Connect to MCP Servers** (direct or via proxy)
2. **List Available Tools** exposed by server
3. **Test Tool Execution** with custom inputs
4. **View Resources** and read their contents
5. **Test Prompts** with different arguments
6. **Debug Messages** in real-time
7. **Monitor Connection Health**

### Inspector Interface Overview

```
┌────────────────────────────────────────────────────────────┐
│  Connection Type: [Direct] [Proxy]                         │
│  Server URL: https://project-1-04.eduhk.hk/mcp/sse         │
│  [Connect]                                                  │
├────────────────────────────────────────────────────────────┤
│  ┌─────────┬─────────┬──────────┬─────────┐               │
│  │ Tools   │Resources│ Prompts  │ Logs    │               │
│  └─────────┴─────────┴──────────┴─────────┘               │
│                                                             │
│  Available Tools:                                          │
│  - aws_bedrock_invoke_model                                │
│  - search_database                                         │
│                                                             │
│  [Test Tool] [View Schema] [Execute]                       │
└────────────────────────────────────────────────────────────┘
```

---

## Connection Types Explained

### 1. Direct Connection

**What it is**: Browser connects directly to your MCP server

```
┌──────────────┐       HTTPS/SSE       ┌──────────────┐
│   Browser    │◄─────────────────────►│  MCP Server  │
│  (Inspector) │   Direct Connection    │ (Port 8080)  │
└──────────────┘                        └──────────────┘
```

**When to use:**
- ✅ Testing local MCP servers (`http://localhost:8080/mcp/sse`)
- ✅ Public MCP servers with CORS enabled
- ✅ Development and debugging

**Requirements:**
- Server must allow CORS (Cross-Origin Resource Sharing)
- SSE endpoint must be accessible from browser
- HTTPS certificate must be valid (for production)

**Configuration in Inspector:**
```
Connection Type: Direct
Server URL: https://project-1-04.eduhk.hk/mcp/sse
Transport: SSE
Custom Headers: (optional)
```

### 2. Proxy Connection

**What it is**: Inspector connects through MCP Inspector's proxy server

```
┌──────────────┐    HTTPS    ┌───────────────┐    SSE    ┌──────────────┐
│   Browser    │◄───────────►│ Inspector     │◄─────────►│  MCP Server  │
│  (Inspector) │              │ Proxy Server  │           │ (Port 8080)  │
└──────────────┘              └───────────────┘           └──────────────┘
```

**When to use:**
- ✅ MCP servers without CORS headers
- ✅ MCP servers behind authentication
- ✅ Servers in private networks (via proxy relay)
- ✅ Avoiding browser security restrictions

**Requirements:**
- MCP Inspector proxy server running
- Network access from proxy to your MCP server
- Proxy authentication (if configured)

**Configuration in Inspector:**
```
Connection Type: Proxy
Proxy URL: https://inspector-proxy.example.com
Target Server: http://localhost:8080/mcp/sse
Authentication: (if required)
```

---

## How to Use MCP Inspector

### Step 1: Access MCP Inspector

**Option A**: Use official hosted version
- URL: `https://inspector.modelcontextprotocol.io` (if available)
- No installation required
- Latest features

**Option B**: Run locally
```bash
# Clone the repository
git clone https://github.com/modelcontextprotocol/inspector.git
cd inspector

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 2: Connect to Your MCP Server

#### For Direct Connection:

1. Select **"Direct"** connection type
2. Enter your server URL:
   ```
   https://project-1-04.eduhk.hk/mcp/sse
   ```
3. Click **"Connect"**

#### For Proxy Connection:

1. Select **"Proxy"** connection type
2. Enter proxy URL (if using Inspector's proxy)
3. Enter your server URL in "Target Server"
4. Add authentication if required
5. Click **"Connect"**

### Step 3: Explore Your MCP Server

Once connected, you'll see tabs:

#### **Tools Tab**
Lists all tools your server exposes:
```json
[
  {
    "name": "aws_bedrock_invoke_model",
    "description": "Invoke AWS Bedrock model",
    "inputSchema": {
      "type": "object",
      "properties": {
        "model_id": {"type": "string"},
        "prompt": {"type": "string"}
      }
    }
  }
]
```

**Actions:**
- Click tool name to view full schema
- Click "Test" to execute with custom input
- View results in real-time

#### **Resources Tab**
Shows available data resources:
```json
[
  {
    "uri": "mcp://langsmith/traces",
    "name": "LangSmith Traces",
    "mimeType": "application/json"
  }
]
```

**Actions:**
- Click "Read" to fetch resource content
- View structured data
- Test different URI parameters

#### **Prompts Tab**
Pre-configured prompts:
```json
[
  {
    "name": "analyze_code",
    "description": "Analyze code quality",
    "arguments": [
      {"name": "file_path", "required": true}
    ]
  }
]
```

**Actions:**
- Test prompts with different arguments
- View generated AI instructions
- Validate prompt templates

#### **Logs Tab**
Real-time message log:
```
[2024-01-15 10:30:45] → Request: tools/list
[2024-01-15 10:30:46] ← Response: 3 tools found
[2024-01-15 10:30:50] → Request: tools/call (aws_bedrock_invoke_model)
[2024-01-15 10:30:52] ← Response: Model invoked successfully
```

### Step 4: Test Tools

1. **Select a tool** from Tools tab
2. **Fill in parameters**:
   ```json
   {
     "model_id": "anthropic.claude-v2",
     "prompt": "What is MCP?"
   }
   ```
3. **Click "Execute"**
4. **View response**:
   ```json
   {
     "content": [
       {
         "type": "text",
         "text": "MCP is Model Context Protocol..."
       }
     ]
   }
   ```

---

## Debugging SSE Connection Issues

### Issue 1: Connection Refused

**Symptoms:**
```
Error: Failed to connect to https://project-1-04.eduhk.hk/mcp/sse
net::ERR_CONNECTION_REFUSED
```

**Debug Steps:**

1. **Check if server is running**:
   ```bash
   # On Ubuntu server
   docker ps | grep mtr-mcp-server
   ```
   ✅ Should show: "Up X minutes (healthy)"

2. **Test health endpoint**:
   ```bash
   curl https://project-1-04.eduhk.hk/mcp/health
   ```
   ✅ Should return: `{"status":"healthy","service":"mtr-mcp-server"}`

3. **Test SSE endpoint locally**:
   ```bash
   # On Ubuntu server (local test)
   curl -N http://localhost:8080/mcp/sse
   ```
   ✅ Should establish connection (might hang - that's OK for SSE)

4. **Test through NGINX**:
   ```bash
   curl -N https://project-1-04.eduhk.hk/mcp/sse
   ```
   ❌ If this fails → NGINX configuration issue

### Issue 2: NGINX Not Proxying SSE

**Symptoms:**
- Health endpoint works
- SSE endpoint times out or returns 404/502

**Root Cause:**
Missing NGINX location block for `/mcp/` path

**Solution:**
Add the location block from `nginx-mcp-location-block.conf` to your NGINX config:

```bash
# Edit NGINX config
sudo nano /etc/nginx/sites-available/project-1-04.eduhk.hk

# Add the location block (see nginx-mcp-location-block.conf)

# Test configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

**Critical NGINX Settings for SSE:**
```nginx
proxy_buffering off;        # MUST HAVE - buffering breaks SSE
proxy_cache off;            # MUST HAVE - caching breaks real-time
proxy_http_version 1.1;     # Required for keep-alive
proxy_set_header Connection '';  # Keep connection open
```

### Issue 3: CORS Errors (Direct Connection)

**Symptoms:**
```
Access to fetch at 'https://project-1-04.eduhk.hk/mcp/sse' from origin 
'https://inspector.modelcontextprotocol.io' has been blocked by CORS policy
```

**Solution 1**: Add CORS headers in NGINX:
```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
add_header 'Access-Control-Allow-Headers' 'Content-Type, Accept' always;
```

**Solution 2**: Use Proxy connection type instead of Direct

### Issue 4: SSL Certificate Errors

**Symptoms:**
```
net::ERR_CERT_AUTHORITY_INVALID
```

**Debug:**
```bash
# Check certificate
openssl s_client -connect project-1-04.eduhk.hk:443 -servername project-1-04.eduhk.hk

# Verify certificate chain
curl -v https://project-1-04.eduhk.hk/mcp/health
```

**Solutions:**
- Ensure certificate is valid and not expired
- Check certificate chain is complete
- For development: Use proxy connection to bypass browser SSL checks

### Issue 5: Connection Drops/Timeouts

**Symptoms:**
- Connection established but drops after a few seconds
- Timeout errors in Inspector

**Root Causes:**
1. **NGINX timeouts too short**
2. **Proxy buffering enabled**
3. **Firewall dropping long-lived connections**

**Solution:**
```nginx
# In NGINX location block
proxy_read_timeout 86400s;   # 24 hours
proxy_send_timeout 86400s;   # 24 hours
```

### Debugging Workflow

Use this systematic approach:

```
1. Test Docker Container
   ↓ ✅
2. Test Local Endpoint (localhost:8080)
   ↓ ✅
3. Test NGINX Health Proxy (/mcp/health)
   ↓ ✅
4. Test NGINX SSE Proxy (/mcp/sse)
   ↓ ❌ (YOUR CURRENT ISSUE)
5. Check NGINX Configuration
   ↓
6. Add/Fix NGINX Location Block
   ↓
7. Reload NGINX
   ↓
8. Test SSE Connection Again
   ↓ ✅
9. Connect with MCP Inspector
```

---

## Common Problems and Solutions

### Problem: "Server not responding to tools/list"

**Cause**: MCP server doesn't implement required methods

**Solution**: Ensure your FastAPI server implements:
```python
from fastmcp import FastMCP

mcp = FastMCP("mtr-mcp-server")

# Required: List tools
@mcp.tool()
def my_tool(arg: str) -> str:
    """Tool description"""
    return f"Result: {arg}"

# Required: Initialize
@mcp.initialize()
async def initialize():
    """Initialize server capabilities"""
    return {"protocolVersion": "0.1.0"}
```

### Problem: "Authentication required"

**Cause**: Server behind authentication proxy

**Solutions:**
1. **Add auth headers in Inspector**:
   ```
   Custom Headers:
   Authorization: Bearer YOUR_TOKEN
   ```

2. **Use proxy connection** with auth credentials

3. **Configure NGINX to pass auth**:
   ```nginx
   proxy_set_header Authorization $http_authorization;
   proxy_pass_header Authorization;
   ```

### Problem: "JSON-RPC parse error"

**Cause**: Invalid message format

**Debug**:
1. Check Inspector Logs tab for exact message
2. Validate JSON syntax
3. Ensure `jsonrpc: "2.0"` is set
4. Check method names match server implementation

**Solution**: Review MCP protocol specification for correct format

### Problem: "Proxy health check failed"

**Cause**: Proxy can't reach your MCP server

**Debug**:
```bash
# On proxy server
curl http://localhost:8080/mcp/sse
```

**Solutions:**
- Check network connectivity
- Verify firewall rules
- Ensure server is running
- Check proxy configuration

---

## Real-World Example: Your MCP Server

### Your Setup

```
Component Diagram:
┌──────────────────────────────────────────────────────────────┐
│                      Ubuntu Server                            │
│  project-1-04.eduhk.hk                                        │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  NGINX (Port 443 - HTTPS)                               │ │
│  │  SSL: dept-wildcard.eduhk certificates                  │ │
│  │                                                          │ │
│  │  / → Flowise (Port 3000)                                │ │
│  │  /langgraphplayground/ → LangGraph (Port 2024)          │ │
│  │  /mcp/ → ❌ NOT CONFIGURED (MISSING!)                   │ │
│  └────────────────┬────────────────────────────────────────┘ │
│                   │                                           │
│  ┌────────────────▼─────────────────┐                        │
│  │  Docker: mtr-mcp-server          │                        │
│  │  Port: 8080                      │                        │
│  │  Image: mtr-mcp-fastapi          │                        │
│  │  Status: healthy ✅              │                        │
│  │                                  │                        │
│  │  Endpoints:                      │                        │
│  │  - /mcp/health ✅                │                        │
│  │  - /mcp/sse ❓ (blocked by NGINX)│                        │
│  │  - /mcp/tools                    │                        │
│  │  - /mcp/resources                │                        │
│  └──────────────────────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

### Current Status

✅ **Working:**
- Docker container running and healthy
- Local endpoint accessible: `http://localhost:8080/mcp/health`
- NGINX proxying health check: `https://project-1-04.eduhk.hk/mcp/health`

❌ **Not Working:**
- SSE endpoint through NGINX: `https://project-1-04.eduhk.hk/mcp/sse`
- MCP Inspector cannot connect

### Root Cause Analysis

Your NGINX config (`/etc/nginx/sites-available/project-1-04.eduhk.hk`) has:
- ✅ Location block for `/` (Flowise)
- ✅ Location block for `/langgraphplayground/` (LangGraph)
- ❌ **MISSING location block for `/mcp/`**

**Why health endpoint works:**
The health check is likely succeeding due to a fallback rule or you tested locally. The SSE endpoint specifically requires the location block with SSE-specific settings.

### Solution Steps

**Step 1**: Add NGINX location block
```bash
# On Ubuntu server
sudo nano /etc/nginx/sites-available/project-1-04.eduhk.hk

# Add the location block from nginx-mcp-location-block.conf
# Place it BEFORE the location / block (order matters!)
```

**Step 2**: Test NGINX configuration
```bash
sudo nginx -t
```
Expected output:
```
nginx: configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**Step 3**: Reload NGINX
```bash
sudo systemctl reload nginx
```

**Step 4**: Test SSE endpoint
```bash
# Should now establish connection
curl -N https://project-1-04.eduhk.hk/mcp/sse
```

**Step 5**: Connect with MCP Inspector
```
Connection Type: Direct
Server URL: https://project-1-04.eduhk.hk/mcp/sse
Click: Connect
```

### Testing Checklist

Run these tests in order:

```bash
# 1. Docker container health
docker ps | grep mtr-mcp

# 2. Local health check
curl http://localhost:8080/mcp/health

# 3. Local SSE endpoint
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp/sse

# 4. NGINX health proxy
curl https://project-1-04.eduhk.hk/mcp/health

# 5. NGINX SSE proxy (after config update)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# 6. MCP Inspector connection
# Use Inspector UI to connect
```

### Expected Inspector Behavior

Once connected successfully:

1. **Connection indicator** turns green
2. **Tools tab** shows available tools:
   ```
   - aws_bedrock_invoke_model
   - [other tools from your FastAPI server]
   ```
3. **Resources tab** shows available resources
4. **Logs tab** shows successful connection messages:
   ```
   [Connected to https://project-1-04.eduhk.hk/mcp/sse]
   [Received: tools/list response]
   ```

### Monitoring

**Check NGINX logs** for SSE connections:
```bash
# Access log
sudo tail -f /var/log/nginx/access.log | grep mcp

# Error log
sudo tail -f /var/log/nginx/error.log | grep mcp
```

**Check Docker logs**:
```bash
docker logs -f mtr-mcp-server
```

---

## Advanced Tips

### 1. Custom Headers for Authentication

In MCP Inspector (Direct connection):
```
Custom Headers:
X-API-Key: your-api-key-here
Authorization: Bearer your-token-here
```

In NGINX:
```nginx
location /mcp/ {
    # Pass custom headers
    proxy_set_header X-API-Key $http_x_api_key;
    proxy_set_header Authorization $http_authorization;
    
    # ... other settings ...
}
```

### 2. Rate Limiting SSE Connections

In NGINX:
```nginx
limit_req_zone $binary_remote_addr zone=mcp_sse:10m rate=10r/m;

location /mcp/sse {
    limit_req zone=mcp_sse burst=5 nodelay;
    # ... SSE settings ...
}
```

### 3. Monitoring SSE Health

Create a monitoring script:
```bash
#!/bin/bash
# check-sse-health.sh

while true; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
             -N -H "Accept: text/event-stream" \
             https://project-1-04.eduhk.hk/mcp/sse \
             --max-time 5)
    
    if [ "$STATUS" -eq 200 ]; then
        echo "$(date): SSE endpoint healthy"
    else
        echo "$(date): SSE endpoint down (HTTP $STATUS)"
        # Alert or restart service
    fi
    
    sleep 60
done
```

### 4. Debugging with Browser DevTools

1. Open Inspector in browser
2. Press F12 (DevTools)
3. Go to **Network tab**
4. Filter by "sse" or "EventStream"
5. Watch request/response headers
6. Monitor SSE events in real-time

---

## Summary

### Key Takeaways

1. **MCP** = Standard protocol for AI tools & data access
2. **SSE** = Transport mechanism (requires special NGINX config)
3. **MCP Inspector** = Debugging tool (like Postman for MCP)
4. **Direct Connection** = Browser → MCP Server (needs CORS)
5. **Proxy Connection** = Browser → Proxy → MCP Server (no CORS needed)

### Your Next Steps

1. ✅ **Add NGINX location block** (from `nginx-mcp-location-block.conf`)
2. ✅ **Reload NGINX** (`sudo systemctl reload nginx`)
3. ✅ **Test SSE endpoint** (`curl -N https://project-1-04.eduhk.hk/mcp/sse`)
4. ✅ **Connect MCP Inspector** (Direct connection)
5. ✅ **Explore tools/resources** in Inspector
6. ✅ **Monitor logs** for issues

### Quick Reference Commands

```bash
# Test local endpoint
curl http://localhost:8080/mcp/health

# Test through NGINX
curl https://project-1-04.eduhk.hk/mcp/health

# Test SSE (should stream events)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Check NGINX syntax
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx

# Check Docker logs
docker logs -f mtr-mcp-server

# Monitor NGINX logs
sudo tail -f /var/log/nginx/access.log
```

### Resources

- **MCP Specification**: https://github.com/modelcontextprotocol/specification
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **Your Project**: https://github.com/enoch-sit/mtrmcp
- **SSE Specification**: https://html.spec.whatwg.org/multipage/server-sent-events.html

---

## Troubleshooting Decision Tree

```
Cannot connect to MCP server
│
├─ Health endpoint working?
│  ├─ No → Check Docker container status
│  └─ Yes ↓
│
├─ SSE endpoint local (localhost:8080)?
│  ├─ No → Check FastAPI server implementation
│  └─ Yes ↓
│
├─ SSE endpoint through NGINX?
│  ├─ No → ⚠️ NGINX configuration issue
│  │         → Add /mcp/ location block
│  │         → Enable proxy_buffering off
│  │         → Reload NGINX
│  └─ Yes ↓
│
├─ CORS errors in browser?
│  ├─ Yes → Add CORS headers or use Proxy connection
│  └─ No ↓
│
├─ SSL certificate errors?
│  ├─ Yes → Check certificate validity
│  └─ No ↓
│
└─ Connection drops after few seconds?
   └─ Increase NGINX timeouts (proxy_read_timeout)
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-15  
**For Project**: mtr-mcp-fastapi-example  
**Server**: project-1-04.eduhk.hk
