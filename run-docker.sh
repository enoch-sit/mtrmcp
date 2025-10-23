#!/bin/bash

# MTR MCP Server Docker Runner
# Runs everything under /mcp path

echo "=================================="
echo "🚇 MTR MCP Server Docker Setup"
echo "=================================="

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build the image
echo "🔨 Building Docker image..."
docker-compose build

# Run the MCP server (without NGINX)
echo "🚀 Starting MCP server..."
docker-compose up -d mtr-mcp-server

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
sleep 10

# Check health
echo "🏥 Health check..."
curl -f http://localhost:8000/mcp/health || echo "❌ Health check failed"

echo ""
echo "✅ MTR MCP Server is running!"
echo ""
echo "📡 Available endpoints:"
echo "   🏠 Service root: http://localhost:8000/mcp/"
echo "   🏥 Health check: http://localhost:8000/mcp/health" 
echo "   📡 SSE endpoint: http://localhost:8000/mcp/sse"
echo "   📖 API docs: http://localhost:8000/mcp/docs"
echo "   ℹ️  MCP info: http://localhost:8000/mcp/info"
echo ""
echo "🔧 MCP Inspector:"
echo "   Use SSE URL: http://localhost:8000/mcp/sse"
echo ""
echo "📋 Docker commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop server: docker-compose down"
echo "   With NGINX: docker-compose --profile production up -d"
echo ""
echo "=================================="