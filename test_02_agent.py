"""
Test 2: Simple LangGraph Agent with a dummy tool
"""
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, add_messages
from typing import TypedDict, Annotated

load_dotenv()

print("🧪 Test 2: Simple Agent with Tools")
print("=" * 60)

# Define state with proper message reducer
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Use add_messages reducer

# Create a simple dummy tool
@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is sunny and 25°C"

# Initialize LLM with tools
llm = ChatBedrock(
    model_id="amazon.nova-lite-v1:0",
    region_name="us-east-1",
    model_kwargs={"temperature": 0.7, "max_tokens": 200}
)

llm_with_tools = llm.bind_tools([get_weather])

# Define agent nodes
def call_model(state: AgentState):
    """Call the LLM"""
    messages = state["messages"]
    print(f"\n📨 Messages sent to LLM ({len(messages)} messages):")
    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        content_preview = str(msg.content)[:50] if hasattr(msg, 'content') else "N/A"
        print(f"   {i+1}. {msg_type}: {content_preview}...")
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def execute_tools(state: AgentState):
    """Execute tool calls"""
    last_message = state["messages"][-1]
    tool_results = []
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            print(f"  🔧 Calling tool: {tool_call['name']} with args: {tool_call['args']}")
            result = get_weather.invoke(tool_call["args"])
            tool_results.append(
                ToolMessage(
                    content=result,
                    tool_call_id=tool_call["id"]
                )
            )
    
    return {"messages": tool_results}

def should_continue(state: AgentState):
    """Router"""
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "end"

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", execute_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
workflow.add_edge("tools", "agent")

app = workflow.compile()

# Test it
print("\n📝 Testing agent...")
print("Query: What's the weather in Hong Kong?")
result = app.invoke({"messages": [HumanMessage(content="What's the weather in Hong Kong?")]})

# Get final response
for msg in reversed(result["messages"]):
    if isinstance(msg, AIMessage) and msg.content:
        print(f"✅ Agent response: {msg.content}")
        break

print("\n✅ Test 2 PASSED: Simple agent with tools works!")
