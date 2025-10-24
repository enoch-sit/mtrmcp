"""
Quick connection test for MCP server
"""
import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

async def test_connection():
    mcp_server_url = os.getenv("MCP_SERVER_URL", "https://project-1-04.eduhk.hk/mcp/sse")
    
    print(f"🔗 Testing connection to: {mcp_server_url}")
    print("=" * 60)
    
    try:
        # Use Streamable HTTP transport (2025-06-18 protocol)
        async with streamablehttp_client(mcp_server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                print("✓ Connecting...")
                await session.initialize()
                print("✓ Connection successful!")
                
                # Test listing tools
                print("\n📋 Listing tools...")
                tools = await session.list_tools()
                print(f"   Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test listing resources
                print("\n📚 Listing resources...")
                resources = await session.list_resources()
                print(f"   Found {len(resources.resources)} resources:")
                for res in resources.resources:
                    print(f"   - {res.uri}: {res.name}")
                
                # Test calling a tool
                print("\n🔧 Testing tool call...")
                result = await session.call_tool(
                    "get_next_train_schedule",
                    arguments={"line": "TKL", "sta": "TKO", "lang": "EN"}
                )
                print(f"   Tool result: {result.content[0].text[:100]}...")
                
                print("\n" + "=" * 60)
                print("✅ All tests passed!")
                
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if MCP server is running")
        print("2. Verify URL in .env file")
        print("3. Check network connection")

if __name__ == "__main__":
    asyncio.run(test_connection())
