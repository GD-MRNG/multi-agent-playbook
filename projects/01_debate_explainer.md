# Phase 1 — Debate: The Three Primitives

## Why This Conversation Is Happening

The natural instinct when building an AI system to do something complex — write an argument and evaluate it, research a topic and summarise it, generate code and test it — is to write one big prompt. Something like: "You are a debate assistant. Given this motion, argue both sides and then pick the winner." This feels reasonable. It produces plausible output. It also fails in a consistent, hard-to-diagnose way: the same model that generates the argument is the one evaluating it, which means it tends to validate its own output rather than scrutinise it. This is not a quirk of bad prompting — it is a structural property of asking one entity to both produce and judge its own work.

Multi-agent orchestration is the engineering response to that structural problem. Instead of one prompt doing everything, you define multiple agents with distinct identities and responsibilities, connect them through a shared process, and let each one do only the thing it was set up to do. The debate crew is the minimal version of this idea: one agent argues for the motion, the same agent (in a different task context) argues against it, and a separate judge agent reads both arguments and decides the winner. Three tasks. Two agents. One crew. Nothing more complex than it needs to be.

The reason this crew is Phase 1 is that every subsequent phase in the playbook — financial research, stock picking, autonomous code execution — builds on the same three building blocks introduced here. An engineer who understands what an `Agent`, a `Task`, and a `Crew` are, and why they are kept separate, can read any crew in this repository and immediately understand its structure.

---

## What You Need To Know First

**What a system prompt actually does.** When you talk to an LLM in a chat interface, you see the conversation. What you do not see is a hidden system prompt that was sent first, before your message, which shapes how the model responds. The system prompt sets the model's identity, constraints, and objectives for the entire conversation. Role-based prompting works by writing a specific, constraining system prompt: "You are a fair judge with a reputation for weighing arguments without factoring in your own views." That sentence changes how the model reasons, not just what it knows.

**What a YAML config file is.** YAML is a plain-text format for structured data — keys and values, with indentation to show hierarchy. It is not code: there are no loops, no conditionals, no functions. It is closer to a settings file than a program. In this repo, `agents.yaml` holds the identity definition for each agent (role, goal, backstory, LLM), and `tasks.yaml` holds the work definition for each task (description, expected output, which agent runs it). Both files are read by Python at runtime.

**What a Python decorator is.** A decorator is syntax that wraps a function with additional behaviour, written as `@something` on the line above the function definition. In CrewAI's class-based scaffold, `@agent` tells the framework "this method returns an Agent and should be registered automatically," `@task` does the same for Tasks, and `@crew` does it for the Crew itself. The practical effect is that you do not need to manually list agents and tasks when constructing the crew — the decorators do the bookkeeping for you.

---

## The Key Ideas, Connected

**The three primitives — Agent, Task, Crew — exist to separate three different concerns.** An `Agent` is a persona with a goal and a backstory; it defines *who* is doing the work. A `Task` is a unit of work with a description and an expected output; it defines *what* is being done. A `Crew` is the orchestrator that binds agents and tasks together and defines the execution process; it defines *how* the work flows. Keeping these separate means you can change one without touching the others — swap the LLM in an agent's config without rewriting the task, or change a task's expected output format without touching the agent's identity.

**Role, goal, and backstory together define an agent's cognitive boundary.** These are not decoration. The `role` tells the model what kind of entity it is. The `goal` specifies what it is optimising for. The `backstory` establishes constraints and character: "You're an experienced debater with a knack for concise but convincing arguments." The backstory is the part that does the most work — it is effectively a constrained system prompt that reduces the surface area of the model's behaviour, pushing it toward a specific style and away from generic, hedging responses. An agent with a thin backstory produces thin output.

**The same agent can play different roles in different tasks.** In this crew, a single `debater` agent handles both the `propose` and `oppose` tasks. This works because tasks are stateless contexts — each task invocation gets its own conversation, shaped by the task description. The `propose` task tells the debater to argue *for* the motion; the `oppose` task tells it to argue *against* the same motion. The debater's identity (concise, convincing) is consistent across both tasks, but the task description overrides the direction of the argument. This distinction — between an agent's persistent identity and a task's specific instruction — is one of the more important things to have clear before the crews get more complex.

**`Process.sequential` turns tasks into a pipeline with automatic context inheritance.** When a crew runs sequentially, tasks execute in the order they are defined. Each task's output is automatically added to the context of every task that follows it. The judge's `decide` task does not have an explicit `context` field in `tasks.yaml`, yet the judge reads both arguments — because by the time `decide` runs, the outputs of `propose` and `oppose` are already in the pipeline. This automatic context flow is what makes sequential mode the right starting point: you do not need to wire tasks together manually, and the information flows in the order you think about the problem.

**`output_file` separates persistence from logic.** Setting `output_file: output/decide.md` on a task tells CrewAI to write that task's output to disk automatically. There is no file-handling code in `crew.py`. The framework handles it. This keeps the Python focused on orchestration, not I/O — a meaningful separation that becomes more important as crews grow.

---

## Handles and Anchors

Think of a crew like a TV production. The writer writes the script; the director does not also write. The judge scores the performance; the actors do not also judge. Asking one person to write, act, and judge simultaneously produces mediocre work in all three dimensions. A crew formalises the separation that any thoughtful production already practices.

Sequential process is a pipeline. The `propose` stage hands its output to `oppose`, which hands both to `decide`. If you squint, it looks exactly like a Unix pipe: `propose | oppose | decide`. Each stage consumes the accumulated output of everything upstream.

The backstory is a system prompt with identity. If you stripped away the CrewAI abstractions and wrote this as raw API calls, the backstory would be the first paragraph of a `role: system` message. What CrewAI adds is a consistent pattern for writing those system messages — one that encourages you to think in terms of *who this entity is* rather than *what commands it should follow*. The identity framing produces more coherent, harder-to-derail agents than instruction framing.

---

## What This Changes When You Build

An engineer who understands the Agent/Task/Crew separation will stop collapsing multi-step reasoning into one prompt, because they can now name what goes wrong when they do: the same cognitive context that generates output is the one being asked to evaluate it, which is structurally biased toward validation.

An engineer who understands `Process.sequential` and automatic context inheritance will not manually concatenate outputs between tasks. They will trust the pipeline and add explicit `context` fields only when they need to control exactly which prior task outputs reach a given task — not as default practice.

An engineer who understands YAML config separation will change agent behaviour by editing `agents.yaml` and task instructions by editing `tasks.yaml`, without touching `crew.py`. The Python file describes structure; the YAML files describe content. A change to what an agent *is* or what a task *asks for* should not require a code review — it should require a config edit.

An engineer who understands role-based backstories will write constraining ones, not vague ones. "You are a helpful assistant" is a non-backstory — it describes nothing specific enough to constrain behaviour. "You are a fair judge with a reputation for weighing arguments without factoring in your own views" is a backstory — it gives the model a specific identity to inhabit and a specific bias to resist.

An engineer who has seen `output_file` work will stop writing file-handling boilerplate inside agent logic. Persistence is a property of the task, not a responsibility of the agent.
