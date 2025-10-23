# Ubuntu Quick Commands for MTR MCP Server

## 🚀 One-Liner Commands (Copy & Paste to Ubuntu Terminal)

### Option 1: Docker with Port 8080 (Recommended)
```bash
cd ~/mtrmcp && export HOST_PORT=8080 && docker-compose down && docker-compose build && docker-compose up -d mtr-mcp-server && sleep 3 && curl http://localhost:8080/mcp/health
```

### Option 2: Direct Python Run with Port 8080
```bash
cd ~/mtrmcp && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python fastapi_mcp_integration.py 8080 0.0.0.0
```

### Option 3: Auto-detect Available Port and Start
```bash
cd ~/mtrmcp && chmod +x start-ubuntu.sh && ./start-ubuntu.sh
```

## 🔍 Test Commands (After Starting)

### Health Check (Replace 8080 with your port)
```bash
curl http://localhost:8080/mcp/health
```

### Get Service Info
```bash
curl http://localhost:8080/mcp/ | jq
```

### Get MCP Capabilities
```bash
curl http://localhost:8080/mcp/info | jq
```

### Test SSE Endpoint (MCP Inspector URL)
```bash
curl -N http://localhost:8080/mcp/sse
```

## 🛑 Stop Commands

### Stop Docker Container
```bash
docker-compose down
```

### Stop Python Process
```bash
# Find and kill Python process
pkill -f "fastapi_mcp_integration.py"
```

## 🔧 Port Management

### Find Available Ports
```bash
for port in {8080..8090}; do if ! netstat -tln | grep -q ":$port "; then echo "Port $port is available"; fi; done
```

### Check What's Using Port 8080
```bash
sudo lsof -i :8080
```

### Your Current Ports in Use
Based on your system:
- Port 80: Web server ❌
- Port 8000: ChromaDB (flowise-chroma) ❌  
- Port 3000: Flowise ❌
- Port 5432: PostgreSQL ❌
- Port 8080: Available ✅ (recommended)

## 📝 Environment Variables

### Set Custom Port for Docker
```bash
export HOST_PORT=8080
docker-compose up -d mtr-mcp-server
```

### Create .env file for persistent settings
```bash
echo "HOST_PORT=8080" > .env
echo "MCP_SERVER_URL=http://localhost:8080/mcp/sse" >> .env
```