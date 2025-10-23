# MTR MCP Server - PowerShell Startup Script
# ============================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 MTR MCP Server - PowerShell Startup" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to your PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install/upgrade dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip | Out-Host
pip install -r requirements.txt | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Show menu
do {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "🎯 Choose deployment option:" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "1. FastAPI with MCP Integration (recommended)" -ForegroundColor White
    Write-Host "2. Standalone MCP Server only" -ForegroundColor White
    Write-Host "3. Run tests" -ForegroundColor White
    Write-Host "4. Docker deployment" -ForegroundColor White
    Write-Host "5. Show service status" -ForegroundColor White
    Write-Host "6. Exit" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "🌐 Starting FastAPI with MCP Integration..." -ForegroundColor Green
            Write-Host ""
            Write-Host "📍 Endpoints will be available at:" -ForegroundColor Cyan
            Write-Host "  - FastAPI Server: http://localhost:8000" -ForegroundColor White
            Write-Host "  - API Documentation: http://localhost:8000/docs" -ForegroundColor White
            Write-Host "  - MCP Proxy: http://localhost:8000/mcp" -ForegroundColor White
            Write-Host "  - Health Check: http://localhost:8000/health" -ForegroundColor White
            Write-Host ""
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
            Write-Host ""
            python fastapi_integration.py fastapi 8000
            return
        }
        "2" {
            Write-Host ""
            Write-Host "🚀 Starting Standalone MCP Server..." -ForegroundColor Green
            Write-Host ""
            Write-Host "📍 MCP Server will be available at:" -ForegroundColor Cyan
            Write-Host "  - SSE Endpoint: http://localhost:8001/sse" -ForegroundColor White
            Write-Host "  - MCP Inspector: Use http://localhost:8001/sse" -ForegroundColor White
            Write-Host ""
            Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
            Write-Host ""
            python fastapi_integration.py standalone 8001
            return
        }
        "3" {
            Write-Host ""
            Write-Host "🧪 Running test suite..." -ForegroundColor Green
            Write-Host ""
            python deploy.py test
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "4" {
            Write-Host ""
            Write-Host "🐳 Docker deployment options:" -ForegroundColor Cyan
            Write-Host "1. Build and run Docker container" -ForegroundColor White
            Write-Host "2. Run with Docker Compose" -ForegroundColor White
            Write-Host "3. Back to main menu" -ForegroundColor White
            Write-Host ""
            
            $dockerChoice = Read-Host "Enter choice (1-3)"
            
            switch ($dockerChoice) {
                "1" {
                    Write-Host "Building and running Docker container..." -ForegroundColor Yellow
                    docker build -t mtr-mcp-server .
                    docker run -p 8000:8000 -p 8001:8001 --name mtr-mcp mtr-mcp-server
                    return
                }
                "2" {
                    Write-Host "Running with Docker Compose..." -ForegroundColor Yellow
                    docker-compose up
                    return
                }
                "3" {
                    continue
                }
                default {
                    Write-Host "Invalid choice." -ForegroundColor Red
                }
            }
        }
        "5" {
            Write-Host ""
            Write-Host "📊 Checking service status..." -ForegroundColor Green
            python deploy.py status
            Write-Host ""
            Read-Host "Press Enter to continue"
        }
        "6" {
            Write-Host ""
            Write-Host "👋 Goodbye!" -ForegroundColor Green
            Write-Host ""
            return
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
        }
    }
} while ($true)