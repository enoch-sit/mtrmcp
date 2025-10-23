# What is LangSmith?

> **Source**: Retrieved from GitHub using MCP (Model Context Protocol)
> **Repository**: [langchain-ai/langsmith-docs](https://github.com/langchain-ai/langsmith-docs)
> **Date**: October 21, 2025

---

## 📋 Overview

**LangSmith** is a platform for building **production-grade LLM applications**. It allows you to closely monitor and evaluate your application, so you can ship quickly and with confidence.

### Key Value Proposition

> "LangSmith enables you to **debug, test, evaluate, and monitor** AI applications built on any LLM framework — or no framework at all."

---

## 🎯 Core Features

LangSmith provides **three main pillars** for LLM application development:

### 1. 🔍 **Observability** (Tracing & Monitoring)

**What it does:**
- Provides LLM-native observability to track every step of your application
- Captures traces of LLM calls, tool usage, and agent behavior
- Helps debug non-deterministic LLM behavior

**Key capabilities:**
- **Tracing**: Track every LLM call, retrieval, tool invocation
- **Dashboards**: View metrics like RPS (requests per second), error rates, costs
- **Alerts**: Get notified when things go wrong
- **Production monitoring**: Track real-world usage patterns

**Why it matters:**
> "LLMs are non-deterministic by nature, meaning they can produce unexpected results. This makes them trickier than normal to debug."

**Use cases:**
- Debugging failing agent runs
- Understanding why an LLM gave a particular response
- Monitoring production traffic patterns
- Cost tracking across different models

---

### 2. ✅ **Evaluations** (Testing & Validation)

**What it does:**
- Helps you build high-quality evaluation datasets
- Runs automated tests on your LLM applications
- Collects human feedback to improve quality

**Key capabilities:**
- **Dataset creation**: Build test sets from production data
- **Automated evaluators**: Off-the-shelf metrics (correctness, hallucination detection, etc.)
- **Custom evaluators**: Write your own evaluation logic
- **Human feedback**: Annotation queues for manual review
- **Comparison**: Track performance improvements over time

**Why it matters:**
> "The quality and development speed of AI applications depends on high-quality evaluation datasets and metrics to test and optimize your applications on."

**Use cases:**
- Testing prompt changes before deployment
- A/B testing different models
- Detecting regressions in agent behavior
- Collecting user feedback on responses

---

### 3. 📝 **Prompt Engineering** (Iteration & Versioning)

**What it does:**
- Provides tools to create, test, and manage prompts
- Enables collaboration on prompt development
- Automatic version control for prompts

**Key capabilities:**
- **Prompt hub**: Centralized storage for prompts
- **Playground**: Interactive environment to test prompts
- **Version control**: Automatic tracking of prompt changes
- **Programmatic access**: Use prompts in code via API
- **Collaboration**: Share and iterate with team members

**Why it matters:**
> "While traditional software applications are built by writing code, AI applications involve writing prompts to instruct the LLM on what to do."

**Use cases:**
- Iterating on system prompts
- Testing different prompt variations
- Managing prompts across environments (dev/staging/prod)
- Collaborating with non-technical team members on prompts

---

## 🔗 Framework Integration

### Framework-Agnostic Design

LangSmith works with **any LLM framework** or no framework at all:

- ✅ **LangChain** (Python/JS)
- ✅ **LangGraph** (agentic workflows)
- ✅ **OpenAI SDK**
- ✅ **Anthropic SDK**
- ✅ **Custom applications**
- ✅ **Any HTTP-based LLM API**

### Seamless LangChain/LangGraph Integration

If you're using LangChain or LangGraph, enable tracing with **a single environment variable**:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
```

That's it! All your LangChain/LangGraph runs will automatically be traced to LangSmith.

---

## 🏗️ Architecture

### How LangSmith Fits Into Your Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   Your LLM Application                   │
│  (LangGraph Agent / LangChain Chain / Custom Code)      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ Traces, Metrics, Logs
                  ▼
┌─────────────────────────────────────────────────────────┐
│                     LangSmith Platform                   │
├─────────────────────────────────────────────────────────┤
│  📊 Observability   │  ✅ Evaluations  │  📝 Prompts    │
├─────────────────────┼──────────────────┼─────────────────┤
│  • Traces           │  • Datasets      │  • Prompt Hub   │
│  • Dashboards       │  • Evaluators    │  • Playground   │
│  • Alerts           │  • Human Review  │  • Versioning   │
│  • Cost Tracking    │  • A/B Testing   │  • Collaboration│
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Development Lifecycle with LangSmith

### 1. **Prototyping Phase**
- Use **Playground** to experiment with prompts
- Add **tracing** to see what your agent is doing
- Test different models and configurations

### 2. **Testing Phase**
- Create **evaluation datasets** from prototype runs
- Run **automated evaluations** on prompt changes
- Compare performance across different approaches

### 3. **Beta Testing**
- Monitor **real user interactions** via traces
- Collect **human feedback** on responses
- Identify edge cases and failure modes

### 4. **Production**
- Track **key metrics** (latency, cost, error rates)
- Set up **alerts** for anomalies
- Continuously evaluate with **production traffic**

---

## 🔥 Real-World Use Cases

### 1. Debugging Agent Failures

**Scenario**: Your LangGraph agent sometimes fails to answer user questions.

**How LangSmith helps:**
- View the full trace showing every agent step
- See which tool calls succeeded/failed
- Understand the LLM's reasoning at each decision point
- Identify patterns in failures

### 2. Optimizing Costs

**Scenario**: Your OpenAI bill is too high.

**How LangSmith helps:**
- Dashboard showing cost per request
- Identify expensive operations (long prompts, many tool calls)
- Compare costs across different models
- Track cost trends over time

### 3. Improving Quality

**Scenario**: Users report your chatbot gives incorrect information.

**How LangSmith helps:**
- Create dataset from problematic conversations
- Run evaluations with correctness metrics
- Test new prompts against the dataset
- Compare results before/after changes

### 4. Team Collaboration

**Scenario**: Product manager wants to improve prompts without touching code.

**How LangSmith helps:**
- PM edits prompts in the UI
- Playground shows immediate results
- Version control tracks changes
- Devs pull latest prompt programmatically

---

## 📊 Example: Tracing a LangGraph Agent

### What You See in LangSmith

When your LangGraph agent runs, LangSmith captures:

```
📍 Run: "When is the next train?"
├─ 🤖 Agent Node (Nova Lite)
│  ├─ Input: HumanMessage("When is the next train?")
│  ├─ LLM Call: amazon.nova-lite-v1:0
│  │  ├─ Tokens: 150 input, 80 output
│  │  ├─ Cost: $0.0002
│  │  └─ Latency: 1.2s
│  └─ Output: ToolCall(get_train_schedule, {line: "TKL", sta: "TKO"})
│
├─ 🔧 Tools Node (MCP Call)
│  ├─ Tool: get_train_schedule
│  ├─ Args: {line: "TKL", sta: "TKO", lang: "EN"}
│  ├─ Result: "Next train in 3 minutes..."
│  └─ Latency: 0.5s
│
└─ 🤖 Agent Node (Final Response)
   ├─ Input: ToolMessage("Next train in 3 minutes...")
   ├─ LLM Call: amazon.nova-lite-v1:0
   ├─ Output: AIMessage("The next train arrives in 3 minutes...")
   └─ Total Time: 2.1s
```

### Insights You Get

- **What happened**: Complete execution trace
- **Why it happened**: LLM reasoning and decisions
- **How long it took**: Per-step latency
- **How much it cost**: Token usage and cost
- **What went wrong**: Error messages and stack traces (if any)

---

## 💡 How LangSmith Relates to Your MTR Demo

### Current State (Without LangSmith)

```python
# Your langgraph_demo_with_history.py
async def create_mcp_agent_with_history():
    # ... build agent ...
    result = await app.ainvoke({"messages": [...]})
    # You only see the final result
```

**What you're missing:**
- ❌ Can't see what the agent was "thinking"
- ❌ Don't know which tool calls were made
- ❌ No cost tracking
- ❌ Hard to debug when things go wrong

### With LangSmith (3 lines of code)

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"

# Same code as before
result = await app.ainvoke({"messages": [...]})

# Now you can see EVERYTHING in the LangSmith UI!
```

**What you get:**
- ✅ Visual trace of every agent step
- ✅ Cost breakdown per LLM call
- ✅ Latency metrics
- ✅ Tool call arguments and results
- ✅ Historical comparison across runs

---

## 🎓 Educational Value

### Why LangSmith is Essential for Learning

If you're teaching students about LLM applications, LangSmith provides:

1. **Transparency**: Students can see what's happening inside the "black box"
2. **Debugging**: Learn to diagnose and fix agent failures
3. **Optimization**: Understand trade-offs (cost, latency, quality)
4. **Best practices**: Industry-standard observability patterns

### Example Teaching Scenario

**Lesson**: "Understanding LangGraph Agent Behavior"

**Without LangSmith:**
```
Teacher: "The agent calls the MCP server to get train data."
Student: "How do I know it actually did that?"
Teacher: "Trust me." 😅
```

**With LangSmith:**
```
Teacher: "Let's look at the trace in LangSmith."
Student: "Oh! I can see the agent decided to call get_train_schedule 
          with line='TKL' and sta='TKO'!"
Teacher: "Exactly! And see how it used that result in the final answer?"
Student: "This makes so much sense now!" 🎓
```

---

## 🆚 LangSmith vs. Other Tools

| Feature | LangSmith | Traditional APM (e.g., Datadog) | Print Debugging |
|---------|-----------|----------------------------------|-----------------|
| **LLM-Native** | ✅ Built for LLMs | ❌ Generic metrics | ❌ No structure |
| **Traces** | ✅ Every LLM call | ⚠️ HTTP requests only | ❌ Manual logging |
| **Cost Tracking** | ✅ Token-level | ❌ Infrastructure only | ❌ No tracking |
| **Evaluations** | ✅ Built-in | ❌ Requires custom setup | ❌ No automation |
| **Prompts** | ✅ Version control | ❌ Not supported | ❌ In code only |
| **Learning Curve** | Low | High | None (but ineffective) |

---

## 📚 Resources

### Official Documentation
- **Website**: https://docs.smith.langchain.com/
- **GitHub Docs**: https://github.com/langchain-ai/langsmith-docs
- **SDK**: https://github.com/langchain-ai/langsmith-sdk
- **Cookbook**: https://github.com/langchain-ai/langsmith-cookbook

### Quick Links
- [Getting Started](https://docs.smith.langchain.com/)
- [Tracing Guide](https://docs.smith.langchain.com/observability)
- [Evaluation Guide](https://docs.smith.langchain.com/evaluation)
- [Prompt Engineering](https://docs.smith.langchain.com/prompt_engineering/quickstarts/quickstart_ui)

---

## 🚀 Next Steps for Your Project

### Option 1: Add LangSmith to Your Demo

```bash
# 1. Sign up at https://smith.langchain.com/
# 2. Get your API key
# 3. Add to .env
echo "LANGCHAIN_TRACING_V2=true" >> .env
echo "LANGCHAIN_API_KEY=lsv2_pt_xxx..." >> .env

# 4. Run your demo (no code changes needed!)
python langgraph_demo_with_history.py

# 5. View traces at https://smith.langchain.com/
```

### Option 2: Create a Teaching Demo

**Goal**: Show students how LangSmith helps debug agents

1. Create intentionally broken agent
2. Run with LangSmith tracing
3. Show students the trace to diagnose issue
4. Fix the agent
5. Compare before/after traces

### Option 3: Build Evaluation Pipeline

**Goal**: Test your MTR agent across multiple scenarios

```python
from langsmith import evaluate

# Create test dataset
dataset = [
    {"input": "Next train at TKO?", "expected": "TKL line"},
    {"input": "Airport Express schedule?", "expected": "AEL line"},
    # ... more test cases
]

# Run evaluation
results = evaluate(
    lambda x: agent.ainvoke(x["input"]),
    data=dataset,
    evaluators=[correctness, latency]
)
```

---

## 🎯 TL;DR

**LangSmith is like DevTools for LLM applications.**

Just as browser DevTools lets you inspect web pages:
- 🔍 See network requests
- 📊 Profile performance
- 🐛 Debug JavaScript

**LangSmith lets you inspect LLM applications:**
- 🔍 See LLM calls and tool invocations
- 📊 Track costs and latency
- 🐛 Debug agent behavior
- ✅ Test with evaluations
- 📝 Manage prompts

**It's essential for:**
- Building production LLM apps
- Teaching students about AI systems
- Debugging complex agent workflows
- Optimizing costs and performance

---

## 💬 Summary

LangSmith is **the observability and evaluation platform** for LLM applications. It provides the tools you need to:

1. **See** what your LLM is doing (tracing)
2. **Test** that it works correctly (evaluations)
3. **Improve** it over time (prompt management)
4. **Monitor** it in production (dashboards)

For your educational chatbot project, LangSmith would make the LangGraph agent behavior **visible and understandable** to students, transforming it from a "black box" into a transparent, debuggable system.

---

*Retrieved via GitHub MCP on October 21, 2025*
*Source: https://github.com/langchain-ai/langsmith-docs*
