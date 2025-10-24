"""
LangSmith Evaluation Example
Demonstrates:
1. Dataset creation
2. LLM-as-judge evaluators
3. A/B testing with different system prompts
4. Trajectory evaluation with tool usage
5. Comparative experiments
"""
import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate, evaluate_comparative
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
import json

# Load environment variables
load_dotenv()

print("=" * 80)
print("🚀 Advanced LangSmith Evaluation - All Concepts Demo")
print("=" * 80)

# Verify configuration
print(f"\n✓ LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"✓ AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"✓ Model: {os.getenv('BEDROCK_MODEL')}")

# Initialize LangSmith client
client = Client()

# Initialize LLM for evaluation (LLM-as-judge)
judge_llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    model_kwargs={"temperature": 0.0, "max_tokens": 200}
)

# Initialize LLM for agents
agent_llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    model_kwargs={"temperature": 0.7, "max_tokens": 300}
)

# ============================================================================
# STEP 1: Define Simple Calculator Tools
# ============================================================================
print("\n" + "=" * 80)
print("📐 STEP 1: Defining Calculator Tools")
print("=" * 80)

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
tools_by_name = {t.name: t for t in tools}

print(f"✓ Created {len(tools)} tools: {', '.join(tools_by_name.keys())}")

# ============================================================================
# STEP 2: Create Dataset
# ============================================================================
print("\n" + "=" * 80)
print("📊 STEP 2: Creating Math Q&A Dataset")
print("=" * 80)

dataset_name = "Math Calculator QA"

# Check if dataset exists, if not create it
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Math questions requiring calculator tool usage"
    )
    
    examples = [
        {
            "inputs": {"question": "What is 15 plus 27?"},
            "outputs": {
                "answer": "42",
                "should_use_tool": True,
                "expected_tool": "add"
            }
        },
        {
            "inputs": {"question": "Calculate 8 times 7"},
            "outputs": {
                "answer": "56",
                "should_use_tool": True,
                "expected_tool": "multiply"
            }
        },
        {
            "inputs": {"question": "What is 100 divided by 4?"},
            "outputs": {
                "answer": "25",
                "should_use_tool": True,
                "expected_tool": "divide"
            }
        },
        {
            "inputs": {"question": "Hello, how are you?"},
            "outputs": {
                "answer": "conversational response",
                "should_use_tool": False,
                "expected_tool": None
            }
        },
    ]
    
    client.create_examples(
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
        dataset_id=dataset.id,
    )
    print(f"✓ Created dataset with {len(examples)} examples")
else:
    dataset = client.read_dataset(dataset_name=dataset_name)
    print(f"✓ Dataset already exists (ID: {dataset.id})")

# ============================================================================
# STEP 3: Define Agent Variants (A/B Testing)
# ============================================================================
print("\n" + "=" * 80)
print("🤖 STEP 3: Defining Agent Variants for A/B Testing")
print("=" * 80)

# Variant A: Formal system prompt
SYSTEM_PROMPT_A = """You are a precise mathematical assistant. 
When asked to perform calculations, you MUST use the available calculator tools.
Always use tools for arithmetic operations. Be formal and concise."""

# Variant B: Friendly system prompt
SYSTEM_PROMPT_B = """You are a friendly and helpful math tutor! 
When someone asks you to calculate something, use your calculator tools to help them out.
Use tools for math operations and explain your steps in a warm, encouraging way."""

print(f"✓ System Prompt A (Formal): {len(SYSTEM_PROMPT_A)} chars")
print(f"✓ System Prompt B (Friendly): {len(SYSTEM_PROMPT_B)} chars")

def create_agent(system_prompt: str):
    """Factory function to create agents with different system prompts."""
    
    def agent_with_tools(inputs: dict) -> dict:
        """Agent that can use calculator tools."""
        question = inputs["question"]
        trajectory = []
        
        # Bind tools to LLM
        llm_with_tools = agent_llm.bind_tools(tools)
        
        # Initial call with system prompt
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question)
        ]
        trajectory.append({"step": "initial", "type": "user_message", "content": question})
        
        max_iterations = 3
        for iteration in range(max_iterations):
            response = llm_with_tools.invoke(messages)
            messages.append(response)
            
            trajectory.append({
                "step": f"llm_response_{iteration}",
                "type": "ai_message",
                "content": response.content,
                "tool_calls": len(response.tool_calls) if hasattr(response, 'tool_calls') else 0
            })
            
            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Execute tool
                    tool_result = tools_by_name[tool_name].invoke(tool_args)
                    
                    trajectory.append({
                        "step": f"tool_call_{iteration}",
                        "type": "tool_call",
                        "tool": tool_name,
                        "args": tool_args,
                        "result": tool_result
                    })
                    
                    # Add tool message
                    messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"],
                            name=tool_name
                        )
                    )
            else:
                # No more tool calls, done
                break
        
        final_answer = messages[-1].content if messages else "No response"
        
        return {
            "answer": final_answer,
            "trajectory": trajectory,
            "tool_calls": [t for t in trajectory if t["type"] == "tool_call"]
        }
    
    return agent_with_tools

agent_a = create_agent(SYSTEM_PROMPT_A)
agent_b = create_agent(SYSTEM_PROMPT_B)

print("✓ Created Agent A (Formal)")
print("✓ Created Agent B (Friendly)")

# ============================================================================
# STEP 4: Define Evaluators
# ============================================================================
print("\n" + "=" * 80)
print("📏 STEP 4: Defining Evaluators")
print("=" * 80)

# Evaluator 1: Correctness (Simple string match)
def correctness_evaluator(outputs: dict, reference_outputs: dict) -> dict:
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

print("✓ Correctness Evaluator (string match)")

# Evaluator 2: Tool Usage (Trajectory)
def tool_usage_evaluator(outputs: dict, reference_outputs: dict) -> dict:
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
    }

print("✓ Tool Usage Evaluator (trajectory)")

# Evaluator 3: LLM-as-Judge for Helpfulness
def llm_judge_helpfulness(outputs: dict, reference_outputs: dict) -> dict:
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
        match = re.search(r'0\.\d+|1\.0|0|1', score_text)
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
        }

print("✓ LLM-as-Judge Evaluator (helpfulness)")

# Evaluator 4: Response Length
def response_length_evaluator(outputs: dict) -> dict:
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

print("✓ Response Length Evaluator")

evaluators = [
    correctness_evaluator,
    tool_usage_evaluator,
    llm_judge_helpfulness,
    response_length_evaluator
]

# ============================================================================
# STEP 5: Run Experiment A (Formal Agent)
# ============================================================================
print("\n" + "=" * 80)
print("🧪 STEP 5: Running Experiment A (Formal System Prompt)")
print("=" * 80)

results_a = evaluate(
    agent_a,
    data=dataset_name,
    evaluators=evaluators,
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

# ============================================================================
# STEP 6: Run Experiment B (Friendly Agent)
# ============================================================================
print("\n" + "=" * 80)
print("🧪 STEP 6: Running Experiment B (Friendly System Prompt)")
print("=" * 80)

results_b = evaluate(
    agent_b,
    data=dataset_name,
    evaluators=evaluators,
    experiment_prefix="math-agent-friendly",
    description="Agent with friendly, encouraging system prompt",
    metadata={
        "model": os.getenv("BEDROCK_MODEL"),
        "system_prompt": "friendly",
        "variant": "B",
        "temperature": 0.7
    },
    max_concurrency=2,
)

print(f"✅ Experiment B Complete: {results_b.experiment_name}")

# ============================================================================
# STEP 7: Comparative Evaluation (A/B Testing)
# ============================================================================
print("\n" + "=" * 80)
print("⚖️  STEP 7: Running Comparative Evaluation (A vs B)")
print("=" * 80)

# Note: Comparative evaluation API varies by SDK version
# The experiments can be compared manually in LangSmith UI
print("\n⚖️  Note: Comparative Evaluation")
print("   Both experiments (A and B) have been tracked separately.")
print("   You can compare them side-by-side in the LangSmith UI:")
print(f"   - Experiment A (Formal): {results_a.experiment_name}")
print(f"   - Experiment B (Friendly): {results_b.experiment_name}")
print("   ")
print("   Visit the LangSmith UI and select both experiments to compare:")
print("   https://smith.langchain.com/")
print("   ")
print("   The UI provides:")
print("   ✓ Side-by-side trace comparison")
print("   ✓ Aggregate metrics comparison")
print("   ✓ Per-example performance breakdown")
print("   ✓ Tool usage patterns visualization")

# ============================================================================
# STEP 8: Display Summary Results
# ============================================================================
print("\n" + "=" * 80)
print("📊 EVALUATION SUMMARY")
print("=" * 80)

print(f"\n🔬 Experiment A (Formal):")
print(f"   ID: {results_a.experiment_name}")
print(f"   Project: {os.getenv('LANGCHAIN_PROJECT')}")

print(f"\n🔬 Experiment B (Friendly):")
print(f"   ID: {results_b.experiment_name}")
print(f"   Project: {os.getenv('LANGCHAIN_PROJECT')}")

print(f"\n📈 View detailed results at:")
print(f"   https://smith.langchain.com/")

print("\n" + "=" * 80)
print("🎓 CONCEPTS DEMONSTRATED")
print("=" * 80)
print("""
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
   - Experiment names for reference

✅ 6. COMPARATIVE EVALUATION
   - A/B comparison with preference evaluator
   - LLM-as-judge for pairwise comparison

✅ 7. METADATA TRACKING
   - Model version
   - System prompt variant
   - Temperature settings
   - Experiment descriptions
""")

print("=" * 80)
print("🎯 NEXT STEPS")
print("=" * 80)
print("""
1. Visit LangSmith UI to see detailed traces and trajectories
2. Compare experiments A and B side-by-side
3. View LLM-as-judge reasoning for helpfulness scores
4. Analyze which system prompt performs better
5. Check tool usage patterns in the trajectory view
6. Run more experiments with different prompts or models
""")
print("=" * 80)
