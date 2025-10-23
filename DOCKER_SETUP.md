# MTR MCP Server - Docker Setup

This repository contains a FastAPI-based MCP (Model Context Protocol) server for Hong Kong MTR train schedules, designed to run everything under the `/mcp` path prefix.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### Run with Docker Compose

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd mtr-mcp-fastapi-example
   ```

2. **Run the setup script:**
   
   **Windows (PowerShell):**
   ```powershell
   .\run-docker.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   run-docker.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./run-docker.sh
   ```

3. **Or manually with Docker Compose:**
   ```bash
   docker-compose up -d mtr-mcp-server
   ```

### Endpoints

All endpoints are served under the `/mcp` path:

| Endpoint | Description | URL |
|----------|-------------|-----|
| **Service Root** | Main service information | `http://localhost:8000/mcp/` |
| **Health Check** | Service health status | `http://localhost:8000/mcp/health` |
| **SSE Endpoint** | Server-Sent Events for MCP Inspector | `http://localhost:8000/mcp/sse` |
| **JSON-RPC** | MCP protocol endpoint | `http://localhost:8000/mcp/jsonrpc` |
| **API Documentation** | FastAPI auto-generated docs | `http://localhost:8000/mcp/docs` |
| **MCP Info** | Available tools, resources, prompts | `http://localhost:8000/mcp/info` |
| **Tools** | Execute MCP tools | `POST http://localhost:8000/mcp/tools/{tool_name}` |
| **Resources** | Access MCP resources | `GET http://localhost:8000/mcp/resources/{path}` |
| **Prompts** | List/get MCP prompts | `GET http://localhost:8000/mcp/prompts` |

## 🔧 MCP Inspector Setup

To use the MCP Inspector with this server:

1. Open [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
2. Connect to: `http://localhost:8000/mcp/sse`
3. The server will provide SSE (Server-Sent Events) for real-time communication

## 🐳 Docker Configuration

### Docker Compose Services

- **mtr-mcp-server**: Main MCP server running on port 8000
- **nginx** (optional): Reverse proxy for production (use with `--profile production`)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_HOST` | `0.0.0.0` | Server bind address |
| `MCP_SERVER_PORT` | `8000` | Server port |
| `LOG_LEVEL` | `info` | Logging level |

### Docker Commands

```bash
# Start only the MCP server
docker-compose up -d mtr-mcp-server

# Start with NGINX reverse proxy
docker-compose --profile production up -d

# View logs
docker-compose logs -f mtr-mcp-server

# Stop services
docker-compose down

# Rebuild and restart
docker-compose build && docker-compose up -d mtr-mcp-server
```

## 🌐 Production Setup with NGINX

For production deployment where other services occupy the root path (`/`), use the NGINX configuration:

1. **Run with NGINX profile:**
   ```bash
   docker-compose --profile production up -d
   ```

2. **Manual NGINX setup:**
   - Copy `nginx-mcp.conf` to your NGINX configuration
   - The configuration routes `/mcp/*` to the FastAPI server
   - Root path (`/`) serves a landing page with links to MCP endpoints

### Sample NGINX Configuration

The included `nginx-mcp.conf` provides:
- Proxy `/mcp/` requests to the FastAPI server
- Landing page at `/` with endpoint information
- Proper SSE (Server-Sent Events) handling
- Security headers
- Health check endpoint at `/nginx-health`

## 📡 Available MCP Features

### Tools
- `get_next_train_schedule`: Get next train schedule for MTR stations
- `get_next_train_structured`: Get structured next train information

### Resources
- `mtr://stations/list`: List of all MTR stations
- `mtr://lines/map`: MTR system lines and connections

### Prompts
- `check_next_train`: Check next train for a specific station
- `plan_mtr_journey`: Plan a journey using MTR
- `compare_stations`: Compare train schedules between stations

## 🔍 Testing the Service

### Health Check
```bash
curl http://localhost:8000/mcp/health
```

### Service Information
```bash
curl http://localhost:8000/mcp/
```

### MCP Capabilities
```bash
curl http://localhost:8000/mcp/info
```

### Execute a Tool (Example)
```bash
curl -X POST http://localhost:8000/mcp/tools/get_next_train_schedule \
  -H "Content-Type: application/json" \
  -d '{"station": "Central", "line": "Island Line"}'
```

## 📁 File Structure

```
├── fastapi_mcp_integration.py  # Main FastAPI server with /mcp routes
├── mcp_server.py              # Original MCP server implementation
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── nginx-mcp.conf             # NGINX configuration for /mcp routing
├── requirements.txt           # Python dependencies
├── run-docker.sh              # Linux/Mac startup script
├── run-docker.bat             # Windows batch startup script
├── run-docker.ps1             # PowerShell startup script
└── README.md                  # This file
```

## 🚨 Troubleshooting

### Port Already in Use
If port 8000 is occupied:
```bash
# Change the port in docker-compose.yml or use environment variable
export MCP_SERVER_PORT=8001
docker-compose up -d mtr-mcp-server
```

### Container Health Check Failing
```bash
# Check container logs
docker-compose logs mtr-mcp-server

# Check if the service is responding
curl http://localhost:8000/mcp/health
```

### NGINX Issues
```bash
# Test NGINX configuration
docker-compose exec nginx nginx -t

# Check NGINX logs
docker-compose logs nginx
```

## 🔄 Development Mode

For development, you can run without Docker:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run directly:**
   ```bash
   python fastapi_mcp_integration.py 8000
   ```

## 📝 Notes

- **Path Prefix**: All routes are under `/mcp` to avoid conflicts with other services
- **SSE Support**: Proper Server-Sent Events handling for MCP Inspector
- **Health Checks**: Docker health checks ensure container reliability
- **Security**: Non-root user in Docker container
- **Logging**: Structured logging with configurable levels
- **CORS**: Configured for cross-origin requests (adjust for production)

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs mtr-mcp-server`
2. Verify endpoints: `curl http://localhost:8000/mcp/health`
3. Check Docker status: `docker-compose ps`