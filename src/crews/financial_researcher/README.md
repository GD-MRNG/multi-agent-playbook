# Phase 2 — Financial Researcher

**Paper pattern: Augmented LLM**

From [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): the foundational building block of agentic systems is an LLM augmented with retrieval, tools, and memory. Tools extend what an agent can do beyond its training data; the agent decides when to use them based on the task at hand.

---

## What this demonstrates

Phase 1 showed that separating concerns across agents improves reasoning quality. Phase 2 shows the next gap: agents with no access to the outside world silently produce wrong answers whenever the question depends on current information. A model trained through late 2024 does not know today's date — ask it to research "recent news about Apple" without telling it the date and it will anchor "recent" to its training era, not yours. The output looks plausible; the data is stale.

Three additions fix this: a tool that gives the researcher live web access, an explicit `context` declaration that makes the data dependency readable in config, and `current_date` injected as a runtime input at every layer where the model interprets time-relative language.

**Tools belong to agents, not tasks.** `SerperDevTool()` is attached to the researcher at construction in `crew.py` — it is a property of the agent, not a directive in the task. The task says what to accomplish; the agent decides whether and how to use its tools to get there. The analyst has no tools: its job is synthesis, not retrieval, and giving it search capability would let it go off-script.

---

## Key files

- `config/agents.yaml` — researcher (with `SerperDevTool`) and analyst (no tools); both backstories inject `{current_date}`
- `config/tasks.yaml` — `analysis_task` declares `context: [research_task]` explicitly
- `crew.py` — tools attached at agent construction; `current_date` passed in via `inputs`

---

## What to observe

**Run it:**
```bash
uv run python main.py financial_researcher
```

Watch the researcher make multiple tool calls in the verbose output — it is querying the Serper API in real time, not recalling training data. The analyst receives the researcher's output via context and writes a structured report without making any tool calls of its own.

**Experiments to try:**

Remove `{current_date}` from the researcher's backstory in `agents.yaml` (leave it in the task description) and rerun. Observe whether the search queries become less anchored to the present. Then remove it from the task description too. This demonstrates why temporal grounding requires injection at multiple layers — backstory shapes how the agent frames queries; task description shapes how it interprets "recent" in the expected output.

Add a `context` field to `research_task` in `tasks.yaml` that references a non-existent prior task. Observe the error — this confirms that `context` is a structural dependency, not a comment.

Change the company in `main.py` to `"Nvidia"` or `"Tesla"`. No YAML changes needed — `{company}` is interpolated at runtime.

---

## Deeper reading

`projects/02_financial_researcher.md` — phase description with sample output  
`projects/02_financial_researcher_explainer.md` — detailed walkthrough of tools vs. task instructions, temporal drift as a distinct failure mode from hallucination, and why explicit `context` beats implicit sequential dependencies as crews grow
