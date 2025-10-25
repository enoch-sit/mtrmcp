// Slide data for MCP Concepts Guide presentation
const slidesData = [
    {
        title: "What is MCP (Model Context Protocol)?",
        bullets: [
            "An open protocol created by Anthropic that standardizes how AI applications communicate with external data sources and tools.",
            "Like USB-C for AI - one universal interface for all context sources, enabling seamless integration.",
            "Uses JSON-RPC 2.0 over stdio or HTTP/SSE transports with a three-layer architecture: Application → Data → Transport."
        ],
        code: `# Before MCP: Every agent needs custom code
LangGraph Agent 1 → Custom Code A → API A
LangGraph Agent 2 → Custom Code B → API A  
LangGraph Agent 1 → Custom Code C → API B

# With MCP: One protocol, infinite possibilities
LangGraph Agent 1 ─┐
LangGraph Agent 2 ─┼─→ MCP Protocol → MCP Server A
LangGraph Agent 3 ─┘                 → MCP Server B`,
        mermaid: `graph LR
    A["🤖 AI Agent"] --> B["📡 MCP Protocol"]
    B --> C["🖥️ MCP Server A"]
    B --> D["🖥️ MCP Server B"]
    B --> E["🖥️ MCP Server C"]
    
    style A fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style B fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px
    style C fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style D fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style E fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px`
    },
    {
        title: "What is JSON-RPC?",
        bullets: [
            "JSON-RPC (JSON Remote Procedure Call) is a lightweight protocol for calling functions on a remote server as if they were local.",
            "Uses simple JSON format for requests (client asks), responses (server replies), and notifications (one-way messages).",
            "MCP chose JSON-RPC because it's simple, bidirectional, language-agnostic, standardized, and lightweight."
        ],
        code: `# Request (Client asks server to do something)
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {"name": "calculator", "args": {"a": 5, "b": 3}}
}

# Response (Server replies with result)
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"content": [{"type": "text", "text": "8"}]}
}

# Notification (One-way, no response expected)
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}`,
        mermaid: `sequenceDiagram
    participant Client as 🖥️ Client
    participant Server as 🌐 Server
    
    Client->>Server: Request (id:1, method, params)
    Server->>Client: Response (id:1, result)
    Server-->>Client: Notification (method only)
    
    Note over Client,Server: JSON-RPC 2.0 Protocol`
    },
    {
        title: "Understanding HTTP & SSE",
        bullets: [
            "HTTP is the foundation of web communication - a text-based protocol using request-response model with methods (GET, POST, etc.).",
            "SSE (Server-Sent Events) enables real-time server→client streaming over HTTP, keeping connections open for continuous updates.",
            "HTTP is UTF-8 encoded text (not Base64), packaged into TCP packets for network transmission with automatic reliability."
        ],
        code: `# Traditional HTTP (Request-Response)
Client: "GET /data HTTP/1.1"  →  Server
Client  ← "200 OK: Here's data"  Server
[Connection closes]

# SSE (Server Streaming)
Client: "GET /events HTTP/1.1"  →  Server
        "Accept: text/event-stream"
        ← "data: Update 1"        Server
        ← "data: Update 2"        Server
        ← "data: Update 3"        Server
[Connection stays open]`,
        mermaid: `graph TD
    A["📱 Application Layer<br/>(HTTP UTF-8 text)"]
    B["🔗 Transport Layer<br/>(TCP packets ~1460 bytes)"]
    C["🌐 Network Layer<br/>(IP routing)"]
    D["⚡ Physical Layer<br/>(Network hardware)"]
    
    A --> B
    B --> C
    C --> D
    
    style A fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style B fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style C fill:#FFF3E0,stroke:#FF9800,stroke-width:3px
    style D fill:#FFEBEE,stroke:#F44336,stroke-width:3px`
    },
    {
        title: "HTTP+SSE vs HTTP Streamable Evolution",
        bullets: [
            "OLD (HTTP+SSE, 2024-11-05): Required TWO separate endpoints - /messages (POST) and /sse (GET) - complex to configure.",
            "NEW (HTTP Streamable, 2025-06-18): ONE unified /mcp endpoint handles both POST and GET - simpler, more secure.",
            "Benefits: 50% fewer endpoints, unified security, easier CORS, better load balancing, flexible responses (JSON or SSE)."
        ],
        code: `# OLD: HTTP+SSE (DEPRECATED)
@app.post("/messages")
async def handle_messages(request):
    # Handle JSON-RPC messages
    
@app.get("/sse")
async def handle_sse(request):
    # Handle SSE stream

# NEW: HTTP Streamable (CURRENT)
@app.api_route("/mcp", methods=["GET", "POST"])
async def handle_mcp(request):
    if request.method == "POST":
        # Can return JSON or SSE stream
    elif request.method == "GET":
        # Return SSE stream`,
        mermaid: `graph LR
    subgraph OLD["❌ HTTP+SSE (Deprecated)"]
        C1["👤 Client"] --> E1["POST /messages"]
        C1 <--> E2["GET /sse"]
    end
    
    subgraph NEW["✅ HTTP Streamable (Current)"]
        C2["👤 Client"] --> E3["POST/GET /mcp"]
        C2 <--> E3
    end
    
    style OLD fill:#FFEBEE,stroke:#F44336,stroke-width:3px
    style NEW fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style E3 fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px`
    },
    {
        title: "MCP Transport: stdio",
        bullets: [
            "stdio transport enables local process communication - client launches MCP server as subprocess and communicates via stdin/stdout.",
            "Messages are newline-delimited JSON-RPC on single lines, UTF-8 encoded. Server can write logs to stderr (not protocol).",
            "Best for: Desktop apps (Claude, VS Code), local integrations, low latency. NOT for: remote servers, web apps, multiple clients."
        ],
        code: `# Client launches server as subprocess
$ /path/to/mcp-server

# Client sends to stdin
{"jsonrpc":"2.0","id":1,"method":"initialize",...}

# Server responds via stdout
{"jsonrpc":"2.0","id":1,"result":{...}}

# Server logs to stderr (optional)
[2025-10-25 10:30:15] INFO: Server initialized

# Claude Desktop config example
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/Users/data"]
    }
  }
}`,
        mermaid: `graph TD
    A["🖥️ MCP Client<br/>(Parent Process)<br/>e.g., Claude Desktop"]
    B["🔧 MCP Server<br/>(Child Process)<br/>e.g., Filesystem Server"]
    
    A -->|"stdin: JSON-RPC messages"| B
    B -->|"stdout: JSON-RPC responses"| A
    B -.->|"stderr: logs (optional)"| A
    
    style A fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style B fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px`
    },
    {
        title: "MCP Transport: HTTP Streamable",
        bullets: [
            "HTTP Streamable enables remote web service communication with one unified /mcp endpoint for POST (send) and GET (receive SSE).",
            "Server can respond with direct JSON (simple requests) or SSE stream (complex requests with progress updates).",
            "Session management via Mcp-Session-Id header links all requests, enables stateful multi-turn interactions."
        ],
        code: `# 1. Initialize (POST /mcp)
POST /mcp HTTP/1.1
{"jsonrpc":"2.0","id":1,"method":"initialize",...}

Response:
Mcp-Session-Id: session-abc-123
{"jsonrpc":"2.0","id":1,"result":{...}}

# 2. Open SSE Stream (GET /mcp)
GET /mcp HTTP/1.1
Mcp-Session-Id: session-abc-123
Accept: text/event-stream

# 3. Send Tool Call (POST /mcp)
POST /mcp HTTP/1.1
Mcp-Session-Id: session-abc-123
{"jsonrpc":"2.0","id":2,"method":"tools/call",...}`,
        mermaid: `sequenceDiagram
    participant C as 🖥️ MCP Client
    participant S as 🌐 MCP Server
    
    C->>S: POST /mcp: Initialize
    S->>C: 200 OK + Session-Id
    C->>S: GET /mcp: Open SSE stream
    S-->>C: SSE stream (stays open)
    C->>S: POST /mcp: Tool call
    S->>C: JSON response OR
    S-->>C: SSE stream response
    S-->>C: Notification (async)
    
    Note over C,S: One endpoint, flexible responses`
    },
    {
        title: "MCP Core Primitive: Resources",
        bullets: [
            "Resources are passive data sources that clients can READ (like files, database records, API responses) - context for LLMs.",
            "Resources have URIs (e.g., file:///, db://), MIME types (text/plain, application/json), and optional metadata.",
            "Flow: Client requests resources/list → Server returns available resources → Client reads specific resource by URI."
        ],
        code: `# 1. List available resources
Request:  {"jsonrpc":"2.0","id":1,"method":"resources/list"}
Response: {
  "resources": [
    {
      "uri": "file:///project/README.md",
      "name": "Project README",
      "mimeType": "text/plain"
    },
    {
      "uri": "db://users/12345",
      "name": "User Profile",
      "mimeType": "application/json"
    }
  ]
}

# 2. Read specific resource
Request:  {"jsonrpc":"2.0","id":2,"method":"resources/read",
           "params":{"uri":"file:///project/README.md"}}
Response: {"contents":[{"uri":"...", "text":"..."}]}`,
        mermaid: `graph LR
    A["👤 User"] --> B["🤖 AI Agent"]
    B --> C["📖 Resources<br/>(READ ONLY)"]
    C --> D["🖥️ MCP Server"]
    
    D -.-> E["📄 Files"]
    D -.-> F["🗄️ Database"]
    D -.-> G["🌐 APIs"]
    
    style A fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style B fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style C fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px
    style D fill:#FFF3E0,stroke:#FF9800,stroke-width:2px`
    },
    {
        title: "MCP Core Primitive: Prompts",
        bullets: [
            "Prompts are reusable templates/workflows (like 'code review template', 'SQL query generator') with placeholders for arguments.",
            "Server defines prompts with names, descriptions, and argument schemas. Client can request and use them with custom values.",
            "Flow: Client requests prompts/list → Server returns templates → Client gets prompt with args → Server returns filled template."
        ],
        code: `# 1. List available prompts
Request:  {"jsonrpc":"2.0","id":1,"method":"prompts/list"}
Response: {
  "prompts": [
    {
      "name": "code-review",
      "description": "Review code for best practices",
      "arguments": [
        {"name": "language", "description": "Programming language"}
      ]
    }
  ]
}

# 2. Get prompt with arguments
Request:  {"jsonrpc":"2.0","id":2,"method":"prompts/get",
           "params":{"name":"code-review",
                     "arguments":{"language":"Python"}}}
Response: {
  "messages": [
    {"role": "user", "content": "Review this Python code..."}
  ]
}`,
        mermaid: `graph TD
    A["👤 User"] --> B["🤖 AI Agent"]
    B --> C["📝 Prompts<br/>(TEMPLATES)"]
    C --> D["🖥️ MCP Server"]
    
    D -.-> E["📋 Code Review Template"]
    D -.-> F["🔍 SQL Query Template"]
    D -.-> G["✍️ Writing Template"]
    
    style A fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style B fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style C fill:#E0F2F1,stroke:#009688,stroke-width:3px
    style D fill:#FFF3E0,stroke:#FF9800,stroke-width:2px`
    },
    {
        title: "MCP Core Primitive: Tools",
        bullets: [
            "Tools are executable functions that agents can CALL to perform actions (like calculations, file writes, API calls) - active operations.",
            "Tools have names, descriptions (critical for LLM decision), and input schemas (JSON Schema for validation).",
            "Flow: Client requests tools/list → Server returns available tools → Client calls tool → Server executes & returns result."
        ],
        code: `# 1. List available tools
Request:  {"jsonrpc":"2.0","id":1,"method":"tools/list"}
Response: {
  "tools": [
    {
      "name": "calculator",
      "description": "Perform arithmetic calculations",
      "inputSchema": {
        "type": "object",
        "properties": {
          "operation": {"type": "string"},
          "a": {"type": "number"},
          "b": {"type": "number"}
        }
      }
    }
  ]
}

# 2. Call tool
Request:  {"jsonrpc":"2.0","id":2,"method":"tools/call",
           "params":{"name":"calculator",
                     "arguments":{"operation":"add","a":5,"b":3}}}
Response: {"content":[{"type":"text","text":"8"}]}`,
        mermaid: `graph LR
    A["👤 User"] --> B["🤖 AI Agent"]
    B --> C["🔧 Tools<br/>(EXECUTE)"]
    C --> D["🖥️ MCP Server"]
    
    D -.-> E["🧮 Calculator"]
    D -.-> F["📝 File Writer"]
    D -.-> G["🌐 API Caller"]
    
    style A fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style B fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style C fill:#FFEBEE,stroke:#F44336,stroke-width:3px
    style D fill:#FFF3E0,stroke:#FF9800,stroke-width:2px`
    },
    {
        title: "MCP Primitives: When to Use Which?",
        bullets: [
            "Use Resources when: You need to READ data (files, docs, DB records) for context without modification - passive data access.",
            "Use Prompts when: You want reusable templates/workflows with placeholders - structured guidance for LLMs.",
            "Use Tools when: You need to EXECUTE actions (calculations, writes, API calls) that change state - active operations."
        ],
        code: `# Decision Tree
if need_to_read_data:
    use_resources()  # Passive: Read-only access
    # Examples: Read file, query DB, fetch API data
    
elif need_template_workflow:
    use_prompts()    # Templates: Reusable patterns
    # Examples: Code review, SQL generation, writing guide
    
elif need_to_execute_action:
    use_tools()      # Active: Execute operations
    # Examples: Calculate, write file, call API, transform data
    
# Key Differences:
# Resources = READ  (passive, context)
# Prompts   = GUIDE (templates, workflows)
# Tools     = DO    (active, actions)`,
        mermaid: `graph TD
    START["❓ What do you need?"]
    
    START --> Q1{"Need to READ<br/>data?"}
    START --> Q2{"Need reusable<br/>TEMPLATE?"}
    START --> Q3{"Need to EXECUTE<br/>action?"}
    
    Q1 -->|Yes| R["📖 Use RESOURCES"]
    Q2 -->|Yes| P["📝 Use PROMPTS"]
    Q3 -->|Yes| T["🔧 Use TOOLS"]
    
    R -.-> R1["Read files"]
    R -.-> R2["Query DB"]
    P -.-> P1["Code review"]
    P -.-> P2["SQL template"]
    T -.-> T1["Calculate"]
    T -.-> T2["Write file"]
    
    style START fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px
    style R fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px
    style P fill:#E0F2F1,stroke:#009688,stroke-width:3px
    style T fill:#FFEBEE,stroke:#F44336,stroke-width:3px`
    },
    {
        title: "MCP Lifecycle: Initialization Phase",
        bullets: [
            "Client sends initialize request with protocol version and capabilities (experimental, roots, sampling).",
            "Server responds with its protocol version, capabilities (resources, tools, prompts, logging), and server info.",
            "Client sends initialized notification to confirm completion. Connection is now ready for interactions."
        ],
        code: `# 1. Client → Server: Initialize request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "experimental": {},
      "roots": {"listChanged": true},
      "sampling": {}
    },
    "clientInfo": {"name": "MyClient", "version": "1.0.0"}
  }
}

# 2. Server → Client: Initialize response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "resources": {"subscribe": true, "listChanged": true},
      "tools": {"listChanged": true},
      "prompts": {"listChanged": true},
      "logging": {}
    },
    "serverInfo": {"name": "MyServer", "version": "1.0.0"}
  }
}

# 3. Client → Server: Initialized notification
{"jsonrpc": "2.0", "method": "notifications/initialized"}`,
        mermaid: `sequenceDiagram
    participant C as 🖥️ Client
    participant S as 🌐 Server
    
    C->>S: initialize (protocol, capabilities)
    S->>C: result (protocol, capabilities, info)
    C->>S: notifications/initialized
    
    Note over C,S: ✅ Connection ready!
    
    rect rgb(232, 245, 233)
        Note right of S: Server now accepts:<br/>- resources/list<br/>- tools/list<br/>- prompts/list
    end`
    },
    {
        title: "MCP Lifecycle: Discovery & Interaction",
        bullets: [
            "Discovery: Client lists available resources/prompts/tools from server to understand capabilities.",
            "Interaction: Client reads resources (for context), gets prompts (for templates), calls tools (for actions).",
            "Server can send notifications when lists change (resources/tools/prompts updated) - client can re-query."
        ],
        code: `# DISCOVERY PHASE
# List resources
{"jsonrpc":"2.0","id":2,"method":"resources/list"}
→ {"resources":[{"uri":"file:///data","name":"Data"}]}

# List tools
{"jsonrpc":"2.0","id":3,"method":"tools/list"}
→ {"tools":[{"name":"calculator","description":"..."}]}

# List prompts
{"jsonrpc":"2.0","id":4,"method":"prompts/list"}
→ {"prompts":[{"name":"review","description":"..."}]}

# INTERACTION PHASE
# Read resource
{"jsonrpc":"2.0","id":5,"method":"resources/read",
 "params":{"uri":"file:///data"}}

# Call tool
{"jsonrpc":"2.0","id":6,"method":"tools/call",
 "params":{"name":"calculator","arguments":{...}}}

# Get prompt
{"jsonrpc":"2.0","id":7,"method":"prompts/get",
 "params":{"name":"review","arguments":{...}}}`,
        mermaid: `graph TD
    subgraph DISCOVERY["🔍 Discovery Phase"]
        D1["1️⃣ resources/list"]
        D2["2️⃣ tools/list"]
        D3["3️⃣ prompts/list"]
    end
    
    subgraph INTERACTION["⚡ Interaction Phase"]
        I1["📖 resources/read"]
        I2["🔧 tools/call"]
        I3["📝 prompts/get"]
    end
    
    DISCOVERY --> INTERACTION
    
    style DISCOVERY fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style INTERACTION fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px`
    },
    {
        title: "MCP + LangGraph Integration",
        bullets: [
            "LangGraph agents use MCP to access external tools and data during decision-making loops.",
            "Flow: User input → Agent decides → Calls MCP tools OR reads MCP resources → LLM processes → Responds to user.",
            "MCP provides standardized interface for tools/resources, LangGraph provides agent orchestration and state management."
        ],
        code: `from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool

# Define MCP-backed tool
@tool
def mcp_calculator(operation: str, a: float, b: float) -> float:
    """Calculate using MCP calculator tool."""
    # Calls MCP server's calculator tool
    response = mcp_client.call_tool(
        "calculator", 
        {"operation": operation, "a": a, "b": b}
    )
    return response["content"][0]["text"]

# Create LangGraph agent with MCP tools
llm = ChatBedrockConverse(model="amazon.nova-lite-v1:0")
tools = [mcp_calculator]
agent = create_react_agent(llm, tools)

# Use agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is 15 + 27?"}]
})`,
        mermaid: `graph TD
    A["👤 User Input"] --> B["🤖 LangGraph Agent"]
    B --> C{"🤔 Decision"}
    
    C -->|"Need calculation"| D["🔧 MCP Tools"]
    C -->|"Need context"| E["📖 MCP Resources"]
    C -->|"Direct answer"| F["💬 LLM Response"]
    
    D --> G["🧠 LLM Processing"]
    E --> G
    F --> H["✅ User Response"]
    G --> H
    
    style A fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style B fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style C fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px
    style D fill:#FFEBEE,stroke:#F44336,stroke-width:2px
    style E fill:#F3E5F5,stroke:#9C27B0,stroke-width:2px
    style G fill:#F8BBD0,stroke:#AB47BC,stroke-width:3px`
    },
    {
        title: "MCP Architecture: Three Layers",
        bullets: [
            "Application Layer: AI applications (Claude, VS Code, custom agents) that consume MCP services.",
            "Data Layer: MCP servers exposing resources, tools, and prompts through standardized MCP protocol.",
            "Transport Layer: stdio (local) or HTTP Streamable (remote) carrying JSON-RPC messages between layers."
        ],
        code: `# LAYER 1: APPLICATION LAYER
# AI apps that consume MCP
- Claude Desktop (Anthropic)
- VS Code Extensions
- LangGraph Agents
- Custom AI Applications

# LAYER 2: DATA LAYER (MCP Servers)
# Expose capabilities via MCP protocol
- Filesystem Server (read/write files)
- Database Server (query/update DB)
- API Server (call external APIs)
- Calculator Server (math operations)

# LAYER 3: TRANSPORT LAYER
# How messages travel
- stdio: stdin/stdout (local)
- HTTP Streamable: POST/GET /mcp (remote)

# Message Format: JSON-RPC 2.0
{"jsonrpc":"2.0","id":1,"method":"...","params":{...}}`,
        mermaid: `graph TB
    subgraph APP["📱 Application Layer"]
        A1["Claude Desktop"]
        A2["VS Code"]
        A3["LangGraph Agent"]
    end
    
    subgraph PROTOCOL["📡 MCP Protocol (JSON-RPC 2.0)"]
        P1["Resources"]
        P2["Tools"]
        P3["Prompts"]
    end
    
    subgraph DATA["🖥️ Data Layer (MCP Servers)"]
        D1["Filesystem"]
        D2["Database"]
        D3["APIs"]
    end
    
    subgraph TRANSPORT["🌐 Transport Layer"]
        T1["stdio (local)"]
        T2["HTTP Streamable (remote)"]
    end
    
    APP --> PROTOCOL
    PROTOCOL --> DATA
    PROTOCOL -.-> TRANSPORT
    
    style APP fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style PROTOCOL fill:#FFF9C4,stroke:#FBC02D,stroke-width:3px
    style DATA fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style TRANSPORT fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px`
    },
    {
        title: "Real-World Example: MTR MCP Server",
        bullets: [
            "MTR (Morning-Tea-Research) MCP server deployed at https://project-1-04.eduhk.hk/mcp/ using HTTP Streamable transport.",
            "Provides resources (research papers, data), tools (analysis, calculations), and prompts (research templates).",
            "LangGraph agents connect to MTR server, discover capabilities, and use them for research assistance tasks."
        ],
        code: `# MTR MCP Server Configuration
URL: https://project-1-04.eduhk.hk/mcp/
Transport: HTTP Streamable
Protocol: MCP 2025-06-18

# Capabilities
Resources:
  - Research papers (URI: paper://paper-id)
  - Dataset records (URI: data://dataset-id)
  
Tools:
  - Statistical analysis
  - Data transformation
  - Citation generator
  
Prompts:
  - Literature review template
  - Research methodology template
  - Paper summary template

# Client Usage
from mcp import Client

client = Client("https://project-1-04.eduhk.hk/mcp/")
await client.initialize()

# List tools
tools = await client.list_tools()

# Call analysis tool
result = await client.call_tool(
    "statistical_analysis",
    {"data": [...], "method": "regression"}
)`,
        mermaid: `graph LR
    A["👨‍🔬 Researcher"] --> B["🤖 LangGraph Agent"]
    B <--> C["🌐 MTR MCP Server<br/>project-1-04.eduhk.hk/mcp"]
    
    C --> D["📖 Resources<br/>(Papers, Data)"]
    C --> E["🔧 Tools<br/>(Analysis)"]
    C --> F["📝 Prompts<br/>(Templates)"]
    
    style A fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px
    style B fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style C fill:#FFF3E0,stroke:#FF9800,stroke-width:3px
    style D fill:#F3E5F5,stroke:#9C27B0,stroke-width:2px
    style E fill:#FFEBEE,stroke:#F44336,stroke-width:2px
    style F fill:#E0F2F1,stroke:#009688,stroke-width:2px`
    },
    {
        title: "MCP Benefits & Use Cases",
        bullets: [
            "Benefits: Universal interface (no custom code per service), language-agnostic, bidirectional, standardized protocol.",
            "Use Cases: Desktop AI assistants (Claude + filesystem), IDE integrations (VS Code + databases), Research agents (LangGraph + MTR).",
            "Future: Growing ecosystem of MCP servers (Slack, GitHub, Notion, etc.) enabling richer AI agent capabilities."
        ],
        code: `# USE CASE 1: Claude Desktop + Filesystem
# Access local files directly in Claude
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", 
               "/Users/projects"]
    }
  }
}

# USE CASE 2: VS Code + Database
# Query databases from AI assistant in IDE
const client = new MCPClient("stdio", {
  command: "mcp-database-server",
  args: ["--connection", "postgresql://localhost/mydb"]
});

# USE CASE 3: LangGraph + Multiple MCP Servers
agent = create_react_agent(llm, [
  mcp_filesystem_tools,
  mcp_database_tools,
  mcp_api_tools,
  mcp_calculator_tools
])
# Agent has access to all MCP capabilities!`,
        mermaid: `graph TB
    subgraph BENEFITS["✨ MCP Benefits"]
        B1["🔌 Universal Interface"]
        B2["🌐 Language-Agnostic"]
        B3["🔄 Bidirectional"]
        B4["📋 Standardized"]
    end
    
    subgraph USECASES["🎯 Use Cases"]
        U1["💻 Claude + Files"]
        U2["🔧 VS Code + DB"]
        U3["🤖 Agent + Multiple Servers"]
    end
    
    subgraph ECOSYSTEM["🌱 Growing Ecosystem"]
        E1["Slack"]
        E2["GitHub"]
        E3["Notion"]
        E4["Google Drive"]
        E5["Databases"]
    end
    
    BENEFITS --> USECASES
    USECASES --> ECOSYSTEM
    
    style BENEFITS fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style USECASES fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style ECOSYSTEM fill:#FFF3E0,stroke:#FF9800,stroke-width:3px`
    },
    {
        title: "Key Takeaways",
        bullets: [
            "MCP is the universal protocol for AI-context integration - like USB-C but for AI applications and data sources.",
            "Three core primitives: Resources (READ data), Prompts (TEMPLATES), Tools (EXECUTE actions) - choose based on need.",
            "Two transports: stdio (local subprocess) for desktop apps, HTTP Streamable (web service) for remote/multi-client scenarios.",
            "LangGraph + MCP = Powerful combination of agent orchestration + standardized external capabilities.",
            "HTTP Streamable is the current standard (2025-06-18) - one /mcp endpoint, session management, flexible responses."
        ],
        code: `# MCP in a Nutshell

# 1. PROTOCOL
JSON-RPC 2.0 over stdio or HTTP Streamable

# 2. PRIMITIVES
Resources = READ  (passive data)
Prompts   = GUIDE (templates)
Tools     = DO    (active operations)

# 3. TRANSPORTS
stdio:           Local (subprocess communication)
HTTP Streamable: Remote (web service, one endpoint)

# 4. LIFECYCLE
Initialize → Discover → Interact → Update

# 5. INTEGRATION
LangGraph Agent + MCP Server = 🚀

# Remember:
✅ Use Resources for context (read-only)
✅ Use Prompts for templates (reusable patterns)
✅ Use Tools for actions (execute operations)
✅ Use HTTP Streamable for new servers (not HTTP+SSE)
✅ Session IDs link requests in HTTP Streamable`,
        mermaid: `graph TD
    START["🎯 MCP<br/>Universal AI Protocol"]
    
    START --> P["📡 Protocol<br/>JSON-RPC 2.0"]
    START --> T["🌐 Transports<br/>stdio | HTTP Streamable"]
    START --> C["🎨 Primitives<br/>Resources | Prompts | Tools"]
    
    P --> I["🔄 Integration"]
    T --> I
    C --> I
    
    I --> R["🚀 Result<br/>AI agents with<br/>standardized capabilities"]
    
    style START fill:#FFF9C4,stroke:#FBC02D,stroke-width:4px
    style P fill:#E3F2FD,stroke:#2196F3,stroke-width:3px
    style T fill:#F3E5F5,stroke:#9C27B0,stroke-width:3px
    style C fill:#E8F5E9,stroke:#4CAF50,stroke-width:3px
    style I fill:#FFE0B2,stroke:#FB8C00,stroke-width:3px
    style R fill:#C8E6C9,stroke:#66BB6A,stroke-width:4px`
    }
];
