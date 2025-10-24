# MTR MCP Server - Complete Documentation

> **Production Server**: https://project-1-04.eduhk.hk/mcp/  
> **Last Updated**: October 24, 2025  
> **Version**: 3.0 (Full MCP Feature Set with Memory)

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Production Deployment](#-production-deployment)
3. [Quick Start](#-quick-start)
4. [Testing with MCP Inspector](#-testing-with-mcp-inspector)
5. [LangGraph Integration](#-langgraph-integration)
6. [Local Development](#-local-development)
7. [Documentation](#-documentation)
8. [Architecture](#-architecture)
9. [Key Features](#-key-features)
10. [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This project implements a **production-ready Model Context Protocol (MCP) server** for Hong Kong's MTR (Mass Transit Railway) system, integrated with **LangGraph agents** and **AWS Bedrock Nova Lite** for natural language interactions.

### What's Included

- ✅ **Full MCP Server** with Tools, Resources, and Prompts
- ✅ **LangGraph Agent** with conversation memory
- ✅ **Natural Language Processing** for 93 MTR stations
- ✅ **Dual Tool Interface** (human-friendly + machine-readable)
- ✅ **Real-time MTR Data** from Hong Kong government API
- ✅ **Production Deployment** with SSL/TLS on NGINX
- ✅ **LangSmith Integration** for observability
- ✅ **Complete Test Suite** with 6 test files

### Technologies

- **MCP Server**: FastMCP (Python) + FastAPI
- **LLM Framework**: LangGraph + LangChain
- **AI Model**: AWS Bedrock Nova Lite
- **Transport**: Server-Sent Events (SSE)
- **Memory**: MemorySaver (persistent conversations)
- **Deployment**: Docker + NGINX reverse proxy

---

## 🌐 Production Deployment

**🚀 LIVE SERVER**: The MCP server is deployed and ready to use!

### Endpoints

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **SSE (Main)** | `https://project-1-04.eduhk.hk/mcp/sse` | Streamable HTTP for MCP clients |
| **Health** | `https://project-1-04.eduhk.hk/mcp/health` | Server health status |
| **Info** | `https://project-1-04.eduhk.hk/mcp/info` | Server capabilities |
| **Docs** | `https://project-1-04.eduhk.hk/mcp/docs` | API documentation |

### Architecture

```
Internet (HTTPS:443)
    ↓
NGINX Reverse Proxy
    ├─ SSL/TLS termination
    ├─ SSE-optimized (no buffering)
    └─ Location: /mcp/ → http://127.0.0.1:8080/mcp/
    ↓
Docker Container (:8080)
    ├─ Python 3.11 slim
    ├─ Health checks
    └─ Auto-restart
    ↓
FastAPI Application (fastapi_mcp_integration.py)
    ├─ MCP Protocol: 2025-06-18 (Streamable HTTP)
    ├─ SSE connection handling
    └─ JSON-RPC message routing
    ↓
MCP Server (mcp_server.py)
    ├─ 2 Tools (train schedules)
    ├─ 2 Resources (stations, network)
    └─ 3 Prompts (journey planning)
    ↓
MTR API (data.gov.hk)
```

### Deployment Features

- ✅ **MCP Protocol**: 2025-06-18 (Streamable HTTP)
- ✅ **SSL/TLS**: Encrypted HTTPS connections
- ✅ **NGINX**: SSE-optimized reverse proxy configuration
- ✅ **Docker**: Containerized deployment with health checks
- ✅ **24/7 Uptime**: Production-ready with monitoring
- ✅ **Auto-Restart**: Container restarts on failure

### Quick Test

```bash
# Health check
curl https://project-1-04.eduhk.hk/mcp/health

# Expected: {"status":"healthy","service":"mtr-mcp-server",...}

# SSE endpoint (streaming)
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Expected: event: message
#           data: {"jsonrpc":"2.0",...}
```

---

## 🚀 Quick Start

### 1. Installation

```powershell
# Clone or navigate to project directory
cd C:\Users\user\Documents\mtr-mcp-fastapi-example

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
# AWS Bedrock Credentials (required for LangGraph demo)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
BEDROCK_MODEL=amazon.nova-lite-v1:0

# MCP Server - Use production server (no local setup needed!)
MCP_SERVER_URL=https://project-1-04.eduhk.hk/mcp/sse

# Alternative: Use local development server
# MCP_SERVER_URL=http://localhost:8080/mcp/sse

# LangSmith (Optional - for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=mtr-demo
```

### 3. Run LangGraph Demo

**No local MCP server needed!** Just run:

```powershell
# Run the full MCP demo with production server
python langgraph_demo_full_mcp.py
```

**What happens:**
1. ✅ Connects to production MCP server at `https://project-1-04.eduhk.hk/mcp/sse`
2. ✅ Loads MCP resources (93 MTR stations, network map)
3. ✅ Creates LangGraph agent with MCP tools
4. ✅ Demonstrates 5-turn conversation with memory
5. ✅ Shows context-aware multi-turn interactions

**Sample Output:**

```
✓ MCP Server URL: https://project-1-04.eduhk.hk/mcp/sse
  (Using deployed production server)
✓ Environment variables loaded
✓ Using model: amazon.nova-lite-v1:0

🚀 Connecting to MCP server...
   ✓ Attempting to connect to https://project-1-04.eduhk.hk/mcp/sse

📚 Loading MCP Resources...
   Found 2 resources:
   - mtr://stations/list: MTR Stations List
   - mtr://lines/map: MTR Lines Map
   ✓ Loaded station reference

🔧 Loading MCP Tools...
   Found 2 tools:
   - get_next_train_schedule: Get MTR train schedule
   - get_next_train_structured: Get structured JSON data

🤖 Building LangGraph Agent...
   ✓ Agent ready with Tools, Resources, and Prompts

💬 Starting Multi-turn Conversation with Memory
...
```

---

## 🧪 Testing with MCP Inspector

### GUI Mode

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector
```

**Configuration:**
- **Connection Type**: Direct
- **Server URL**: `https://project-1-04.eduhk.hk/mcp/sse`

**What you can test:**

1. **Tools Tab**
   - `get_next_train_schedule` - Human-friendly format
   - `get_next_train_structured` - JSON format
   - Test with parameters: `line=TKL`, `sta=TKO`

2. **Resources Tab**
   - `mtr://stations/list` - View all 93 stations with codes
   - `mtr://lines/map` - View network topology

3. **Prompts Tab**
   - `check_next_train` - Quick schedule check
   - `plan_mtr_journey` - Multi-step journey planning
   - `compare_stations` - Station comparison

4. **Real-time Testing**
   - Execute tools and see live MTR data
   - View SSE message streams
   - Debug protocol messages

### CLI Mode

```bash
# List available tools
npx @modelcontextprotocol/inspector --cli \
  https://project-1-04.eduhk.hk/mcp/sse \
  --method tools/list

# Call a tool
npx @modelcontextprotocol/inspector --cli \
  https://project-1-04.eduhk.hk/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line=TKL \
  --tool-arg sta=TKO

# Read a resource
npx @modelcontextprotocol/inspector --cli \
  https://project-1-04.eduhk.hk/mcp/sse \
  --method resources/read \
  --uri mtr://stations/list
```

---

## 🤖 LangGraph Integration

### Architecture

The LangGraph agent uses the MCP server to provide natural language access to MTR data:

```
User Query
    ↓
LangGraph Agent (AWS Bedrock Nova Lite)
    ↓
Decision: Need MTR data?
    ├─ YES → Call MCP Tool
    │         ↓
    │      MCP Server (production)
    │         ↓
    │      MTR API
    │         ↓
    │      Return data to agent
    │         ↓
    │      Format response
    └─ NO → Use memory/knowledge
    ↓
Natural language response
    ↓
Save to memory (for next turn)
```

### Memory & Multi-turn Context

The agent maintains conversation history:

```python
# Turn 1
User: "When is the next train at Tseung Kwan O?"
Agent: [Calls MCP tool] "Next train in 3 minutes to LOHAS Park"
Memory: Saves "Tseung Kwan O" context

# Turn 2 (references previous)
User: "What about the other direction?"
Agent: [Uses memory] "Next train in 5 minutes to North Point"

# Turn 3
User: "Compare it with Hong Kong station"
Agent: [Remembers TKO] [Calls tool for HOK] [Compares both]
```

### Key Features

- ✅ **Tools**: 2 MCP tools (human + machine formats)
- ✅ **Resources**: 2 MCP resources (stations + network)
- ✅ **Prompts**: 3 MCP prompts (templates)
- ✅ **Memory**: MemorySaver for conversation history
- ✅ **Context**: Multi-turn context awareness

---

## 💻 Local Development (Optional)

If you want to run your own MCP server locally for development:

### Start Local Server

```powershell
# Option A: FastAPI integration (recommended)
python fastapi_mcp_integration.py

# Option B: Original MCP server
python mcp_server.py
```

**Expected output:**

```
============================================================
🚀 Starting MTR MCP Server under /mcp
============================================================
🌐 Server: http://0.0.0.0:8080
📡 SSE Endpoint: http://0.0.0.0:8080/mcp/sse
📖 API Docs: http://0.0.0.0:8080/mcp/docs
🔍 Health Check: http://0.0.0.0:8080/mcp/health
============================================================
```

### Local Endpoints

- **SSE**: `http://localhost:8080/mcp/sse`
- **Health**: `http://localhost:8080/mcp/health`
- **Info**: `http://localhost:8080/mcp/info`
- **Docs**: `http://localhost:8080/mcp/docs`

### Docker Deployment

```bash
# Build and run locally
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### When to Use Local vs Production

**Use Production (`https://project-1-04.eduhk.hk/mcp/sse`) when:**
- ✅ Demonstrating to others
- ✅ Running on machines without Docker
- ✅ Sharing with remote collaborators
- ✅ Final validation before changes

**Use Local (`http://localhost:8080/mcp/sse`) when:**
- 🔧 Developing new MCP features
- 🐛 Testing protocol changes
- 🔍 Debugging with breakpoints
- 📝 Iterating on prompts/tools

---

## 📚 Documentation

This repository contains **comprehensive documentation**:

### Core Documents

1. **[README.md](./README.md)** (This file)
   - Project overview
   - Production deployment info
   - Quick start guide
   - Testing instructions

2. **[MCP_GUIDE.md](./MCP_GUIDE.md)**
   - Complete MCP protocol reference
   - Protocol specification (2025-06-18)
   - FastAPI implementation guide
   - MCP Inspector usage
   - Debugging & troubleshooting
   - LangGraph integration patterns

3. **[MTR_API.md](./MTR_API.md)**
   - MTR API documentation
   - All 10 lines and 93 stations
   - API endpoints and parameters
   - Response formats
   - Code examples (Python, JavaScript, React)

4. **[DEPLOYMENT_INFO.md](./DEPLOYMENT_INFO.md)**
   - Detailed deployment architecture
   - Security best practices
   - Troubleshooting guide
   - Protocol version comparison
   - NGINX configuration

### Key Topics

- **MCP Protocol**: What is MCP, why it matters, three primitives (Tools, Resources, Prompts)
- **Streamable HTTP**: Latest protocol version (2025-06-18) with SSE transport
- **FastAPI Integration**: How `fastapi_mcp_integration.py` implements MCP
- **Production Deployment**: NGINX configuration, Docker setup, SSL/TLS
- **LangGraph Agents**: Building AI agents with MCP tools and memory
- **System Prompts**: Guiding AI behavior with MTR domain knowledge
- **LangSmith**: Observability and tracing for LLM applications

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   CLIENT LAYER                          │
│  • MCP Inspector (debugging)                            │
│  • LangGraph Agent (AI application)                     │
│  • Custom clients (your applications)                   │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS/SSE
┌──────────────────▼──────────────────────────────────────┐
│               TRANSPORT LAYER                           │
│  • NGINX Reverse Proxy                                  │
│  • SSL/TLS Termination                                  │
│  • SSE Optimization (no buffering)                      │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP
┌──────────────────▼──────────────────────────────────────┐
│              APPLICATION LAYER                          │
│  • FastAPI (fastapi_mcp_integration.py)                 │
│  • MCP Protocol Handler (2025-06-18)                    │
│  • JSON-RPC Message Router                              │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                MCP SERVER LAYER                         │
│  • MCP Business Logic (mcp_server.py)                   │
│  • Tools: get_next_train_schedule,                      │
│           get_next_train_structured                     │
│  • Resources: mtr://stations/list,                      │
│               mtr://lines/map                           │
│  • Prompts: check_next_train,                           │
│             plan_mtr_journey,                           │
│             compare_stations                            │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│                 DATA LAYER                              │
│  • MTR Next Train API (data.gov.hk)                     │
│  • Real-time train schedules                            │
│  • 10 lines, 93 stations                                │
└─────────────────────────────────────────────────────────┘
```

### File Structure

```
mtr-mcp-fastapi-example/
├── README.md                          # This file (complete guide)
├── MCP_GUIDE.md                       # MCP protocol reference
├── MTR_API.md                         # MTR API documentation
├── DEPLOYMENT_INFO.md                 # Deployment details
│
├── fastapi_mcp_integration.py         # FastAPI + MCP (deployed)
├── mcp_server.py                      # MCP business logic
├── langgraph_demo_full_mcp.py         # LangGraph demo
│
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Docker configuration
├── Dockerfile                         # Container definition
├── .env                               # Environment variables
│
└── test_*.py                          # Test suite (6 files)
```

---

## ✨ Key Features

### MCP Features (Complete Implementation)

| Feature Type | Count | Examples |
|--------------|-------|----------|
| **Tools** | 2 | `get_next_train_schedule`, `get_next_train_structured` |
| **Resources** | 2 | `mtr://stations/list`, `mtr://lines/map` |
| **Prompts** | 3 | `check_next_train`, `plan_mtr_journey`, `compare_stations` |

### Tool 1: `get_next_train_schedule` (Human-Friendly)

**Purpose**: Display train schedules in readable format

**Input**: `line="TKL"`, `sta="TKO"`, `lang="EN"`

**Output Example**:
```
🚇 MTR Train Schedule for TKL-TKO
🕐 Current Time: 2025-10-24 14:30:00

🔼 UPBOUND Trains:
  1. 🚆 Platform 1 → LHP - 2 minutes
  2. 🚆 Platform 1 → LHP - 8 minutes

🔽 DOWNBOUND Trains:
  1. 🚆 Platform 2 → NOP - 3 minutes

✅ Status: Normal operation
```

### Tool 2: `get_next_train_structured` (Machine-Readable)

**Purpose**: Provide structured JSON for programmatic access

**Input**: `line="TKL"`, `sta="TKO"`, `lang="EN"`

**Output Example**:
```json
{
  "resolved_line": "TKL",
  "resolved_station": "TKO",
  "timestamp": "2025-10-24 14:30:00",
  "up": [
    {"dest": "LHP", "ttnt": "2", "plat": "1", "time": "14:32:00"}
  ],
  "down": [
    {"dest": "NOP", "ttnt": "3", "plat": "2", "time": "14:33:00"}
  ],
  "error": null
}
```

### Natural Language Support

- ✅ **93 MTR Stations** with fuzzy matching
- ✅ **Full Names**: `"Tseung Kwan O"` → `"TKO"`
- ✅ **Line Names**: `"Airport Express"` → `"AEL"`
- ✅ **Case-insensitive**: `"hong kong"` works
- ✅ **Typo-tolerant**: `"Tseng Kwan O"` → `"TKO"`

### Supported MTR Lines

| Line Code | Name | Stations | Example Stations |
|-----------|------|----------|------------------|
| **TKL** | Tseung Kwan O | 8 | TKO, LHP, POA, NOP |
| **AEL** | Airport Express | 5 | HOK, KOW, AIR, AWE |
| **ISL** | Island Line | 17 | KET, ADM, CEN, CHW |
| **TCL** | Tung Chung Line | 8 | HOK, OLY, TSY, TUC |
| **TML** | Tuen Ma Line | 27 | WKS, DIH, HOM, TUM |
| **EAL** | East Rail Line | 16 | ADM, UNI, SHS, LMC |
| **SIL** | South Island Line | 5 | ADM, OCP, SOH |
| **TWL** | Tsuen Wan Line | 16 | TST, MOK, LAK, TSW |
| **KTL** | Kwun Tong Line | 17 | WHA, YMT, DIH, TIK |
| **DRL** | Disneyland | 2 | SUN, DIS |

---

## 🐛 Troubleshooting

### Connection Errors

**Symptom**: "Failed to connect to MCP server"

**Solution**:
```bash
# 1. Verify server is reachable
curl https://project-1-04.eduhk.hk/mcp/health

# Expected: {"status":"healthy",...}

# 2. Test SSE endpoint
curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse

# Expected: event: message
#           data: {"jsonrpc":"2.0",...}

# 3. Check your MCP_SERVER_URL in .env
echo $env:MCP_SERVER_URL  # PowerShell
```

### Protocol Errors

**Symptom**: "Invalid protocol version" or "Method not found"

**Solution**:
- ✅ Ensure you're using protocol version `2025-06-18`
- ✅ Update MCP SDK: `pip install --upgrade mcp`
- ✅ Check server sends `"protocolVersion": "2025-06-18"` in initialize response

### AWS Bedrock Errors

**Symptom**: "AWS credentials not configured"

**Solution**:
```powershell
# Option 1: Set in .env file
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# Option 2: AWS CLI
aws configure
```

### MCP Inspector Connection Issues

**Symptom**: Inspector shows "Connection Error"

**Solution**:
1. **Check server URL**: `https://project-1-04.eduhk.hk/mcp/sse`
2. **Connection Type**: Use "Direct" (not Proxy)
3. **Test manually**: `curl -N -H "Accept: text/event-stream" https://project-1-04.eduhk.hk/mcp/sse`
4. **Browser console**: Check for CORS or SSL errors

### LangGraph Demo Errors

**Symptom**: Demo fails to start

**Common fixes**:
```powershell
# 1. Check environment variables
cat .env

# 2. Test MCP connection independently
curl https://project-1-04.eduhk.hk/mcp/health

# 3. Verify AWS credentials
python test_01_aws_bedrock.py

# 4. Check Python dependencies
pip install -r requirements.txt --upgrade
```

---

## 📖 Learn More

### Official Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP GitHub**: https://github.com/modelcontextprotocol
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangSmith**: https://docs.smith.langchain.com/
- **MTR Open Data**: https://data.gov.hk/en-data/dataset/mtr-data2-nexttrain-data

### Project Resources

- **GitHub Repository**: https://github.com/enoch-sit/mtrmcp
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **FastMCP**: https://github.com/jlowin/fastmcp

---

## 🤝 Contributing

This is an educational project for learning MCP, FastAPI, and LangGraph.

**To contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with MCP Inspector
5. Submit a pull request

---

## 📝 License

MIT License (if applicable)

---

## 🎉 Summary

### What This Project Demonstrates

✅ **Complete MCP Protocol** - All three primitives (Tools, Resources, Prompts)  
✅ **Production Deployment** - NGINX + Docker + SSL/TLS  
✅ **Streamable HTTP** - Latest MCP protocol (2025-06-18)  
✅ **LangGraph Integration** - AI agents with memory  
✅ **Real-world API** - Hong Kong MTR live data  
✅ **Natural Language** - Fuzzy matching for 93 stations  
✅ **Dual Interfaces** - Human-friendly + machine-readable  
✅ **Testing Tools** - MCP Inspector + complete test suite  
✅ **Observability** - LangSmith tracing  
✅ **Documentation** - Comprehensive guides  

### Quick Commands

```bash
# Test production server
curl https://project-1-04.eduhk.hk/mcp/health

# Use MCP Inspector
npx @modelcontextprotocol/inspector

# Run LangGraph demo
python langgraph_demo_full_mcp.py
```

---

**Deployment Status**: ✅ Production Ready  
**Server URL**: `https://project-1-04.eduhk.hk/mcp/sse`  
**Last Updated**: October 24, 2025  
**Maintainer**: Project Team
