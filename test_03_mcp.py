"""
Test 3: MCP Server connection and tool calls
"""
import asyncio
import os
from dotenv import load_dotenv
from mcp.client.sse import sse_client
from mcp import ClientSession

load_dotenv()

async def test_mcp():
    print("🧪 Test 3: MCP Server Connection")
    print("=" * 60)
    
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/sse")
    print(f"✓ MCP Server URL: {mcp_url}")
    
    print("\n📡 Connecting to MCP server...")
    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"✅ Connected! Found {len(tools.tools)} tool(s):")
            for tool in tools.tools:
                print(f"   • {tool.name}: {tool.description}")
            
            # Test calling the MTR tool
            print("\n🔧 Testing tool call...")
            print("   Calling: get_next_train_schedule(line='TKL', sta='TKO', lang='EN')")
            
            result = await session.call_tool(
                "get_next_train_schedule",
                arguments={"line": "TKL", "sta": "TKO", "lang": "EN"}
            )
            
            # Extract and display result
            if result.content:
                import json
                data = json.loads(result.content[0].text)
                print(f"✅ Got train data!")
                print(f"   Status: {data['status']} - {data['message']}")
                print(f"   System time: {data['sys_time']}")
                
                # Show first UP train
                if 'TKL-TKO' in data['data'] and data['data']['TKL-TKO']['UP']:
                    first_train = data['data']['TKL-TKO']['UP'][0]
                    print(f"   Next UP train: Platform {first_train['plat']} to {first_train['dest']} in {first_train['ttnt']} min")
            
            print("\n✅ Test 3 PASSED: MCP server is working!")

if __name__ == "__main__":
    asyncio.run(test_mcp())
