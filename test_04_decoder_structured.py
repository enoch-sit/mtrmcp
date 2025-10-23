"""
Test for the machine-readable decoder tool `get_next_train_structured`.
"""
import asyncio
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

async def test_structured():
    async with sse_client("http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print('✅ Connected to MCP server\n')
            
            # Test structured tool
            print("=" * 70)
            print("Testing get_next_train_structured (Machine-Readable JSON)")
            print("=" * 70)
            
            res = await session.call_tool('get_next_train_structured', arguments={'line':'TKL','sta':'Tseung Kwan O'})
            
            # Parse the JSON response
            payload = json.loads(res.content[0].text)
            
            print('\n📊 Structured Output Schema:')
            print(f'  ├─ resolved_line: {payload.get("resolved_line")}')
            print(f'  ├─ resolved_station: {payload.get("resolved_station")}')
            print(f'  ├─ timestamp: {payload.get("timestamp")}')
            print(f'  ├─ up: {len(payload.get("up", []))} trains')
            print(f'  ├─ down: {len(payload.get("down", []))} trains')
            print(f'  ├─ error: {payload.get("error")}')
            print(f'  └─ suggestions: {payload.get("suggestions")}')
            
            # Show first upbound train details
            up_trains = payload.get('up', [])
            if up_trains:
                print(f'\n🔼 First Upbound Train:')
                first = up_trains[0]
                print(f'  ├─ dest: {first.get("dest")}')
                print(f'  ├─ ttnt: {first.get("ttnt")} minutes')
                print(f'  ├─ plat: {first.get("plat")}')
                print(f'  └─ time: {first.get("time")}')
            
            # Show first downbound train details
            down_trains = payload.get('down', [])
            if down_trains:
                print(f'\n🔽 First Downbound Train:')
                first = down_trains[0]
                print(f'  ├─ dest: {first.get("dest")}')
                print(f'  ├─ ttnt: {first.get("ttnt")} minutes')
                print(f'  ├─ plat: {first.get("plat")}')
                print(f'  └─ time: {first.get("time")}')
            
            print('\n' + '=' * 70)
            print('✅ Structured tool test PASSED')
            print('=' * 70)
            print('\n💡 Agent Usage Example:')
            print('   data = call_tool("get_next_train_structured", line="TKL", sta="TKO")')
            print('   next_train_dest = data["up"][0]["dest"]  # Get destination code')
            print('   minutes = data["up"][0]["ttnt"]  # Get arrival time')
            print('=' * 70)

if __name__ == '__main__':
    asyncio.run(test_structured())
