---
name: writing-style
description: >
  Apply Glenn's personal technical writing style when producing any documentation,
  README files, concept explanations, learning notes, or written content about
  technical topics. Use this skill whenever the user asks to write, draft, or
  rewrite technical content — including project READMEs, concept explainers,
  learning notes, phase descriptions, specification documents, or any prose
  that explains how something works or why it matters. Also use this when the
  user says "write this in my style", "document this", or asks to produce content
  for a technical audience. If technical writing is involved in any way, invoke
  this skill.
---

# Technical Writing Style Guide

This skill captures a specific, opinionated writing style for technical content.
The goal is documentation and explanations that respect the reader's intelligence,
give them genuine understanding rather than surface familiarity, and never waste
a sentence.

---

## The Core Philosophy

Every piece of technical writing has one job: move the reader from not understanding
something to understanding it, in the fewest possible words. The enemy is not
complexity — it is vagueness, generality, and structure that substitutes for thought.

Two principles govern everything else:

**Problem before concept.** The reader needs a reason to care before they can absorb
information. Establish the concrete failure mode, the gap, or the friction that makes
this topic worth understanding. What breaks without this knowledge? What decisions go
wrong? Name that first.

**Chain, don't list.** Ideas should earn each other. Each concept should feel like it
naturally leads to the next, with explicit connective tissue between them. A reader
who finishes a section should feel like they followed an argument, not scanned a
reference page.

---

## Voice and Tone

**Authoritative and direct.** State things. Do not hedge unless the hedge is meaningful.
"DNS TTLs affect how quickly changes propagate" — not "DNS TTLs can potentially affect
propagation speed in some cases." Confidence comes from precision, not certainty about
everything.

**Respect the reader.** Assume intelligence. Do not explain what is already implied.
Do not add a sentence just to soften a landing. If a concept is hard, say it is hard
and then explain it.

**No throat-clearing.** Never open with "In this post, we will explore..." or
"It's important to understand that..." or "This section covers...". Get straight to
the substance. The first sentence should be doing real work.

**No empty emphasis.** Avoid phrases that assert importance without conveying it:
"this is crucial", "it's worth noting", "engineers should be aware of". Instead,
show why it matters by completing the thought: "An engineer who understands X will
approach Y differently because Z."

---

## Sentence and Paragraph Construction

**One idea per paragraph, fully developed.** The opening sentence states the
paragraph's claim. The rest develops, qualifies, or illustrates it. When you move
to a new idea, start a new paragraph.

**Dense, not long.** Sentences carry a lot of information. Use semicolons, colons,
and parentheticals to pack precision into a sentence without making it ramble.
A parenthetical aside is for adding a precise clarification mid-sentence without
breaking the flow: "TTLs (how long DNS records are cached)" is better than a
separate sentence explaining TTLs.

**Periodic sentences for emphasis.** Build to a point. Front-load context and
qualification, land the conclusion at the end of the sentence where the emphasis falls.

**Concrete numbers over vague adjectives.** "hundreds or thousands of unit tests"
not "many unit tests." "under ten minutes" not "fast." "99.5% of requests" not
"almost all requests."

---

## What to Avoid

**Bullet points for conceptual content.** When explaining how something works,
why it matters, or what the tradeoffs are — use prose. Even when introducing
multiple items (three types of memory, five network concepts), embed them in
connected paragraphs. Bullet points are for reference material, not explanation.

**Passive voice.** "The load balancer distributes traffic" not "traffic is distributed
by the load balancer." Active voice keeps the reader oriented to what is acting and
what is being acted upon.

**Hedging language for things that are true.** Reserve "may", "might", and "can"
for genuine uncertainty. When something is reliably true, state it as true.

**Generality as conclusion.** Never end a section with a vague statement of
importance. End with the most specific, concrete implication of what was just explained.

---

## Key Writing Patterns

### Defining a concept
State it in one complete, precise sentence. Follow immediately with what it means
in practice, then what breaks without it.

Good: "Observability is the property of a system that allows you to understand
its internal state by examining its external outputs."

Avoid: "Observability is basically about being able to see what's happening inside
your system."

### Contrast as explanation
Use what something IS NOT to sharpen what it IS. This is especially effective for
concepts that are frequently confused or conflated.

Good: "Monitoring tells you that something is wrong. Observability tells you why."

### Tracing consequences
Explain a concept by following its failure mode to a concrete outcome. Don't just
say what a thing does — say what happens when it's absent or wrong.

Good: "The service may be perfectly healthy but unreachable because a firewall rule
is blocking the port."

### Chaining ideas
Make the connection between consecutive ideas explicit. Phrases like "This means...",
"Which introduces a problem:", "The consequence of this is...", and "That is why..."
are not transitions — they are load-bearing connective tissue.

---

## Structure for Longer Pieces

For concept explanations and learning documentation, use the following section
structure. Section names should be used as written.

**Why This Conversation Is Happening**
Two to three paragraphs. The engineering problem or real-world condition that created
the need for this concept. What breaks, slows down, or goes wrong without it.
Give the reader a problem to hold before asking them to understand anything.

**What You Need To Know First**
Two to four prerequisite concepts. For each: a plain-language explanation that is
deliberately limited — just enough to remove the blocker, not a full treatment.
Test: could a reader who has only heard the term follow the article without getting stuck?

**The Key Ideas, Connected**
Walk through the central ideas in the order they build on each other. For each:
state it in one plain sentence, explain what it actually means, then show how it
leads to the next idea. A chain, not a list.

**Handles and Anchors**
Two or three concrete ways to hold the material in memory: an analogy, a comparison
to a known concept, or a sentence that captures the core tension. Each handle should
let the reader explain the concept clearly to a colleague in five minutes without
referring back to the source.

**What This Changes When You Build**
Three to five specific implications for working engineers. Complete the sentence:
"An engineer who understands this will approach X differently because Z." No
generalities.

---

## Examples of the Style in Practice

**Too vague:**
"Memory is an important feature in CrewAI that helps agents remember things across
tasks and sessions. There are different types of memory you can use."

**In style:**
"Memory in CrewAI solves a specific problem: by default, each task a crew runs
starts from scratch. The agent completing the third task has no awareness of what
the first task produced, unless that information is explicitly passed via context.
Memory extends this in two directions — within a single run (short-term memory,
stored and retrieved via RAG) and across multiple runs (long-term memory, persisted
to SQLite). The distinction matters because the use cases are different: short-term
memory helps an agent mid-run recall something from earlier in the same session,
while long-term memory lets a crew avoid repeating itself across separate executions
— picking the same stock twice, for instance, because it has forgotten the previous
decision."

---

**Too generic:**
"Testing is important for ensuring code quality and catching bugs early."

**In style:**
"Testing is frequently discussed as a quality practice, but its primary operational
function is something different: it is the mechanism that gives a team the confidence
to deploy continuously. Without a reliable test suite, every deployment is a gamble.
With one, deployment becomes a mechanical process with a known risk profile."
