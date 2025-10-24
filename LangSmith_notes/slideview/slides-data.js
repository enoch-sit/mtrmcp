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
    }
];
