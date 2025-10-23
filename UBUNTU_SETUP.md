# Ubuntu Setup Guide for MTR MCP Server

## 🐧 Ubuntu Environment Setup

Since you have existing services running on ports 80 and 8000, we'll use port **8080** for the MTR MCP server.

### Current Port Usage (from your system):
- Port 80: Web server
- Port 8000: ChromaDB (flowise-chroma container)
- Port 3000: Flowise
- Port 5432: PostgreSQL

### Recommended Port: 8080

## 🚀 Quick Start Commands for Ubuntu

### 1. **Clone Repository** (if not already done)
```bash
git clone https://github.com/enoch-sit/mtrmcp.git
cd mtrmcp
```

### 2. **Check Available Ports**
```bash
# Check what's running on common ports
netstat -tlnp | grep -E ':(8080|8081|8082|9000)'

# Or use ss command
ss -tlnp | grep -E ':(8080|8081|8082|9000)'
```

### 3. **Install Dependencies**
```bash
# Install Python pip if not available
sudo apt update
sudo apt install python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. **Run Directly with Port 8080**
```bash
# Run FastAPI MCP server on port 8080
python fastapi_mcp_integration.py 8080

# Or specify host and port explicitly
python -c "
import sys
sys.argv = ['fastapi_mcp_integration.py', '8080', '0.0.0.0']
exec(open('fastapi_mcp_integration.py').read())
"
```

### 5. **Docker Setup with Port 8080**

#### Option A: Environment Variable
```bash
# Set custom port via environment variable
export MCP_SERVER_PORT=8080
docker-compose up -d mtr-mcp-server
```

#### Option B: Override docker-compose port
```bash
# Run with custom port mapping
docker-compose run -d --name mtr-mcp-server -p 8080:8000 --rm mtr-mcp-server
```

#### Option C: Create override file
```bash
# Create docker-compose.override.yml
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  mtr-mcp-server:
    ports:
      - "8080:8000"
    environment:
      - MCP_SERVER_PORT=8000
EOF

# Run with override
docker-compose up -d mtr-mcp-server
```

### 6. **Test the Service**
```bash
# Health check
curl http://localhost:8080/mcp/health

# Service info
curl http://localhost:8080/mcp/ | jq

# MCP capabilities
curl http://localhost:8080/mcp/info | jq
```

## 🔧 Configuration Files to Update

### 1. Update docker-compose.yml ports section:
```yaml
services:
  mtr-mcp-server:
    ports:
      - "8080:8000"  # Host:Container
```

### 2. Update NGINX configuration (if using):
```nginx
# Update nginx-mcp.conf
upstream mtr_mcp {
    server localhost:8080;
}
```

## 🌐 Access URLs (Port 8080)

After starting on port 8080, your endpoints will be:

| Service | URL | Purpose |
|---------|-----|---------|
| **Service Root** | `http://localhost:8080/mcp/` | Main service info |
| **Health Check** | `http://localhost:8080/mcp/health` | Service status |
| **SSE Endpoint** | `http://localhost:8080/mcp/sse` | MCP Inspector |
| **API Docs** | `http://localhost:8080/mcp/docs` | FastAPI docs |
| **MCP Info** | `http://localhost:8080/mcp/info` | Available tools |

## 🔍 MCP Inspector Setup
- Connect to: `http://localhost:8080/mcp/sse`
- Or if accessing from another machine: `http://YOUR_IP:8080/mcp/sse`

## 🐳 Production Docker Commands

```bash
# Build and run on port 8080
docker build -t mtr-mcp-server .
docker run -d --name mtr-mcp-server -p 8080:8000 mtr-mcp-server

# View logs
docker logs -f mtr-mcp-server

# Stop container
docker stop mtr-mcp-server
docker rm mtr-mcp-server
```

## 🚨 Troubleshooting

### Port Still Occupied?
```bash
# Find what's using the port
sudo lsof -i :8080
# or
sudo netstat -tlnp | grep :8080

# Kill process if needed (replace PID)
sudo kill -9 <PID>
```

### Alternative Ports
If 8080 is also occupied, try these ports:
- 8081, 8082, 8083 (common alternatives)
- 9000, 9001, 9002 (application ports)
- 7000, 7001, 7002 (development ports)

### Check Available Ports
```bash
# Find available ports in range
for port in {8080..8090}; do
  if ! netstat -tln | grep -q ":$port "; then
    echo "Port $port is available"
  fi
done
```

## 📝 Notes for Ubuntu Environment

1. **Firewall**: Make sure UFW allows the port if enabled
   ```bash
   sudo ufw allow 8080
   ```

2. **Docker permissions**: Add user to docker group if needed
   ```bash
   sudo usermod -aG docker $USER
   # Then logout and login again
   ```

3. **Python version**: Ensure Python 3.8+ is installed
   ```bash
   python3 --version
   ```

4. **Virtual environment**: Always use virtual environment for Python projects
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```