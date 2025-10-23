# 🔍 Complete MCP Inspector Guide
## For Beginners: Understanding, Using, and Debugging MCP Servers

---

## 📚 Table of Contents

1. [What is MCP? - The Big Picture](#what-is-mcp---the-big-picture)
2. [What is MCP Inspector?](#what-is-mcp-inspector)
3. [Architecture Deep Dive](#architecture-deep-dive)
4. [Getting Started](#getting-started)
5. [UI Mode - Visual Testing](#ui-mode---visual-testing)
6. [CLI Mode - Automation & Scripting](#cli-mode---automation--scripting)
7. [Connecting to Different Server Types](#connecting-to-different-server-types)
8. [Debugging Your MCP Server](#debugging-your-mcp-server)
9. [Security & Best Practices](#security--best-practices)
10. [Practical Examples](#practical-examples)
11. [Common Issues & Solutions](#common-issues--solutions)

---

## 🎯 What is MCP? - The Big Picture

### The Problem MCP Solves

Imagine you're building an AI application and you need it to:
- Access your database
- Read files from your system
- Call external APIs
- Perform calculations

Without MCP, you'd have to:
1. Write custom code for each integration
2. Figure out authentication/authorization each time
3. Handle errors differently for each service
4. Maintain multiple connection protocols

### Enter MCP (Model Context Protocol)

**MCP is a standardized protocol that lets AI applications ("clients") communicate with data sources and tools ("servers")** in a consistent way.

Think of it like **HTTP for AI** - just like HTTP standardized how web browsers talk to websites, MCP standardizes how AI talks to tools and data.

### MCP Core Concepts

```
┌─────────────┐                    ┌──────────────┐
│  AI Client  │ ◄──── MCP ────────►│  MCP Server  │
│  (Claude,   │                    │  (Your MTR   │
│   GPT, etc) │                    │   Server)    │
└─────────────┘                    └──────────────┘
```

#### 1. **Tools** 🛠️
Functions that the AI can call to perform actions.

**Example from your MTR server:**
```python
@mcp.tool()
def get_next_train_schedule(line: str, sta: str):
    """Get next train arrival times"""
    # Returns: "Next trains at Central: 2 mins, 5 mins, 8 mins"
```

**Why it matters:** The AI can now "call" this function when a user asks about trains!

#### 2. **Resources** 📚
Data or information the AI can read.

**Example:**
```
Resource URI: mtr://stations/list
Content: List of all 80+ MTR stations
```

**Why it matters:** The AI can access your data without you hardcoding it!

#### 3. **Prompts** 💬
Pre-written templates that help users interact with your server.

**Example:**
```
Prompt: "check_next_train"
Template: "Check next train for {station} on {line}"
```

**Why it matters:** Guides users on how to use your tools effectively!

---

## 🔍 What is MCP Inspector?

**MCP Inspector is a developer tool that lets you test, debug, and understand your MCP server BEFORE connecting it to an AI.**

### Think of it like:
- **Postman** for REST APIs
- **Browser DevTools** for web pages
- **Database GUI** for SQL databases

But specifically designed for MCP servers!

### Why You Need It

Without MCP Inspector, you'd be:
❌ Flying blind - no way to see if your server works
❌ Guessing - no visibility into what data is being sent/received
❌ Slow debugging - need to connect to real AI to test

With MCP Inspector:
✅ See exactly what your server exposes
✅ Test tools with real inputs
✅ Debug errors in real-time
✅ Validate your server before production

---

## 🏗️ Architecture Deep Dive

### The Two Components

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Inspector System                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐           ┌──────────────────┐      │
│  │  MCP Inspector   │           │   MCP Proxy      │      │
│  │  Client (MCPI)   │ ◄────────►│   Server (MCPP)  │      │
│  │                  │           │                  │      │
│  │  React Web UI    │   HTTP    │  Node.js Server  │      │
│  │  Port: 6274      │           │  Port: 6277      │      │
│  └──────────────────┘           └──────────────────┘      │
│                                          │                  │
│                                          │ MCP Protocol     │
│                                          ▼                  │
│                                  ┌──────────────────┐      │
│                                  │   Your MCP       │      │
│                                  │   Server         │      │
│                                  │  (MTR Server)    │      │
│                                  └──────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. **MCP Inspector Client (MCPI)** - The UI
- **What:** React-based web interface
- **Port:** 6274 (MCPI on phone keypad)
- **Purpose:** Visual testing and exploration
- **You see:** Forms, buttons, JSON responses, real-time updates

**User Experience:**
```
Browser: http://localhost:6274
┌────────────────────────────────────────┐
│  [Connect to Server]  [Tools] [Config] │
│                                        │
│  Available Tools:                      │
│  ☑ get_next_train_schedule            │
│  ☑ get_next_train_structured          │
│                                        │
│  [Test Tool] ▶                        │
└────────────────────────────────────────┘
```

#### 2. **MCP Proxy Server (MCPP)** - The Bridge
- **What:** Node.js backend server
- **Port:** 6277 (MCPP on phone keypad)
- **Purpose:** Protocol translation
- **Handles:** STDIO, SSE, Streamable HTTP

**Why it exists:**
```
Browser can't talk STDIO → Proxy converts → STDIO Server ✅
Browser can't spawn processes → Proxy handles it ✅
Browser has CORS limits → Proxy bypasses ✅
```

#### 3. **Your MCP Server** - The Thing Being Tested
- **What:** Your actual MCP server (like MTR server)
- **Port:** Variable (yours is 8080)
- **Purpose:** Provides tools/resources/prompts
- **Protocols:** SSE, Streamable HTTP, STDIO

---

## 🚀 Getting Started

### Installation

**Option 1: Quick Start (No Installation)**
```bash
npx @modelcontextprotocol/inspector
```
Opens on `http://localhost:6274`

**Option 2: Test Specific Server**
```bash
npx @modelcontextprotocol/inspector node build/index.js
```

**Option 3: Test Remote Server (Your MTR Server)**
```bash
npx @modelcontextprotocol/inspector
# Then in UI: Enter http://localhost:8080/mcp/sse
```

**Option 4: Docker**
```bash
docker run --rm --network host -p 6274:6274 -p 6277:6277 \
  ghcr.io/modelcontextprotocol/inspector:latest
```

### First Connection - Step by Step

#### Step 1: Start Your MCP Server
```bash
# Your MTR server
docker-compose up -d mtr-mcp-server

# Verify it's running
curl http://localhost:8080/mcp/health
```

#### Step 2: Open MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```
Browser opens at: `http://localhost:6274`

#### Step 3: Configure Connection

**In the Inspector UI:**

1. **Select Transport Type:** SSE (for your server)
2. **Enter Server URL:** `http://localhost:8080/mcp/sse`
3. **Connection Type:** Direct (since no proxy needed)
4. **Click:** Connect

**Authentication (if enabled):**
- You'll see a session token in your terminal
- Enter it in the "Proxy Session Token" field
- Or use the pre-filled URL from terminal

#### Step 4: Explore Your Server

Once connected, you'll see:

```
✅ Connected to mtr_next_train

📦 Tools (2)
  • get_next_train_schedule
  • get_next_train_structured

📚 Resources (2)
  • mtr://stations/list
  • mtr://lines/map

📝 Prompts (3)
  • check_next_train
  • plan_mtr_journey
  • compare_stations
```

---

## 🎨 UI Mode - Visual Testing

### Overview of UI Sections

```
┌─────────────────────────────────────────────────────────┐
│  MCP Inspector                    [⚙️ Config] [📋 Export]│
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────────────────────┐ │
│  │  Sidebar    │  │    Main Panel                    │ │
│  │             │  │                                  │ │
│  │  Connection │  │  ┌────────────────────────────┐ │ │
│  │  Settings   │  │  │  Tools Tab                 │ │ │
│  │             │  │  │  - List all tools          │ │ │
│  │  Transport: │  │  │  - Test with parameters    │ │ │
│  │  ◉ SSE      │  │  │  - See responses           │ │ │
│  │  ○ STDIO    │  │  └────────────────────────────┘ │ │
│  │  ○ HTTP     │  │                                  │ │
│  │             │  │  ┌────────────────────────────┐ │ │
│  │  URL:       │  │  │  Resources Tab             │ │ │
│  │  [____]     │  │  │  - Browse resources        │ │ │
│  │             │  │  │  - View content            │ │ │
│  │  [Connect]  │  │  └────────────────────────────┘ │ │
│  │             │  │                                  │ │
│  │  Status:    │  │  ┌────────────────────────────┐ │ │
│  │  🟢 Active  │  │  │  Prompts Tab               │ │ │
│  │             │  │  │  - Test prompts            │ │ │
│  │             │  │  │  - Fill parameters         │ │ │
│  └─────────────┘  │  └────────────────────────────┘ │ │
│                   │                                  │ │
│                   │  Request History (bottom)        │ │
│                   │  ┌────────────────────────────┐ │ │
│                   │  │ → tools/list     200 OK    │ │ │
│                   │  │ → tools/call     200 OK    │ │ │
│                   │  └────────────────────────────┘ │ │
│                   └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Testing Tools

#### Example: Test `get_next_train_schedule`

**Step 1: Select Tool**
- Click "Tools" tab
- Find `get_next_train_schedule`
- Click "Test Tool"

**Step 2: Fill Parameters**
```
Field: line
Value: Island Line

Field: sta  
Value: Central

Field: lang
Value: EN
```

**Step 3: Execute**
- Click "Call Tool"
- See real-time response

**Expected Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Next trains at Central:\n- Platform 1: 2 mins\n- Platform 1: 5 mins\n- Platform 1: 8 mins"
    }
  ]
}
```

### Testing Resources

#### Example: Browse MTR Stations

**Step 1: Navigate**
- Click "Resources" tab
- See: `mtr://stations/list`

**Step 2: Read Resource**
- Click on the resource
- View JSON content

**Response:**
```json
{
  "stations": [
    {"code": "CEN", "name": "Central", "line": "Island Line"},
    {"code": "ADM", "name": "Admiralty", "line": "Island Line"},
    ...
  ]
}
```

### Testing Prompts

#### Example: Use `check_next_train` Prompt

**Step 1: Select Prompt**
- Click "Prompts" tab
- Choose `check_next_train`

**Step 2: Fill Template**
```
Station: Central
Line: Island Line
```

**Step 3: Execute**
- Click "Get Prompt"
- See formatted prompt
- Can use this with AI

**Result:**
```
System: You are helping with MTR train schedules
User: Check the next train for Central station on Island Line
```

### Request History

**Bottom panel shows:**
```
┌────────────────────────────────────────────────┐
│ Request History                                │
├────────────────────────────────────────────────┤
│ ▶ tools/list                      200 OK  1.2s │
│ ▶ tools/call: get_next_train...  200 OK  0.8s │
│ ▶ resources/read: mtr://...      200 OK  0.3s │
│ ▶ prompts/get: check_next_train  200 OK  0.5s │
└────────────────────────────────────────────────┘
```

**Click any request to:**
- See full request body
- View complete response
- Debug errors
- Copy for CLI use

---

## ⌨️ CLI Mode - Automation & Scripting

### Why Use CLI Mode?

Perfect for:
- **Automation:** CI/CD pipelines
- **Scripting:** Batch testing
- **AI Integration:** Cursor, GitHub Copilot
- **Quick Testing:** No UI needed
- **Documentation:** Generate examples

### Basic CLI Usage

```bash
# Start in CLI mode
npx @modelcontextprotocol/inspector --cli node build/index.js
```

### Common CLI Commands

#### 1. **List All Tools**
```bash
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method tools/list
```

**Output:**
```json
{
  "tools": [
    {
      "name": "get_next_train_schedule",
      "description": "Get next train arrival schedule",
      "inputSchema": {
        "type": "object",
        "properties": {
          "line": {"type": "string"},
          "sta": {"type": "string"}
        }
      }
    }
  ]
}
```

#### 2. **Call a Tool**
```bash
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="Island Line" \
  --tool-arg sta="Central"
```

**Output:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Next trains at Central: 2 mins, 5 mins, 8 mins"
    }
  ]
}
```

#### 3. **List Resources**
```bash
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method resources/list
```

#### 4. **Read a Resource**
```bash
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method resources/read \
  --resource-uri "mtr://stations/list"
```

#### 5. **Get a Prompt**
```bash
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method prompts/get \
  --prompt-name check_next_train \
  --prompt-arg station="Central"
```

### CLI with Remote Servers (Your MTR Server)

```bash
# Connect to remote SSE server
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/list

# Call tool on remote server
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="Island Line" \
  --tool-arg sta="Central"
```

### CLI with Config Files

**Create `mcp-config.json`:**
```json
{
  "mcpServers": {
    "mtr-server": {
      "type": "sse",
      "url": "http://localhost:8080/mcp/sse"
    }
  }
}
```

**Use it:**
```bash
npx @modelcontextprotocol/inspector --cli \
  --config mcp-config.json \
  --server mtr-server \
  --method tools/list
```

### Advanced CLI: JSON Arguments

```bash
# Pass complex JSON
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method tools/call \
  --tool-name get_next_train_structured \
  --tool-arg 'options={"format": "json", "include_delays": true}'
```

### CLI with Custom Headers (HTTPS)

```bash
npx @modelcontextprotocol/inspector --cli \
  https://your-mcp-server.com/mcp/sse \
  --transport http \
  --method tools/list \
  --header "Authorization: Bearer your-token" \
  --header "X-API-Key: your-api-key"
```

---

## 🔌 Connecting to Different Server Types

### Understanding Transport Types

```
┌─────────────────────────────────────────────────────────┐
│              MCP Transport Protocols                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  STDIO (Standard Input/Output)                         │
│  ├─ Local processes only                               │
│  ├─ Command-line servers                               │
│  └─ Example: node server.js                            │
│                                                         │
│  SSE (Server-Sent Events)                              │
│  ├─ HTTP-based streaming                               │
│  ├─ Remote servers                                     │
│  └─ Example: http://localhost:8080/mcp/sse  ← YOUR MTR │
│                                                         │
│  Streamable HTTP                                        │
│  ├─ HTTP with bi-directional streaming                 │
│  ├─ Remote servers                                     │
│  └─ Example: http://localhost:8080/mcp                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1. STDIO Transport (Local Servers)

**When to use:**
- Testing local development servers
- Command-line tools
- Servers that run as processes

**UI Configuration:**
```
Transport Type: STDIO
Command: node
Arguments: build/index.js
Environment: (optional)
  KEY=value
```

**CLI:**
```bash
npx @modelcontextprotocol/inspector node build/index.js

# With arguments
npx @modelcontextprotocol/inspector node build/index.js arg1 arg2

# With environment variables
npx @modelcontextprotocol/inspector \
  -e API_KEY=secret \
  -e DEBUG=true \
  node build/index.js
```

### 2. SSE Transport (Your MTR Server)

**When to use:**
- Remote HTTP servers
- FastAPI servers
- Cloud deployments

**UI Configuration:**
```
Transport Type: SSE
Server URL: http://localhost:8080/mcp/sse
Connection Type: Direct
```

**CLI:**
```bash
# Local server
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/list

# Remote HTTPS server
npx @modelcontextprotocol/inspector --cli \
  https://yourdomain.com:8080/mcp/sse \
  --method tools/list
```

### 3. Streamable HTTP Transport

**When to use:**
- Bidirectional streaming needed
- Modern HTTP/2 or HTTP/3 servers

**UI Configuration:**
```
Transport Type: Streamable HTTP
Server URL: http://localhost:8080/mcp
Connection Type: Direct
```

**CLI:**
```bash
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp \
  --transport http \
  --method tools/list
```

### Configuration Files

**Create `mcp.json`:**
```json
{
  "mcpServers": {
    "local-stdio": {
      "type": "stdio",
      "command": "node",
      "args": ["build/index.js"],
      "env": {
        "DEBUG": "true"
      }
    },
    "mtr-sse": {
      "type": "sse",
      "url": "http://localhost:8080/mcp/sse"
    },
    "remote-https": {
      "type": "sse",
      "url": "https://production.example.com/mcp/sse"
    }
  }
}
```

**Use in UI:**
- Import config file
- Select server from dropdown

**Use in CLI:**
```bash
npx @modelcontextprotocol/inspector --cli \
  --config mcp.json \
  --server mtr-sse \
  --method tools/list
```

---

## 🐛 Debugging Your MCP Server

### Debug Workflow

```
1. Server Not Responding
   ↓
2. Check Connection
   ↓
3. Verify Tools/Resources
   ↓
4. Test with Real Data
   ↓
5. Check Logs
   ↓
6. Fix Issues
   ↓
7. Re-test
```

### Common Issues & How Inspector Helps

#### Issue 1: Server Won't Connect

**Symptoms:**
```
❌ Connection failed
❌ Timeout error
❌ 404 Not Found
```

**Debug Steps:**

1. **Check Server is Running**
```bash
# Your MTR server
curl http://localhost:8080/mcp/health

# Should return:
{"status":"healthy"...}
```

2. **Verify URL in Inspector**
```
✅ Correct: http://localhost:8080/mcp/sse
❌ Wrong: http://localhost:8080/sse
❌ Wrong: http://localhost:8080/mcp
```

3. **Check Connection Type**
```
For remote servers: Use "Direct"
For local stdio: Use "Proxy"
```

4. **View Inspector Logs**
```
Inspector Terminal:
- Connection attempts
- Error messages
- Authentication issues
```

#### Issue 2: Tool Not Working

**Symptoms:**
```
❌ Tool executes but returns error
❌ Wrong output
❌ Missing parameters
```

**Debug Steps:**

1. **Check Tool Schema**
```javascript
// In Inspector UI: Tools → tool_name → View Schema

{
  "inputSchema": {
    "type": "object",
    "properties": {
      "line": {"type": "string", "required": true},
      "sta": {"type": "string", "required": true}
    }
  }
}
```

2. **Test with Known Good Data**
```bash
# Start simple
--tool-arg line="Island Line"
--tool-arg sta="Central"

# Then add complexity
--tool-arg line="Island Line"
--tool-arg sta="Central"
--tool-arg lang="EN"
```

3. **Check Request History**
```
Inspector UI → Bottom Panel → Request History
- Click failed request
- See exact JSON sent
- Compare with expected format
```

4. **Validate Response Format**
```json
// MCP expects this format:
{
  "content": [
    {
      "type": "text",
      "text": "Your response here"
    }
  ]
}

// Not this:
{
  "result": "Your response here"  // ❌ Wrong!
}
```

#### Issue 3: Resource Not Found

**Symptoms:**
```
❌ 404 on resource URI
❌ Empty resource list
```

**Debug Steps:**

1. **List All Resources First**
```bash
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method resources/list
```

2. **Check URI Format**
```
✅ Correct: mtr://stations/list
❌ Wrong: stations/list
❌ Wrong: /stations/list
```

3. **Test in UI**
```
Resources Tab → Click resource → Should load content
If fails → Check server logs
```

#### Issue 4: Authentication Errors

**Symptoms:**
```
❌ 401 Unauthorized
❌ 403 Forbidden
❌ Token required
```

**Debug Steps:**

1. **Get Session Token**
```bash
# When you start Inspector, you'll see:
🔑 Session token: abc123...
```

2. **Set in UI**
```
Config → Proxy Session Token → Paste token
```

3. **Or Use Pre-filled URL**
```bash
http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=abc123...
```

4. **For Remote Servers with Custom Auth**
```
In UI:
- Custom Headers section
- Add: Authorization: Bearer your-token

In CLI:
--header "Authorization: Bearer your-token"
```

### Debugging Best Practices

#### 1. **Start with List Operations**
```bash
# Always start here
--method tools/list      # See what's available
--method resources/list  # Check resources
--method prompts/list    # View prompts
```

#### 2. **Use Request History**
- Every request is logged
- Click to see full details
- Copy successful requests for documentation

#### 3. **Test Incrementally**
```
1. Connect to server ✓
2. List tools ✓
3. Call simple tool ✓
4. Call tool with parameters ✓
5. Call complex tool ✓
```

#### 4. **Compare UI vs CLI**
```
If UI works but CLI doesn't:
- Check CLI command format
- Verify URL/parameters match

If CLI works but UI doesn't:
- Check browser console
- Verify proxy is running
```

#### 5. **Enable Verbose Logging**
```bash
# Server side
DEBUG=* node build/index.js

# Inspector side
CLIENT_PORT=6274 SERVER_PORT=6277 npm run dev
```

---

## 🔒 Security & Best Practices

### Security Features

#### 1. **Authentication (Default: ON)**

**How it works:**
```bash
When you start Inspector:
🔑 Session token: 3a1c267f...

This token is required for ALL requests
```

**Why it's important:**
- Prevents unauthorized access
- Protects against RCE attacks
- Secures local process execution

**❌ NEVER DISABLE IN PRODUCTION**
```bash
# DON'T DO THIS unless you understand the risks
DANGEROUSLY_OMIT_AUTH=true npm start
```

#### 2. **Local-only Binding (Default: ON)**

**Default behavior:**
```
Inspector binds to: localhost (127.0.0.1)
Result: Only accessible from your machine
```

**To allow network access (DEVELOPMENT ONLY):**
```bash
HOST=0.0.0.0 npm start
⚠️  WARNING: Exposes to network!
```

#### 3. **DNS Rebinding Protection**

**What it prevents:**
- Malicious websites accessing your Inspector
- Cross-origin attacks

**How to configure:**
```bash
ALLOWED_ORIGINS=http://localhost:6274,http://localhost:8000 npm start
```

### Best Practices

#### 1. **For Development**

✅ **DO:**
- Use authentication
- Bind to localhost
- Use strong session tokens
- Keep Inspector updated
- Close Inspector when not in use

❌ **DON'T:**
- Disable authentication
- Expose to public internet
- Share session tokens
- Run as root/admin
- Leave Inspector running unattended

#### 2. **For Production Testing**

✅ **DO:**
- Test in isolated environment
- Use HTTPS for remote connections
- Rotate authentication tokens
- Monitor access logs
- Use VPN/private network

❌ **DON'T:**
- Test against production servers directly
- Use production credentials
- Expose Inspector publicly
- Skip authentication
- Test with real user data

#### 3. **For CI/CD Pipelines**

```bash
# Good: Automated testing in CI
npx @modelcontextprotocol/inspector --cli \
  node build/index.js \
  --method tools/list

# Use exit codes for validation
if [ $? -eq 0 ]; then
  echo "✅ MCP server tests passed"
else
  echo "❌ MCP server tests failed"
  exit 1
fi
```

---

## 💡 Practical Examples

### Example 1: Test Your MTR Server

**Scenario:** You just deployed your MTR MCP server and want to verify it works.

**Step-by-Step:**

```bash
# 1. Start your server
docker-compose up -d mtr-mcp-server

# 2. Open Inspector
npx @modelcontextprotocol/inspector

# 3. In UI:
#    - Transport: SSE
#    - URL: http://localhost:8080/mcp/sse
#    - Click Connect

# 4. Test listing stations
#    Tools → get_next_train_schedule
#    line: "Island Line"
#    sta: "Central"
#    Click "Call Tool"

# 5. Verify response
#    Should see: "Next trains at Central: ..."
```

**CLI Version:**
```bash
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="Island Line" \
  --tool-arg sta="Central"
```

### Example 2: Debug Why Tool Fails

**Scenario:** Your tool works in server but fails in Inspector.

```bash
# Step 1: List tools to see schema
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/list \
  | jq '.tools[] | select(.name=="get_next_train_schedule")'

# Output shows required parameters:
{
  "name": "get_next_train_schedule",
  "inputSchema": {
    "properties": {
      "line": {"type": "string"},
      "sta": {"type": "string"},
      "lang": {"type": "string", "default": "EN"}
    },
    "required": ["line", "sta"]
  }
}

# Step 2: Test with minimal required params
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="ISL" \
  --tool-arg sta="CEN"

# Step 3: Add optional parameters
npx @modelcontextprotocol/inspector --cli \
  http://localhost:8080/mcp/sse \
  --method tools/call \
  --tool-name get_next_train_schedule \
  --tool-arg line="ISL" \
  --tool-arg sta="CEN" \
  --tool-arg lang="EN"
```

### Example 3: Create Config for Claude Desktop

**Scenario:** You want to use your MTR server with Claude Desktop.

```bash
# Step 1: Open Inspector UI
npx @modelcontextprotocol/inspector

# Step 2: Configure your server
#    Transport: SSE
#    URL: http://localhost:8080/mcp/sse

# Step 3: Click "Server Entry" button
#    Copies this to clipboard:

{
  "type": "sse",
  "url": "http://localhost:8080/mcp/sse",
  "note": "For SSE connections, add this URL directly in your MCP Client"
}

# Step 4: Add to Claude config
#    File: ~/Library/Application Support/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "mtr-server": {
      "type": "sse",
      "url": "http://localhost:8080/mcp/sse"
    }
  }
}

# Step 5: Restart Claude Desktop
#    Now Claude can call your MTR tools!
```

### Example 4: Automated Testing in CI/CD

**Scenario:** Test your MCP server in GitHub Actions.

```yaml
# .github/workflows/test-mcp.yml
name: Test MCP Server

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '22'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build MCP server
        run: npm run build
      
      - name: Start MCP server
        run: |
          node build/index.js &
          sleep 5
      
      - name: Test with Inspector CLI
        run: |
          # Test 1: List tools
          npx @modelcontextprotocol/inspector --cli \
            node build/index.js \
            --method tools/list
          
          # Test 2: Call a tool
          npx @modelcontextprotocol/inspector --cli \
            node build/index.js \
            --method tools/call \
            --tool-name get_next_train_schedule \
            --tool-arg line="ISL" \
            --tool-arg sta="CEN"
          
          # Test 3: List resources
          npx @modelcontextprotocol/inspector --cli \
            node build/index.js \
            --method resources/list
```

---

## 🚨 Common Issues & Solutions

### Issue: "Connection Refused"

**Symptoms:**
```
Error: connect ECONNREFUSED 127.0.0.1:8080
```

**Solutions:**
```bash
# 1. Check server is running
curl http://localhost:8080/mcp/health

# 2. Verify port
netstat -tlnp | grep :8080

# 3. Check firewall
sudo ufw status

# 4. Try different URL formats
http://localhost:8080/mcp/sse  ✅
http://127.0.0.1:8080/mcp/sse  ✅
http://0.0.0.0:8080/mcp/sse    ❌
```

### Issue: "404 Not Found"

**Symptoms:**
```
Error: 404 Not Found on /sse
```

**Solutions:**
```bash
# Check exact endpoint path
✅ http://localhost:8080/mcp/sse
❌ http://localhost:8080/sse
❌ http://localhost:8080/mcp

# Verify server routes
curl -v http://localhost:8080/mcp/info
```

### Issue: "Timeout"

**Symptoms:**
```
Error: Request timeout after 30000ms
```

**Solutions:**
```bash
# 1. Increase timeout in Inspector Config
MCP_SERVER_REQUEST_TIMEOUT=60000

# 2. Check server performance
docker stats mtr-mcp-server

# 3. Test with simpler request first
--method tools/list  # Fast
--method tools/call  # Slower
```

### Issue: "Invalid JSON Response"

**Symptoms:**
```
Error: Unexpected token < in JSON
```

**Solutions:**
```python
# Server MUST return this format:
{
  "content": [
    {
      "type": "text",
      "text": "Your response"
    }
  ]
}

# NOT HTML:
<html>...</html>  # ❌

# NOT plain string:
"response"  # ❌
```

### Issue: "CORS Error"

**Symptoms:**
```
Access to fetch blocked by CORS policy
```

**Solutions:**
```python
# In your FastAPI server:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📖 Further Resources

### Official Documentation
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [Debugging Guide](https://modelcontextprotocol.io/docs/tools/debugging)

### Your MTR Server
- **Health Check:** `http://localhost:8080/mcp/health`
- **SSE Endpoint:** `http://localhost:8080/mcp/sse`
- **API Docs:** `http://localhost:8080/mcp/docs`
- **MCP Info:** `http://localhost:8080/mcp/info`

### Quick Reference

```bash
# Start Inspector
npx @modelcontextprotocol/inspector

# CLI mode
npx @modelcontextprotocol/inspector --cli http://localhost:8080/mcp/sse

# With config
npx @modelcontextprotocol/inspector --config mcp.json

# List tools
--method tools/list

# Call tool
--method tools/call --tool-name NAME --tool-arg key=value

# List resources
--method resources/list

# Read resource
--method resources/read --resource-uri URI

# Get prompts
--method prompts/list
```

---

## 🎓 Summary: From Zero to Hero

### What You've Learned

1. **MCP Basics**
   - What MCP is and why it matters
   - Tools, Resources, Prompts concepts
   - How MCP connects AI to your data

2. **MCP Inspector**
   - Architecture (MCPI + MCPP)
   - UI mode for visual testing
   - CLI mode for automation
   - Connection types (STDIO, SSE, HTTP)

3. **Practical Skills**
   - Connect to any MCP server
   - Test tools with real data
   - Debug common issues
   - Create production configs
   - Automate testing

4. **Best Practices**
   - Security (authentication, binding)
   - Debugging workflow
   - CI/CD integration
   - Production considerations

### Next Steps

1. **Connect to Your MTR Server**
   ```bash
   npx @modelcontextprotocol/inspector
   # URL: http://localhost:8080/mcp/sse
   ```

2. **Test All Features**
   - List and call tools
   - Browse resources
   - Try prompts

3. **Create Config**
   - Export for Claude Desktop
   - Save for future use

4. **Automate**
   - Add CLI tests
   - Set up CI/CD
   - Document your API

### You're Now Ready To:
✅ Test any MCP server confidently  
✅ Debug issues systematically  
✅ Create production configurations  
✅ Automate testing workflows  
✅ Integrate with AI clients  

**Happy Testing! 🚀**