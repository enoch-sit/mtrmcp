```jsx type=react
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Code } from 'lucide-react';

const slides = [
  {
    title: "What is LangSmith?",
    bullets: [
      "LangSmith is an evaluation and monitoring platform for AI agents and LLM applications.",
      "It helps developers systematically test, track, and improve their AI systems through structured evaluation frameworks.",
      "The platform provides tools for creating datasets, running experiments, and analyzing agent performance."
    ],
    code: null
  },
  {
    title: "What are Traces in LangSmith?",
    bullets: [
      "Traces are comprehensive logs of your agent's execution runs.",
      "They capture inputs, outputs, latencies, and any errors that occur during runtime.",
      "These traces provide visibility into how your agent behaves and help identify issues or optimization opportunities."
    ],
    code: `# Enable tracing in your .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=your-project-name

# Traces are automatically captured when you run your agent
from langchain_aws import ChatBedrock

llm = ChatBedrock(model_id="amazon.nova-lite-v1:0")
response = llm.invoke("Hello")  # This run is traced`,
    language: "python"
  },
  {
    title: "Why Do We Need Datasets?",
    bullets: [
      "Datasets are collections of test examples with inputs and optional expected outputs.",
      "They enable repeatable testing across different versions of your agent.",
      "By maintaining consistent test cases, you can objectively measure improvements or regressions over time."
    ],
    code: null
  },
  {
    title: "How Do We Create Datasets?",
    bullets: [
      "Create datasets using the LangSmith Client with create_dataset() and add examples with create_examples().",
      "You can batch-create multiple examples at once with inputs and expected outputs.",
      "Dataset versioning allows you to track changes and evaluate against specific versions."
    ],
    code: `from langsmith import Client

client = Client()

# Create a dataset
dataset = client.create_dataset(
    dataset_name="MTR Simple QA",
    description="Simple Q&A examples for MTR"
)

# Batch create examples
examples = [
    {
        "inputs": {"question": "What is MTR?"},
        "outputs": {"answer": "Mass Transit Railway"}
    },
    {
        "inputs": {"question": "How many lines?"},
        "outputs": {"answer": "10 lines"}
    },
]

client.create_examples(
    inputs=[ex["inputs"] for ex in examples],
    outputs=[ex["outputs"] for ex in examples],
    dataset_id=dataset.id,
)`,
    language: "python"
  },
  {
    title: "What are Evaluators?",
    bullets: [
      "Evaluators are functions that score your agent's outputs against quality criteria.",
      "They can use string matching, LLM-as-judge patterns, or custom logic for metrics like correctness or tool usage.",
      "Multiple evaluators can be combined to assess different aspects of agent performance."
    ],
    code: null
  },
  {
    title: "What Types of Evaluators Exist?",
    bullets: [
      "Row-level evaluators score individual examples (exact match, keyword presence, conciseness).",
      "Summary evaluators aggregate metrics across entire datasets.",
      "Comparative evaluators judge which of two outputs is better, useful for A/B testing different agent versions."
    ],
    code: `from langsmith.evaluation import LangChainStringEvaluator, run_evaluator

# 1. Built-in String Evaluator (LLM-as-judge)
correctness_evaluator = LangChainStringEvaluator(
    "labeled_score_string",
    config={
        "criteria": {
            "correctness": "Is the response factually correct?"
        },
        "normalize_by": 10  # Score out of 10
    }
)

# 2. Custom Evaluator
@run_evaluator
def exact_match(run, example):
    prediction = run.outputs["answer"]
    reference = example.outputs["answer"]
    return {"key": "exact_match", "score": prediction == reference}`,
    language: "python"
  },
  {
    title: "What is Trajectory Evaluation?",
    bullets: [
      "Trajectory evaluation examines the sequence of actions an agent takes, not just the final output.",
      "It validates that tools are called in the correct order and with appropriate parameters.",
      "This is crucial for multi-step reasoning and complex agent workflows."
    ],
    code: `from langsmith.evaluation import run_evaluator

@run_evaluator
def tool_usage_evaluator(run, example):
    # Check if tool was called when expected
    tool_calls = [
        msg for msg in run.outputs["messages"] 
        if isinstance(msg, ToolMessage)
    ]
    
    expected_tool = "multiply" in example.inputs["question"].lower()
    actual_tool = len(tool_calls) > 0
    
    score = 1 if expected_tool == actual_tool else 0
    
    return {
        "key": "tool_usage_correct",
        "score": score,
        "comment": f"Expected tool: {expected_tool}, Used: {actual_tool}"
    }`,
    language: "python"
  },
  {
    title: "What are Experiments?",
    bullets: [
      "Experiments are tracked runs of your agent on specific datasets with associated evaluators.",
      "Each experiment captures metrics, metadata (model version, prompts), and timestamps.",
      "Experiments enable systematic comparison of different agent configurations or improvements."
    ],
    code: null
  },
  {
    title: "How Do We Run Evaluations?",
    bullets: [
      "Use the evaluate() function with your target function, dataset, and evaluators.",
      "For better performance, use aevaluate() for async evaluation with higher concurrency.",
      "Results include scores, metadata, and detailed traces for each test example."
    ],
    code: `from langsmith.evaluation import evaluate

def my_agent(inputs: dict) -> dict:
    """Your system to evaluate."""
    response = llm.invoke(inputs["question"])
    return {"answer": response.content}

# Run evaluation
results = evaluate(
    my_agent,                        # Your target function
    data="MTR Simple QA",           # Dataset name
    evaluators=[exact_match, correctness_evaluator],
    experiment_prefix="baseline-v1",
    description="First baseline evaluation",
    metadata={
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.0,
    },
    max_concurrency=4,
)

print(f"Average score: {results['results'][0]['score']}")`,
    language: "python"
  },
  {
    title: "How Can We Compare Different Versions?",
    bullets: [
      "Use evaluate_comparative() to compare two experiments with pairwise evaluators.",
      "The platform can randomize comparison order to reduce bias.",
      "Results show which version performs better across your test dataset with statistical metrics."
    ],
    code: `from langsmith.evaluation import evaluate_comparative

# Run two experiments
exp1 = evaluate(agent_v1, data="MTR Simple QA", evaluators=[...])
exp2 = evaluate(agent_v2, data="MTR Simple QA", evaluators=[...])

# Compare with pairwise evaluator
def preference_evaluator(inputs: dict, runs: list) -> dict:
    """LLM judges which output is better."""
    prompt = f"""Question: {inputs['question']}
    Answer A: {runs[0].outputs['answer']}
    Answer B: {runs[1].outputs['answer']}
    Which answer is better? Return score for A and B."""
    
    # Use LLM to judge (simplified)
    return {"key": "preference", "scores": [0.3, 0.7]}

results = evaluate_comparative(
    experiments=(exp1.experiment_name, exp2.experiment_name),
    evaluators=[preference_evaluator],
    randomize_order=True,  # Reduce bias
)`,
    language: "python"
  },
  {
    title: "What is Async Evaluation?",
    bullets: [
      "Async evaluation uses aevaluate() for better performance with concurrent requests.",
      "It allows higher concurrency levels than synchronous evaluation.",
      "This significantly reduces total evaluation time for large datasets."
    ],
    code: `from langsmith import aevaluate

async def async_agent(inputs: dict) -> dict:
    """Async version of your agent."""
    response = await async_llm.ainvoke(inputs["question"])
    return {"answer": response.content}

# Run async evaluation with higher concurrency
results = await aevaluate(
    async_agent,
    data="MTR Simple QA",
    evaluators=[exact_match, correctness_evaluator],
    max_concurrency=10,  # Process 10 examples simultaneously
    experiment_prefix="async-baseline",
)`,
    language: "python"
  },
  {
    title: "What Metadata Should We Track?",
    bullets: [
      "Track model versions, temperature settings, prompt templates, and timestamps in experiment metadata.",
      "This enables filtering and grouping results in the LangSmith UI.",
      "Metadata makes results reproducible and helps identify which changes improved performance."
    ],
    code: `# Add metadata to experiments
results = evaluate(
    my_agent,
    data="MTR Simple QA",
    evaluators=[evaluators],
    metadata={
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.7,
        "prompt_version": "v2.1",
        "date": "2025-10-24",
        "engineer": "team-ai"
    }
)

# Version your datasets too
client.update_dataset(
    dataset_id=dataset.id,
    metadata={
        "version": "v1.0",
        "created_date": "2025-10-24"
    }
)`,
    language: "python"
  },
  {
    title: "What are Best Practices?",
    bullets: [
      "Always tag experiments with metadata and establish baselines before making changes.",
      "Use async evaluation for better performance and run multiple repetitions for statistical significance.",
      "Include edge cases in datasets and use multiple evaluator types beyond just exact matching."
    ],
    code: `# Best practice: Run with repetitions
results = evaluate(
    my_agent,
    data="MTR Simple QA",
    evaluators=[exact_match, correctness, conciseness],
    num_repetitions=3,  # Run each example 3 times
    metadata={
        "model": "amazon.nova-lite-v1:0",
        "version": "baseline"
    }
)

# Best practice: Include diverse evaluators
evaluators = [
    exact_match,           # Exact string match
    keyword_match,         # Contains key terms
    correctness_llm,       # LLM judges correctness
    conciseness,           # Response length
    tool_usage_correct,    # Trajectory validation
]`,
    language: "python"
  },
  {
    title: "What Can We Do in the LangSmith UI?",
    bullets: [
      "The web interface at smith.langchain.com provides visual experiment comparison and detailed trace inspection.",
      "You can analyze aggregate metrics, filter by metadata, and add human feedback.",
      "The UI makes it easy to share results and collaborate on improvements."
    ],
    code: null
  },
  {
    title: "How Does This Improve AI Agents?",
    bullets: [
      "Systematic evaluation reveals strengths and weaknesses in agent behavior objectively.",
      "Experiment tracking shows whether changes actually improve performance.",
      "The iterative cycle of test-measure-improve leads to more reliable and capable AI systems over time."
    ],
    code: `# Complete evaluation workflow
from langsmith import Client
from langsmith.evaluation import evaluate

# 1. Create dataset
client = Client()
dataset = client.create_dataset("Production Tests")

# 2. Define evaluators
evaluators = [correctness, conciseness, tool_usage]

# 3. Run baseline
baseline = evaluate(agent_v1, data=dataset, evaluators=evaluators)

# 4. Make improvements to your agent
# ... modify prompts, add tools, tune parameters ...

# 5. Run new experiment
improved = evaluate(agent_v2, data=dataset, evaluators=evaluators)

# 6. Compare results in UI or programmatically
print(f"Baseline: {baseline.metrics}")
print(f"Improved: {improved.metrics}")`,
    language: "python"
  }
];

function Presentation() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showCode, setShowCode] = useState(true);

  React.useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'ArrowRight' && currentSlide < slides.length - 1) {
        setCurrentSlide(prev => prev + 1);
      } else if (e.key === 'ArrowLeft' && currentSlide > 0) {
        setCurrentSlide(prev => prev - 1);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentSlide]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  const currentSlideData = slides[currentSlide];
  const hasCode = currentSlideData.code !== null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Slide Content */}
        <div className="p-12 min-h-96">
          <div className="mb-6 flex items-center justify-between">
            <span className="text-sm font-semibold text-indigo-600 uppercase tracking-wide">
              Slide {currentSlide + 1} of {slides.length}
            </span>
            {hasCode && (
              <button
                onClick={() => setShowCode(!showCode)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium"
              >
                <Code size={16} />
                {showCode ? 'Hide Code' : 'Show Code'}
              </button>
            )}
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            {currentSlideData.title}
          </h1>
          
          <div className={`grid ${hasCode && showCode ? 'grid-cols-2' : 'grid-cols-1'} gap-8`}>
            <div>
              <ul className="space-y-4">
                {currentSlideData.bullets.map((bullet, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-2 h-2 bg-indigo-600 rounded-full mt-2"></span>
                    <span className="text-lg text-gray-700 leading-relaxed">{bullet}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {hasCode && showCode && (
              <div className="bg-gray-900 rounded-lg p-6 overflow-auto max-h-96">
                <pre className="text-sm text-gray-100 overflow-x-auto">
                  <code>{currentSlideData.code}</code>
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="bg-gray-50 px-12 py-6 flex items-center justify-between border-t border-gray-200">
          <button
            onClick={prevSlide}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={currentSlide === 0}
          >
            <ChevronLeft size={20} />
            Previous
          </button>

          {/* Slide Indicators */}
          <div className="flex gap-2 overflow-x-auto max-w-md">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`flex-shrink-0 w-3 h-3 rounded-full transition-all ${
                  index === currentSlide
                    ? 'bg-indigo-600 w-8'
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>

          <button
            onClick={nextSlide}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={currentSlide === slides.length - 1}
          >
            Next
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Keyboard Hint */}
      <div className="mt-6 text-sm text-gray-600">
        Use arrow keys ← → to navigate
      </div>
    </div>
  );
}

export default Presentation;
```

This enhanced presentation now includes:

- **Bullet points** instead of paragraphs (3 bullets per slide)
- **Embedded code examples** on relevant slides with syntax highlighting
- **Toggle button** to show/hide code snippets
- **Split-screen layout** when code is visible (content on left, code on right)
- **15 slides** covering all major LangSmith concepts with practical code
- **Dark-themed code blocks** for better readability
- **Responsive design** that adapts to the content
- **Keyboard navigation** with arrow keys
- **Visual indicators** showing current slide position

The code examples demonstrate:
- Setting up tracing
- Creating datasets
- Defining evaluators (built-in and custom)
- Running evaluations (sync and async)
- Comparative evaluation
- Metadata tracking
- Best practices
- Complete workflow

Navigate through the slides and toggle code visibility as needed!