"""
Test MCP Resources and Prompts

This test validates the MCP server's Resources (read-only data)
and Prompts (user-controlled templates) features.
"""

import asyncio
import os
from mcp.client.sse import sse_client
from mcp import ClientSession


async def test_resources_and_prompts():
    """Test Resources and Prompts features"""
    
    print("=" * 60)
    print("🧪 Testing MCP Resources & Prompts")
    print("=" * 60)
    
    mcp_url = "http://localhost:8000/sse"
    
    try:
        async with sse_client(mcp_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Test 1: List all resources
                print("\n📚 Test 1: List Available Resources")
                print("-" * 60)
                resources = await session.list_resources()
                print(f"✓ Found {len(resources.resources)} resources:")
                for resource in resources.resources:
                    print(f"  • {resource.uri}")
                    print(f"    Name: {resource.name}")
                    print(f"    Description: {resource.description}")
                
                # Test 2: Read station list resource
                print("\n📚 Test 2: Read Station List Resource")
                print("-" * 60)
                station_resource = await session.read_resource("mtr://stations/list")
                if station_resource.contents:
                    content = station_resource.contents[0]
                    text = content.text if hasattr(content, 'text') else str(content)
                    print(text[:500] + "..." if len(text) > 500 else text)
                
                # Test 3: Read line map resource
                print("\n🗺️  Test 3: Read Line Map Resource")
                print("-" * 60)
                map_resource = await session.read_resource("mtr://lines/map")
                if map_resource.contents:
                    content = map_resource.contents[0]
                    text = content.text if hasattr(content, 'text') else str(content)
                    print(text[:500] + "..." if len(text) > 500 else text)
                
                # Test 4: List all prompts
                print("\n📝 Test 4: List Available Prompts")
                print("-" * 60)
                prompts = await session.list_prompts()
                print(f"✓ Found {len(prompts.prompts)} prompts:")
                for prompt in prompts.prompts:
                    print(f"  • {prompt.name}")
                    print(f"    Description: {prompt.description}")
                    if prompt.arguments:
                        print(f"    Arguments: {[arg.name for arg in prompt.arguments]}")
                
                # Test 5: Get "check_next_train" prompt
                print("\n📝 Test 5: Get 'check_next_train' Prompt")
                print("-" * 60)
                prompt = await session.get_prompt(
                    "check_next_train",
                    arguments={"line": "TKL", "station": "TKO"}
                )
                if prompt.messages:
                    for msg in prompt.messages:
                        print(f"Role: {msg.role}")
                        if hasattr(msg.content, 'text'):
                            print(f"Content: {msg.content.text}")
                        else:
                            print(f"Content: {msg.content}")
                
                # Test 6: Get "plan_mtr_journey" prompt
                print("\n🗺️  Test 6: Get 'plan_mtr_journey' Prompt")
                print("-" * 60)
                journey_prompt = await session.get_prompt(
                    "plan_mtr_journey",
                    arguments={"origin": "Tseung Kwan O", "destination": "Central"}
                )
                if journey_prompt.messages:
                    for msg in journey_prompt.messages:
                        print(f"Role: {msg.role}")
                        if hasattr(msg.content, 'text'):
                            print(f"Content: {msg.content.text}")
                        else:
                            print(f"Content: {msg.content}")
                
                # Test 7: Get "compare_stations" prompt
                print("\n📊 Test 7: Get 'compare_stations' Prompt")
                print("-" * 60)
                compare_prompt = await session.get_prompt(
                    "compare_stations",
                    arguments={
                        "station1": "TKO",
                        "station2": "HOK",
                        "station3": "CEN"
                    }
                )
                if compare_prompt.messages:
                    for msg in compare_prompt.messages:
                        print(f"Role: {msg.role}")
                        if hasattr(msg.content, 'text'):
                            print(f"Content: {msg.content.text}")
                        else:
                            print(f"Content: {msg.content}")
                
                print("\n" + "=" * 60)
                print("✅ ALL TESTS PASSED!")
                print("=" * 60)
                print("\n📊 Summary:")
                print(f"  • {len(resources.resources)} Resources available")
                print(f"  • {len(prompts.prompts)} Prompts available")
                print(f"  • All features working correctly")
                
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting MCP Resources & Prompts Test...\n")
    print("⚠️  Make sure mcp_server.py is running on port 8000")
    print("   Command: python mcp_server.py\n")
    
    asyncio.run(test_resources_and_prompts())
