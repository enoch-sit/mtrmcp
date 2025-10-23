"""
MCP Server Module for FastAPI Integration
=========================================

This module provides a configurable MCP server that can be run on different ports
and integrated with FastAPI applications.
"""

import os
import requests
from typing import Dict
from mcp.server.fastmcp import FastMCP
from difflib import get_close_matches

# Import station and line data from the main server
from mcp_server import (
    STATION_NAMES, 
    LINE_NAMES,
    resolve_station_code,
    resolve_line_code,
    format_train_schedule
)


def create_mcp_server(server_name: str = "mtr_next_train") -> FastMCP:
    """
    Create a new MCP server instance with all tools, resources, and prompts.
    
    This allows us to create multiple server instances for different ports
    or configurations.
    """
    mcp = FastMCP(server_name)
    
    @mcp.tool()
    def get_next_train_schedule(line: str, sta: str, lang: str = "EN") -> str:
        """
        Get the next train arrival schedule for an MTR line and station.
        Returns HUMAN-READABLE formatted text, not raw JSON.
        
        Accepts BOTH station names (e.g., "Tseung Kwan O") AND codes (e.g., "TKO").
        Accepts BOTH line names (e.g., "Tseung Kwan O Line") AND codes (e.g., "TKL").

        Args:
            line: MTR line name or code. Examples:
                Names: "Airport Express", "Tseung Kwan O Line", "Island Line"
                Codes: "AEL", "TKL", "ISL"
                
            sta: Station name or code. Examples:
                Names: "Tseung Kwan O", "Hong Kong", "Admiralty"
                Codes: "TKO", "HOK", "ADM"
                
            lang: Language - 'EN' for English or 'TC' for Traditional Chinese. Default: 'EN'.

        Returns:
            Human-readable formatted train schedule
        """
        # Convert names to codes if needed
        line_code = resolve_line_code(line)
        station_code = resolve_station_code(sta)
        
        # Log the resolution for debugging (helpful for users)
        resolution_info = ""
        if line.lower() != line_code.lower():
            resolution_info += f"📝 Resolved line: '{line}' → '{line_code}'\n"
        if sta.lower() != station_code.lower():
            resolution_info += f"📝 Resolved station: '{sta}' → '{station_code}'\n"
        
        url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={line_code}&sta={station_code}&lang={lang}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Add resolution info to output if conversions happened
                result = format_train_schedule(data)
                if resolution_info and "⚠️" not in result and "❌" not in result:
                    result = resolution_info + "\n" + result
                elif resolution_info:
                    result = resolution_info + result
                    
                return result
            else:
                return f"❌ Error: API request failed with status {response.status_code}"
        except requests.exceptions.Timeout:
            return "❌ Error: Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    @mcp.tool()
    def get_next_train_structured(line: str, sta: str, lang: str = "EN") -> Dict:
        """
        Machine-friendly tool returning structured JSON for programmatic agents.

        Output schema:
        {
          "resolved_line": "TKL",
          "resolved_station": "TKO", 
          "timestamp": "2025-10-21T11:03:35Z",
          "up": [ {"dest":"POA","ttnt":"2","plat":"1","time":"11:05:35"}, ... ],
          "down": [ ... ],
          "raw": { ... },  # original API response
          "error": null | {"code": "NT-204", "message": "The contents are empty!" },
          "suggestions": ["Check station name","Try code like TKO","Try again later"]
        }

        This tool is intended for other agents to parse programmatically.
        """
        line_code = resolve_line_code(line)
        station_code = resolve_station_code(sta)

        url = f"https://rt.data.gov.hk/v1/transport/mtr/getSchedule.php?line={line_code}&sta={station_code}&lang={lang}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return {
                    "resolved_line": line_code,
                    "resolved_station": station_code,
                    "timestamp": None,
                    "up": [],
                    "down": [],
                    "raw": None,
                    "error": {"code": f"HTTP-{response.status_code}", "message": response.text},
                    "suggestions": ["Check network/API status"]
                }

            data = response.json()

            # Handle API error wrappers
            if "error" in data:
                ec = data.get("error", {})
                return {
                    "resolved_line": line_code,
                    "resolved_station": station_code,
                    "timestamp": data.get("curr_time"),
                    "up": [],
                    "down": [],
                    "raw": data,
                    "error": {"code": ec.get("errorCode"), "message": ec.get("errorMsg")},
                    "suggestions": [
                        "Check station name or code",
                        "Try using the station code (e.g., TKO)",
                        "Try again later if real-time data is unavailable"
                    ]
                }

            station_data = data.get("data", {})
            if not station_data:
                return {
                    "resolved_line": line_code,
                    "resolved_station": station_code,
                    "timestamp": data.get("curr_time"),
                    "up": [],
                    "down": [],
                    "raw": data,
                    "error": {"code": "NT-204", "message": "The contents are empty!"},
                    "suggestions": ["Station may not have realtime data right now"]
                }

            station_key = list(station_data.keys())[0]
            trains = station_data[station_key]

            def normalize_list(arr):
                out = []
                for t in arr:
                    out.append({
                        "dest": t.get("dest"),
                        "ttnt": t.get("ttnt"),
                        "plat": t.get("plat"),
                        "time": t.get("time"),
                    })
                return out

            up = normalize_list(trains.get("UP", []))
            down = normalize_list(trains.get("DOWN", []))

            return {
                "resolved_line": line_code,
                "resolved_station": station_code,
                "timestamp": data.get("curr_time"),
                "up": up,
                "down": down,
                "raw": data,
                "error": None,
                "suggestions": []
            }
        except requests.exceptions.Timeout:
            return {"resolved_line": line_code, "resolved_station": station_code, "timestamp": None, "up": [], "down": [], "raw": None, "error": {"code": "TIMEOUT", "message": "Request timed out"}, "suggestions": ["Try again"]}
        except Exception as e:
            return {"resolved_line": line_code, "resolved_station": station_code, "timestamp": None, "up": [], "down": [], "raw": None, "error": {"code": "EXCEPTION", "message": str(e)}, "suggestions": ["Check server logs"]}

    @mcp.resource("mtr://stations/list")
    def get_station_list() -> str:
        """
        Resource: Complete list of all MTR stations with codes.
        Provides read-only reference data for station codes and names.
        """
        result = ["# MTR Station Reference\n"]
        result.append("Complete list of all 80+ MTR stations across 10 lines:\n\n")
        
        lines = {
            "TKL - Tseung Kwan O Line": ["TKO", "LHP", "HAH", "POA", "TIK", "YAT", "QUB", "NOP"],
            "AEL - Airport Express": ["HOK", "KOW", "TSY", "AIR", "AWE"],
            "ISL - Island Line": ["KET", "HKU", "SYP", "SHW", "CEN", "ADM", "WAC", "CAB", "TIH", "FOH", "NOP", "QUB", "TAK", "SWH", "SKW", "HFC", "CHW"],
            "TCL - Tung Chung Line": ["OLY", "NAC", "LAK", "SUN", "TUC"],
            "TML - Tuen Ma Line": ["WKS", "MOS", "HEO", "TSH", "SHM", "CIO", "STW", "CKT", "TAW", "HIK", "DIH", "KAT", "SUW", "TKW", "HOM", "HUH", "ETS", "AUS", "MEF", "TWW", "KSR", "YUL", "LOP", "TIS", "SIH", "TUM"],
            "EAL - East Rail Line": ["EXC", "MKK", "KOT", "SHT", "FOT", "RAC", "UNI", "TAP", "TWO", "FAN", "SHS", "LMC", "LOW"],
            "SIL - South Island Line": ["OCP", "WCH", "LET", "SOH"],
            "TWL - Tsuen Wan Line": ["TST", "JOR", "YMT", "MOK", "PRE", "SSP", "CSW", "LCK", "KWF", "KWH", "TWH", "TSW"],
            "KTL - Kwun Tong Line": ["WHA", "SKM", "LOF", "WTS", "CHH", "KOB", "NTK", "KWT", "LAT"],
            "DRL - Disneyland Resort Line": ["SUN", "DIS"]
        }
        
        for line_name, stations in lines.items():
            result.append(f"## {line_name}")
            result.append(f"Stations: {', '.join(stations)}\n")
        
        return "\n".join(result)

    @mcp.resource("mtr://lines/map")
    def get_line_map() -> str:
        """
        Resource: MTR line connectivity and interchange information.
        """
        return """# MTR Line Map & Interchanges

## Complete Interchange Stations (21 stations)

All stations where multiple MTR lines intersect at the same physical station:

| Station Name | Code | Connecting Lines |
|--------------|------|------------------|
| Admiralty | ADM | EAL, ISL, SIL, TWL |
| Central | CEN | ISL, TWL |
| Diamond Hill | DIH | KTL, TML |
| Ho Man Tin | HOM | KTL, TML |
| Hong Kong | HOK | AEL, TCL |
| Hung Hom | HUH | EAL, TML |
| Kowloon | KOW | AEL, TCL |
| Kowloon Tong | KOT | EAL, KTL |
| Lai King | LAK | TCL, TWL |
| Mei Foo | MEF | TML, TWL |
| Mong Kok | MOK | KTL, TWL |
| Nam Cheong | NAC | TCL, TML |
| North Point | NOP | ISL, TKL |
| Prince Edward | PRE | KTL, TWL |
| Quarry Bay | QUB | ISL, TKL |
| Sunny Bay | SUN | DRL, TCL |
| Tai Wai | TAW | EAL, TML |
| Tiu Keng Leng | TIK | KTL, TKL |
| Tsing Yi | TSY | AEL, TCL |
| Yau Ma Tei | YMT | KTL, TWL |
| Yau Tong | YAT | KTL, TKL |
"""

    @mcp.prompt()
    def check_next_train(line: str, station: str) -> str:
        """
        Prompt: Quick train schedule check.
        """
        return f"""Check the next train arrival at {station} station on the {line} line.

Please use the get_next_train_schedule tool to:
1. Get real-time train schedules
2. Show both upbound and downbound trains
3. Highlight the next arriving train
4. Mention any service delays

Respond in a friendly, conversational way."""

    @mcp.prompt()
    def plan_mtr_journey(origin: str, destination: str) -> str:
        """
        Prompt: Plan MTR journey between two stations.
        """
        return f"""Help me plan an MTR journey from {origin} to {destination}.

Please:
1. Use the mtr://lines/map resource to find the route
2. Check next trains at {origin} using get_next_train_schedule
3. Identify any interchange stations needed
4. Estimate total journey time
5. Provide step-by-step directions

Be helpful and mention the platform numbers and train destinations."""

    @mcp.prompt()
    def compare_stations(station1: str, station2: str, station3: str = "") -> str:
        """
        Prompt: Compare train frequencies at multiple stations.
        """
        stations = [station1, station2]
        if station3:
            stations.append(station3)
        
        stations_list = ", ".join(stations)
        
        return f"""Compare the next train arrivals at these stations: {stations_list}

Please use get_next_train_structured for each station to:
1. Get structured train data programmatically
2. Extract wait times for upbound and downbound trains
3. Compare which station has the soonest train
4. Recommend the best station based on timing

Present the comparison in a clear table format."""
    
    return mcp


def run_configurable_mcp_server(port: int = 8000, host: str = "127.0.0.1"):
    """
    Run MCP server with configurable port using uvicorn directly.
    
    This bypasses the FastMCP.run() limitation and allows us to specify
    the port and host for the SSE server.
    """
    import uvicorn
    
    # Create MCP server instance
    server = create_mcp_server("mtr_next_train_configurable")
    
    print("=" * 60)
    print("🚀 Starting Configurable MCP Server")
    print("=" * 60)
    print(f"📡 SSE Endpoint: http://{host}:{port}/sse")
    print(f"🔍 MCP Inspector: Use http://{host}:{port}/sse")
    print(f"⚠️  Note: http://{host}:{port} (without /sse) will give 404")
    print("=" * 60)
    print("\n✨ Features:")
    print("   📦 2 Tools: get_next_train_schedule, get_next_train_structured")
    print("   📚 2 Resources: mtr://stations/list, mtr://lines/map")
    print("   📝 3 Prompts: check_next_train, plan_mtr_journey, compare_stations")
    print("=" * 60)
    
    # Get the ASGI app from the FastMCP server
    app = server._app  # Access the internal ASGI app
    
    # Run with uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    
    run_configurable_mcp_server(port=port, host=host)