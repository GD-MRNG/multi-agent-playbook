# Project 1 — Debate

## What This Project Does

Two debater agents argue for and against a motion, then a judge agent reads both arguments and decides the winner. All three outputs are written to disk. The motion is hardcoded in `main.py` and can be changed before each run.

## New Concepts Introduced

**`Agent`, `Task`, `Crew` — the three core primitives**
An `Agent` is a role with a goal and a backstory. A `Task` is a unit of work assigned to an agent. A `Crew` binds agents and tasks together and runs them. Nothing happens until you call `.kickoff()`.

**`Process.sequential`**
Tasks run in the order they are defined. Each task's output is automatically available as context to the tasks that follow. In this crew: propose → oppose → decide, so the judge always sees both arguments.

**`@CrewBase`, `@agent`, `@task`, `@crew` decorators**
The class-based scaffold that wires YAML config to Python objects. `@agent` methods return `Agent` instances; `@task` methods return `Task` instances; `@crew` assembles them. The decorators also auto-populate `self.agents` and `self.tasks` so you don't have to list them manually.

**YAML config (`agents.yaml`, `tasks.yaml`)**
Agent roles, goals, and backstories live in `agents.yaml`. Task descriptions and expected outputs live in `tasks.yaml`. Keeping these in config rather than code makes it easy to change agent behaviour without touching Python.

**`output_file`**
Setting `output_file` on a task writes the agent's response to disk automatically. No file-handling code needed. In this crew each agent writes to `output/propose.md`, `output/oppose.md`, and `output/decide.md`.

**LLM selection**
All agents use `openai/gpt-4o-mini` — cheap and fast, sufficient for both argument generation and evaluation at this scale. LLM is a one-line change per agent in `agents.yaml`.

## Key Principles

**Separation of config and code.** The YAML files define *what* the agents are and *what* they should do. The Python defines *how* they are wired together. This makes it easy to experiment with different prompts, models, or task descriptions without touching the orchestration logic.

**Sequential process as a pipeline.** Each task produces output that flows into the next. The crew is essentially a pipeline where agents hand off to one another in a defined order. This is the simplest mental model for multi-agent systems and the right starting point before introducing parallelism or hierarchy.

**Role clarity drives output quality.** The debater's backstory explicitly frames it as an experienced debater. The judge's backstory emphasises impartiality. Giving agents a clear identity and purpose — not just a task description — produces more coherent and on-character responses.

## Sample Output

**Motion:** *AI will do more harm than good*

**Propose (excerpt):**
> The rise of AI is leading to significant job displacement across various industries. As machines and algorithms become increasingly capable of performing tasks once done by humans, millions face unemployment, economic instability, and reduced job opportunities... AI's potential to generate misinformation and manipulate public perception poses a threat to societal cohesion. Deepfakes, automated disinformation campaigns, and algorithm-driven echo chambers can destabilize democratic processes.

**Oppose (excerpt):**
> AI has the potential to drive unprecedented advancements in numerous fields, including healthcare, education, and climate change... while job displacement is a genuine concern, AI can create new opportunities and enhance productivity across sectors. A historical look at technological advances shows that while certain jobs may become obsolete, new ones emerge.

**Decide (verdict):**
> The concerns raised by the proponents of the motion often reflect immediate and real-world issues that have already begun to manifest, suggesting that the harms of AI are not just theoretical but present and escalating... I conclude that the motion "AI will do more harm than good" is the more convincing position.

## What to Try

- Change the motion in `main.py` to something more lighthearted (e.g. `"Pineapple belongs on pizza"`) and observe how the agents adapt their argumentation style
- Swap the judge to `openai/gpt-4o` and compare the verdict reasoning
- Add a `context` field to the `decide` task in `tasks.yaml` explicitly listing `[propose, oppose]` — observe that the behaviour is identical, which confirms sequential auto-context is working
- Add a fourth task: a `summariser` agent that writes a one-paragraph summary of the debate for a general audience
