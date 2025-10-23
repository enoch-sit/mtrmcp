"""
FastAPI Integration for MCP Server
==================================

This module provides two approaches for serving the MCP server:
1. Standalone approach: MCP server on separate port with NGINX proxy
2. Integrated approach: MCP server mounted in FastAPI app

Based on the fastapi-integration.md documentation.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from typing import Optional
import logging
import subprocess
import sys

# Import the configurable MCP server
from mcp_server_configurable import create_mcp_server, run_configurable_mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages the MCP server lifecycle"""
    
    def __init__(self):
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
    
    def start_mcp_server(self, port: int = 8001):
        """Start MCP server in a separate thread"""
        def run_server():
            try:
                logger.info(f"Starting MCP server on port {port}")
                self.is_running = True
                
                # Use the configurable MCP server
                run_configurable_mcp_server(port=port, host="127.0.0.1")
            except Exception as e:
                logger.error(f"MCP server error: {e}")
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Wait for server to start
        max_retries = 10
        for i in range(max_retries):
            if self.is_running:
                logger.info(f"MCP server started successfully on port {port}")
                return True
            time.sleep(0.5)
        
        logger.error("Failed to start MCP server")
        return False
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if self.server_thread and self.server_thread.is_alive():
            self.is_running = False
            logger.info("MCP server stopped")


# Global MCP server manager
mcp_manager = MCPServerManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan"""
    # Startup
    logger.info("Starting FastAPI application with MCP integration")
    
    # Start MCP server on port 8001
    success = mcp_manager.start_mcp_server(port=8001)
    if not success:
        logger.error("Failed to start MCP server during FastAPI startup")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")
    mcp_manager.stop_mcp_server()


# Create FastAPI app with lifespan management
app = FastAPI(
    title="MTR MCP FastAPI Server",
    description="FastAPI integration for MTR MCP Server with SSE transport",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "MTR MCP FastAPI Server",
        "version": "1.0.0",
        "mcp_status": "running" if mcp_manager.is_running else "stopped",
        "endpoints": {
            "mcp_sse": "/mcp",
            "mcp_direct": "http://localhost:8001/sse",
            "health": "/health",
            "docs": "/docs"
        },
        "description": "FastAPI integration for MTR MCP Server providing Hong Kong MTR train schedules"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_server": "running" if mcp_manager.is_running else "stopped",
        "timestamp": time.time()
    }


@app.get("/mcp")
async def mcp_proxy():
    """
    Proxy endpoint for MCP SSE connection
    
    This endpoint proxies requests to the MCP server's SSE endpoint.
    Use this URL in MCP Inspector: http://localhost:8000/mcp
    """
    if not mcp_manager.is_running:
        raise HTTPException(
            status_code=503, 
            detail="MCP server is not running"
        )
    
    # Redirect to the actual MCP SSE endpoint
    # In a production environment, you'd proxy the actual SSE stream
    return RedirectResponse(url="http://localhost:8001/sse", status_code=307)


@app.api_route("/mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def mcp_proxy_with_path(path: str, request: Request):
    """
    Proxy endpoint that forwards all requests to MCP server
    
    This handles any path under /mcp/ and forwards it to the MCP server
    """
    if not mcp_manager.is_running:
        raise HTTPException(
            status_code=503, 
            detail="MCP server is not running"
        )
    
    # In a real implementation, you would:
    # 1. Forward the request to http://localhost:8001/{path}
    # 2. Stream the response back
    # 3. Handle SSE streaming properly
    
    # For now, redirect to the SSE endpoint for SSE requests
    if path == "sse" or request.method == "GET":
        return RedirectResponse(url="http://localhost:8001/sse", status_code=307)
    
    raise HTTPException(
        status_code=404, 
        detail=f"Path /{path} not supported in proxy mode"
    )


# Additional utility endpoints

@app.get("/mcp/info")
async def mcp_info():
    """Get MCP server information"""
    return {
        "server_name": "mtr_next_train",
        "transport": "sse",
        "endpoint": "http://localhost:8001/sse",
        "proxy_endpoint": "http://localhost:8000/mcp",
        "features": {
            "tools": 2,
            "resources": 2, 
            "prompts": 3
        },
        "tools": [
            "get_next_train_schedule",
            "get_next_train_structured"
        ],
        "resources": [
            "mtr://stations/list",
            "mtr://lines/map"
        ],
        "prompts": [
            "check_next_train",
            "plan_mtr_journey", 
            "compare_stations"
        ]
    }


@app.get("/mcp/status")
async def mcp_status():
    """Get detailed MCP server status"""
    return {
        "running": mcp_manager.is_running,
        "thread_alive": mcp_manager.server_thread.is_alive() if mcp_manager.server_thread else False,
        "server_url": "http://localhost:8001/sse",
        "proxy_url": "http://localhost:8000/mcp",
        "instructions": {
            "mcp_inspector": "Connect to: http://localhost:8000/mcp or http://localhost:8001/sse",
            "direct_access": "Use http://localhost:8001/sse for direct MCP access",
            "nginx_config": "Add location /mcp { proxy_pass http://localhost:8001/sse; } for production"
        }
    }


def run_standalone_mcp(port: int = 8001):
    """
    Run MCP server standalone (Approach 1 from documentation)
    
    This is the recommended approach for production with NGINX proxy.
    """
    print("=" * 70)
    print("🚀 Starting MCP Server (Standalone Mode)")
    print("=" * 70)
    print(f"📡 SSE Endpoint: http://127.0.0.1:{port}/sse")
    print(f"🔍 MCP Inspector: Use http://127.0.0.1:{port}/sse")
    print(f"⚠️  Note: http://127.0.0.1:{port} (without /sse) will give 404")
    print("=" * 70)
    print("\n✨ Features:")
    print("   📦 2 Tools: get_next_train_schedule, get_next_train_structured")
    print("   📚 2 Resources: mtr://stations/list, mtr://lines/map")
    print("   📝 3 Prompts: check_next_train, plan_mtr_journey, compare_stations")
    print("=" * 70)
    print("\n📋 NGINX Configuration:")
    print(f"""
    location /mcp {{
        proxy_pass http://localhost:{port}/sse;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }}
    """)
    print("=" * 70)

    # Use the configurable MCP server
    run_configurable_mcp_server(port=port, host="127.0.0.1")


def run_fastapi_integrated(port: int = 8000):
    """
    Run FastAPI with integrated MCP server (Approach 2 from documentation)
    
    This runs both FastAPI and MCP server together.
    """
    print("=" * 70)
    print("🚀 Starting FastAPI with MCP Integration")
    print("=" * 70)
    print(f"🌐 FastAPI Server: http://localhost:{port}")
    print(f"📡 MCP Proxy Endpoint: http://localhost:{port}/mcp")
    print(f"📡 MCP Direct Endpoint: http://localhost:8001/sse")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 MCP Inspector: Use http://localhost:{port}/mcp")
    print("=" * 70)
    print("\n📋 Available Endpoints:")
    print(f"   GET  / - Service information")
    print(f"   GET  /health - Health check")
    print(f"   GET  /mcp - MCP SSE proxy")
    print(f"   GET  /mcp/info - MCP server info")
    print(f"   GET  /mcp/status - MCP server status")
    print(f"   GET  /docs - API documentation")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "standalone":
            # Run standalone MCP server only
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
            run_standalone_mcp(port)
        
        elif mode == "fastapi":
            # Run FastAPI with integrated MCP server
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
            run_fastapi_integrated(port)
        
        else:
            print("Usage:")
            print("  python fastapi_integration.py standalone [port]  - Run standalone MCP server")
            print("  python fastapi_integration.py fastapi [port]     - Run FastAPI with MCP integration")
            sys.exit(1)
    else:
        # Default: Run FastAPI with integrated MCP server
        run_fastapi_integrated()