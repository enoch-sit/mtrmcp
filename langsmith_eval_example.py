"""
Simple LangSmith Evaluation Example
Demonstrates dataset creation, evaluators, and experiment tracking
"""
import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 LangSmith Evaluation Example")
print("=" * 70)

# Verify configuration
print(f"\n✓ LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"✓ AWS_REGION: {os.getenv('AWS_REGION')}")
print(f"✓ Model: {os.getenv('BEDROCK_MODEL')}")

# Initialize LangSmith client
client = Client()

# ============================================================================
# STEP 1: Create a Dataset
# ============================================================================
dataset_name = "MTR Simple QA"

print(f"\n📊 Creating dataset: {dataset_name}")

# Check if dataset exists
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Simple Q&A examples for MTR train information"
    )
    
    # Create examples
    examples = [
        {
            "inputs": {"question": "What is MTR?"},
            "outputs": {"answer": "Mass Transit Railway, Hong Kong's metro system"}
        },
        {
            "inputs": {"question": "How many MTR lines are there?"},
            "outputs": {"answer": "10 lines"}
        },
        {
            "inputs": {"question": "What does TKL stand for?"},
            "outputs": {"answer": "Tseung Kwan O Line"}
        },
    ]
    
    client.create_examples(
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
        dataset_id=dataset.id,
    )
    print(f"✓ Created {len(examples)} examples")
else:
    print("✓ Dataset already exists")

# ============================================================================
# STEP 2: Define Target Function (System to Evaluate)
# ============================================================================
llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL", "amazon.nova-lite-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    model_kwargs={"temperature": 0.0, "max_tokens": 100}
)

def simple_qa(inputs: dict) -> dict:
    """Simple Q&A system using Bedrock."""
    response = llm.invoke([HumanMessage(content=inputs["question"])])
    return {"answer": response.content}

# ============================================================================
# STEP 3: Define Evaluators
# ============================================================================

# Evaluator 1: Exact match
def exact_match(outputs: dict, reference_outputs: dict) -> dict:
    """Check if answer exactly matches expected answer."""
    score = outputs["answer"].lower() == reference_outputs["answer"].lower()
    return {"key": "exact_match", "score": int(score)}

# Evaluator 2: Contains keywords
def contains_keywords(outputs: dict, reference_outputs: dict) -> dict:
    """Check if answer contains key terms from reference."""
    answer = outputs["answer"].lower()
    reference = reference_outputs["answer"].lower()
    # Simple keyword extraction (first word of each phrase)
    keywords = reference.split()[0:2]  # First 2 words
    score = any(kw in answer for kw in keywords)
    return {"key": "contains_keywords", "score": int(score)}

# Evaluator 3: Conciseness
def is_concise(outputs: dict) -> dict:
    """Check if answer is concise (< 100 chars)."""
    score = len(outputs["answer"]) < 100
    return {"key": "concise", "score": int(score)}

# ============================================================================
# STEP 4: Run Evaluation
# ============================================================================
print("\n🔬 Running evaluation...")
print("   Evaluators: exact_match, contains_keywords, concise")

results = evaluate(
    simple_qa,
    data=dataset_name,
    evaluators=[exact_match, contains_keywords, is_concise],
    experiment_prefix="simple-qa-baseline",
    description="Baseline evaluation of simple Q&A system",
    metadata={
        "model": os.getenv("BEDROCK_MODEL"),
        "temperature": 0.0,
        "version": "v1.0"
    },
    max_concurrency=2,
)

# ============================================================================
# STEP 5: Display Results
# ============================================================================
print("\n" + "=" * 70)
print("✅ Evaluation Complete!")
print("=" * 70)

# Print summary
print(f"\n📈 Experiment: {results.experiment_name}")
print(f"📊 View results: https://smith.langchain.com/")
print(f"🔗 Project: {os.getenv('LANGCHAIN_PROJECT')}")

# Print summary
print(f"\n� Summary:")
print(f"   Total examples evaluated: 3")
print(f"   Experiment ID: {results.experiment_name}")
print(f"   View detailed results at LangSmith UI")

print("\n" + "=" * 70)
print("🎓 Next Steps:")
print("   1. Visit LangSmith UI to see detailed traces")
print("   2. Compare this experiment with future runs")
print("   3. Try different models or prompts")
print("   4. Add more evaluators (LLM-as-judge, trajectory, etc.)")
print("=" * 70)
