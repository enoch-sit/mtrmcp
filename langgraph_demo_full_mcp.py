"""
LangGraph Demo - Full MCP Feature Showcase with Memory
======================================================

This enhanced demo demonstrates ALL MCP features PLUS conversation memory:

🔧 MCP Features:
1. Tools (Model-controlled): get_next_train_schedule, get_next_train_structured
2. Resources (Application-controlled): mtr://stations/list, mtr://lines/map  
3. Prompts (User-controlled): check_next_train, plan_mtr_journey, compare_stations

💾 Memory Features:
4. Persistent conversation history using MemorySaver
5. Multi-turn context awareness
6. Reference to previous queries and stations

Flow:
- Discovers and loads MCP Resources as context
- Uses Prompts to guide user interactions  
- Invokes both human-friendly and structured Tools
- Maintains conversation memory across all turns
- Demonstrates contextual references like "that station", "previous query"
- Complete journey planning with historical context
"""

import asyncio
import os
from typing import Annotated
from dotenv import load_dotenv

from langchain_aws import ChatBedrock
from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from typing import TypedDict, Annotated

# Load environment variables
load_dotenv()

# Check environment variables first
def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with AWS credentials or run: aws configure")
        return False
    
    print("✓ Environment variables loaded")
    print(f"✓ Using model: {os.getenv('BEDROCK_MODEL', 'amazon.nova-lite-v1:0')}")
    print(f"✓ AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    return True

# AWS Bedrock LLM (with proper credential validation)
def create_llm():
    """Create AWS Bedrock LLM with proper error handling"""
    if not check_environment():
        return None
        
    try:
        llm = ChatBedrock(
            model_id=os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.7,
                "max_tokens": 5000,
            }
        )
        print("✓ AWS Bedrock LLM initialized")
        return llm
    except Exception as e:
        print(f"❌ AWS Bedrock initialization failed: {e}")
        return None


class AgentState(TypedDict):
    """State for LangGraph agent - same as working demo."""
    messages: Annotated[list, add_messages]


async def load_mcp_resources(session: ClientSession) -> dict:
    """
    Load all MCP Resources as context.
    
    Returns:
        dict with 'stations' and 'network' keys containing resource content
    """
    print("\n📚 Loading MCP Resources...")
    
    # List available resources
    resources = await session.list_resources()
    print(f"   Found {len(resources.resources)} resources:")
    for res in resources.resources:
        print(f"   - {res.uri}: {res.name}")
    
    # Read station list resource
    station_content = await session.read_resource("mtr://stations/list")
    stations_text = station_content.contents[0].text
    print(f"   ✓ Loaded station reference ({len(stations_text)} chars)")
    
    # Read network map resource
    network_content = await session.read_resource("mtr://lines/map")
    network_text = network_content.contents[0].text
    print(f"   ✓ Loaded network map ({len(network_text)} chars)")
    
    return {
        "stations": stations_text,
        "network": network_text
    }


async def demonstrate_prompts(session: ClientSession):
    """
    Demonstrate all MCP Prompts (user-controlled templates).
    """
    print("\n💬 Demonstrating MCP Prompts...")
    
    # List available prompts
    prompts = await session.list_prompts()
    print(f"   Found {len(prompts.prompts)} prompts:")
    for p in prompts.prompts:
        args = ", ".join([a.name for a in p.arguments]) if p.arguments else "none"
        print(f"   - {p.name}({args}): {p.description}")
    
    # Example 1: Quick schedule check
    print("\n   Example 1: Quick Schedule Check")
    prompt1 = await session.get_prompt(
        "check_next_train",
        arguments={"line": "TKL", "station": "TKO"}
    )
    print(f"   Prompt: {prompt1.messages[0].content.text[:100]}...")
    
    # Example 2: Journey planning
    print("\n   Example 2: Journey Planning")
    prompt2 = await session.get_prompt(
        "plan_mtr_journey",
        arguments={"origin": "Tseung Kwan O", "destination": "Central"}
    )
    print(f"   Prompt: {prompt2.messages[0].content.text[:100]}...")
    
    # Example 3: Station comparison
    print("\n   Example 3: Station Comparison")
    prompt3 = await session.get_prompt(
        "compare_stations",
        arguments={
            "station1": "Tseung Kwan O",
            "station2": "North Point",
            "station3": "Admiralty"
        }
    )
    print(f"   Prompt: {prompt3.messages[0].content.text[:100]}...")


async def create_mcp_tools(session: ClientSession):
    """
    Discover and wrap MCP Tools for LangChain.
    
    Returns:
        Tuple of (tool_decorators, tool_functions)
        - tool_decorators: List for .bind_tools()
        - tool_functions: Dict for manual execution
    """
    print("\n🔧 Loading MCP Tools...")
    
    # List available tools
    tools_list = await session.list_tools()
    print(f"   Found {len(tools_list.tools)} tools:")
    for t in tools_list.tools:
        print(f"   - {t.name}: {t.description}")
    
    # Create actual async functions that call MCP
    async def get_next_train_schedule_func(line: str, sta: str, lang: str = "EN") -> str:
        """Execute get_next_train_schedule via MCP"""
        result = await session.call_tool("get_next_train_schedule", arguments={"line": line, "sta": sta, "lang": lang})
        if result.content:
            return str(result.content[0].text if hasattr(result.content[0], 'text') else result.content[0])
        return str(result)
    
    async def get_next_train_structured_func(line: str, sta: str, lang: str = "EN") -> str:
        """Execute get_next_train_structured via MCP"""
        result = await session.call_tool("get_next_train_structured", arguments={"line": line, "sta": sta, "lang": lang})
        if result.content:
            return str(result.content[0].text if hasattr(result.content[0], 'text') else result.content[0])
        return str(result)
    
    # Create tool decorators for LangChain
    @tool
    async def get_next_train_schedule(line: str, sta: str, lang: str = "EN") -> str:
        """Get MTR train schedule (human-friendly). Use line codes like TKL, AEL and station codes like TKO, HOK."""
        return await get_next_train_schedule_func(line, sta, lang)
    
    @tool
    async def get_next_train_structured(line: str, sta: str, lang: str = "EN") -> str:
        """Get MTR train schedule (JSON format). Use line codes like TKL, AEL and station codes like TKO, HOK."""
        return await get_next_train_structured_func(line, sta, lang)
    
    tool_decorators = [get_next_train_schedule, get_next_train_structured]
    tool_functions = {
        "get_next_train_schedule": get_next_train_schedule_func,
        "get_next_train_structured": get_next_train_structured_func
    }
    
    print(f"   ✓ Wrapped {len(tool_decorators)} tools for LangChain")
    
    return tool_decorators, tool_functions


def create_agent_graph(mcp_tools, resources: dict, tool_functions: dict):
    """
    Create LangGraph agent with MCP tools and resource context.
    Uses MANUAL tool execution like langgraph_demo_with_history.py (WORKING pattern)
    
    Args:
        mcp_tools: List of wrapped MCP tool decorators
        resources: Dict with station and network resource content
        tool_functions: Dict mapping tool names to actual async functions
    """
    # Create LLM inside this function
    llm = create_llm()
    if llm is None:
        print("\n❌ Error: Cannot create agent without AWS Bedrock LLM")
        print("   Please configure AWS credentials and restart")
        return None
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(mcp_tools)
    
    # System message with resource context
    SYSTEM_PROMPT = f"""You are an MTR (Hong Kong Mass Transit Railway) assistant with access to:

🔧 TOOLS (Model-controlled - you decide when to call):
- get_next_train_schedule: Returns human-friendly text format (use line and sta codes like TKL, TKO)
- get_next_train_structured: Returns JSON with programmatic data (use line and sta codes)

📚 RESOURCES (Application-provided context):

{resources['stations']}

{resources['network']}

When helping users:
1. Use the station reference and network map to understand locations
2. Always use station CODES (TKO, HOK, CEN) and line CODES (TKL, AEL, ISL) in tool calls
3. Choose the appropriate tool:
   - get_next_train_schedule for direct user responses
   - get_next_train_structured when analyzing data programmatically
4. Translate user's station names to codes (e.g., "Tseung Kwan O" → "TKO")
5. Remember context from previous messages in the conversation
6. When users refer to "that station", "the same line", or "previous query", use conversation history

Be concise, helpful, and conversational!"""
    
    # Define agent node
    async def call_model(state: AgentState):
        """Call the LLM with current state"""
        messages = state["messages"]
        
        # Inject system prompt if not already present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    # Define tool execution node (SIMPLIFIED - like working demo)
    async def execute_tools(state: AgentState):
        """Execute any tool calls from the LLM - SIMPLIFIED EXECUTION"""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = []
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                try:
                    # Execute the tool function directly
                    if tool_call["name"] in tool_functions:
                        result = await tool_functions[tool_call["name"]](**tool_call["args"])
                        tool_results.append(
                            ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call["id"]
                            )
                        )
                    else:
                        tool_results.append(
                            ToolMessage(
                                content=f"Error: Tool {tool_call['name']} not found",
                                tool_call_id=tool_call["id"]
                            )
                        )
                except Exception as e:
                    tool_results.append(
                        ToolMessage(
                            content=f"Error executing tool: {str(e)}",
                            tool_call_id=tool_call["id"]
                        )
                    )
        
        return {"messages": tool_results}
    
    def should_continue(state: AgentState):
        """Determine if we should continue or end"""
        last_message = state["messages"][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "end"
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", execute_tools)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # After tools, go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile with memory for conversation history
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


async def run_full_mcp_demo():
    """
    Main demo: showcases all MCP features in action.
    
    ⚠️  IMPORTANT: This demo requires:
    1. MCP server running (either local or deployed)
    2. AWS credentials configured for Bedrock
    3. Proper MCP protocol version (2025-06-18 Streamable HTTP)
    """
    print("=" * 70)
    print("🚇 MTR MCP Demo - Full Feature Showcase")
    print("=" * 70)
    
    # Determine MCP server URL (prefer deployed production server)
    mcp_server_url = os.getenv("MCP_SERVER_URL", "https://project-1-04.eduhk.hk/mcp/sse")
    
    # Connect to MCP server
    print("\n🚀 Connecting to MCP server...")
    print(f"   ✓ Attempting to connect to {mcp_server_url}")
    
    if "localhost" in mcp_server_url or "127.0.0.1" in mcp_server_url:
        print("   (Make sure mcp_server.py or fastapi_mcp_integration.py is running locally)")
    else:
        print("   (Using deployed production server)")
    
    try:
        # Connect to MCP server via Streamable HTTP (2025-06-18 protocol)
        async with streamablehttp_client(mcp_server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Phase 1: Load Resources (Application-controlled)
                resources = await load_mcp_resources(session)
                
                # Phase 2: Demonstrate Prompts (User-controlled)
                await demonstrate_prompts(session)
                
                # Phase 3: Create Tools (Model-controlled)
                mcp_tools, tool_functions = await create_mcp_tools(session)
                
                # Phase 4: Build agent with full context
                print("\n🤖 Building LangGraph Agent...")
                app = create_agent_graph(mcp_tools, resources, tool_functions)
                
                if app is None:
                    print("\n" + "=" * 70)
                    print("⚠️  Demo stopped - AWS credentials required for agent")
                    print("=" * 70)
                    print("\n✅ MCP Features Successfully Demonstrated:")
                    print("   ✓ Resources: Loaded 2 resources (stations list, network map)")
                    print("   ✓ Prompts: Demonstrated 3 prompts (check, plan, compare)")
                    print("   ✓ Tools: Wrapped 2 tools for LangChain")
                    print("\nTo run the full agent demo:")
                    print("   1. Configure AWS credentials: aws configure")
                    print("   2. Or set environment variables:")
                    print("      set AWS_ACCESS_KEY_ID=your-key")
                    print("      set AWS_SECRET_ACCESS_KEY=your-secret")
                    print("   3. Run again: python langgraph_demo_full_mcp.py")
                    return
                
                print("   ✓ Agent ready with Tools, Resources, and Prompts")
                
                # 🎨 VISUALIZATION: Generate graph diagram with memory
                print("\n📊 GRAPH VISUALIZATION (With Memory):")
                print("=" * 70)
                try:
                    # Method 1: Mermaid diagram (always works)
                    mermaid_code = app.get_graph().draw_mermaid()
                    with open("graph_mermaid_full_mcp.txt", "w", encoding="utf-8") as f:
                        f.write(mermaid_code)
                    print("✓ Mermaid diagram saved to: graph_mermaid_full_mcp.txt")
                    print("  View online: https://mermaid.live/")
                    
                    # Method 2: PNG image (if graphviz installed)
                    try:
                        png_data = app.get_graph().draw_mermaid_png()
                        with open("graph_diagram_full_mcp.png", "wb") as f:
                            f.write(png_data)
                        print("✓ PNG diagram saved to: graph_diagram_full_mcp.png")
                    except Exception:
                        print("  (PNG generation skipped - install graphviz for PNG output)")
                except Exception as e:
                    print(f"⚠️  Visualization failed: {e}")
                print("=" * 70 + "\n")
                
                # Configuration for the conversation thread with memory
                config = {"configurable": {"thread_id": "full-mcp-demo-conversation"}}
                
                # Helper function to chat with memory
                async def chat_with_memory(user_message: str, config: dict):
                    """Send a message and get response while maintaining history"""
                    result = await app.ainvoke(
                        {"messages": [HumanMessage(content=user_message)]},
                        config=config
                    )
                    
                    # Extract the final AI response (skip messages with tool calls)
                    for msg in reversed(result["messages"]):
                        if isinstance(msg, AIMessage):
                            # Check if this is a tool-calling message
                            has_tool_calls = (hasattr(msg, 'tool_calls') and msg.tool_calls) or \
                                           (isinstance(msg.content, list) and 
                                            any(isinstance(c, dict) and c.get('type') == 'tool_use' for c in msg.content))
                            
                            if not has_tool_calls and msg.content:
                                # Extract text content
                                if isinstance(msg.content, str):
                                    return msg.content
                                elif isinstance(msg.content, list):
                                    # Nova Lite returns list of content blocks
                                    text_parts = [c.get('text', '') for c in msg.content if isinstance(c, dict) and c.get('type') == 'text']
                                    return ''.join(text_parts) if text_parts else str(msg.content)
                    
                    return "No response generated"
                
                # Phase 5: Interactive conversation with memory
                print("\n" + "=" * 70)
                print("💬 Starting Multi-turn Conversation with Memory")
                print("=" * 70)
                
                # Multi-turn conversation scenarios demonstrating memory and context
                print("\n🔄 Turn 1: Initial Query (MCP Resources + Tools)")
                print("-" * 70)
                print("👤 User: What's the next train from Tseung Kwan O to Hong Kong?")
                response = await chat_with_memory(
                    "What's the next train from Tseung Kwan O to Hong Kong?",
                    config
                )
                print(f"🤖 Assistant: {response}")
                
                print("\n\n🔄 Turn 2: Context Reference (Memory)")
                print("-" * 70)
                print("👤 User: What about trains going the other direction?")
                response = await chat_with_memory(
                    "What about trains going the other direction?",
                    config
                )
                print(f"🤖 Assistant: {response}")
                
                print("\n\n🔄 Turn 3: Different Station (Structured Tool)")
                print("-" * 70)
                print("👤 User: Now check Airport Express at Hong Kong station - give me structured data")
                response = await chat_with_memory(
                    "Now check Airport Express at Hong Kong station - give me structured data",
                    config
                )
                print(f"🤖 Assistant: {response}")
                
                print("\n\n🔄 Turn 4: Multi-station Comparison (Using History)")
                print("-" * 70)
                print("👤 User: Compare the first station I asked about with the Airport Express station")
                response = await chat_with_memory(
                    "Compare the first station I asked about with the Airport Express station",
                    config
                )
                print(f"🤖 Assistant: {response}")
                
                print("\n\n🔄 Turn 5: Journey Planning (Resources + Memory)")
                print("-" * 70)
                print("👤 User: Plan the best route between those two stations I mentioned")
                response = await chat_with_memory(
                    "Plan the best route between those two stations I mentioned",
                    config
                )
                print(f"🤖 Assistant: {response}")
                
                print("\n" + "=" * 70)
                print("✅ Full MCP Demo with Memory Complete!")
                print("=" * 70)
                print("\nFeatures Demonstrated:")
                print("✓ Resources: Loaded station list and network map as context")
                print("✓ Prompts: Showed check_next_train, plan_mtr_journey, compare_stations")
                print("✓ Tools: Used both human-friendly and structured tools")
                print("✓ Memory: Maintained conversation history across all turns")
                print("✓ Context: Referenced previous queries using memory")
                print("✓ LangGraph: Multi-turn conversation with tool routing")
                
                # Show conversation history
                print("\n📜 Full Conversation History:")
                print("-" * 70)
                try:
                    final_state = await app.aget_state(config)
                    for i, msg in enumerate(final_state.values["messages"], 1):
                        if isinstance(msg, HumanMessage):
                            print(f"{i}. 👤 User: {msg.content}")
                        elif isinstance(msg, AIMessage) and msg.content and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                            # Show only final responses, not tool-calling messages
                            content_preview = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                            print(f"{i}. 🤖 Agent: {content_preview}")
                        elif isinstance(msg, SystemMessage):
                            print(f"{i}. ⚙️ System: [MCP Resources & System prompt loaded]")
                except Exception as e:
                    print(f"   Could not retrieve conversation history: {e}")
                
                print("\n" + "=" * 70)
                print("🎉 All MCP Features + Memory Successfully Integrated!")
                print("=" * 70)
                print("✨ This demo now combines:")
                print("   • Complete MCP Protocol (Tools, Resources, Prompts)")
                print("   • Persistent Memory & Multi-turn Context")
                print("   • LangGraph State Management")
                print("   • AWS Bedrock Nova Lite Integration")
                
                # LangSmith tracing info
                if os.getenv("LANGCHAIN_TRACING_V2") == "true":
                    print("\n" + "=" * 70)
                    print("📊 LangSmith Tracing Enabled!")
                    print("=" * 70)
                    print("View detailed traces at: https://smith.langchain.com/")
                    print("\nYou can see:")
                    print("  • Every LLM call (Nova Lite) with token usage and cost")
                    print("  • Tool invocations with MCP server calls")
                    print("  • Memory operations and state persistence")
                    print("  • Multi-turn conversation flow")
                    print("  • Latency breakdown per step")
                    print("=" * 70)
                else:
                    print("\nℹ️  Enable LangSmith tracing for detailed observability:")
                    print("   set LANGCHAIN_TRACING_V2=true")
                    print("   set LANGCHAIN_API_KEY=your-api-key")
                
                print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("\nTroubleshooting:")
        print("   1. Check MCP server URL in .env file:")
        print("      MCP_SERVER_URL=https://project-1-04.eduhk.hk/mcp/sse (production)")
        print("      or")
        print("      MCP_SERVER_URL=http://localhost:8080/mcp/sse (local)")
        print("   2. If using local server, ensure it's running:")
        print("      python fastapi_mcp_integration.py")
        print("   3. Verify AWS credentials are configured")
        print("   4. Check network connection")


def main():
    """Main entry point"""
    print("\n🚀 Starting Full MCP Demo with Memory & Multi-turn Context...\n")
    
    # Check MCP server URL
    mcp_server_url = os.getenv("MCP_SERVER_URL", "https://project-1-04.eduhk.hk/mcp/sse")
    print(f"✓ MCP Server URL: {mcp_server_url}")
    
    if "localhost" in mcp_server_url or "127.0.0.1" in mcp_server_url:
        print("  (Using local development server)")
    else:
        print("  (Using deployed production server)")
    
    # Check environment variables
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        print("Note: MCP features will still be demonstrated without AWS credentials")
        print()
    else:
        print("✓ Environment variables loaded")
        print(f"✓ Using model: {os.getenv('BEDROCK_MODEL', 'amazon.nova-lite-v1:0')}")
        print(f"✓ AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    
    # Check LangSmith tracing status
    if os.getenv("LANGCHAIN_TRACING_V2") == "true":
        api_key = os.getenv("LANGCHAIN_API_KEY", "")
        if api_key:
            print(f"✓ LangSmith tracing enabled")
            print(f"  API Key: {api_key[:15]}...{api_key[-4:]}")
            print(f"  View traces at: https://smith.langchain.com/")
        else:
            print("⚠️  LANGCHAIN_TRACING_V2=true but no API key found")
    else:
        print("ℹ️  LangSmith tracing disabled (set LANGCHAIN_TRACING_V2=true to enable)")
    
    print()
    
    # Run the async demo
    asyncio.run(run_full_mcp_demo())


if __name__ == "__main__":
    main()
