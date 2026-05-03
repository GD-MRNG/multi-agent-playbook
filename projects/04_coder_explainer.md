# Phase 4 — Coder: Code Execution, Sandboxing, and Execution Loops

## Why This Conversation Is Happening

Every crew in the first three phases has the same fundamental limitation: agents produce text. The financial analyst writes a report. The stock picker writes a decision. The debate judge writes a verdict. None of them can verify their own output by testing it against reality. If the analyst's arithmetic is wrong, the report is wrong. There is no feedback loop.

Code execution changes this qualitatively. An agent that can run code can observe real outputs — not predicted outputs, not outputs extrapolated from training data, but the actual result of the program executing. The Leibniz series converges to π/4; the agent can verify this by computing it to 10,000 terms and checking the answer rather than asserting it from memory. This closes a feedback loop that text generation cannot close: the agent writes code, runs it, sees what actually happens, and can fix mistakes before declaring the task complete.

But code execution introduces a risk that text generation does not. A language model that produces text affects nothing beyond the string it returns. A language model that executes code is an actor — it can read environment variables, write files, make network calls, and consume CPU and memory. The sandbox exists because the appropriate response to giving an agent execution capability is to control what that execution can reach. And the retry limits exist because an agentic loop that can run indefinitely will sometimes do exactly that, at real cost.

This phase is short in terms of new concepts — four agent-level parameters and a task split — but each one addresses a failure mode that becomes live the moment code execution is enabled.

---

## What You Need To Know First

**What a code interpreter is.** A code interpreter is a process that accepts a code snippet as input, executes it, and returns the output (stdout) as a string. When `allow_code_execution=True` is set on a CrewAI agent, the agent gets access to a tool that wraps a code interpreter. From the agent's perspective, calling the tool looks like calling any other tool: it sends a Python snippet and receives back a string. The string is the printed output of the program.

**What Docker is.** Docker is a container runtime. A Docker container is an isolated process environment — it has its own filesystem, its own network stack, and no access to the host system beyond what is explicitly allowed. Running code in a Docker container means the code cannot read your machine's environment variables, write to your home directory, or make outbound network calls unless the container configuration permits it. The container is spun up when the code runs and torn down when it finishes. The startup overhead is seconds, not minutes.

**What stdout is.** `stdout` is the standard output stream — in Python, anything printed with `print()`. When a code interpreter runs a snippet, it captures stdout and returns it as a string. An agent that calls the code execution tool receives whatever the program printed as the tool's result. A program that computes a value but never prints it produces no output the agent can observe.

---

## The Key Ideas, Connected

**`allow_code_execution=True` gives the agent a code interpreter tool, not a different mode.** This is the same pattern as `SerperDevTool` in Phase 2: you attach a capability to the agent at construction time, and the agent's underlying LLM reasons about when to use it. The agent does not switch into a "coding mode" — it generates text as always, and part of that text is reasoning about whether to call the execution tool. The distinction matters because it means the agent can decide *not* to run code if the task is simple enough to answer from reasoning alone. The tool is available; whether to use it is a decision the agent makes.

**The execution loop is what makes code-capable agents qualitatively different from text generators.** An agent without code execution reasons about what the output should be and returns it. An agent with code execution can write a first attempt, run it, observe the actual output, identify the discrepancy if there is one, fix the code, and run it again. This loop — write, execute, observe, revise — is the same process a developer follows at a terminal. The agent's goal field makes this explicit: "First you plan how the code will work, then you write the code, then you run it and check the output." The checking step is only meaningful because the output is real.

**`code_execution_mode="safe"` runs code in a Docker container instead of the host process.** The default execution mode — `"unsafe"` — runs the code in the same Python process as the CrewAI agent, which means executed code has full access to the host filesystem, environment variables, and network. `"safe"` mode spins up a Docker container, runs the code inside it, captures stdout, and returns the result. The container cannot reach the host. For any code you did not write yourself — any code an LLM generated — safe mode is the correct default. The overhead is small; the downside of skipping it is that an LLM-generated snippet with a bug or an unexpected side effect can affect your host system in ways that are difficult to undo.

**`max_execution_time` and `max_retry_limit` are circuit breakers, not preferences.** An agent in an execution loop can fail to converge. A bug that the agent cannot fix within its current reasoning context will produce an infinite loop: run code, observe failure, attempt fix, run code, observe the same failure, attempt another fix. Without limits, this loop runs until you interrupt it or exhaust your token budget. `max_execution_time=30` caps each individual code execution at 30 seconds — a program that hangs or runs too long is terminated. `max_retry_limit=3` caps the number of fix-and-retry cycles after a failure. Set both values before the first run, not after the first infinite loop. The cost of setting conservative limits is occasionally hitting them on a legitimate task; the cost of skipping them is a runaway agent billing tokens until something external interrupts it.

**Splitting write and execute into separate tasks produces two clean artifacts instead of one mixed blob.** A single task instructed to write and run code will narrate its entire process — reasoning, code draft, execution, stdout, interpretation — into one output file. That output is human-readable but not machine-useful: you cannot pipe it to another tool, and importing it into a downstream task requires the next agent to parse prose. Splitting `write_code_task` (which writes only the raw `.py` file) from `execute_code_task` (which runs the code from context and writes only the stdout) gives you two artifacts with single, clear purposes. The `write_code_task` config makes this explicit: "Output only the raw code — no explanation, no markdown fences." The task description is doing the separation work that the task split enforces structurally.

---

## Handles and Anchors

Think of code execution as giving the agent a terminal window. Before, the agent could only describe what a program would do. Now it can run the program, read the output, and decide whether to try again. The terminal is bounded — it lives inside a Docker container, has a timeout, and can only retry a fixed number of times — but within those bounds, the agent's interaction with code is the same loop a developer uses.

Docker sandboxing is cheap insurance with an asymmetric payoff. The cost is a few seconds of container startup per execution. The benefit is that LLM-generated code — which is occasionally wrong in ways that have side effects — cannot reach your host filesystem, read your API keys from environment variables, or make unintended network requests. The argument for skipping the sandbox is almost always convenience; the argument for keeping it is that you cannot predict all the ways generated code might behave, and the container costs almost nothing to run.

`max_retry_limit` is a circuit breaker, not a confidence setting. Setting it to 3 does not mean the agent is limited to three good ideas — it means the loop terminates after three failed attempts even if the agent has not converged. A task that needs more than three retries either has an ambiguous specification, needs a more capable model, or requires human input. The limit forces you to confront that earlier rather than discovering it through an unexpectedly large API bill.

---

## What This Changes When You Build

An engineer who understands that code execution is a tool will design task descriptions that describe *what* to achieve, not *how* to execute it. The agent decides when to run code based on whether execution is the right way to verify or produce the result. Task descriptions that embed execution instructions ("run the code using the interpreter tool") are treating a tool decision as a task specification — which collapses the separation that makes the agent useful.

An engineer who understands the execution loop will test code-capable agents with tasks that cannot be answered correctly from training data alone: a hash function, a precise numerical computation, a file operation with a verifiable result. These tasks confirm that code is actually running rather than being hallucinated. An agent that "executes" code by predicting what the output would be — rather than running it — produces plausible-looking output that fails on any verification test.

An engineer who understands `code_execution_mode` will set `"safe"` as the default and treat `"unsafe"` as a deliberate exception that requires a written reason. The default in CrewAI is unsafe; the safe default in practice is to override it. Any workflow that runs code from an LLM — which is all of them — is running code you did not write, and sandbox isolation is the minimum control appropriate for that situation.

An engineer who understands `max_execution_time` and `max_retry_limit` will set both before the first run and tune them based on observed behaviour. Starting conservative — 30 seconds per execution, 3 retries — and loosening only when a legitimate task hits the ceiling is cheaper than starting permissive and discovering the failure mode through runaway execution.

An engineer who understands the write/execute task split will apply the same principle to any workflow where an agent produces an artifact and then works with it: generate the artifact in one task with a focused expected output, process or use it in a second task via context. The split keeps output files clean, makes the pipeline legible, and prevents the mixed-blob problem from propagating to downstream stages.
