#!/bin/bash

# MTR MCP Server - Ubuntu Quick Start
# Automatically detects available port and starts the server

echo "🐧 MTR MCP Server - Ubuntu Environment"
echo "======================================="

# Function to check if port is available
check_port() {
    local port=$1
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        return 1  # Port is occupied
    else
        return 0  # Port is available
    fi
}

# Find available port
AVAILABLE_PORT=""
for port in 8080 8081 8082 9000 9001 7000 7001; do
    if check_port $port; then
        AVAILABLE_PORT=$port
        break
    fi
done

if [ -z "$AVAILABLE_PORT" ]; then
    echo "❌ No available ports found in common range"
    echo "💡 Manually specify a port: ./start-ubuntu.sh [PORT]"
    exit 1
fi

# Use provided port or detected available port
PORT=${1:-$AVAILABLE_PORT}

echo "🔍 Port Analysis:"
echo "   - Port 80: $(check_port 80 && echo "Available" || echo "Occupied")"
echo "   - Port 8000: $(check_port 8000 && echo "Available" || echo "Occupied (likely ChromaDB)")"
echo "   - Port 8080: $(check_port 8080 && echo "Available" || echo "Occupied")"
echo ""
echo "✅ Selected Port: $PORT"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker detected - Starting with Docker Compose..."
    
    # Set environment variable for port
    export HOST_PORT=$PORT
    
    # Stop any existing container
    docker-compose down -v 2>/dev/null
    
    # Build and start
    docker-compose build
    docker-compose up -d mtr-mcp-server
    
    echo "⏳ Waiting for container to start..."
    sleep 5
    
    # Health check
    if curl -f http://localhost:$PORT/mcp/health &>/dev/null; then
        echo "✅ Container started successfully!"
    else
        echo "⚠️  Container may still be starting. Check logs:"
        echo "   docker-compose logs -f mtr-mcp-server"
    fi
    
else
    echo "🐍 Docker not found - Starting with Python..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Install with:"
        echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    
    # Start server
    echo "🚀 Starting FastAPI MCP server on port $PORT..."
    python fastapi_mcp_integration.py $PORT 0.0.0.0
fi

echo ""
echo "🌐 Service URLs:"
echo "   📡 Service Root: http://localhost:$PORT/mcp/"
echo "   🏥 Health Check: http://localhost:$PORT/mcp/health"
echo "   📡 SSE Endpoint: http://localhost:$PORT/mcp/sse"
echo "   📖 API Documentation: http://localhost:$PORT/mcp/docs"
echo ""
echo "🔧 MCP Inspector:"
echo "   Connect to: http://localhost:$PORT/mcp/sse"
echo ""
echo "📋 Management Commands:"
echo "   View logs: docker-compose logs -f (if Docker)"
echo "   Stop service: docker-compose down (if Docker)"
echo "   Or Ctrl+C (if Python direct)"
echo ""
echo "======================================="