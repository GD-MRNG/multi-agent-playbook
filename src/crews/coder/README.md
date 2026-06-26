# Section 5 — Coder

**Paper pattern: Evaluator-optimizer**

From [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents): one LLM call generates a response while another provides evaluation and feedback in a loop until a quality criterion is met. The generator and evaluator are separate cognitive stances — the same model that wrote the code also runs it and reads the error, acting as its own evaluator.

---

## What this demonstrates

An LLM without a feedback mechanism can only assert that its code is correct — it cannot verify it. Giving the agent a code execution tool closes a real feedback loop: write code, run it, read stdout (or the error), revise, run again. The agent is not switching modes; it has a tool it can call when it decides execution is useful, the same way it would call a search API or write to a file.

The evaluator-optimizer pattern here is compressed into a single agent: the same Python Developer writes the code and evaluates the output. What makes it work as a loop rather than a one-shot is the circuit breakers — without them, a misbehaving agent can retry indefinitely and burn tokens on a task it will never complete.

**Docker sandboxing is a security boundary, not a convenience setting.** `code_execution_mode="safe"` spins up an isolated Docker container so executed code cannot access the host filesystem, environment variables, or network. In any deployment context where compliance or data sensitivity matters — which is most production contexts — running LLM-generated code outside a sandbox is not a viable option. Docker isolation is the minimum control appropriate for code you did not write. The default in CrewAI is `"unsafe"`; overriding it is the right default practice.

**Separating code generation from execution keeps output files clean.** A single task that writes and runs code produces a mixed blob: prose reasoning, code, stdout, all interleaved. Splitting into `write_code_task` and `execute_code_task` gives two usable artifacts: a clean `.py` file and a plain output file. The execute task receives the code via `context: [write_code_task]` — no additional wiring needed.

---

## Key files

- `config/agents.yaml` — one agent: `python_developer` with `allow_code_execution: true`, `code_execution_mode: safe`, `max_execution_time: 30`, `max_retry_limit: 3`
- `config/tasks.yaml` — two tasks: `write_code_task` (output to `.py`) and `execute_code_task` (context from write task, output to `.txt`)
- `crew.py` — sequential process; Docker must be running before `.kickoff()`

---

## What to observe

**Run it (Docker Desktop must be running):**
```bash
uv run python main.py coder
```

Watch the verbose output for the execution loop: the agent writes code, calls the execution tool, reads the result, and either accepts it or revises and retries. The number of iterations varies by task complexity.

**Experiments to try:**

Change `"assignment"` in `main.py` to something the LLM cannot fake — e.g., `"Print the SHA-256 hash of the string 'crewai-phase4'"`. If code is actually executing, the hash will be correct. If the agent is hallucinating output rather than running code, the hash will be wrong or absent.

Introduce a deliberate ambiguity in the assignment: `"Calculate pi to 100 decimal places without importing any libraries"`. Watch how many retries the agent uses and how it adapts its approach across iterations.

Lower `max_retry_limit` to `1` and observe how the agent fails — does it give up gracefully or partially complete the task?

