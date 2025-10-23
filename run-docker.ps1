# MTR MCP Server Docker Runner - PowerShell
# Runs everything under /mcp path

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "🚇 MTR MCP Server Docker Setup" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Cyan

try {
    # Stop any existing containers
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down

    # Build the image
    Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
    docker-compose build

    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed"
    }

    # Run the MCP server (without NGINX)
    Write-Host "🚀 Starting MCP server..." -ForegroundColor Yellow
    docker-compose up -d mtr-mcp-server

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start MCP server"
    }

    # Wait for service to be ready
    Write-Host "⏳ Waiting for service to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10

    # Check health
    Write-Host "🏥 Health check..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/mcp/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Health check passed" -ForegroundColor Green
        } else {
            Write-Host "❌ Health check failed - Status: $($response.StatusCode)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Health check failed - $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "✅ MTR MCP Server is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📡 Available endpoints:" -ForegroundColor Cyan
    Write-Host "   🏠 Service root: http://localhost:8000/mcp/" -ForegroundColor White
    Write-Host "   🏥 Health check: http://localhost:8000/mcp/health" -ForegroundColor White
    Write-Host "   📡 SSE endpoint: http://localhost:8000/mcp/sse" -ForegroundColor White
    Write-Host "   📖 API docs: http://localhost:8000/mcp/docs" -ForegroundColor White
    Write-Host "   ℹ️  MCP info: http://localhost:8000/mcp/info" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 MCP Inspector:" -ForegroundColor Cyan
    Write-Host "   Use SSE URL: http://localhost:8000/mcp/sse" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Docker commands:" -ForegroundColor Cyan
    Write-Host "   View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "   Stop server: docker-compose down" -ForegroundColor White
    Write-Host "   With NGINX: docker-compose --profile production up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan

    # Optional: Open browser
    $openBrowser = Read-Host "Open browser to MCP service? (y/N)"
    if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
        Start-Process "http://localhost:8000/mcp/"
    }
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check Docker is running and try again." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")