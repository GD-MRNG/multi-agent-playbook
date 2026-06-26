# Section 3 — Router

**Paper pattern: Routing**

From [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): routing classifies an input and directs it to a specialized followup task. It allows for separation of concerns and the use of more focused subagents that are better optimised for their particular task.

---

## What this demonstrates

A generalist agent asked to answer both technical and policy questions about government digital services will produce mediocre answers to both. The expertise required to answer "how should we implement JWT refresh tokens?" is different from the expertise required to answer "what data residency obligations apply to citizen health records?" — and the backstory, goal, and task framing for each are different too. Routing solves this by deciding first, then acting with the right specialist.

The workflow is two LLM calls, not one:

1. **Classify** — a lightweight classifier agent reads the query and returns a structured route decision: `technical` or `policy`, with a one-sentence reasoning. This uses `output_pydantic` (from Section 4) to produce a typed `RouteDecision` object rather than freeform text.
2. **Route** — Python code reads `decision.route` and calls the appropriate specialist crew. The routing logic is explicit and readable; there is no hidden branching inside a single prompt.

The key property of this pattern is that the caller does not need to know which specialist ran. The response lands in `output/router/response.md` regardless of the route taken. The routing decision is a separator, not a visible output.

**Structure differs from the other sections.** Previous crews are single `@CrewBase` classes with a `kickoff()` called directly from `main.py`. The router is a `Router` class that orchestrates three sub-crews: classifier, technical, and policy. Each sub-crew is independently defined and independently runnable. The `Router.kickoff()` method holds the routing logic. This is a natural structure for any workflow where the execution path is not known until an initial classification step completes.

---

## Key files

```
src/crews/router/
  router.py              # routing logic — classify, read route, dispatch
  classifier/crew.py     # ClassifierCrew — outputs RouteDecision(route, reasoning)
  technical/crew.py      # TechnicalCrew — answers implementation questions
  policy/crew.py         # PolicyCrew — answers compliance/governance questions
```

Each sub-crew has its own `config/agents.yaml` and `config/tasks.yaml`.

---

## What to observe

**Run it:**
```bash
uv run python main.py router
```

The default query in `main.py` is technical. Watch the classifier run first and print its routing decision, then watch the technical analyst respond. The verbose output from the classifier will show the `RouteDecision` JSON being produced.

**Switch to the policy route:** uncomment the policy query in `main.py`:
```python
"query": "What data residency obligations apply when storing citizen health records in a commercial cloud provider?"
```

Rerun. The classifier routes differently; the policy analyst handles it instead. The same `output/router/response.md` path is written — the caller's interface is identical regardless of which specialist ran.

**Experiments to try:**

Submit an ambiguous query — e.g., `"Should we use a government-approved cloud for sensitive data?"` — and observe how the classifier resolves the ambiguity. The `reasoning` field in the route decision shows the classifier's logic.

Submit a query that spans both domains — e.g., `"What are the technical and regulatory requirements for storing citizen biometric data?"` — and observe which route is chosen. This is a known limitation of binary routing; the classifier must commit to one path. A more sophisticated implementation would use a multi-label classifier or route to both specialists and synthesise the results.

Try replacing the two specialist agents with the same `gpt-4o-mini` model and identical backstories. Does the routing still produce meaningfully different responses? This tests whether the specialist backstories are doing real work or just cosmetic differentiation.

---

## The routing pattern's trade-offs

Routing improves quality for queries that fall cleanly into one category. It degrades gracefully when categories overlap — the worst outcome is a slightly wrong specialist, not a broken pipeline. The cost is one extra LLM call for the classifier: acceptable when the specialists are meaningfully different, wasteful when a single generalist would do equally well.

The explicit Python routing decision (rather than asking one LLM to classify and respond in a single prompt) makes the decision visible, testable, and replaceable. You can log every routing decision, inspect the `reasoning` field, and tune the classifier independently of the specialists.
