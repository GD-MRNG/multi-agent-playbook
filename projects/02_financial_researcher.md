# Project 2 — Financial Researcher

## What This Project Does

A researcher agent searches the web for current information about a company, then an analyst agent reads that research and writes a polished, structured report. The report is saved to `output/financial_researcher/report.md`. The company name and current date are passed in as inputs from `main.py`.

## New Concepts Introduced

**`SerperDevTool` — giving agents access to the web**
Tools extend what an agent can do beyond its training data. `SerperDevTool` wraps the Serper API to perform live Google searches. You attach tools to an agent at construction time — not at the task level. The agent then decides when to use the tool based on the task description. Only the researcher gets the search tool; the analyst works purely from what the researcher passes it.

**`context` — explicit task dependencies**
In Phase 1, sequential order implicitly made prior output available. `context` makes dependencies explicit: the `analysis_task` declares `context: [research_task]`, which tells CrewAI to pass the researcher's full output to the analyst as structured input. Use `context` when a task genuinely depends on specific prior results and you want that dependency to be readable in config.

**Input variables — injecting runtime values into config**
YAML config files support `{placeholder}` syntax. Any key in the `inputs` dict passed to `.kickoff()` is interpolated throughout agents and tasks at runtime. This is how `{company}` and `{current_date}` reach the agent backstories and task descriptions without hardcoding them. Inputs are the right place for anything that changes between runs.

**Temporal grounding — telling agents what day it is**
LLMs don't know today's date unless told. Without grounding, a model may anchor searches and analysis to its training era rather than the present. The fix is to inject `current_date` as an input at all three layers: the agent backstory (so queries target recent data), and both task descriptions (so "recent" and "current" are interpreted correctly). One layer alone is often not enough.

## Key Principles

**Tools belong to agents, not tasks.** An agent's tools define its capabilities. The task describes what to accomplish — the agent decides how, including whether and how to use its tools. This separation means you can give the same agent different tasks without changing its tool configuration.

**`context` makes data flow legible.** In a larger crew, implicit sequential context can be hard to reason about. Explicit `context` fields in `tasks.yaml` serve as documentation: you can read the config and immediately see which tasks feed which. Prefer explicit over implicit as crews grow.

**Prompt grounding is part of the architecture.** Knowing when agent outputs will be wrong — not just when the code is wrong — is part of building reliable crews. Date-grounding, explicit output format instructions, and role-specific backstories are prompt-level architecture decisions with real impact on output quality.

## Sample Output

**Company:** Apple  
**Run date:** May 3, 2026

> As of May 2026, Apple Inc. is demonstrating remarkable financial performance, marked by a substantial increase in revenue and a healthy stock price reflecting strong market capitalization. The company's revenue reached **$111.2 billion** in Q2 2026, indicating a **17% year-over-year growth**. However, despite this impressive growth, Apple faces considerable challenges, particularly from increasing competition in artificial intelligence and supply chain complexities due to geopolitical tensions.

Key figures surfaced by the researcher:
- Q2 2026 revenue: $111.2 billion (+17% YoY)
- Stock price: $280.14 (May 1, 2026), market cap ~$2.4 trillion
- Upcoming WWDC 2026 keynote: June 8, 2026
- CEO transition: John Ternus succeeding Tim Cook
- Analyst 2026 price range: $231.53 – $313.83

## What to Try

- Change `"company"` in `main.py` to a different company (e.g. `"Nvidia"` or `"Tesla"`) and rerun — no other changes needed
- Remove `{current_date}` from the researcher's backstory and observe whether the search results shift toward older data
- Add a third agent — a `skeptic` — whose task is to challenge the analyst's conclusions using the same research context
- Move the analyst to `openai/gpt-4o` and compare the depth and structure of the report against `gpt-4o-mini`
