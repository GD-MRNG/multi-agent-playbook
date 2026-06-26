# Section 1 — Debate

**Paper pattern: Prompt chaining**

From [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): decompose a task into a sequence of steps where each LLM call processes the output of the previous one. The value is that you can use different model identities for different steps and prevent a single context from both producing and evaluating its own work.

---

## What this demonstrates

The natural instinct when building an AI system to do something complex is to write one big prompt. This fails in a consistent way: the same model that generates an argument is the one evaluating it, so it validates its own output rather than scrutinises it. That is not a prompting failure — it is a structural one.

This crew fixes the structure. One agent argues for the motion, the same agent (in a separate task context) argues against it, and a different agent reads both and judges. Three tasks. Two agents. Sequential process. The judge has never seen its own argument — only the two it is asked to weigh.

This is the prompt chaining pattern at its simplest: each task processes the accumulated output of the tasks before it, and different task contexts can impose different cognitive stances on the same underlying model.

**Prompt engineering in practice:** the role/goal/backstory fields in `agents.yaml` are not decoration — they are constrained system prompts that shape model behaviour. "You are a fair judge with a reputation for weighing arguments without factoring in your own views" produces different output than "You are a helpful assistant." Writing precise, identity-grounding backstories is prompt engineering at the agent level.

---

## Key files

- `config/agents.yaml` — two agents: `debater` and `judge`, each with a constraining backstory
- `config/tasks.yaml` — three tasks: `propose`, `oppose`, `decide`; outputs to `output/debate/`
- `crew.py` — sequential process; `@CrewBase` decorators wire YAML to Python

---

## What to observe

**Run it:**
```bash
uv run python main.py debate
```

Watch the verbose output and notice: the debater argues *for* the motion in task 1, then argues *against* the same motion in task 2 — same agent, different task context. The judge in task 3 reads both. It has no memory of generating either argument.

**Experiments to try:**

Change the motion in `main.py` to something trivial (`"Pineapple belongs on pizza"`) and observe how the agents adapt. The structure stays constant; only the content changes.

Add `context: [propose, oppose]` explicitly to the `decide` task in `tasks.yaml` and rerun. The output will be identical — confirming that `Process.sequential` is already passing all prior outputs downstream automatically. Explicit `context` makes the dependency visible in config; sequential mode handles it implicitly.

Swap `judge` to `openai/gpt-4o` and compare the depth of verdict reasoning against `gpt-4o-mini`.

