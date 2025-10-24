# Complete MCP Guide
## Model Context Protocol - From Concepts to Production

**Last Updated**: January 2025  
**Version**: 3.0 Consolidated

---

## 📑 Table of Contents

1. [Introduction to MCP](#introduction-to-mcp)
2. [MCP Architecture](#mcp-architecture)
3. [Protocol Specification](#protocol-specification)
4. [FastAPI Implementation](#fastapi-implementation)
5. [MCP Inspector Guide](#mcp-inspector-guide)
6. [Debugging & Troubleshooting](#debugging--troubleshooting)
7. [Production Deployment](#production-deployment)
8. [LangGraph Integration](#langgraph-integration)

---

## Introduction to MCP

### What is MCP?

**Model Context Protocol (MCP)** is an open protocol created by Anthropic that standardizes how AI applications communicate with external data sources and tools.

**Think of MCP as:**
- 🔌 A "USB port" for AI applications - standard interface for any context source
- 📚 A library card catalog - helps AI find and access information
- 🔧 A universal toolbox - provides tools AI can use

### Why MCP Matters

**Before MCP**:
```
AI App 1 → Custom Integration A → Service A
AI App 2 → Custom Integration B → Service A
AI App 1 → Custom Integration C → Service B
```

**With MCP**:
```
AI App 1 ─┐
AI App 2 ─┼─→ MCP Protocol → MCP Server A (Service A)
AI App 3 ─┘                 → MCP Server B (Service B)
```

### Three Core Primitives

#### 🔧 **Tools** (Model-Controlled)
Functions that AI can invoke to perform actions.

```python
@mcp.tool()
def get_next_train_schedule(line: str, sta: str) -> str:
    """Get real-time train arrivals"""
    return call_mtr_api(line, sta)
```

**Use Case**: Actions that change state or fetch dynamic data

#### 📚 **Resources** (Application-Controlled)
Static/semi-static data sources that provide context.

```python
@mcp.resource("mtr://stations/list")
def get_station_list() -> str:
    """Returns list of all 93 MTR stations"""
    return "# MTR Stations\n..."
```

**Use Case**: Reference data, documentation, schemas

#### 💬 **Prompts** (User-Controlled)
Reusable templates for AI interactions.

```python
@mcp.prompt()
def check_next_train(line: str, station: str) -> str:
    """Template for checking train schedules"""
    return f"Please check trains at {station} on line {line}..."
```

**Use Case**: Common workflows, structured queries

---

## MCP Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│         APPLICATION LAYER                   │
│  (AI App, LangGraph Agent, Claude Desktop)  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         DATA LAYER (Inner)                  │
│  • JSON-RPC 2.0 Messages                    │
│  • Lifecycle Management (initialize)        │
│  • Primitives (tools, resources, prompts)   │
│  • Notifications                            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         TRANSPORT LAYER (Outer)             │
│  • stdio (Local processes)                  │
│  • Streamable HTTP (Remote servers)         │
│  • Custom transports                        │
└─────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **MCP Host** - The AI application (Claude, VS Code, custom agent)
#### 2. **MCP Client** - Component that connects to a single MCP server
#### 3. **MCP Server** - Your FastAPI service exposing resources/tools

**Important**: Each MCP Client maintains a **dedicated 1:1 connection** with its MCP Server.

---

## Protocol Specification

### JSON-RPC 2.0 Format

All MCP communication uses **JSON-RPC 2.0**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Initialization Sequence

```
Client                                   Server
  │                                        │
  │ ──── initialize (protocolVersion) ──>  │
  │                                        │
  │ <── InitializeResult (capabilities) ─  │
  │                                        │
  │ ──── notifications/initialized ─────>  │
  │                                        │
  │ ═══════ Session Active ═══════════════ │
```

### Transport Mechanisms

#### **stdio Transport** (Local)
- Local MCP servers on same machine
- stdin/stdout communication
- Zero network overhead
- Secure (no network exposure)

#### **Streamable HTTP Transport** (Remote)
- Remote MCP servers over network
- Protocol Version: `2025-06-18`
- Dual HTTP methods (POST + GET)
- Session management with tokens

**Critical Difference from Old Protocol (2024-11-05)**:

| Aspect | OLD (2024-11-05) | NEW (2025-06-18) |
|--------|------------------|------------------|
| Connection | GET `/sse` → separate POST endpoint | POST `/sse` with initialize → SSE response |
| Initialization | Client connects, then sends initialize | Client POST initialize, server streams response |
| Endpoint Discovery | `event: endpoint` with separate URL | No separate endpoint - same URL for all |

---

## FastAPI Implementation

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│   fastapi_mcp_integration.py                │
│   (HTTP/SSE Transport Layer)                │
│                                             │
│   ┌────────────────────────────────────┐    │
│   │ POST /mcp/sse                      │    │
│   │   • Streamable HTTP (2025-06-18)   │    │
│   │   • Receives JSON-RPC messages     │    │
│   │   • Returns SSE stream             │    │
│   └──────────┬─────────────────────────┘    │
│              │ imports & calls              │
│              ▼                              │
│   ┌────────────────────────────────────┐    │
│   │ mcp_server.py                      │    │
│   │   (MCP Business Logic)             │    │
│   │   @mcp.tool()                      │    │
│   │   @mcp.resource()                  │    │
│   │   @mcp.prompt()                    │    │
│   └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Correct Implementation (Streamable HTTP)

```python
from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
import json
import uuid
import asyncio

app = FastAPI()
active_sessions = {}

@app.api_route("/mcp/sse", methods=["POST", "GET"])
async def sse_endpoint(request: Request):
    """Streamable HTTP endpoint (MCP 2025-06-18)"""
    
    if request.method == "POST":
        # Client sending InitializeRequest or other JSON-RPC
        body = await request.json()
        method = body.get("method")
        
        if method == "initialize":
            # Return SSE stream with InitializeResult
            session_id = str(uuid.uuid4())
            
            async def init_stream():
                # Send InitializeResult as first message
                init_result = {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True},
                            "prompts": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "mtr-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
                
                # CRITICAL: Send as SSE message event
                yield f"event: message\ndata: {json.dumps(init_result)}\n\n"
                
                # Keep connection alive with heartbeats
                while True:
                    await asyncio.sleep(30)
                    if await request.is_disconnected():
                        break
                    
                    heartbeat = {
                        "jsonrpc": "2.0",
                        "method": "notifications/message",
                        "params": {
                            "level": "info",
                            "data": {"type": "heartbeat", "status": "running"}
                        }
                    }
                    yield f"event: message\ndata: {json.dumps(heartbeat)}\n\n"
            
            return StreamingResponse(
                init_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
        elif method == "tools/list":
            # Return JSON response (NOT SSE)
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "get_next_train_schedule",
                            "description": "Get MTR train schedule",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "line": {"type": "string"},
                                    "sta": {"type": "string"}
                                },
                                "required": ["line", "sta"]
                            }
                        }
                    ]
                }
            }
```

### Key Implementation Patterns

1. **Dual Protocol Support** - Accept both POST and GET
2. **SSE Stream Format** - Use `event: message\ndata: {...}\n\n`
3. **Session Management** - Generate unique session IDs
4. **Heartbeats** - Keep connection alive every 30 seconds
5. **Error Handling** - Return JSON-RPC error objects

---

## MCP Inspector Guide

### What is MCP Inspector?

MCP Inspector is a web-based debugging tool for MCP servers - like **Postman for MCP APIs**.

### Two Components

```
┌─────────────────────────────────────────────┐
│   MCP Inspector Client (MCPI)               │
│   React Web UI - Port 6274                  │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│   MCP Proxy Server (MCPP)                   │
│   Node.js Server - Port 6277                │
└──────────────┬──────────────────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────────────────┐
│   Your MCP Server (MTR Server)              │
│   Port 8080                                 │
└─────────────────────────────────────────────┘
```

### Getting Started

```bash
# Quick start
npx @modelcontextprotocol/inspector

# Opens on http://localhost:6274
```

### Connection Types

#### **Direct Connection to Production Server**
Browser connects directly to the deployed MCP server.

```
Connection Type: Direct
Server URL: https://project-1-04.eduhk.hk/mcp/sse
```

**Status**: ✅ Production server deployed and accessible

#### **Direct Connection to Local Development**
Browser connects to local MCP server (requires CORS enabled).

```
Connection Type: Direct
Server URL: http://localhost:8080/mcp/sse
```

#### **Proxy Connection**
Inspector connects through proxy server (alternative method).

```
Connection Type: Proxy
Proxy URL: https://inspector-proxy.example.com
Target Server: https://project-1-04.eduhk.hk/mcp/sse
```

### Testing Tools

1. **Select tool** from Tools tab
2. **Fill parameters**: `line="TKL"`, `sta="TKO"`
3. **Execute tool**
4. **View response** in real-time

### CLI Mode

```bash
# List tools
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/list

# Call tool
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="TKL" \
  --tool-arg sta="TKO"
```

---

## Debugging & Troubleshooting

### Common Issues

#### Issue 1: "Connection Error" in MCP Inspector

**Symptoms**: Inspector shows "Connection Error"

**Diagnosis**:
```bash
# Check server logs
docker logs mtr-mcp-server

# Test SSE endpoint
curl -N -H "Accept: text/event-stream" https://your-server.com/mcp/sse
```

**Solution**:
1. Echo client's protocol version in response
2. Ensure SSE format: `event: message\ndata: {...}\n\n`
3. Implement POST endpoint for Streamable HTTP

#### Issue 2: "Method not found"

**Cause**: Handler missing or not registered

**Solution**: Add all required handlers:
- `initialize`
- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`
- `prompts/list`
- `prompts/get`

#### Issue 3: NGINX Not Proxying SSE

**Root Cause**: Missing NGINX location block for `/mcp/`

**Solution**:
```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8080/mcp/;
    proxy_http_version 1.1;
    proxy_buffering off;  # CRITICAL for SSE
    proxy_cache off;
    proxy_read_timeout 86400s;
    proxy_set_header Connection "";
}
```

### Debugging Workflow

```
1. Test Docker Container
   ↓ ✅
2. Test Local Endpoint (localhost:8080)
   ↓ ✅
3. Test NGINX Health Proxy (/mcp/health)
   ↓ ✅
4. Test NGINX SSE Proxy (/mcp/sse)
   ↓ ❌ (Common failure point)
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

### Testing Commands

**🌐 Production Server (Deployed)**

```bash
# Test production server health
curl https://project-1-04.eduhk.hk/mcp/health

# Test production SSE endpoint (should stream events)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Expected SSE output:
# event: message
# data: {"jsonrpc":"2.0",...}

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
# URL: https://project-1-04.eduhk.hk/mcp/sse
```

**💻 Local Development Server (Optional)**

```bash
# 1. Check Docker health (if using Docker locally)
docker ps | grep mtr-mcp

# 2. Test local health
curl http://localhost:8080/mcp/health

# 3. Test local SSE
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp/sse
```

---

## Production Deployment

### Live Deployment

**🌐 Production Server**: `https://project-1-04.eduhk.hk/mcp/`

The MTR MCP server is currently deployed with:

**Architecture:**
```
Client Request
    ↓
NGINX (Port 443, SSL/TLS)
    ↓
Reverse Proxy (/mcp/ location)
    ↓
Docker Container (Port 8080)
    ↓
FastAPI (fastapi_mcp_integration.py)
    ↓
MCP Server (mcp_server.py)
```

**Endpoints:**
- **SSE**: `https://project-1-04.eduhk.hk/mcp/sse` (Streamable HTTP)
- **Health**: `https://project-1-04.eduhk.hk/mcp/health`
- **Info**: `https://project-1-04.eduhk.hk/mcp/info`
- **Docs**: `https://project-1-04.eduhk.hk/mcp/docs`

**Features:**
- ✅ Streamable HTTP Protocol (2025-06-18)
- ✅ SSL/TLS encryption
- ✅ SSE-optimized NGINX configuration
- ✅ Docker containerization with health checks
- ✅ Automatic reconnection handling
- ✅ 24/7 availability

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py fastapi_mcp_integration.py ./

HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:8080/mcp/health || exit 1

EXPOSE 8080

CMD ["python", "fastapi_mcp_integration.py"]
```

### NGINX Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name project-1-04.eduhk.hk;
    
    ssl_certificate /path/to/cert.crt;
    ssl_certificate_key /path/to/cert.key;
    
    location /mcp/ {
        # Proxy to FastAPI
        proxy_pass http://127.0.0.1:8080/mcp/;
        
        # SSE MUST use HTTP/1.1
        proxy_http_version 1.1;
        
        # Disable buffering (critical for SSE)
        proxy_buffering off;
        proxy_cache off;
        
        # Keep connection alive
        proxy_set_header Connection "";
        
        # Long timeouts for SSE (24 hours)
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
        
        # Pass headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Best Practices

- ✅ SSL/TLS for all connections
- ✅ Authentication for API endpoints
- ✅ Rate limiting
- ✅ Input validation
- ✅ CORS restrictions
- ✅ Security headers (HSTS, X-Frame-Options)
- ✅ Environment variables for secrets
- ✅ Regular dependency updates

---

## LangGraph Integration

### Agent Architecture

```python
from langgraph.graph import StateGraph, add_messages
from langchain_aws import ChatBedrock

# Connect to MCP Server
async with sse_client("http://127.0.0.1:8080/mcp/sse") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Load MCP Resources
        resources = await load_mcp_resources(session)
        
        # Create MCP Tools
        tools, tool_funcs = await create_mcp_tools(session)
        
        # Build LangGraph Agent
        llm = ChatBedrock(model_id="amazon.nova-lite-v1:0")
        llm_with_tools = llm.bind_tools(tools)
        
        # Define agent nodes
        async def call_model(state):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
            response = await llm_with_tools.ainvoke(messages)
            return {"messages": [response]}
        
        async def execute_tools(state):
            last_message = state["messages"][-1]
            tool_results = []
            for tool_call in last_message.tool_calls:
                result = await tool_funcs[tool_call["name"]](**tool_call["args"])
                tool_results.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                ))
            return {"messages": tool_results}
        
        # Build graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", execute_tools)
        workflow.add_edge("tools", "agent")
        
        # Compile with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
```

### Memory & Multi-turn Conversations

```python
# Memory configuration
config = {"configurable": {"thread_id": "demo-conversation"}}

# Turn 1
response1 = await app.ainvoke(
    {"messages": [HumanMessage(content="Next train from TKO?")]},
    config=config
)

# Turn 2 - References Turn 1 context
response2 = await app.ainvoke(
    {"messages": [HumanMessage(content="What about the other direction?")]},
    config=config  # SAME thread_id = memory persists!
)
```

---

## Summary

### Key Takeaways

1. **MCP** = Standard protocol for AI tools & data access
2. **Three Primitives**: Tools (AI-controlled), Resources (App-controlled), Prompts (User-controlled)
3. **Two Transports**: stdio (local) and Streamable HTTP (remote)
4. **Critical for SSE**: `proxy_buffering off`, HTTP/1.1, long timeouts
5. **MCP Inspector** = Essential debugging tool (like Postman for MCP)
6. **Protocol Version**: Use 2025-06-18 (Streamable HTTP) not 2024-11-05

### Quick Reference Commands

**🌐 Production Server:**
```bash
# Test deployed server health
curl https://project-1-04.eduhk.hk/mcp/health

# Test deployed SSE endpoint (should stream events)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Connect with MCP Inspector
npx @modelcontextprotocol/inspector
# URL: https://project-1-04.eduhk.hk/mcp/sse
```

**💻 Local Development:**
```bash
# Test local endpoint
curl http://localhost:8080/mcp/health

# Test local SSE
curl -N -H "Accept: text/event-stream" http://localhost:8080/mcp/sse
```

**🔧 Server Management:**
```bash
# Check NGINX syntax
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx

# Check Docker logs
docker logs -f mtr-mcp-server
```

### Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **FastMCP**: https://github.com/jlowin/fastmcp
- **LangGraph**: https://langchain-ai.github.io/langgraph/

---

**Document Version**: 3.0 Consolidated  
**Last Updated**: January 2025  
**License**: MIT
