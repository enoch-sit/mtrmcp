"""
FastAPI Integration for MCP Server - All under /mcp path
========================================================

This module serves the entire MCP server under the /mcp path prefix.
Designed for Docker deployment where / is occupied by other services.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from typing import Optional, Dict, Any
import logging
import json
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active SSE sessions
active_sessions = {}


class MCPServerManager:
    """Manages the MCP server lifecycle for internal communication"""
    
    def __init__(self):
        self.mcp_server = None
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None
        self._initialize_mcp()
    
    def _initialize_mcp(self):
        """Initialize the MCP server components"""
        try:
            from mcp.server.fastmcp import FastMCP
            
            # Create MCP server instance
            self.mcp_server = FastMCP("mtr_next_train")
            
            # Import and register all the tools, resources, and prompts
            self._register_mcp_components()
            
            logger.info("MCP server components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
    
    def _register_mcp_components(self):
        """Register MCP tools, resources, and prompts"""
        try:
            # We'll use the original MCP server instance directly
            # instead of trying to copy internal attributes
            from mcp_server import mcp as original_mcp
            self.mcp_server = original_mcp
            
            logger.info("MCP components registered successfully")
        except Exception as e:
            logger.error(f"Failed to register MCP components: {e}")
    
    async def handle_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request internally"""
        try:
            if not self.mcp_server:
                raise Exception("MCP server not initialized")
            
            # Process the MCP request
            # This would need to be implemented based on MCP protocol
            response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "result": {"status": "success", "message": "MCP request processed"}
            }
            
            return response
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -1, "message": str(e)}
            }


# Global MCP server manager
mcp_manager = MCPServerManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan"""
    # Startup
    logger.info("Starting FastAPI application with MCP under /mcp")
    mcp_manager.is_running = True
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")
    mcp_manager.is_running = False


# Create FastAPI app
app = FastAPI(
    title="MTR MCP Server",
    description="MCP Server for Hong Kong MTR train schedules - served under /mcp",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/mcp"  # This makes all routes relative to /mcp
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint (will be accessible at /mcp/)
@app.get("/")
async def mcp_root():
    """MCP service root endpoint"""
    return {
        "service": "MTR MCP Server",
        "version": "1.0.0",
        "description": "Hong Kong MTR train schedule MCP server",
        "protocol": "MCP (Model Context Protocol)",
        "transport": "HTTP/JSON-RPC",
        "status": "running" if mcp_manager.is_running else "stopped",
        "endpoints": {
            "sse": "/mcp/sse",
            "jsonrpc": "/mcp/jsonrpc", 
            "info": "/mcp/info",
            "health": "/mcp/health",
            "docs": "/mcp/docs"
        },
        "timestamp": datetime.now().isoformat()
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if mcp_manager.is_running else "unhealthy",
        "service": "mtr-mcp-server",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    }


# MCP Info endpoint
@app.get("/info")
async def mcp_info():
    """Get MCP server capabilities and information"""
    return {
        "server": {
            "name": "mtr_next_train",
            "version": "1.0.0",
            "description": "Hong Kong MTR train schedule service"
        },
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True
        },
        "tools": [
            {
                "name": "get_next_train_schedule",
                "description": "Get next train schedule for MTR stations"
            },
            {
                "name": "get_next_train_structured", 
                "description": "Get structured next train information"
            }
        ],
        "resources": [
            {
                "uri": "mtr://stations/list",
                "name": "MTR Stations List",
                "description": "List of all MTR stations"
            },
            {
                "uri": "mtr://lines/map",
                "name": "MTR Lines Map", 
                "description": "MTR system lines and connections"
            }
        ],
        "prompts": [
            {
                "name": "check_next_train",
                "description": "Check next train for a specific station"
            },
            {
                "name": "plan_mtr_journey",
                "description": "Plan a journey using MTR"
            },
            {
                "name": "compare_stations", 
                "description": "Compare train schedules between stations"
            }
        ]
    }


# SSE endpoint for MCP Inspector compatibility
@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for MCP Inspector - MCP Protocol Compatible"""
    
    import uuid
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {"created": datetime.now(), "active": True}
    
    async def event_stream():
        try:
            # MCP REQUIRED: Send endpoint event first
            endpoint_path = f"/mcp/messages/?session_id={session_id}"
            yield f"event: endpoint\ndata: {endpoint_path}\n\n"
            logger.info(f"SSE session {session_id}: sent endpoint event")
            
            # Keep connection alive with heartbeats as JSON-RPC notifications
            heartbeat_count = 0
            while True:
                # Check if client is still connected
                if await request.is_disconnected():
                    logger.info(f"SSE session {session_id}: client disconnected")
                    break
                
                # Send heartbeat as MCP notification (optional)
                heartbeat_count += 1
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/message",
                    "params": {
                        "level": "info",
                        "logger": "mcp-server",
                        "data": {
                            "type": "heartbeat",
                            "count": heartbeat_count,
                            "timestamp": datetime.now().isoformat(),
                            "status": "running" if mcp_manager.is_running else "stopped"
                        }
                    }
                }
                
                # MCP FORMAT: Send as 'message' event with JSON-RPC data
                yield f"event: message\ndata: {json.dumps(notification)}\n\n"
                
                # Wait before next heartbeat
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE stream error for session {session_id}: {e}")
        finally:
            # Cleanup session
            active_sessions.pop(session_id, None)
            logger.info(f"SSE session {session_id}: cleaned up")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control, Last-Event-ID"
        }
    )


# MCP Messages endpoint - handles JSON-RPC requests
@app.post("/messages/")
async def handle_mcp_messages(
    request: Request,
    session_id: str = None
):
    """Handle MCP JSON-RPC messages via POST (required for MCP protocol)"""
    
    # Validate session
    if not session_id:
        return JSONResponse(
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "session_id required"}},
            status_code=400
        )
    
    if session_id not in active_sessions:
        logger.warning(f"Unknown session_id: {session_id}")
        # Continue anyway - session might have been created earlier
    
    try:
        # Parse JSON-RPC request
        json_rpc_request = await request.json()
        logger.info(f"Received MCP message for session {session_id}: {json_rpc_request}")
        
        # Validate JSON-RPC format
        if json_rpc_request.get("jsonrpc") != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": json_rpc_request.get("id"),
                "error": {"code": -32600, "message": "Invalid JSON-RPC version"}
            })
        
        method = json_rpc_request.get("method")
        request_id = json_rpc_request.get("id")
        params = json_rpc_request.get("params", {})
        
        # Handle MCP methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "mtr_next_train",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_next_train_schedule",
                            "description": "Get next train schedule for MTR stations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "station": {
                                        "type": "string",
                                        "description": "MTR station code (e.g., 'CEN', 'TST')"
                                    },
                                    "line": {
                                        "type": "string",
                                        "description": "MTR line name (optional)"
                                    }
                                },
                                "required": ["station"]
                            }
                        },
                        {
                            "name": "get_next_train_structured",
                            "description": "Get structured next train information with details",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "station": {"type": "string"},
                                    "direction": {"type": "string", "enum": ["UP", "DOWN"]}
                                },
                                "required": ["station"]
                            }
                        }
                    ]
                }
            })
        
        elif method == "resources/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "resources": [
                        {
                            "uri": "mtr://stations/list",
                            "name": "MTR Stations List",
                            "description": "List of all MTR stations",
                            "mimeType": "application/json"
                        },
                        {
                            "uri": "mtr://lines/map",
                            "name": "MTR Lines Map",
                            "description": "MTR system lines and connections",
                            "mimeType": "application/json"
                        }
                    ]
                }
            })
        
        elif method == "prompts/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "prompts": [
                        {
                            "name": "check_next_train",
                            "description": "Check next train for a specific station",
                            "arguments": [
                                {"name": "station", "description": "Station code", "required": True}
                            ]
                        },
                        {
                            "name": "plan_mtr_journey",
                            "description": "Plan a journey using MTR",
                            "arguments": [
                                {"name": "from", "description": "Starting station", "required": True},
                                {"name": "to", "description": "Destination station", "required": True}
                            ]
                        }
                    ]
                }
            })
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Mock tool execution
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Tool '{tool_name}' executed with arguments: {json.dumps(arguments)}\n\nResult: Mock data - integrate with actual MTR API"
                        }
                    ]
                }
            })
        
        else:
            # Unknown method
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            })
    
    except Exception as e:
        logger.error(f"Error handling MCP message: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": json_rpc_request.get("id") if 'json_rpc_request' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }, status_code=500)


# JSON-RPC endpoint for MCP protocol
@app.post("/jsonrpc")
async def jsonrpc_endpoint(request: Request):
    """JSON-RPC endpoint for MCP protocol communication"""
    try:
        request_data = await request.json()
        logger.info(f"Received MCP request: {request_data}")
        
        # Handle the MCP request
        response = await mcp_manager.handle_mcp_request(request_data)
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"JSON-RPC error: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        })


# Tools endpoint (for direct tool access)
@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, request: Request):
    """Execute a specific MCP tool"""
    try:
        request_data = await request.json()
        
        # Mock tool execution - replace with actual MCP tool calling
        if tool_name == "get_next_train_schedule":
            result = {
                "tool": tool_name,
                "arguments": request_data,
                "result": "Mock train schedule data - implement actual MTR API integration"
            }
        elif tool_name == "get_next_train_structured":
            result = {
                "tool": tool_name,
                "arguments": request_data, 
                "result": {
                    "station": request_data.get("station", "Unknown"),
                    "next_trains": ["Mock train 1", "Mock train 2"],
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return JSONResponse(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Resources endpoint
@app.get("/resources/{resource_path:path}")
async def get_resource(resource_path: str):
    """Get MCP resource by path"""
    try:
        if resource_path == "stations/list":
            # Mock stations list - replace with actual data
            return {
                "uri": "mtr://stations/list",
                "content": {
                    "stations": [
                        {"code": "CEN", "name": "Central", "line": "Island Line"},
                        {"code": "ADM", "name": "Admiralty", "line": "Island Line"},
                        {"code": "TST", "name": "Tsim Sha Tsui", "line": "Tsuen Wan Line"},
                        # Add more stations as needed
                    ]
                }
            }
        elif resource_path == "lines/map":
            return {
                "uri": "mtr://lines/map", 
                "content": {
                    "lines": [
                        {"name": "Island Line", "color": "#0075C8"},
                        {"name": "Tsuen Wan Line", "color": "#E2231A"},
                        {"name": "Kwun Tong Line", "color": "#7B9D3F"}
                    ]
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Resource '{resource_path}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resource error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Prompts endpoint
@app.get("/prompts")
async def list_prompts():
    """List available MCP prompts"""
    return {
        "prompts": [
            {
                "name": "check_next_train",
                "description": "Check next train for a specific station",
                "arguments": [
                    {"name": "station", "type": "string", "required": True}
                ]
            },
            {
                "name": "plan_mtr_journey", 
                "description": "Plan a journey using MTR",
                "arguments": [
                    {"name": "from", "type": "string", "required": True},
                    {"name": "to", "type": "string", "required": True}
                ]
            },
            {
                "name": "compare_stations",
                "description": "Compare train schedules between stations", 
                "arguments": [
                    {"name": "stations", "type": "array", "required": True}
                ]
            }
        ]
    }


@app.get("/prompts/{prompt_name}")
async def get_prompt(prompt_name: str, request: Request):
    """Get a specific prompt template"""
    # Mock prompt responses - replace with actual prompt handling
    prompts = {
        "check_next_train": "Please check the next train schedule for station: {station}",
        "plan_mtr_journey": "Plan the best route from {from} to {to} using MTR",
        "compare_stations": "Compare train schedules between these stations: {stations}"
    }
    
    if prompt_name not in prompts:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
    
    return {
        "name": prompt_name,
        "template": prompts[prompt_name],
        "description": f"Prompt template for {prompt_name}"
    }


# Add custom OpenAPI documentation
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    from fastapi.openapi.utils import get_openapi
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MTR MCP Server API",
        version="1.0.0",
        description="Model Context Protocol server for Hong Kong MTR train schedules",
        routes=app.routes,
    )
    
    # Add MCP-specific information to OpenAPI schema
    openapi_schema["info"]["x-mcp-server"] = {
        "name": "mtr_next_train",
        "version": "1.0.0",
        "capabilities": ["tools", "resources", "prompts"]
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Run the FastAPI server with MCP under /mcp"""
    print("=" * 70)
    print("🚀 Starting MTR MCP Server under /mcp")
    print("=" * 70)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📡 MCP Root: http://{host}:{port}/mcp/")
    print(f"📡 SSE Endpoint: http://{host}:{port}/mcp/sse")
    print(f"📡 JSON-RPC: http://{host}:{port}/mcp/jsonrpc")
    print(f"📖 API Docs: http://{host}:{port}/mcp/docs")
    print(f"🔍 Health Check: http://{host}:{port}/mcp/health")
    print("=" * 70)
    print("\n📋 Available Endpoints:")
    print("   GET  /mcp/ - Service information")
    print("   GET  /mcp/health - Health check")
    print("   GET  /mcp/info - MCP capabilities")
    print("   GET  /mcp/sse - Server-Sent Events")
    print("   POST /mcp/jsonrpc - JSON-RPC endpoint")
    print("   POST /mcp/tools/{tool_name} - Execute tools")
    print("   GET  /mcp/resources/{path} - Get resources")
    print("   GET  /mcp/prompts - List prompts")
    print("   GET  /mcp/docs - API documentation")
    print("=" * 70)
    print("\n🔧 MCP Inspector Setup:")
    print(f"   Use SSE URL: http://{host}:{port}/mcp/sse")
    print("=" * 70)
    
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    host = "0.0.0.0"
    port = 8080
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        host = sys.argv[2]
    
    run_server(host, port)