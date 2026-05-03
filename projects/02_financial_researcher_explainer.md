# Phase 2 — Financial Researcher: Tools, Context, and Temporal Grounding

## Why This Conversation Is Happening

Phase 1 established the structure: an Agent is a persona, a Task is a unit of work, a Crew is the orchestrator. The debate crew proved the structure works. What it did not prove is that the structure is useful for anything beyond reasoning over a fixed prompt — because the debate agents had no access to the outside world. They could only reason from training data, which means any crew that depends on current information would silently produce wrong answers without ever failing in a detectable way.

The financial researcher crew is the first one to confront that gap directly. A researcher agent performs live web searches using the Serper API, then an analyst agent reads the research and writes a structured report. Two new mechanics appear: tools (which extend what an agent can do) and explicit context (which makes task dependencies legible in config). A third problem — one that is easier to miss — also appears: LLMs do not know what day it is. A model trained through late 2024 does not experience the passage of time. Ask it to "research recent news about Apple" without telling it the date and it will anchor the word "recent" to its training era, not yours. This is not a hallucination — the model is not making something up — it is temporal drift, a distinct failure mode that requires a different fix.

Understanding tools, context, and temporal grounding together gives you the foundation for any crew that needs to interact with the real world. Miss one of the three and the output looks plausible but degrades in a way that is difficult to catch in testing.

---

## What You Need To Know First

**What a training cutoff is.** A large language model is trained on a snapshot of text from the internet up to a certain date. After that date, it has no knowledge of events, prices, company news, or anything else that happened. The model does not know it has a cutoff — it will answer questions about "current" events using whatever is closest in its training data, which may be months or years out of date. Any crew that needs current information must route around the training cutoff using tools.

**What an API key is.** An API key is a credential that authenticates your requests to an external service. `SerperDevTool` wraps the Serper API, which performs Google searches programmatically. Without a valid `SERPER_API_KEY` in the environment, the tool call fails and the agent has nothing to work with. Tools that call external services always have this dependency — it is the first thing to check when a tool-equipped agent produces no output.

**What string interpolation is.** When a string contains a placeholder like `{company}` or `{current_date}`, interpolation means replacing that placeholder with a real value at runtime. CrewAI supports this in YAML config: any key in the `inputs` dict passed to `.kickoff(inputs={"company": "Apple", "current_date": "May 3, 2026"})` is substituted throughout all agent and task configs before the crew runs. This is how a single set of YAML files serves any company without modification.

---

## The Key Ideas, Connected

**Tools define what an agent is capable of; tasks define what it is asked to do.** This distinction is load-bearing. In `crew.py`, `SerperDevTool()` is passed to the researcher at construction time — it is a property of the agent, not a property of any task. The researcher is an entity that can search the web. Whether it actually searches, and what it searches for, is determined by the task description at runtime. The analyst, by contrast, has no tools. It cannot search the web; it can only reason over what it is given. This is intentional: the analyst's job is synthesis, not retrieval, and giving it search capability would just create an opportunity for it to go off-script.

**The agent decides when to use its tools, not the framework.** This is the part that surprises engineers coming from deterministic code. You do not call `SerperDevTool` explicitly anywhere in the researcher's task or agent definition. You attach it to the agent, and the agent's underlying LLM reasons about whether a tool call is needed to complete the task. Because the research task says "focus on news and data from the past 12 months," the agent infers it needs current information and issues search queries accordingly. The tool is a capability the agent can reach for, like knowing a language — not an instruction to execute.

**Explicit `context` makes task dependencies visible in config.** Phase 1 used sequential auto-context: every task's output flowed silently to the tasks that followed. That works for simple linear crews, but it is opaque — you cannot look at `tasks.yaml` and immediately see which tasks feed which. In Phase 2, `analysis_task` declares `context: [research_task]` explicitly. This tells CrewAI to pass the researcher's full output as structured input to the analyst, and it tells any reader of the config exactly where the analyst's input comes from. As crews grow in complexity, this legibility matters: implicit dependencies are the first thing to break when you reorder or remove tasks.

**Temporal grounding requires injection at multiple layers, not just one.** The researcher's backstory says: "Today's date is {current_date}. Always search for the most recent information available and prioritize news and data from the past 12 months." Both task descriptions also begin with "Today is {current_date}." This redundancy is deliberate. The backstory grounds the agent's identity — it affects how the model frames search queries. The task description grounds the specific work — it shapes how the model interprets words like "recent" and "current" in the expected output. Injecting the date in only one place leaves the other layers interpreting "recent" relative to training data. The cost of the redundancy is two extra YAML lines; the cost of skipping it is silently stale research.

**Runtime inputs are how anything that changes between runs gets into the crew.** The company name, the current date, and any other variable that differs from one execution to the next should be passed via the `inputs` dict to `.kickoff()`. They should not be hardcoded in YAML. The YAML defines the structure and intent of the crew; inputs fill in the values for a specific run. An engineer who hardens `"Apple"` into a backstory has built a crew that only researches Apple — a config file with a missing variable syntax instead of a reusable system.

---

## Handles and Anchors

Tools are like specialist equipment: a contractor does not carry a concrete mixer in their identity, but when you assign them the task of laying a foundation, they know to bring one. The contractor's capabilities — what equipment they own and know how to use — are fixed properties of who they are. The specific work order tells them where to show up and what to build. This is exactly how `tools=[SerperDevTool()]` works in `crew.py`: the researcher owns the tool, and the task description tells it when to reach for it.

Temporal drift is distinct from hallucination. A hallucinating model makes up facts that do not exist. A temporally drifting model accurately recalls facts from its training data, but those facts are out of date. The financial researcher crew is the first place this distinction matters in practice: a researcher with no date grounding will return real, coherent, confidently-stated financial data — from eighteen months ago. The output passes a surface plausibility check while being materially wrong for any decision that depends on current information.

Explicit context in `tasks.yaml` is a dependency declaration, not a convenience. It is closer to an import statement in code than to a comment. When you read `context: [research_task]` on the analyst's task, you are reading a structural contract: this task requires that output. When you remove it, the analyst loses its input. When you add a new task and forget to wire it into the context chain, you will discover the omission when the output goes vague — not when the crew throws an error.

---

## What This Changes When You Build

An engineer who understands that tools belong to agents will never attach a tool to a task by wrapping it in the task description ("use the search API to..."). They will give the agent the tool and trust the agent to reason about when to use it — which means the task description stays focused on *what* is wanted, not *how* to obtain it.

An engineer who understands temporal drift as a distinct failure mode will inject the current date as a runtime input on any crew that uses time-relative language: "recent," "current," "latest," "this quarter." They will do this at the backstory level and at the task description level, not just one or the other, because the two serve different cognitive functions for the model.

An engineer who understands input variables will never hardcode values that differ between runs into YAML config. They will identify those values at design time, use `{placeholder}` syntax in config, and pass them via `inputs` at runtime. The practical result is that the same crew definition can serve any company, any date, any query — without a single line of Python changing.

An engineer who understands the difference between implicit sequential context and explicit `context` fields will default to making dependencies explicit in any crew with more than two tasks. The extra YAML lines are cheap; the debugging session when you reorder tasks and something breaks is not.

An engineer who has seen a tool-equipped agent perform live retrieval will calibrate their expectations for what tools can and cannot fix. Tools solve the training cutoff problem — they give agents access to information that does not exist in model weights. They do not solve the reasoning quality problem. An analyst that reasons poorly over good research still produces a poor report. Tools are a data-access mechanism, not an intelligence upgrade.
