# crewai-agent-playbook

A hands-on implementation of the agentic AI workflow patterns described in Anthropic's [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents). Each phase uses CrewAI to demonstrate a specific pattern from the paper — prompt chaining, augmented LLM, orchestrator-subagents, evaluator-optimizer, parallelization — through working code you can run and observe.

CrewAI is the vehicle, not the subject. The subject is how multi-agent systems are structured, why those structures behave differently from single-prompt approaches, and what breaks when you get the structure wrong.

## Setup

```bash
# Install dependencies
uv sync --python 3.12

# Copy and fill in your API keys
cp .env.example .env
```

## Running a crew

```bash
uv run python main.py debate
uv run python main.py financial_researcher
uv run python main.py stock_picker
uv run python main.py coder
uv run python main.py engineering_team
uv run python main.py router
```

Inputs are hardcoded per crew in `main.py` — edit them directly before running.

> Phase 4 (`coder`) requires Docker Desktop to be running.

## Phases

| Phase | Crew | Paper Pattern | New concepts |
|---|---|---|---|
| 1 | `debate` | Prompt chaining | `Agent`, `Task`, `Crew`, `Process.sequential`, YAML config, `output_file` |
| 2 | `financial_researcher` | Augmented LLM | `SerperDevTool`, `context` passing between tasks |
| 3 | `stock_picker` | Orchestrator-subagents | Custom `BaseTool`, `output_pydantic`, `Process.hierarchical`, memory |
| 4 | `coder` | Evaluator-optimizer | `allow_code_execution`, Docker sandbox, execution loops |
| 5 | `engineering_team` | Parallelization + orchestrator | Multi-agent specialisation, DAG context, Gradio UI generation |
| 6 | `router` | Routing | Classify-then-dispatch, multi-crew orchestration, typed route decisions |

Each crew folder contains a `README.md` that explains which paper pattern it demonstrates, what to observe when you run it, and where to look in the code.

## Environment variables

```
PYTHONUTF8=1              # prevents emoji encoding errors on Windows
OPENAI_API_KEY=           # all phases
SERPER_API_KEY=           # Phase 2+
DISCORD_WEBHOOK_URL=      # Phase 3+
CREWAI_TRACING_ENABLED=true  # optional — requires crewai login
```

LLM is a one-line change per agent in `agents.yaml`. Swap `openai/gpt-4o-mini` for `anthropic/claude-haiku-4-5` or `google/gemini-2.0-flash` to test multi-provider behaviour with no code changes — just the corresponding API key in `.env`.

## Tracing

CrewAI can capture agent decisions, task timelines, tool usage, LLM calls, tokens, and costs via the [CrewAI AMP](https://app.crewai.com) platform.

```bash
# One-time authentication
crewai login
```

Then set `CREWAI_TRACING_ENABLED=true` in `.env`. Traces appear under the **Traces** tab at [app.crewai.com](https://app.crewai.com).

## Structure

```
src/crews/<name>/
  crew.py                 # @CrewBase class with agents, tasks, crew
  config/agents.yaml      # role, goal, backstory, llm
  config/tasks.yaml       # description, expected_output, agent, output_file
  README.md               # paper pattern, what to observe, experiments

src/crews/router/         # Phase 6 — routing pattern (multi-crew structure)
  router.py               # classify-then-dispatch logic
  classifier/             # sub-crew: classifies the query
  technical/              # sub-crew: handles technical queries
  policy/                 # sub-crew: handles policy/compliance queries

projects/                 # extended learning notes, one per phase
output/                   # generated at runtime, gitignored
```
