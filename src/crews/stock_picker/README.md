# Phase 3 — Stock Picker

**Paper pattern: Orchestrator-subagents**

From [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): an orchestrator directs agents to use tools or undertake tasks with the intention of completing a broader goal. Subagents implement those instructions and report back. The orchestrator sees the full picture; subagents do focused work.

---

## What this demonstrates

Sequential process (Phases 1 and 2) requires the developer to know the optimal task order at design time. For a fixed pipeline, that is fine. For a workflow where the manager might reasonably decide to research companies before ranking them, or re-query the news if the first results are thin, a hardcoded sequence becomes a constraint rather than a feature. Hierarchical process delegates that coordination decision to a manager agent at runtime.

Three new mechanics appear together here: a custom tool that pushes results to an external system (Discord), structured Pydantic output that turns task outputs from prose into typed contracts, and a manager agent that decides how to assign and sequence work across three worker agents.

**The manager is not in the worker pool.** It is constructed inline in `crew()` and passed to `Crew(manager_agent=manager)` — not decorated with `@agent`. The `@agent` decorator registers a method in `self.agents`, the worker pool. A manager added there becomes eligible for task delegation, which would collapse the distinction between coordinator and worker. Keeping the manager separate is what makes the orchestrator-subagent pattern structurally sound.

**Structured output is a contract at the task boundary.** `output_pydantic=TrendingCompanyList` on `find_trending_companies` means the downstream researcher receives a validated Python object it can iterate over — not prose it must parse. The failure mode without this is subtle: the researcher still receives *something*, but if it is freeform text, it must infer how many companies were found and what their tickers are. Pydantic validation moves that failure to the task boundary where it is visible, not silently into the middle of downstream reasoning.

---

## Key files

- `config/agents.yaml` — three worker agents (`news_analyst`, `financial_researcher`, `stock_picker`) on `gpt-4o-mini`; manager uses `gpt-4o`
- `config/tasks.yaml` — three tasks with `output_pydantic` on the first two
- `crew.py` — manager constructed inline; Pydantic models defined; `Memory` configured with namespaced `storage` path
- `tools/discord_tool.py` — custom `BaseTool`: Pydantic input schema + `_run()` posting to webhook

---

## What to observe

**Run it:**
```bash
uv run python main.py stock_picker
```

Watch the verbose output: the manager agent is deciding how to delegate, not executing. Worker agents report back; the manager routes. This is different from sequential process, where the execution order is fixed in Python.

**Experiments to try:**

Remove `output_pydantic` from `find_trending_companies` in `tasks.yaml` and observe how the financial researcher handles freeform prose input compared to a typed list. The difference in output quality shows why structured contracts between tasks matter.

Set `DISCORD_WEBHOOK_URL` to a test webhook and confirm the notification arrives with the correct company name and rationale — this verifies the custom tool is being called, not the result being hallucinated.

Run the crew twice in the same session with memory enabled. On the second run, observe whether the manager avoids re-selecting the same company — this is long-term memory working across executions.

Switch `Process.hierarchical` to `Process.sequential` and observe: does the fixed order still produce a coherent result? If yes, that confirms hierarchical was not strictly necessary for this crew — the manager's value shows only when the order actually needs to vary at runtime.

---

## Deeper reading

`projects/03_stock_picker.md` — phase description with sample output  
`projects/03_stock_picker_explainer.md` — detailed walkthrough of `BaseTool` as an API module, `output_pydantic` as a stage boundary assertion, hierarchical vs. sequential trade-offs, and memory namespacing
