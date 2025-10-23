@echo off
REM MTR MCP Server - Windows Startup Script
REM =========================================

echo.
echo ============================================================
echo 🚀 MTR MCP Server - Windows Startup
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo 📦 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Show menu
:menu
echo.
echo ============================================================
echo 🎯 Choose deployment option:
echo ============================================================
echo 1. FastAPI with MCP Integration (recommended)
echo 2. Standalone MCP Server only
echo 3. Run tests
echo 4. Docker deployment
echo 5. Exit
echo.
set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto fastapi
if "%choice%"=="2" goto standalone
if "%choice%"=="3" goto tests
if "%choice%"=="4" goto docker
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:fastapi
echo.
echo 🌐 Starting FastAPI with MCP Integration...
echo.
echo 📍 Endpoints will be available at:
echo   - FastAPI Server: http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo   - MCP Proxy: http://localhost:8000/mcp
echo   - Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.
python fastapi_integration.py fastapi 8000
goto exit

:standalone
echo.
echo 🚀 Starting Standalone MCP Server...
echo.
echo 📍 MCP Server will be available at:
echo   - SSE Endpoint: http://localhost:8001/sse
echo   - MCP Inspector: Use http://localhost:8001/sse
echo.
echo Press Ctrl+C to stop the server
echo.
python fastapi_integration.py standalone 8001
goto exit

:tests
echo.
echo 🧪 Running test suite...
echo.
python deploy.py test
echo.
pause
goto menu

:docker
echo.
echo 🐳 Docker deployment options:
echo 1. Build and run Docker container
echo 2. Run with Docker Compose
echo 3. Back to main menu
echo.
set /p docker_choice=Enter choice (1-3): 

if "%docker_choice%"=="1" (
    echo Building and running Docker container...
    docker build -t mtr-mcp-server .
    docker run -p 8000:8000 -p 8001:8001 --name mtr-mcp mtr-mcp-server
) else if "%docker_choice%"=="2" (
    echo Running with Docker Compose...
    docker-compose up
) else if "%docker_choice%"=="3" (
    goto menu
) else (
    echo Invalid choice.
    goto docker
)
goto exit

:exit
echo.
echo 👋 Goodbye!
echo.
pause