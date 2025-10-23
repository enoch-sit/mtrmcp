import requests
from typing import Dict
from mcp.server.fastmcp import FastMCP
from difflib import get_close_matches

mcp = FastMCP("mtr_next_train")


# Station name to code mapping (supports both English names and codes)
STATION_NAMES = {
    # Tseung Kwan O Line (TKL)
    "tseung kwan o": "TKO", "tko": "TKO",
    "lohas park": "LHP", "lhp": "LHP",
    "hang hau": "HAH", "hah": "HAH",
    "po lam": "POA", "poa": "POA",
    "tiu keng leng": "TIK", "tik": "TIK",
    "yau tong": "YAT", "yat": "YAT",
    "quarry bay": "QUB", "qub": "QUB",
    "north point": "NOP", "nop": "NOP",
    
    # Airport Express (AEL)
    "hong kong": "HOK", "hok": "HOK",
    "kowloon": "KOW", "kow": "KOW",
    "tsing yi": "TSY", "tsy": "TSY",
    "airport": "AIR", "air": "AIR",
    "asiaworld expo": "AWE", "awe": "AWE",
    
    # Island Line (ISL)
    "kennedy town": "KET", "ket": "KET",
    "hku": "HKU",
    "sai ying pun": "SYP", "syp": "SYP",
    "sheung wan": "SHW", "shw": "SHW",
    "central": "CEN", "cen": "CEN",
    "admiralty": "ADM", "adm": "ADM",
    "wan chai": "WAC", "wac": "WAC",
    "causeway bay": "CAB", "cab": "CAB",
    "tin hau": "TIH", "tih": "TIH",
    "fortress hill": "FOH", "foh": "FOH",
    "tai koo": "TAK", "tak": "TAK",
    "sai wan ho": "SWH", "swh": "SWH",
    "shau kei wan": "SKW", "skw": "SKW",
    "heng fa chuen": "HFC", "hfc": "HFC",
    "chai wan": "CHW", "chw": "CHW",
    
    # Tung Chung Line (TCL)
    "olympic": "OLY", "oly": "OLY",
    "nam cheong": "NAC", "nac": "NAC",
    "lai king": "LAK", "lak": "LAK",
    "sunny bay": "SUN", "sun": "SUN",
    "tung chung": "TUC", "tuc": "TUC",
    
    # Tuen Ma Line (TML)
    "wu kai sha": "WKS", "wks": "WKS",
    "ma on shan": "MOS", "mos": "MOS",
    "heng on": "HEO", "heo": "HEO",
    "tai shui hang": "TSH", "tsh": "TSH",
    "shek mun": "SHM", "shm": "SHM",
    "city one": "CIO", "cio": "CIO",
    "sha tin wai": "STW", "stw": "STW",
    "che kung temple": "CKT", "ckt": "CKT",
    "tai wai": "TAW", "taw": "TAW",
    "hik keng": "HIK", "hik": "HIK",
    "diamond hill": "DIH", "dih": "DIH",
    "kai tak": "KAT", "kat": "KAT",
    "sung wong toi": "SUW", "suw": "SUW",
    "to kwa wan": "TKW", "tkw": "TKW",
    "ho man tin": "HOM", "hom": "HOM",
    "hung hom": "HUH", "huh": "HUH",
    "east tsim sha tsui": "ETS", "ets": "ETS",
    "austin": "AUS", "aus": "AUS",
    "mei foo": "MEF", "mef": "MEF",
    "tsuen wan west": "TWW", "tww": "TWW",
    "kam sheung road": "KSR", "ksr": "KSR",
    "yuen long": "YUL", "yul": "YUL",
    "long ping": "LOP", "lop": "LOP",
    "tin shui wai": "TIS", "tis": "TIS",
    "siu hong": "SIH", "sih": "SIH",
    "tuen mun": "TUM", "tum": "TUM",
    
    # East Rail Line (EAL)
    "exhibition centre": "EXC", "exc": "EXC",
    "mong kok east": "MKK", "mkk": "MKK",
    "kowloon tong": "KOT", "kot": "KOT",
    "sha tin": "SHT", "sht": "SHT",
    "fo tan": "FOT", "fot": "FOT",
    "racecourse": "RAC", "rac": "RAC",
    "university": "UNI", "uni": "UNI",
    "tai po market": "TAP", "tap": "TAP",
    "tai wo": "TWO", "two": "TWO",
    "fanling": "FAN", "fan": "FAN",
    "sheung shui": "SHS", "shs": "SHS",
    "lok ma chau": "LMC", "lmc": "LMC",
    "lo wu": "LOW", "low": "LOW",
    
    # South Island Line (SIL)
    "ocean park": "OCP", "ocp": "OCP",
    "wong chuk hang": "WCH", "wch": "WCH",
    "lei tung": "LET", "let": "LET",
    "south horizons": "SOH", "soh": "SOH",
    
    # Tsuen Wan Line (TWL)
    "tsim sha tsui": "TST", "tst": "TST",
    "jordan": "JOR", "jor": "JOR",
    "yau ma tei": "YMT", "ymt": "YMT",
    "mong kok": "MOK", "mok": "MOK",
    "prince edward": "PRE", "pre": "PRE",
    "sham shui po": "SSP", "ssp": "SSP",
    "cheung sha wan": "CSW", "csw": "CSW",
    "lai chi kok": "LCK", "lck": "LCK",
    "kwai fong": "KWF", "kwf": "KWF",
    "kwai hing": "KWH", "kwh": "KWH",
    "tai wo hau": "TWH", "twh": "TWH",
    "tsuen wan": "TSW", "tsw": "TSW",
    
    # Kwun Tong Line (KTL)
    "whampoa": "WHA", "wha": "WHA",
    "shek kip mei": "SKM", "skm": "SKM",
    "lok fu": "LOF", "lof": "LOF",
    "wong tai sin": "WTS", "wts": "WTS",
    "choi hung": "CHH", "chh": "CHH",
    "kowloon bay": "KOB", "kob": "KOB",
    "ngau tau kok": "NTK", "ntk": "NTK",
    "kwun tong": "KWT", "kwt": "KWT",
    "lam tin": "LAT", "lat": "LAT",
    
    # Disneyland Resort Line (DRL)
    "disneyland resort": "DIS", "dis": "DIS",
    "disneyland": "DIS",  # Alternative name
}

LINE_NAMES = {
    "airport express": "AEL", "ael": "AEL",
    "tung chung line": "TCL", "tcl": "TCL",
    "tuen ma line": "TML", "tml": "TML",
    "tseung kwan o line": "TKL", "tkl": "TKL",
    "east rail line": "EAL", "eal": "EAL",
    "south island line": "SIL", "sil": "SIL",
    "tsuen wan line": "TWL", "twl": "TWL",
    "island line": "ISL", "isl": "ISL",
    "kwun tong line": "KTL", "ktl": "KTL",
    "disneyland resort line": "DRL", "drl": "DRL",
}


def resolve_station_code(station_input: str) -> str:
    """
    Convert station name or code to standard code.
    Supports fuzzy matching for typos (e.g., "Tseng Kwan O" → "TKO").
    """
    normalized = station_input.lower().strip()
    
    # Try exact match first
    if normalized in STATION_NAMES:
        return STATION_NAMES[normalized]
    
    # Try fuzzy matching for typos (80% similarity threshold)
    matches = get_close_matches(normalized, STATION_NAMES.keys(), n=1, cutoff=0.8)
    if matches:
        matched_name = matches[0]
        return STATION_NAMES[matched_name]
    
    # If no match, return uppercase (might be a valid code)
    return station_input.upper()


def resolve_line_code(line_input: str) -> str:
    """
    Convert line name or code to standard code.
    Supports fuzzy matching for typos.
    """
    normalized = line_input.lower().strip()
    
    # Try exact match first
    if normalized in LINE_NAMES:
        return LINE_NAMES[normalized]
    
    # Try fuzzy matching for typos (80% similarity threshold)
    matches = get_close_matches(normalized, LINE_NAMES.keys(), n=1, cutoff=0.8)
    if matches:
        matched_name = matches[0]
        return LINE_NAMES[matched_name]
    
    # If no match, return uppercase (might be a valid code)
    return line_input.upper()


def format_train_schedule(data: Dict) -> str:
    """Convert raw API data into human-readable text."""
    
    # Check for API errors (e.g., NT-204: The contents are empty!)
    if "error" in data:
        error_code = data.get("error", {}).get("errorCode", "Unknown")
        error_msg = data.get("error", {}).get("errorMsg", str(data["error"]))
        
        # Provide helpful messages for common errors
        if error_code == "NT-204" or "empty" in error_msg.lower():
            return (
                f"⚠️ No Train Data Available\n"
                f"Station may not have real-time data at this moment.\n"
                f"Possible reasons:\n"
                f"  • Station is closed or not in service\n"
                f"  • Real-time data temporarily unavailable\n"
                f"  • Station code may be incorrect\n\n"
                f"API Response: {error_code} - {error_msg}"
            )
        else:
            return f"❌ API Error: {error_code} - {error_msg}"
    
    # Check status
    if data.get("status") == 0:
        return f"⚠️ Service Alert: {data.get('message', 'Unknown issue')}"
    
    # Check for delay
    delay_notice = ""
    if data.get("isdelay") == "Y":
        delay_notice = "\n⚠️ Note: Service is currently delayed\n"
    
    # Get station data
    station_data = data.get("data", {})
    if not station_data:
        return "❌ No train data available"
    
    # Get the first (and usually only) station key
    station_key = list(station_data.keys())[0]
    trains = station_data[station_key]
    
    result = []
    result.append(f"🚇 MTR Train Schedule for {station_key}")
    result.append(f"🕐 Current Time: {data.get('curr_time', 'Unknown')}")
    if delay_notice:
        result.append(delay_notice)
    result.append("=" * 60)
    result.append("\nℹ️  Direction Guide:")
    result.append("   🔼 UPBOUND = Trains heading toward outer/peripheral stations")
    result.append("   🔽 DOWNBOUND = Trains heading toward central/city stations")
    result.append("")
    
    # Format UP direction trains
    up_trains = trains.get("UP", [])
    if up_trains:
        result.append("\n🔼 UPBOUND Trains:")
        result.append("-" * 60)
        for idx, train in enumerate(up_trains[:5], 1):  # Show max 5 trains
            ttnt = train.get("ttnt", "?")
            dest = train.get("dest", "Unknown")
            plat = train.get("plat", "?")
            time = train.get("time", "Unknown")
            
            if ttnt == "0" or ttnt == "-":
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - DEPARTING NOW ⚡")
            elif ttnt == "1":
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - 1 minute (arrives {time})")
            else:
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - {ttnt} minutes (arrives {time})")
    else:
        result.append("\n🔼 UPBOUND Trains: No trains scheduled")
    
    # Format DOWN direction trains
    down_trains = trains.get("DOWN", [])
    if down_trains:
        result.append("\n🔽 DOWNBOUND Trains:")
        result.append("-" * 60)
        for idx, train in enumerate(down_trains[:5], 1):  # Show max 5 trains
            ttnt = train.get("ttnt", "?")
            dest = train.get("dest", "Unknown")
            plat = train.get("plat", "?")
            time = train.get("time", "Unknown")
            
            if ttnt == "0" or ttnt == "-":
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - DEPARTING NOW ⚡")
            elif ttnt == "1":
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - 1 minute (arrives {time})")
            else:
                result.append(f"  {idx}. 🚆 Platform {plat} → {dest} - {ttnt} minutes (arrives {time})")
    else:
        result.append("\n🔽 DOWNBOUND Trains: No trains scheduled")
    
    result.append("\n" + "=" * 60)
    result.append("✅ Status: Normal operation" if data.get("isdelay") == "N" else "⚠️ Status: Service delay")
    
    return "\n".join(result)


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
            
            Valid line codes:
            - AEL: Airport Express (HOK, KOW, TSY, AIR, AWE)
            - TCL: Tung Chung Line (HOK, KOW, OLY, NAC, LAK, TSY, SUN, TUC)
            - TML: Tuen Ma Line (WKS, MOS, HEO, TSH, SHM, CIO, STW, CKT, TAW, HIK, DIH, KAT, SUW, TKW, HOM, HUH, ETS, AUS, NAC, MEF, TWW, KSR, YUL, LOP, TIS, SIH, TUM)
            - TKL: Tseung Kwan O Line (NOP, QUB, YAT, TIK, TKO, LHP, HAH, POA)
            - EAL: East Rail Line (ADM, EXC, HUH, MKK, KOT, TAW, SHT, FOT, RAC, UNI, TAP, TWO, FAN, SHS, LOW, LMC)
            - SIL: South Island Line (ADM, OCP, WCH, LET, SOH)
            - TWL: Tsuen Wan Line (CEN, ADM, TST, JOR, YMT, MOK, PRE, SSP, CSW, LCK, MEF, LAK, KWF, KWH, TWH, TSW)
            - ISL: Island Line (KET, HKU, SYP, SHW, CEN, ADM, WAC, CAB, TIH, FOH, NOP, QUB, TAK, SWH, SKW, HFC, CHW)
            - KTL: Kwun Tong Line (WHA, HOM, YMT, MOK, PRE, SKM, KOT, LOF, WTS, DIH, CHH, KOB, NTK, KWT, LAT, YAT, TIK)
            - DRL: Disneyland Resort Line (SUN, DIS)
            
        sta: Station name or code. Examples:
            Names: "Tseung Kwan O", "Hong Kong", "Admiralty"
            Codes: "TKO", "HOK", "ADM"
            
        lang: Language - 'EN' for English or 'TC' for Traditional Chinese. Default: 'EN'.

    Returns:
        Human-readable formatted train schedule with:
        - Current time
        - Direction guide (what upbound/downbound means)
        - Upbound trains: Heading toward outer/peripheral stations
          Examples: TKL up → Po Lam/LOHAS Park, AEL up → Airport/AsiaWorld Expo
        - Downbound trains: Heading toward central/city stations
          Examples: TKL down → North Point, AEL down → Hong Kong Station
        - Platform numbers
        - Destinations
        - Minutes until arrival
        - Arrival times
        - Service status (normal/delayed)
        
    Example output:
        🚇 MTR Train Schedule for TKL-TKO
        🕐 Current Time: 2025-10-21 10:15:00
        ============================================================
        
        ℹ️  Direction Guide:
           🔼 UPBOUND = Trains heading toward outer/peripheral stations
           🔽 DOWNBOUND = Trains heading toward central/city stations
        
        🔼 UPBOUND Trains:
        ------------------------------------------------------------
          1. 🚆 Platform 1 → LHP - 2 minutes (arrives 2025-10-21 10:17:00)
          2. 🚆 Platform 1 → POA - 5 minutes (arrives 2025-10-21 10:20:00)
        
        🔽 DOWNBOUND Trains:
        ------------------------------------------------------------
          1. 🚆 Platform 2 → NOP - 1 minute (arrives 2025-10-21 10:16:00)
          2. 🚆 Platform 2 → TIK - 7 minutes (arrives 2025-10-21 10:22:00)
        
        ============================================================
        ✅ Status: Normal operation
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

    This tool is intended for other agents to parse programmatically. It does NOT return
    human-friendly text (use `get_next_train_schedule` for that).
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
    
    This resource is Application-controlled - clients can include it as context.
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
    Provides read-only data about line connections and interchange stations.
    
    This resource is Application-controlled - helps AI understand MTR network.
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

**Note:** Some stations have out-of-system transfers via walkways (e.g., Central ↔ Hong Kong, 
Tsim Sha Tsui ↔ East Tsim Sha Tsui) but these are NOT same-station interchanges.

## Major Interchange Hubs (4+ lines):
- **Admiralty (ADM)**: 4 lines - EAL, ISL, SIL, TWL (Central hub)

## Line-to-Line Transfer Points:

**Airport Express (AEL) connections:**
- Hong Kong (HOK): AEL ↔ TCL
- Kowloon (KOW): AEL ↔ TCL
- Tsing Yi (TSY): AEL ↔ TCL

**Tseung Kwan O Line (TKL) connections:**
- North Point (NOP): TKL ↔ ISL
- Quarry Bay (QUB): TKL ↔ ISL
- Yau Tong (YAT): TKL ↔ KTL
- Tiu Keng Leng (TIK): TKL ↔ KTL

**Island Line (ISL) connections:**
- Admiralty (ADM): ISL ↔ TWL, SIL, EAL
- Central (CEN): ISL ↔ TWL
- North Point (NOP): ISL ↔ TKL
- Quarry Bay (QUB): ISL ↔ TKL

**Tung Chung Line (TCL) connections:**
- Hong Kong (HOK): TCL ↔ AEL
- Kowloon (KOW): TCL ↔ AEL
- Tsing Yi (TSY): TCL ↔ AEL
- Lai King (LAK): TCL ↔ TWL
- Nam Cheong (NAC): TCL ↔ TML
- Sunny Bay (SUN): TCL ↔ DRL

**Tuen Ma Line (TML) connections:**
- Tai Wai (TAW): TML ↔ EAL
- Diamond Hill (DIH): TML ↔ KTL
- Ho Man Tin (HOM): TML ↔ KTL
- Hung Hom (HUH): TML ↔ EAL
- Nam Cheong (NAC): TML ↔ TCL
- Mei Foo (MEF): TML ↔ TWL

**East Rail Line (EAL) connections:**
- Admiralty (ADM): EAL ↔ ISL, TWL, SIL
- Hung Hom (HUH): EAL ↔ TML
- Kowloon Tong (KOT): EAL ↔ KTL
- Tai Wai (TAW): EAL ↔ TML

**South Island Line (SIL) connections:**
- Admiralty (ADM): SIL ↔ ISL, TWL, EAL

**Tsuen Wan Line (TWL) connections:**
- Admiralty (ADM): TWL ↔ ISL, SIL, EAL
- Central (CEN): TWL ↔ ISL
- Lai King (LAK): TWL ↔ TCL
- Mei Foo (MEF): TWL ↔ TML
- Mong Kok (MOK): TWL ↔ KTL
- Prince Edward (PRE): TWL ↔ KTL
- Yau Ma Tei (YMT): TWL ↔ KTL

**Kwun Tong Line (KTL) connections:**
- Diamond Hill (DIH): KTL ↔ TML
- Ho Man Tin (HOM): KTL ↔ TML
- Kowloon Tong (KOT): KTL ↔ EAL
- Mong Kok (MOK): KTL ↔ TWL
- Prince Edward (PRE): KTL ↔ TWL
- Yau Ma Tei (YMT): KTL ↔ TWL
- Yau Tong (YAT): KTL ↔ TKL
- Tiu Keng Leng (TIK): KTL ↔ TKL

**Disneyland Resort Line (DRL) connections:**
- Sunny Bay (SUN): DRL ↔ TCL

## Complete Station Sequences by Line:

### Airport Express (AEL)
HOK (Hong Kong) → KOW (Kowloon) → TSY (Tsing Yi) → AIR (Airport) → AWE (AsiaWorld Expo)
- 5 stations total
- Express service (limited stops)

### Tseung Kwan O Line (TKL)
**Main Branch:** NOP (North Point) → QUB (Quarry Bay) → YAT (Yau Tong) → TIK (Tiu Keng Leng)
**Branch to LOHAS Park:** TIK → TKO (Tseung Kwan O) → HAH (Hang Hau) → LHP (LOHAS Park)
**Branch to Po Lam:** TIK → TKO (Tseung Kwan O) → HAH (Hang Hau) → POA (Po Lam)
- 8 stations total, 3 branches

### Island Line (ISL)
KET (Kennedy Town) → HKU → SYP (Sai Ying Pun) → SHW (Sheung Wan) → CEN (Central) → ADM (Admiralty) → WAC (Wan Chai) → CAB (Causeway Bay) → TIH (Tin Hau) → FOH (Fortress Hill) → NOP (North Point) → QUB (Quarry Bay) → TAK (Tai Koo) → SWH (Sai Wan Ho) → SKW (Shau Kei Wan) → HFC (Heng Fa Chuen) → CHW (Chai Wan)
- 17 stations total

### Tung Chung Line (TCL)
HOK (Hong Kong) → KOW (Kowloon) → OLY (Olympic) → NAC (Nam Cheong) → LAK (Lai King) → TSY (Tsing Yi) → SUN (Sunny Bay) → TUC (Tung Chung)
- 8 stations total

### Tuen Ma Line (TML)
WKS (Wu Kai Sha) → MOS (Ma On Shan) → HEO (Heng On) → TSH (Tai Shui Hang) → SHM (Shek Mun) → CIO (City One) → STW (Sha Tin Wai) → CKT (Che Kung Temple) → TAW (Tai Wai) → HIK (Hik Keng) → DIH (Diamond Hill) → KAT (Kai Tak) → SUW (Sung Wong Toi) → TKW (To Kwa Wan) → HOM (Ho Man Tin) → HUH (Hung Hom) → ETS (East Tsim Sha Tsui) → AUS (Austin) → NAC (Nam Cheong) → MEF (Mei Foo) → TWW (Tsuen Wan West) → KSR (Kam Sheung Road) → YUL (Yuen Long) → LOP (Long Ping) → TIS (Tin Shui Wai) → SIH (Siu Hong) → TUM (Tuen Mun)
- 27 stations total

### East Rail Line (EAL)
ADM (Admiralty) → EXC (Exhibition Centre) → HUH (Hung Hom) → MKK (Mong Kok East) → KOT (Kowloon Tong) → TAW (Tai Wai) → SHT (Sha Tin) → FOT (Fo Tan) → UNI (University) → TAP (Tai Po Market) → TWO (Tai Wo) → FAN (Fanling) → SHS (Sheung Shui)
**Branch to Lo Wu:** SHS → LOW (Lo Wu)
**Branch to Lok Ma Chau:** SHS → LMC (Lok Ma Chau)
- 16 stations total (including branches)
- Note: RAC (Racecourse) is a special station, operates only on race days

### South Island Line (SIL)
ADM (Admiralty) → OCP (Ocean Park) → WCH (Wong Chuk Hang) → LET (Lei Tung) → SOH (South Horizons)
- 5 stations total

### Tsuen Wan Line (TWL)
CEN (Central) → ADM (Admiralty) → TST (Tsim Sha Tsui) → JOR (Jordan) → YMT (Yau Ma Tei) → MOK (Mong Kok) → PRE (Prince Edward) → SSP (Sham Shui Po) → CSW (Cheung Sha Wan) → LCK (Lai Chi Kok) → MEF (Mei Foo) → LAK (Lai King) → KWF (Kwai Fong) → KWH (Kwai Hing) → TWH (Tai Wo Hau) → TSW (Tsuen Wan)
- 16 stations total

### Kwun Tong Line (KTL)
WHA (Whampoa) → HOM (Ho Man Tin) → YMT (Yau Ma Tei) → MOK (Mong Kok) → PRE (Prince Edward) → SKM (Shek Kip Mei) → KOT (Kowloon Tong) → LOF (Lok Fu) → WTS (Wong Tai Sin) → DIH (Diamond Hill) → CHH (Choi Hung) → KOB (Kowloon Bay) → NTK (Ngau Tau Kok) → KWT (Kwun Tong) → LAT (Lam Tin) → YAT (Yau Tong) → TIK (Tiu Keng Leng)
- 17 stations total

### Disneyland Resort Line (DRL)
SUN (Sunny Bay) → DIS (Disneyland Resort)
- 2 stations total

## Total Network Statistics:
- **10 lines** covering Hong Kong
- **93 stations** (some shared across lines)
- **21 interchange stations** for transfers
- **Longest line:** Tuen Ma Line (27 stations)
- **Shortest line:** Disneyland Resort Line (2 stations)

## Route Planning Tips:
1. Use Admiralty (ADM) for transfers between ISL, TWL, SIL, and EAL
2. Use Quarry Bay (QUB) or North Point (NOP) for ISL ↔ TKL transfers
3. Use Lai King (LAK) for TCL ↔ TWL transfers
4. Use Nam Cheong (NAC) for TCL ↔ TML transfers
5. Airport Express connects at Hong Kong, Kowloon, and Tsing Yi stations
6. Disneyland Resort Line only connects at Sunny Bay (TCL interchange)
"""


@mcp.prompt()
def check_next_train(line: str, station: str) -> str:
    """
    Prompt: Quick train schedule check.
    User-controlled template for checking next train arrivals.
    
    Args:
        line: MTR line name or code (e.g., "TKL" or "Tseung Kwan O Line")
        station: Station name or code (e.g., "TKO" or "Tseung Kwan O")
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
    User-controlled template for journey planning.
    
    Args:
        origin: Starting station name or code
        destination: Ending station name or code
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
    User-controlled template for multi-station analysis.
    
    Args:
        station1: First station to compare
        station2: Second station to compare
        station3: Optional third station to compare
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


if __name__ == "__main__":
    # FastMCP SSE transport configuration
    # The SSE endpoint will be available at http://localhost:8000/sse
    # MCP Inspector should connect to: http://127.0.0.1:8000/sse

    print("=" * 60)
    print("🚀 Starting MCP Server")
    print("=" * 60)
    print("📡 SSE Endpoint: http://127.0.0.1:8000/sse")
    print("🔍 MCP Inspector: Use http://127.0.0.1:8000/sse")
    print("⚠️  Note: http://127.0.0.1:8000 (without /sse) will give 404")
    print("=" * 60)
    print("\n✨ Features:")
    print("   📦 2 Tools: get_next_train_schedule, get_next_train_structured")
    print("   📚 2 Resources: mtr://stations/list, mtr://lines/map")
    print("   📝 3 Prompts: check_next_train, plan_mtr_journey, compare_stations")
    print("=" * 60)

    mcp.run(transport="sse")
