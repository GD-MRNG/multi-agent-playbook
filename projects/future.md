# Future Work

This file captures ideas for extending the repository beyond the five core phases. They are roughly ordered from simpler additions to more architecturally ambitious ones.

---

## 1. Expand the Engineering Team

The most straightforward extension. The Phase 5 crew uses four agents; a real engineering team has more specialised roles. Candidates:

- **Business Analyst** — clarifies requirements, identifies edge cases, and produces a refined spec before the engineering lead sees it
- **UI/UX Designer** — reviews the frontend and suggests improvements to layout and user flow
- **Database Architect** — designs a schema or storage layer when requirements call for persistence
- **Additional Engineers** — split backend into specialist roles (e.g. API layer vs. business logic)
- **QA / Test Engineer with a test plan** — rather than just writing unit tests, this agent writes a test plan first, then executes it and reports pass/fail

The concept this demonstrates is that the quality and coverage of a crew's output scales with the specificity of its roles. More agents isn't always better, but more *focused* agents usually is.

---

## 2. Dynamic Task Creation with Callbacks

The five core phases all use a fixed set of tasks defined ahead of time. The next architectural leap is a crew that decides at runtime how many tasks it needs.

The idea: an Engineering Lead outputs a structured plan (see section 3 below). A callback attached to that task reads the plan and programmatically generates one coding task per module. Those tasks are added to the crew dynamically before execution continues.

```python
Task(
    ...,
    callback=create_coding_tasks   # runs when this task completes
)
```

This transforms the workflow from a scripted pipeline into an adaptive one. The crew designs the system and then builds it — without the number of modules being hardcoded anywhere.

Key concept: callbacks are defined at the task level, not the agent level.

---

## 3. Structured Outputs to Drive Dynamic Architectures

Dynamic task creation requires a reliable contract between the planning stage and the execution stage. Structured outputs (Pydantic models) are how you establish that contract.

Example: the Engineering Lead produces:

```json
{
  "modules": [
    { "name": "database.py", "responsibility": "SQLite persistence layer" },
    { "name": "auth.py", "responsibility": "User authentication and sessions" },
    { "name": "api.py", "responsibility": "REST endpoints" }
  ]
}
```

A callback reads this, creates one `Task` per module, assigns each to a backend engineer agent, and adds them to the crew. The rest of the workflow — testing, frontend, integration — proceeds once all modules are complete.

This pattern is the foundation for genuinely autonomous software generation.

---

## 4. Guardrails

CrewAI supports guardrails at the task level — validation and transformation logic that runs on a task's output before it's passed downstream. This is useful for:

- Enforcing that structured outputs conform to a schema
- Catching hallucinated or malformed content early
- Normalising outputs before they're used as context

Unlike guardrail implementations in some other frameworks, CrewAI allows them at any task, making them particularly valuable in complex pipelines where one bad output can cascade.

---

## 5. Async / Parallel Execution

Once a crew has many independent tasks (e.g. building five modules simultaneously), running them sequentially wastes time. CrewAI supports asynchronous task execution, where tasks without dependencies on each other run in parallel.

This becomes meaningful when combined with dynamic task creation — a crew that generates ten module tasks can build all ten concurrently rather than serially.

---

## 6. Multi-Crew Orchestration with Flows

CrewAI Flows allow multiple crews to be composed into a higher-level pipeline — one crew's output becomes another crew's input, with branching and conditional logic between them.

Example: a Research Crew produces a market analysis, which triggers a Strategy Crew, whose output triggers an Engineering Crew to build something based on the strategy. Each crew is independently defined and tested; the flow wires them together.

This is a natural next step once the five individual crews are solid.

---

## 7. A Top-Level Gradio Launcher (Revisited)

Scrapped from the initial design in favour of simplicity, but worth returning to once the repo is stable. A single `app.py` at the root that lets a user select a crew, provide inputs, and watch streamed agent output in a browser tab. CrewAI supports callbacks that can pipe agent logs to a Gradio interface in real time.

The prerequisite — Docker, API keys, UV — still needs to be set up once. But after that, the interface removes the need to touch a terminal.

---

## 8. Apply to a Real-World System

The most valuable exercise: take a system from your own work or domain and build it with this framework. The five phases are pedagogical; this is where the learning becomes practical.

Good candidates for a first real-world build: a content pipeline, a data processing system, a customer-facing report generator, or any workflow that currently involves multiple people handing off work to each other. If humans do it in sequence with defined roles, a crew can probably model it.
