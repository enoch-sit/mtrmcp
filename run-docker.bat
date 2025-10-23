@echo off
REM MTR MCP Server Docker Runner for Windows
REM Runs everything under /mcp path

echo ==================================
echo 🚇 MTR MCP Server Docker Setup
echo ==================================

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build the image
echo 🔨 Building Docker image...
docker-compose build

REM Run the MCP server (without NGINX)
echo 🚀 Starting MCP server...
docker-compose up -d mtr-mcp-server

REM Wait for service to be ready
echo ⏳ Waiting for service to start...
timeout /t 10 /nobreak >nul

REM Check health
echo 🏥 Health check...
curl -f http://localhost:8000/mcp/health
if %errorlevel% neq 0 (
    echo ❌ Health check failed
) else (
    echo ✅ Health check passed
)

echo.
echo ✅ MTR MCP Server is running!
echo.
echo 📡 Available endpoints:
echo    🏠 Service root: http://localhost:8000/mcp/
echo    🏥 Health check: http://localhost:8000/mcp/health
echo    📡 SSE endpoint: http://localhost:8000/mcp/sse
echo    📖 API docs: http://localhost:8000/mcp/docs
echo    ℹ️  MCP info: http://localhost:8000/mcp/info
echo.
echo 🔧 MCP Inspector:
echo    Use SSE URL: http://localhost:8000/mcp/sse
echo.
echo 📋 Docker commands:
echo    View logs: docker-compose logs -f
echo    Stop server: docker-compose down
echo    With NGINX: docker-compose --profile production up -d
echo.
echo ==================================

pause