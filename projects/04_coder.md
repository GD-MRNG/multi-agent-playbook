# Project 4 — Coder

## What This Project Does

A single Python Developer agent receives a coding assignment, writes clean executable code, runs it in a Docker sandbox, and captures the output. The work is split across two sequential tasks: `write_code_task` produces a runnable `.py` file; `execute_code_task` uses the code from context, executes it, and writes the result to a separate output file. The assignment is hardcoded in `main.py` and can be changed before each run. Docker Desktop must be running.

## New Concepts Introduced

**`allow_code_execution=True` — agents that write and run code**
Setting `allow_code_execution=True` on an `Agent` gives it access to a code interpreter tool. When the agent decides to execute code, it calls this tool with a Python snippet and receives back the stdout. The agent can loop — write code, run it, observe the output, fix bugs, run again — until it is satisfied. This turns the agent from a text generator into something closer to a developer at a terminal.

**`code_execution_mode="safe"` — Docker sandboxing**
The default execution mode runs code in the same process as the agent. `"safe"` mode spins up a Docker container instead, so executed code cannot access the host filesystem, environment variables, or network beyond what Docker allows. This is the right default for any code you did not write yourself. Docker Desktop must be running before calling `.kickoff()`.

**`max_execution_time` and `max_retry_limit` — guardrails on execution loops**
Because an agent with code execution can loop indefinitely — writing, failing, fixing, retrying — you need hard limits. `max_execution_time=30` caps each individual code execution at 30 seconds. `max_retry_limit=3` caps the number of times the agent can retry after a failure. Without these, a misbehaving agent can spin forever and burn tokens.

**Separating code generation from execution across two tasks**
A single task that writes *and* runs code mixes two concerns and produces a mixed output file (prose + code + stdout in one blob). Splitting into `write_code_task` and `execute_code_task` gives you two clean artifacts: a runnable `.py` file and a plain output file. The execute task receives the code via `context: [write_code_task]` — the same context mechanism introduced in Phase 2 — so no additional wiring is needed.

## Key Principles

**Code execution is a tool, not a mode.** The agent doesn't switch into a "coding mode" — it has a tool it can call when it decides execution is useful. From the agent's perspective, running code is the same as calling any other tool: it sends input and receives output. The rest of the reasoning loop is unchanged.

**Sandboxing is cheap insurance.** The overhead of spinning up a Docker container is small relative to the LLM call that precedes it. `code_execution_mode="safe"` should be the default unless you have a specific reason to trust the code being run.

**Separate writing from executing.** An agent that writes and runs code in one task will narrate its reasoning, code, and output into a single blob. Splitting the tasks gives you clean, usable output files as a side effect of the same work.

**Set limits before you need them.** `max_execution_time` and `max_retry_limit` are easy to set and hard to regret skipping. An infinite retry loop costs real money. Set conservative limits first and loosen them only if the task genuinely needs more headroom.

## Sample Output

**Assignment:** Calculate the first 10,000 terms of 1 - 1/3 + 1/5 - 1/7 + ... multiplied by 4  
**Python version:** 3.12

`output/coder/solution.py`:
```python
total = 0.0
sign = 1
for i in range(10000):
    denominator = 2 * i + 1
    total += sign * (1 / denominator)
    sign *= -1
result = 4 * total
print(result)
```

`output/coder/output.txt` (excerpt):
```
3.1414926535900345
```

## What to Try

- Change `"assignment"` in `main.py` to something the LLM cannot fake — e.g. `"Print the SHA-256 hash of the string 'crewai-phase4'"` — to confirm code is actually executing rather than being hallucinated
- Introduce a deliberate bug in the assignment description and observe the agent's retry loop in the verbose logs
- Lower `max_retry_limit` to `1` and give the agent an ambiguous task to see how it fails gracefully
- Add a third task — `explain_code_task` — where a non-executing agent reads the solution via context and writes a plain-English explanation of how it works
