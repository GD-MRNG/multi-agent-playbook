# Phase 3 — Stock Picker: Custom Tools, Structured Output, and Hierarchical Process

## Why This Conversation Is Happening

Phases 1 and 2 established a reliable pattern: define agents in YAML, wire tasks sequentially, inject inputs at runtime. That pattern works well for pipelines with a fixed order and agents that only need to read and reason. The stock picker crew is where three assumptions from those earlier phases start to break down.

First, agents in the debate and financial researcher crews had no way to trigger anything outside the agent system. Research gets written to a file; no one is notified. In production, crews often need to push results to external systems — messaging channels, databases, ticketing systems — and the mechanism for that is a custom tool, not a task instruction.

Second, passing freeform text between tasks becomes fragile at scale. When the financial researcher passes prose to the analyst, the analyst can usually parse it because the format is loose and forgiving. But when a downstream task needs to iterate over a specific list of companies, freeform prose creates a guessing game: did the upstream task return two companies or three? Is the ticker in the first sentence or the second? Structured output enforces the contract at the task boundary rather than hoping the next agent reads it correctly.

Third, sequential process requires the developer to know the optimal task order at design time. For a three-step linear pipeline that never changes, this is fine. For a workflow where the manager might reasonably decide to research companies before ranking them, or re-query the news if the first set of results is thin, a fixed sequence becomes a constraint rather than a feature. Hierarchical process delegates that coordination decision to a manager agent at runtime.

Understanding these three mechanics together — custom tools, `output_pydantic`, and `Process.hierarchical` — gives you the toolkit for crews that interact with the world, pass typed data between stages, and coordinate flexibly rather than rigidly.

---

## What You Need To Know First

**What Pydantic is.** Pydantic is a Python data validation library. You define a class that inherits from `BaseModel` and declare its fields with types. When you instantiate the class with some data, Pydantic validates that the data matches the field types and raises a clear error if it does not. In this crew, Pydantic models define the exact shape of data that flows between tasks — a `TrendingCompanyList` with a list of `TrendingCompany` objects, each with a `name`, `ticker`, and `reason`. The practical effect is that the financial researcher receives a guaranteed-valid, typed list of companies, not a blob of text it must parse.

**What class inheritance is.** When a Python class inherits from another class — `class DiscordNotificationTool(BaseTool)` — it gets all the behaviour of the parent and can add or override specific parts. `BaseTool` provides the CrewAI integration: it handles how the tool is described to the LLM, how the agent decides to call it, and how the result is returned. You only need to implement two things: the input schema (a Pydantic model describing the tool's arguments) and `_run()` (the function that executes when the tool is called). Everything else is inherited.

**What a vector database is.** A vector database stores embeddings — numerical representations of text produced by a language model — and retrieves them by semantic similarity rather than exact keyword match. When CrewAI memory saves a fact, it converts it to an embedding and stores it. When the crew needs to recall something relevant, it converts the query to an embedding and retrieves the stored entries with the closest numerical similarity. This is how memory retrieves "Databricks was picked last run" in response to a query like "which technology companies should we avoid re-selecting" — the semantic match works even when the words are different.

---

## The Key Ideas, Connected

**A custom `BaseTool` wraps any external action in an interface the agent can call autonomously.** The Discord tool is four meaningful lines of code: a Pydantic input schema (`DiscordMessage`), a tool name and description the LLM reads to understand when the tool is appropriate, and a `_run()` method that executes the HTTP POST. The `description` field is the most important one to get right — it is the text the LLM reads when deciding whether to use the tool. "Sends a stock pick decision to a Discord channel via webhook. Provide the chosen company name and a one-sentence rationale." is specific enough that the agent knows exactly when to call it and what to pass. A vague description produces erratic tool usage. The same pattern — schema, description, `_run()` — applies to any external integration you want to give an agent: Slack, a REST API, a database write, a file operation.

**`output_pydantic` turns a task's output from text into a typed contract.** When `find_trending_companies` runs with `output_pydantic=TrendingCompanyList`, CrewAI instructs the LLM to produce output that can be parsed into that model, validates the result, and passes the typed object downstream. The financial researcher receives a Python object it can iterate over, not a string it must interpret. What breaks without this is subtle: the researcher still receives *something* from the upstream task, but it is freeform prose, which means the researcher must infer how many companies were found, what their tickers are, and what the reasons were — all from unstructured text. This works until it does not, and the failure mode is a downstream agent silently working from incomplete or misread input rather than throwing an error. Pydantic validation moves the failure point to the task boundary, where it is visible.

**`Process.hierarchical` replaces a fixed execution sequence with a manager's real-time delegation decisions.** In sequential mode, the developer decides at design time which task runs first, second, third. In hierarchical mode, the manager agent receives the full task list and decides how to assign and sequence them at runtime, based on context. The manager in this crew uses `gpt-4o` while workers use `gpt-4o-mini` — this is deliberate. Coordination requires stronger reasoning than execution. The manager sees the full picture and routes; the workers do focused work. The cost is real: every delegation decision burns manager tokens in addition to worker tokens, which means hierarchical process is more expensive than sequential for equivalent workloads. The right question before choosing hierarchical is whether the execution order is genuinely variable — if the pipeline is always find → research → pick, sequential is correct and cheaper.

**The manager is not in the worker pool, and this distinction matters.** The manager agent in `crew.py` is constructed inline and passed to `Crew(manager_agent=manager)`. It is not decorated with `@agent`. The `@agent` decorator registers a method's return value in `self.agents` — the list of workers. A manager added to `self.agents` would be available for task assignment, which would allow the manager to be delegated tasks instead of delegating them, breaking the coordination model. The inline construction keeps the manager's role unambiguous: it coordinates, it does not execute.

**Memory persists what agents have seen across tasks and across separate crew runs.** The unified `Memory` instance handles three distinct scopes. Short-term memory stores information within a single run, so an agent working late in the pipeline can recall something from an earlier task without it being explicitly passed via `context`. Long-term memory persists to LanceDB across runs, so the crew remembers that Databricks was picked last time and avoids selecting it again. Entity memory tracks named entities — specific companies, people, products — and builds a durable record of what has been observed about each. The `storage` path namespaces the LanceDB directory; without it, two crews running from the same project root would share the same vector store and contaminate each other's memory.

---

## Handles and Anchors

Think of a custom `BaseTool` as an API module you write for your agent. When you build a REST API, you define an endpoint schema (what parameters it accepts), write the handler (what it does when called), and document what it returns. `BaseTool` is the same pattern: the Pydantic `args_schema` is the request schema, `_run()` is the handler, and the `description` is the documentation the agent reads. The agent is the caller; it decides when to invoke the endpoint based on the task at hand.

`output_pydantic` is a type assertion at a stage boundary. In a software pipeline, the safest handoff between stages is one where the data format is validated at the boundary rather than trusted to be correct. Without it, bad output from stage one is bad input to stage two — and stage two might produce plausible-looking results anyway, making the upstream failure invisible. With it, stage one either produces a valid typed object or fails loudly, and stage two receives data it can trust.

The hierarchical process is a staffing agency model. The manager takes the job requirements (the task list), knows the available workers and their capabilities (the agent pool), and assigns work based on what the job needs and who is best suited. The workers do not communicate directly — they report back to the manager, who decides what happens next. Sequential process, by contrast, is an assembly line: each station does its work and passes the result to the next station, regardless of what the previous station produced.

---

## What This Changes When You Build

An engineer who understands `BaseTool` will never embed an external API call in a task description ("and then POST the result to this webhook..."). They will isolate it in a tool with a typed schema and a clear description, attach it to the agent that needs it, and let the agent decide when to invoke it. The task description stays focused on *what* is wanted; the tool handles *how* to reach the outside world.

An engineer who understands `output_pydantic` will define Pydantic models for task outputs before writing the tasks themselves. The model is the interface contract — it specifies what the task is expected to produce and what downstream tasks are entitled to receive. Writing the model first forces precision about the data shape early, when it is cheap to change, rather than after the pipeline is running and a downstream agent is silently working from garbled input.

An engineer who understands hierarchical process will reach for `Process.sequential` by default and switch to `Process.hierarchical` only when they can articulate *why* the execution order needs to be variable at runtime. Sequential is cheaper, simpler to reason about, and easier to debug. Hierarchical is the right tool for genuinely adaptive workflows — not for adding flexibility that the pipeline does not need.

An engineer who understands the manager's placement will never add it to `self.agents` via `@agent`. The manager's role is coordination; adding it to the worker pool makes it eligible for task assignment, which collapses the distinction between the coordinator and the workers it coordinates.

An engineer who understands memory namespacing will set a crew-specific `storage` path from the first run, not after discovering that two crews have corrupted each other's LanceDB store. The path is one argument; the collision is irreversible without clearing the store.
