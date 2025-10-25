// Slide data for LangSmith Evaluation presentation
const slidesData = [
    {
        title: "What is LangSmith Evaluation?",
        bullets: [
            "LangSmith is a platform for evaluating, monitoring, and improving LLM applications with systematic testing frameworks.",
            "It enables developers to create datasets, run experiments, and compare different agent configurations with objective metrics.",
            "The Math Calculator QA system demonstrates evaluation concepts using a practical agent with tool-calling capabilities."
        ],
        code: `# Project Configuration
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=pr-evaluation-test
LANGCHAIN_TRACING_V2=true
BEDROCK_MODEL=amazon.nova-lite-v1:0
AWS_REGION=us-east-1

# Initialize LangSmith client
from langsmith import Client
client = Client()

# All runs are automatically traced`,
        image: "../../.playwright-mcp/01_project_overview.png"
    },
    {
        title: "Why Do We Need Datasets?",
        bullets: [
            "Datasets are collections of test examples with inputs and expected outputs that enable repeatable testing.",
            "They provide consistent test cases to objectively measure improvements or catch regressions across agent versions.",
            "Our Math Calculator QA dataset includes 4 examples covering math operations and edge cases (conversational queries)."
        ],
        code: `from langsmith import Client

client = Client()
dataset_name = "Math Calculator QA"

# Create dataset
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Math questions requiring calculator tool usage"
    )
else:
    dataset = client.read_dataset(dataset_name=dataset_name)`,
        image: "../../.playwright-mcp/02_dataset_examples.png"
    },
    {
        title: "How Do We Create Dataset Examples?",
        bullets: [
            "Use batch creation with create_examples() to add multiple test cases at once with inputs and outputs.",
            "Each example includes the question, expected answer, and metadata about tool usage expectations.",
            "Include edge cases like conversational queries that shouldn't trigger tool usage to validate agent behavior."
        ],
        code: `examples = [
    {
        "inputs": {"question": "What is 15 plus 27?"},
        "outputs": {"answer": "42", "should_use_tool": True, "expected_tool": "add"}
    },
    {
        "inputs": {"question": "Calculate 8 times 7"},
        "outputs": {"answer": "56", "should_use_tool": True, "expected_tool": "multiply"}
    },
    {
        "inputs": {"question": "What is 100 divided by 4?"},
        "outputs": {"answer": "25", "should_use_tool": True, "expected_tool": "divide"}
    },
    {
        "inputs": {"question": "Hello, how are you?"},
        "outputs": {"answer": "conversational response", "should_use_tool": False, "expected_tool": None}
    },
]

# Batch create all examples
client.create_examples(
    inputs=[ex["inputs"] for ex in examples],
    outputs=[ex["outputs"] for ex in examples],
    dataset_id=dataset.id,
)`
    },
    {
        title: "How Do We Define Tools for Agents?",
        bullets: [
            "Tools are Python functions decorated with @tool that agents can call to perform operations.",
            "Clear docstrings are crucial - the LLM uses them to decide when to call each tool.",
            "Our calculator has three tools: add, multiply, and divide with error handling for edge cases."
        ],
        code: `from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide first number by second number."""
    if b == 0:
        return "Error: Division by zero"
    return a / b

tools = [add, multiply, divide]
tools_by_name = {t.name: t for t in tools}`
    },
    {
        title: "What is the Agent Factory Pattern?",
        bullets: [
            "A factory function creates agents with different configurations while maintaining the same core logic.",
            "It enables easy A/B testing by generating variants with different system prompts or parameters.",
            "The factory captures trajectories (execution history) and extracts tool calls for evaluation."
        ],
        code: `def create_agent(system_prompt: str):
    """Factory function to create agents with different system prompts."""
    
    def agent_with_tools(inputs: dict) -> dict:
        question = inputs["question"]
        trajectory = []
        llm_with_tools = agent_llm.bind_tools(tools)
        
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
        trajectory.append({"step": "initial", "type": "user_message", "content": question})
        
        max_iterations = 3
        for iteration in range(max_iterations):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            
            trajectory.append({
                "step": f"llm_response_{iteration}", "type": "ai_message",
                "content": response.content,
                "tool_calls": len(response.tool_calls) if hasattr(response, 'tool_calls') else 0
            })
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
                    trajectory.append({
                        "step": f"tool_call_{iteration}", "type": "tool_call",
                        "tool": tool_call["name"], "args": tool_call["args"], "result": tool_result
                    })
                    messages.append(ToolMessage(content=str(tool_result), 
                                              tool_call_id=tool_call["id"], 
                                              name=tool_call["name"]))
            else:
                break
        
        return {
            "answer": messages[-1].content if messages else "No response",
            "trajectory": trajectory,
            "tool_calls": [t for t in trajectory if t["type"] == "tool_call"]
        }
    
    return agent_with_tools

# Usage
agent_a = create_agent(SYSTEM_PROMPT_A)
agent_b = create_agent(SYSTEM_PROMPT_B)`
    },
    {
        title: "What is a Rule-Based Evaluator?",
        bullets: [
            "Rule-based evaluators use simple logic like string matching or keyword detection for fast, deterministic scoring.",
            "The correctness evaluator checks if the expected numerical answer appears in the agent's response.",
            "They're ideal for clear success criteria but less flexible than LLM-as-judge approaches."
        ],
        code: `def correctness_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    """Check if answer contains the expected numerical result."""
    answer = outputs["answer"].lower()
    expected = str(reference_outputs["answer"]).lower()
    
    # Check if expected answer is in the response
    score = 1 if expected in answer else 0
    
    return {
        "key": "correctness",
        "score": score,
        "comment": f"Expected '{expected}' in answer"
    }

# Example usage:
# Input: "What is 15 plus 27?"
# Expected: "42"
# Agent output: "The answer is 42"
# Score: 1 (correct) ✅`
    },
    {
        title: "What is Trajectory Evaluation?",
        bullets: [
            "Trajectory evaluation examines the sequence of actions an agent takes, not just the final output.",
            "It validates that the correct tools were called when needed and that conversational queries didn't trigger tools.",
            "This is crucial for multi-step reasoning and ensuring agents follow expected behavior patterns."
        ],
        code: `def tool_usage_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    """Check if correct tool was used when needed."""
    should_use_tool = reference_outputs.get("should_use_tool", False)
    expected_tool = reference_outputs.get("expected_tool")
    
    tool_calls = outputs.get("tool_calls", [])
    tools_used = [tc["tool"] for tc in tool_calls]
    
    if should_use_tool:
        if expected_tool in tools_used:
            score = 1
            comment = f"Correctly used {expected_tool}"
        else:
            score = 0
            comment = f"Should use {expected_tool}, but used {tools_used}"
    else:
        if len(tools_used) == 0:
            score = 1
            comment = "Correctly did not use tools"
        else:
            score = 0
            comment = f"Should not use tools, but used {tools_used}"
    
    return {
        "key": "tool_usage",
        "score": score,
        "comment": comment
    }`,
        image: "../../.playwright-mcp/05_trajectory_detail.png"
    },
    {
        title: "What is LLM-as-Judge Evaluation?",
        bullets: [
            "LLM-as-judge uses another LLM to assess subjective qualities like helpfulness, clarity, or tone.",
            "It's more flexible than rule-based evaluators but slower and more expensive due to additional LLM calls.",
            "Use low temperature (0.0) for consistency and clear scoring criteria in the judge prompt."
        ],
        code: `def llm_judge_helpfulness(outputs: dict, reference_outputs: dict) -> dict:
    """Use LLM to judge the helpfulness of the response."""
    
    judge_prompt = f"""You are evaluating an AI assistant's response for helpfulness.

Question: {reference_outputs.get('question', 'N/A')}
Response: {outputs['answer']}

Rate the helpfulness on a scale of 0-1:
- 1.0: Very helpful, clear, and answers the question well
- 0.5: Somewhat helpful but could be clearer
- 0.0: Not helpful or confusing

Respond with ONLY a number between 0 and 1 (e.g., 0.8)"""
    
    try:
        judge_response = judge_llm.invoke([HumanMessage(content=judge_prompt)])
        score_text = judge_response.content.strip()
        
        # Extract number from response
        import re
        match = re.search(r'0\\.\\d+|1\\.0|0|1', score_text)
        if match:
            score = float(match.group())
        else:
            score = 0.5  # Default if can't parse
        
        return {
            "key": "helpfulness_llm_judge",
            "score": score,
            "comment": f"LLM judged: {score_text[:50]}"
        }
    except Exception as e:
        return {
            "key": "helpfulness_llm_judge",
            "score": 0.5,
            "comment": f"Error: {str(e)}"
        }`
    },
    {
        title: "What is Heuristic Evaluation?",
        bullets: [
            "Heuristic evaluators apply simple rules like checking response length, format, or structure.",
            "The response_length evaluator ensures answers are concise (20-200 characters) without being too brief.",
            "They're fast, free, and useful for quick sanity checks but don't assess content quality."
        ],
        code: `def response_length_evaluator(outputs: dict) -> dict:
    """Check if response is appropriately concise."""
    answer = outputs["answer"]
    length = len(answer)
    
    # Good range: 20-200 characters
    if 20 <= length <= 200:
        score = 1
    elif length < 20:
        score = 0.5  # Too short
    else:
        score = 0.7  # A bit long but acceptable
    
    return {
        "key": "response_length",
        "score": score,
        "comment": f"Length: {length} chars"
    }

# Evaluator Type Comparison:
# Rule-Based:    ⚡ Fast | 💵 Free | 🔧 Low flexibility
# Trajectory:    ⚡ Fast | 💵 Free | 🔧 Medium flexibility
# LLM-as-Judge:  🐌 Slow | 💰 Expensive | 🔧 High flexibility
# Heuristic:     ⚡ Fast | 💵 Free | 🔧 Low flexibility`
    },
    {
        title: "How Do We Run an Experiment?",
        bullets: [
            "Use the evaluate() function with your agent, dataset name, evaluators, and metadata for tracking.",
            "Each experiment processes all examples, runs all evaluators, and captures metrics, latency, and traces.",
            "Results are automatically uploaded to LangSmith with a unique experiment name for comparison."
        ],
        code: `from langsmith.evaluation import evaluate

results_a = evaluate(
    agent_a,  # Your target function
    data=dataset_name,
    evaluators=[correctness_evaluator, tool_usage_evaluator, 
                llm_judge_helpfulness, response_length_evaluator],
    experiment_prefix="math-agent-formal",
    description="Agent with formal, precise system prompt",
    metadata={
        "model": os.getenv("BEDROCK_MODEL"),
        "system_prompt": "formal",
        "variant": "A",
        "temperature": 0.7
    },
    max_concurrency=2,
)

print(f"✅ Experiment A Complete: {results_a.experiment_name}")

# What gets tracked:
# ✅ Input: The question
# ✅ Output: Agent's response
# ✅ Trajectory: Full execution trace
# ✅ Evaluator Scores: All 4 evaluator results
# ✅ Latency: How long it took
# ✅ Metadata: Model, variant, temperature, etc.`,
        image: "../../.playwright-mcp/03_experiments_list.png"
    },
    {
        title: "What is A/B Testing with System Prompts?",
        bullets: [
            "A/B testing compares two agent variants to determine which configuration performs better.",
            "Our example tests a formal prompt (concise, directive) vs. a friendly prompt (warm, explanatory).",
            "Both agents use the same tools and dataset but differ in tone and instruction style."
        ],
        code: `# Variant A: Formal system prompt
SYSTEM_PROMPT_A = """You are a precise mathematical assistant. 
When asked to perform calculations, you MUST use the available calculator tools.
Always use tools for arithmetic operations. Be formal and concise."""

# Variant B: Friendly system prompt
SYSTEM_PROMPT_B = """You are a friendly and helpful math tutor! 
When someone asks you to calculate something, use your calculator tools to help them out.
Use tools for math operations and explain your steps in a warm, encouraging way."""

agent_a = create_agent(SYSTEM_PROMPT_A)
agent_b = create_agent(SYSTEM_PROMPT_B)

# What's being tested?
# 📝 Tone: Formal vs. Friendly
# 📏 Length: Concise vs. Explanatory
# 🎯 Instruction: "MUST use" vs. "use your tools to help"`
    },
    {
        title: "How Do We Compare Two Experiments?",
        bullets: [
            "Run both variants on the same dataset with identical evaluators to ensure fair comparison.",
            "Tag each experiment with metadata (variant: A/B) to easily identify and filter results.",
            "In the LangSmith UI, select both experiments and click Compare for side-by-side analysis."
        ],
        code: `# Run Experiment A: Formal
results_a = evaluate(
    agent_a,
    data=dataset_name,
    evaluators=evaluators,
    experiment_prefix="math-agent-formal",
    metadata={"variant": "A", "system_prompt": "formal"},
)

# Run Experiment B: Friendly
results_b = evaluate(
    agent_b,
    data=dataset_name,  # Same dataset!
    evaluators=evaluators,  # Same evaluators!
    experiment_prefix="math-agent-friendly",
    metadata={"variant": "B", "system_prompt": "friendly"},
)

# Navigate to LangSmith UI:
# 1. Go to "Math Calculator QA" → "Experiments" tab
# 2. Click checkboxes for both experiments
# 3. Click "Compare" button
# 4. View side-by-side results with differences highlighted`,
        image: "../../.playwright-mcp/04_experiment_formal_detail.png"
    },
    {
        title: "What Results Did We Get from A/B Testing?",
        bullets: [
            "Formal variant: More concise (1.00 length score), faster (fewer tokens), but lower helpfulness (0.13).",
            "Friendly variant: Higher helpfulness (0.50), more engaging, but slightly longer responses (0.93 length score).",
            "Both variants: Equally correct (0.75), perfect tool usage (1.00) - the trade-off is conciseness vs. engagement."
        ],
        image: "../../.playwright-mcp/06_experiments_comparison.png"
    },
    {
        title: "LangSmith UI: Experiment Results",
        bullets: [
            "The Experiments tab shows aggregate charts for all metrics (correctness, helpfulness, tool usage, length).",
            "Each experiment row displays scores, latencies (P50, P99), error rates, and metadata columns.",
            "Click any experiment to see detailed results for each test example with color-coded scores (green = good, red = bad)."
        ],
        image: "../../.playwright-mcp/03_experiments_list.png"
    },
    {
        title: "LangSmith UI: Metadata Tracking",
        bullets: [
            "Metadata columns enable filtering experiments by model, variant, temperature, and custom tags.",
            "Track model versions, prompt templates, engineers, dates, and git commits for reproducibility.",
            "The UI provides powerful filtering and grouping capabilities for analyzing experiment trends."
        ],
        image: "../../.playwright-mcp/07_metadata_view.png"
    },
    {
        title: "What Metadata Should We Track?",
        bullets: [
            "Track model versions, temperature, prompt templates, and timestamps to enable filtering and reproducibility.",
            "Metadata appears as columns in the experiments table for easy grouping and comparison.",
            "Include engineer/team names, dates, and version numbers for collaborative work tracking."
        ],
        code: `# Add comprehensive metadata to experiments
results = evaluate(
    my_agent,
    data="Math Calculator QA",
    evaluators=evaluators,
    metadata={
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.7,
        "prompt_version": "v2.1",
        "date": "2025-10-24",
        "engineer": "team-ai",
        "git_commit": "a1b2c3d",
        "variant": "baseline"
    }
)

# Version your datasets too
client.update_dataset(
    dataset_id=dataset.id,
    metadata={
        "version": "v1.0",
        "created_date": "2025-10-24",
        "last_updated": "2025-10-24"
    }
)`
    },
    {
        title: "How Do We Capture Agent Trajectories?",
        bullets: [
            "Build trajectory tracking into your agent by appending each step (user message, LLM response, tool call) to an array.",
            "Include step type, content, tool names, arguments, and results for complete execution history.",
            "Return trajectory and extracted tool_calls in the agent output for evaluators to analyze."
        ],
        code: `trajectory = []

# Log user message
trajectory.append({
    "step": "initial", 
    "type": "user_message", 
    "content": question
})

# In agent loop:
for iteration in range(max_iterations):
    response = llm_with_tools.invoke(messages)
    
    # Log LLM response
    trajectory.append({
        "step": f"llm_response_{iteration}",
        "type": "ai_message",
        "content": response.content,
        "tool_calls": len(response.tool_calls) if hasattr(response, 'tool_calls') else 0
    })
    
    # Log tool executions
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            
            trajectory.append({
                "step": f"tool_call_{iteration}",
                "type": "tool_call",
                "tool": tool_call["name"],
                "args": tool_call["args"],
                "result": tool_result
            })

# Return trajectory with final answer
return {
    "answer": final_answer,
    "trajectory": trajectory,
    "tool_calls": [t for t in trajectory if t["type"] == "tool_call"]
}`
    },
    {
        title: "What are Best Practices for Evaluation?",
        bullets: [
            "Use multiple evaluator types (rule-based + trajectory + LLM-judge) for comprehensive assessment.",
            "Always establish a baseline before making changes and run on the same dataset for fair comparison.",
            "Include edge cases in datasets (conversational queries, error conditions) to test boundary behavior."
        ],
        code: `# Best practice: Multiple evaluator types
evaluators = [
    correctness_evaluator,      # Rule-based (exact match)
    tool_usage_evaluator,       # Trajectory (action validation)
    llm_judge_helpfulness,      # LLM-as-judge (quality)
    response_length_evaluator,  # Heuristic (format check)
]

# Best practice: Baseline first
baseline = evaluate(
    current_agent,
    data=dataset_name,
    evaluators=evaluators,
    experiment_prefix="baseline",
    metadata={"version": "v1.0"}
)

# Best practice: Edge cases in dataset
examples = [
    {"inputs": {"question": "What is 5 + 3?"}, ...},  # Normal case
    {"inputs": {"question": "Hello!"}, ...},          # No tool needed
    {"inputs": {"question": "10 / 0"}, ...},          # Error case
    {"inputs": {"question": "Calculate 2+3*4"}, ...}, # Order of operations
]`
    },
    {
        title: "How Do We Optimize Evaluation Performance?",
        bullets: [
            "Use max_concurrency to process multiple examples in parallel (2-4 for safety, up to 10 for speed).",
            "Skip expensive LLM-as-judge evaluators during rapid iteration, add them back for final validation.",
            "Consider using smaller dev datasets (10 examples) for quick testing before running full evaluation."
        ],
        code: `# Fast evaluation with higher concurrency
results = evaluate(
    agent,
    data=dataset_name,
    evaluators=[
        correctness_evaluator,      # Fast ⚡
        tool_usage_evaluator,       # Fast ⚡
        # llm_judge_helpfulness,    # Slow 🐌 - skip for iteration
        response_length_evaluator,  # Fast ⚡
    ],
    max_concurrency=10,  # Higher for speed
)

# Use dev/prod dataset split
dev_dataset = "Math Calculator QA - Dev"    # 10 examples
prod_dataset = "Math Calculator QA"         # 100 examples

# Iterate on dev
dev_results = evaluate(agent, data=dev_dataset, evaluators=fast_evaluators)

# Final validation on prod
prod_results = evaluate(agent, data=prod_dataset, evaluators=all_evaluators)`
    },
    {
        title: "What is the Complete Evaluation Workflow?",
        bullets: [
            "Create dataset → Define evaluators → Run baseline → Make improvements → Run new experiment → Compare.",
            "The iterative cycle of test-measure-improve leads to more reliable and capable AI systems over time.",
            "LangSmith tracks everything: experiments, traces, metrics, and metadata for reproducibility and collaboration."
        ],
        code: `# Complete evaluation workflow
from langsmith import Client
from langsmith.evaluation import evaluate

# 1. Create dataset
client = Client()
dataset = client.create_dataset("Math Calculator QA")
client.create_examples(inputs=[...], outputs=[...], dataset_id=dataset.id)

# 2. Define evaluators
evaluators = [correctness, tool_usage, helpfulness, conciseness]

# 3. Run baseline
baseline = evaluate(
    agent_v1, 
    data=dataset, 
    evaluators=evaluators,
    experiment_prefix="baseline"
)

# 4. Make improvements to your agent
# ... modify prompts, add tools, tune parameters ...

# 5. Run new experiment
improved = evaluate(
    agent_v2, 
    data=dataset,  # Same dataset
    evaluators=evaluators,  # Same evaluators
    experiment_prefix="improved"
)

# 6. Compare results in UI
print(f"Baseline: {baseline.experiment_name}")
print(f"Improved: {improved.experiment_name}")
# Navigate to LangSmith UI → Select both → Compare`
    },
    {
        title: "What Key Insights Did We Learn?",
        bullets: [
            "Systematic evaluation reveals objective trade-offs: formal prompts are concise but less engaging.",
            "Multiple evaluator types catch different issues: correctness, tool usage, helpfulness, and format.",
            "The Math Calculator QA system demonstrates all concepts: datasets, tools, trajectories, evaluators, A/B testing."
        ],
        code: `# Summary: Key Concepts Demonstrated

✅ 1. DATASETS
   - Created 'Math Calculator QA' with 4 examples
   - Includes inputs, expected outputs, and metadata

✅ 2. TOOL USAGE & TRAJECTORY
   - Defined 3 calculator tools (add, multiply, divide)
   - Tracked tool calls in agent trajectory
   - Evaluated correct tool usage

✅ 3. A/B TESTING
   - Variant A: Formal system prompt
   - Variant B: Friendly system prompt
   - Ran separate experiments for each variant

✅ 4. MULTIPLE EVALUATORS
   - Correctness: String match for numerical answers
   - Tool Usage: Trajectory evaluation
   - LLM-as-Judge: Helpfulness assessment
   - Response Length: Conciseness check

✅ 5. EXPERIMENTS
   - Two independent experiments (A and B)
   - Metadata tracking for comparison
   - Full traces and metrics in LangSmith UI

✅ 6. RESULTS
   - Formal: More concise, faster
   - Friendly: More helpful, engaging
   - Both: Equally correct, perfect tool usage`
    },
    
    // ========================================
    // NEW SECTION: MCP Server & FastAPI Integration
    // ========================================
    {
        title: "What is MCP (Model Context Protocol)?",
        bullets: [
            "MCP is an open protocol that standardizes how AI applications connect to external data sources and tools.",
            "It provides a universal interface for LLMs to access context: databases, APIs, file systems, and live services.",
            "MCP uses JSON-RPC 2.0 for communication with three core primitives: Resources, Prompts, and Tools."
        ],
        code: `# MCP Architecture

┌─────────────┐
│  AI Client  │  (Claude Desktop, Cursor, Custom Apps)
│   (LLM)     │
└──────┬──────┘
       │ MCP Protocol (JSON-RPC 2.0)
       │
┌──────▼──────┐
│ MCP Server  │  (Your Backend Service)
└──────┬──────┘
       │
       ├─► 📦 Resources (Read-only data)
       ├─► 📝 Prompts (Templates)
       └─► 🔧 Tools (Actions)

# Protocol Version: 2025-06-18
# Transport: HTTP Streamable, SSE, stdio`
    },
    {
        title: "How Does FastAPI Integrate with MCP?",
        bullets: [
            "FastAPI serves as the ASGI web framework, while FastMCP handles MCP protocol compliance.",
            "The integration allows MCP servers to be mounted at custom paths (e.g., /mcp) in existing FastAPI apps.",
            "FastAPI provides production features: CORS, authentication, routing, while FastMCP ensures JSON-RPC compliance."
        ],
        code: `from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Create FastAPI app
app = FastAPI(root_path="/mcp")

# Create MCP server
mcp = FastMCP("MTR Train Server")

@mcp.tool()
def get_train_schedule(line: str, station: str) -> str:
    """Get real-time MTR train schedule"""
    return query_mtr_api(line, station)

# Mount MCP server to FastAPI
app.mount("/", mcp.streamable_http_app())

# Result: http://yourhost/mcp/
# - Handles MCP protocol automatically
# - Compatible with MCP Inspector
# - Production-ready with FastAPI features`
    },
    {
        title: "What is the MTR MCP Server?",
        bullets: [
            "Real-world production MCP server providing Hong Kong MTR train schedules via government API.",
            "Implements 2 tools (human + machine output), 2 resources (stations/lines), and 3 prompt templates.",
            "Features fuzzy matching for station names (handles typos), multi-language support (EN/TC), and error handling."
        ],
        code: `from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mtr_next_train")

# Tools
@mcp.tool()
def get_next_train_schedule(line: str, sta: str, lang: str = "EN"):
    """Human-readable train schedule with emojis"""
    # Returns: 🚇 formatted schedule with platforms, times
    
@mcp.tool()
def get_next_train_structured(line: str, sta: str, lang: str = "EN"):
    """Machine-readable JSON for AI agents"""
    # Returns: {"up": [...], "down": [...], "timestamp": "..."}

# Resources
@mcp.resource("mtr://stations/list")
def get_station_list():
    """80+ MTR stations across 10 lines"""
    
@mcp.resource("mtr://lines/map")
def get_line_map():
    """21 interchange stations with connectivity"""

# Prompts
@mcp.prompt()
def plan_mtr_journey(origin: str, destination: str):
    """Journey planning prompt template"""`
    },
    {
        title: "What are MCP Protocol Compliance Requirements?",
        bullets: [
            "JSON-RPC 2.0: All messages follow strict request/response format with id, method, params.",
            "Initialization: Server negotiates protocol version (2025-06-18) and declares capabilities during handshake.",
            "Lifecycle Management: Proper startup, request processing, and shutdown with resource cleanup."
        ],
        code: `# Initialization Handshake
# Client → Server:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "clientInfo": {"name": "MCP Inspector"}
  }
}

# Server → Client:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    },
    "serverInfo": {"name": "mtr_next_train", "version": "1.0.0"}
  }
}

# FastMCP handles this automatically!`
    },
    {
        title: "What are FastAPI Mounting Patterns for MCP?",
        bullets: [
            "Embedded: Run MCP as standalone FastAPI app (simplest, single-purpose servers).",
            "Mounted: Integrate MCP into existing FastAPI app at custom path (production pattern).",
            "Multiple Servers: Host multiple specialized MCP servers in one FastAPI app (microservices)."
        ],
        code: `# Pattern 1: Embedded (Standalone)
mcp = FastMCP("Weather Server")
mcp.run(transport="streamable-http")  # Port 8000

# Pattern 2: Mounted to Existing App
app = FastAPI()
mcp = FastMCP("API MCP Server")
app.mount("/mcp", mcp.streamable_http_app())
# Access: http://host/mcp/

# Pattern 3: Multiple MCP Servers
weather_mcp = FastMCP("Weather Server")
news_mcp = FastMCP("News Server")

app = Starlette(routes=[
    Mount("/weather", app=weather_mcp.streamable_http_app()),
    Mount("/news", app=news_mcp.streamable_http_app()),
])
# Access: http://host/weather/, http://host/news/`
    },
    {
        title: "How Does MCP Security Work?",
        bullets: [
            "CORS Configuration: Expose Mcp-Session-Id header for browser-based clients with origin whitelisting.",
            "OAuth 2.1 Authentication: Implement TokenVerifier for JWT validation and scope-based access control.",
            "Localhost Binding: Default to 127.0.0.1 for security, use reverse proxy (nginx/caddy) for production."
        ],
        code: `from starlette.middleware.cors import CORSMiddleware

# CORS for browser clients
app = CORSMiddleware(
    mcp.streamable_http_app(),
    allow_origins=["https://your-app.com"],  # Whitelist
    allow_methods=["GET", "POST", "DELETE"],
    expose_headers=["Mcp-Session-Id"],  # Required!
)

# OAuth 2.1 Authentication
from mcp.server.auth.provider import TokenVerifier

class MyTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str):
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return AccessToken(
            access_token=token,
            scope=payload.get("scope", "")
        )

mcp = FastMCP("Secure Server", token_verifier=MyTokenVerifier())`
    },
    
    // ========================================
    // NEW SECTION: MCP Service Evaluation Framework
    // ========================================
    {
        title: "What is MCP Inspector?",
        bullets: [
            "Official testing and debugging tool for validating MCP server implementations and protocol compliance.",
            "Provides visual UI (port 6274) for interactive testing and CLI mode for automated testing/CI/CD.",
            "Validates initialization, tool schemas, resource access, prompt templates, and error handling."
        ],
        code: `# MCP Inspector Architecture

┌─────────────────┐
│  MCPI (React)   │  Port 6274 - Web UI
│  Visual Testing │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  MCPP (Node.js) │  Port 6277 - Proxy Server
│  MCP Proxy      │
└────────┬────────┘
         │ stdio / SSE / HTTP
         ▼
┌─────────────────┐
│   MCP Server    │  Your Server Under Test
│ (Python/Node)   │
└─────────────────┘

# Supports all transport types:
# - stdio (local subprocess)
# - SSE (Server-Sent Events)
# - HTTP Streamable (production)`
    },
    {
        title: "How Do We Install and Run MCP Inspector?",
        bullets: [
            "UI Mode: Interactive testing via browser at localhost:6274 with form-based tool inputs.",
            "CLI Mode: Automated testing for CI/CD pipelines with JSON output for validation.",
            "Configuration: Supports mcp.json files (Claude Desktop compatible) for server definitions."
        ],
        code: `# UI Mode - Interactive Testing
npx @modelcontextprotocol/inspector node build/index.js

# With environment variables
npx @modelcontextprotocol/inspector -e API_KEY=abc123 node server.js

# Access UI at: http://localhost:6274

# CLI Mode - Automated Testing
# List all tools
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method tools/list

# Call specific tool
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method tools/call \\
  --tool-name get_weather \\
  --tool-arg city=London

# Test remote HTTP server
npx @modelcontextprotocol/inspector --cli \\
  https://api.example.com/mcp \\
  --transport streamable-http \\
  --method tools/list`
    },
    {
        title: "What Does Protocol Compliance Testing Validate?",
        bullets: [
            "Initialization: Protocol version negotiation, capability declaration, server info presence.",
            "JSON-RPC Format: Valid 2.0 messages, correct id matching, proper error codes (-32601, -32602, -32603).",
            "Tool/Resource/Prompt Schemas: Parameter validation, response format, structured output compliance."
        ],
        code: `# Inspector validates all these aspects:

✓ Initialization Handshake
  - Protocol version match (2025-06-18)
  - Capability declaration (tools, resources, prompts)
  - Server info present (name, version)

✓ JSON-RPC 2.0 Compliance
  - Valid message format
  - Correct id matching in responses
  - Standard error codes:
    * -32700: Parse error
    * -32600: Invalid request
    * -32601: Method not found
    * -32602: Invalid params
    * -32603: Internal error

✓ Tool Schema Validation
  - Input parameters match schema
  - Required fields present
  - Response format (content array)
  - Structured output if defined

✓ Resource/Prompt Validation
  - URI format correctness
  - Content type headers
  - Subscription support`
    },
    {
        title: "How Do We Test Tools with MCP Inspector?",
        bullets: [
            "Inspector sends tools/list to discover available tools and their schemas.",
            "Call tools via tools/call with arguments, validates response format and content structure.",
            "Check for proper error handling, timeout behavior, and edge case responses."
        ],
        code: `# Testing Tool Execution Flow

# 1. Discover tools
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method tools/list > tools.json

# Response:
{
  "tools": [
    {
      "name": "get_next_train_schedule",
      "description": "Get MTR train schedule",
      "inputSchema": {
        "type": "object",
        "properties": {
          "line": {"type": "string"},
          "sta": {"type": "string"}
        },
        "required": ["line", "sta"]
      }
    }
  ]
}

# 2. Call tool
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method tools/call \\
  --tool-name get_next_train_schedule \\
  --tool-arg line=TKL \\
  --tool-arg sta=TKO

# 3. Validate response format
# ✓ Contains "result" or "error"
# ✓ Result has "content" array
# ✓ Content items have "type" field`
    },
    {
        title: "What is the MCP Inspector UI Testing Workflow?",
        bullets: [
            "Request History: See all JSON-RPC messages sent with timing information.",
            "Response Details: Full responses with color-coded success/error indicators.",
            "Tool Testing: Form-based inputs for testing tools without writing code."
        ],
        code: `# Inspector UI Features

┌──────────────────────────────────┐
│  MCP Inspector UI (Port 6274)   │
├──────────────────────────────────┤
│                                  │
│  🔌 Connection Status            │
│  ✅ Connected to: node server.js │
│                                  │
│  📋 Tools List                   │
│  ├─ get_next_train_schedule     │
│  ├─ get_next_train_structured   │
│  └─ plan_journey                 │
│                                  │
│  📝 Test Tool                    │
│  Tool: [get_next_train_schedule▼]│
│  ┌──────────────────────────┐   │
│  │ line: TKL                │   │
│  │ sta:  TKO                │   │
│  │ lang: EN                 │   │
│  └──────────────────────────┘   │
│  [Execute Tool]                  │
│                                  │
│  📊 Response                     │
│  ✅ Success (125ms)              │
│  {                               │
│    "content": [{                 │
│      "type": "text",             │
│      "text": "🚇 MTR Train..."  │
│    }]                            │
│  }                               │
└──────────────────────────────────┘`
    },
    {
        title: "How Do We Use Inspector for CI/CD Testing?",
        bullets: [
            "Create test scripts that run Inspector CLI commands and validate JSON output.",
            "Integrate into GitHub Actions or other CI pipelines for automated regression testing.",
            "Use jq or grep to parse results and fail builds on protocol violations or errors."
        ],
        code: `# GitHub Actions CI/CD Example

name: MCP Server Tests
on: [push, pull_request]

jobs:
  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build MCP Server
        run: npm run build
      
      - name: Test Protocol Compliance
        run: |
          npx @modelcontextprotocol/inspector --cli \\
            node build/index.js \\
            --method tools/list > tools.json
          
          # Validate response
          jq -e '.tools | length > 0' tools.json
      
      - name: Test Tool Execution
        run: |
          npx @modelcontextprotocol/inspector --cli \\
            node build/index.js \\
            --method tools/call \\
            --tool-name get_train \\
            --tool-arg line=TKL > result.json
          
          # Check response format
          jq -e '.content[0].type == "text"' result.json`
    },
    {
        title: "What Security Features Does Inspector Provide?",
        bullets: [
            "Session Token Authentication: Auto-generated tokens printed to console, required for proxy access.",
            "Localhost Binding: Inspector only binds to 127.0.0.1 to prevent remote access.",
            "DNS Rebinding Protection: Validates Origin headers to prevent malicious sites from accessing local servers."
        ],
        code: `# Security Configuration

# 1. Session Token (auto-generated)
npx @modelcontextprotocol/inspector node server.js

# Console output:
# 🔑 Session token: 3a1c267fad21f7150b7d624c160b7f09...
# 🌐 Open: http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=3a1c...

# 2. Localhost Binding (default)
# Inspector binds to: 127.0.0.1:6274
# Not accessible from: 192.168.x.x or external IPs

# 3. Origin Validation
# Request from: https://malicious-site.com
# Response: 403 Forbidden

# 4. Testing with Bearer Token
npx @modelcontextprotocol/inspector --cli \\
  https://api.example.com/mcp \\
  --header "Authorization: Bearer YOUR_TOKEN" \\
  --method tools/list

# Security Checklist:
# ✅ Auth Required: Connect without token → 401
# ✅ Origin Validation: Invalid origin → 403
# ✅ Localhost Only: Remote IP → Connection refused
# ✅ HTTPS Enforcement: HTTP in prod → Redirect`
    },
    {
        title: "How Do We Test Resources and Prompts?",
        bullets: [
            "Resources: Test with resources/list and resources/read, validate URI format and content types.",
            "Prompts: Use prompts/list and prompts/get with arguments to test template rendering.",
            "Subscriptions: For dynamic resources, test subscription capabilities and update notifications."
        ],
        code: `# Testing Resources

# List available resources
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method resources/list

# Response:
{
  "resources": [
    {"uri": "mtr://stations/list", "name": "MTR Stations"},
    {"uri": "mtr://lines/map", "name": "MTR Lines Map"}
  ]
}

# Read specific resource
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method resources/read \\
  --resource-uri "mtr://stations/list"

# Testing Prompts

# Get prompt with arguments
npx @modelcontextprotocol/inspector --cli node server.js \\
  --method prompts/get \\
  --prompt-name "plan_mtr_journey" \\
  --prompt-arg origin=TKO \\
  --prompt-arg destination=CEN

# Response:
{
  "messages": [{
    "role": "user",
    "content": {
      "type": "text",
      "text": "Plan journey from TKO to CEN..."
    }
  }]
}`
    },
    {
        title: "What are Inspector Performance Testing Capabilities?",
        bullets: [
            "Latency Measurement: Use time command to measure tool execution duration.",
            "Load Testing: Write custom scripts combining Inspector CLI with concurrent execution.",
            "Timeout Testing: Validate server behavior under slow operations and network delays."
        ],
        code: `# Measure Tool Execution Time
time npx @modelcontextprotocol/inspector --cli node server.js \\
  --method tools/call \\
  --tool-name expensive_operation

# Output: real 0m2.341s

# Load Testing Script (Python)
import asyncio
import subprocess
import time

async def benchmark_tool(iterations: int):
    start = time.time()
    
    tasks = []
    for i in range(iterations):
        tasks.append(
            asyncio.create_subprocess_exec(
                "npx", "@modelcontextprotocol/inspector",
                "--cli", "node", "server.js",
                "--method", "tools/call",
                "--tool-name", "get_data",
                "--tool-arg", f"id={i}"
            )
        )
    
    await asyncio.gather(*tasks)
    
    duration = time.time() - start
    print(f"Completed {iterations} requests in {duration:.2f}s")
    print(f"Average: {duration/iterations*1000:.2f}ms per request")

# Run: asyncio.run(benchmark_tool(100))`
    },
    {
        title: "What are Inspector Configuration Best Practices?",
        bullets: [
            "Use mcp.json for server definitions (compatible with Claude Desktop and Cursor).",
            "Export configurations from UI via 'Server Entry' or 'Servers File' buttons for team sharing.",
            "Track server configs in git for reproducibility and version control."
        ],
        code: `# mcp.json Configuration File

{
  "mcpServers": {
    "mtr-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "MTR_API_KEY": "your-key",
        "DEBUG": "true"
      }
    },
    "remote-server": {
      "type": "streamable-http",
      "url": "https://api.example.com/mcp"
    }
  }
}

# Launch with config
npx @modelcontextprotocol/inspector \\
  --config mcp.json \\
  --server mtr-server

# Export from UI
# 1. Click "Server Entry" → Copy JSON
# 2. Click "Servers File" → Download mcp.json
# 3. Commit to git: git add mcp.json

# Team usage
git clone repo
npx @modelcontextprotocol/inspector --config mcp.json`
    },
    {
        title: "UI Mode vs CLI Mode: When to Use Each?",
        bullets: [
            "UI Mode: Interactive development, visual debugging, exploring server capabilities, beginner-friendly testing.",
            "CLI Mode: Automation, CI/CD pipelines, batch testing, scripted workflows, performance benchmarking.",
            "Both modes test the same server, but UI provides rich visualization while CLI enables automation."
        ],
        code: `# Comparison Table

╔════════════════╦════════════════╦═════════════════╗
║    Feature     ║    UI Mode     ║    CLI Mode     ║
╠════════════════╬════════════════╬═════════════════╣
║ Use Case       ║ Development    ║ Automation      ║
║ Output         ║ Visual UI      ║ JSON/text       ║
║ Tool Testing   ║ Form inputs    ║ Command args    ║
║ Debugging      ║ Rich visuals   ║ Raw JSON        ║
║ Integration    ║ Manual         ║ CI/CD scripts   ║
║ Learning       ║ Beginner       ║ Developer       ║
║ Performance    ║ Single request ║ Batch testing   ║
║ Port           ║ 6274           ║ N/A (no UI)     ║
╚════════════════╩════════════════╩═════════════════╝

# Use UI Mode for:
# - First-time server testing
# - Visual tool exploration
# - Interactive debugging

# Use CLI Mode for:
# - GitHub Actions workflows
# - Pre-commit hooks
# - Load testing
# - Automated regression testing`
    },
    {
        title: "What is the Complete MCP Evaluation Workflow?",
        bullets: [
            "Develop server → Test locally with Inspector UI → Automate tests with Inspector CLI → Deploy with monitoring.",
            "Use Inspector to validate protocol compliance before deploying to production.",
            "Combine Inspector testing with LangSmith evaluation for comprehensive AI system validation."
        ],
        code: `# Complete MCP Evaluation Workflow

# 1. Develop MCP Server
mcp = FastMCP("My Server")

@mcp.tool()
def my_tool(param: str) -> str:
    return f"Result: {param}"

# 2. Test with Inspector UI (Development)
npx @modelcontextprotocol/inspector python server.py
# - Test tools interactively
# - Verify tool schemas
# - Check error cases

# 3. Create Automated Tests (CI/CD)
# test-mcp.sh
#!/bin/bash
npx @modelcontextprotocol/inspector --cli python server.py \\
  --method tools/list
npx @modelcontextprotocol/inspector --cli python server.py \\
  --method tools/call --tool-name my_tool --tool-arg param=test

# 4. Add to CI Pipeline
# .github/workflows/test.yml
- name: Test MCP Server
  run: ./test-mcp.sh

# 5. Deploy with Monitoring
# - Track tool execution times
# - Monitor error rates
# - Log protocol violations

# 6. Integrate with LangSmith (Optional)
# - Use MCP tools in LangGraph agents
# - Evaluate agent+MCP performance
# - Track tool usage patterns`
    },
    {
        title: "MCP + LangSmith: Complete Testing Strategy",
        bullets: [
            "MCP Inspector validates protocol compliance and server functionality (infrastructure layer).",
            "LangSmith evaluates agent behavior and tool usage quality (application layer).",
            "Together they provide end-to-end validation: protocol correctness + agent effectiveness."
        ],
        code: `# Layered Testing Strategy

┌─────────────────────────────────────────┐
│  LAYER 3: Agent Behavior Evaluation     │
│  Tool: LangSmith                        │
│  ├─ Agent correctness                   │
│  ├─ Tool usage patterns                 │
│  ├─ Response quality                    │
│  └─ A/B testing agent configs           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  LAYER 2: MCP Tool Functionality        │
│  Tool: MCP Inspector (UI/CLI)           │
│  ├─ Tool execution correctness          │
│  ├─ Resource access validation          │
│  ├─ Prompt template rendering           │
│  └─ Error handling                      │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  LAYER 1: Protocol Compliance           │
│  Tool: MCP Inspector                    │
│  ├─ JSON-RPC 2.0 format                 │
│  ├─ Initialization handshake            │
│  ├─ Schema validation                   │
│  └─ Transport compatibility             │
└─────────────────────────────────────────┘

# Example: Testing MTR MCP Server

# Layer 1: Protocol (Inspector CLI)
npx @modelcontextprotocol/inspector --cli python mcp_server.py \\
  --method tools/list

# Layer 2: Functionality (Inspector UI)
# Test get_next_train_schedule with TKL/TKO
# Verify formatted output

# Layer 3: Agent Usage (LangSmith)
from langsmith.evaluation import evaluate
results = evaluate(
    mtr_agent,
    data="MTR Journey Planning",
    evaluators=[correctness, tool_usage, helpfulness]
)`
    }
];
