# Orchestrator — dispatch templates and synthesis schema

> Reference doc for `orchestrator`. Read at runtime when the agent is about to
> dispatch sub-agents (Step 5) or compose the final response (Step 6 + Output
> format). Decision logic stays in the supervisor body; the templates and the
> response skeleton live here.

## Goal

Give the orchestrator a stable, copy-paste shape for (a) the prompts it sends
to specialist sub-agents and (b) the unified response it produces at the end.
Without these templates, sub-agents drift in scope and the final response
degrades into a dump of raw agent outputs.

## Inputs

| Source | What to read | Required? |
|---|---|---|
| The decomposition produced in Step 2 | Goal / Needs / Best agent / Surface per subtask | yes |
| The phase plan produced in Step 3 | Phase number, mode (parallel/sequential), subtasks | yes |
| The outputs of completed phases | File paths, summaries, decisions made | yes (for Step 6) |

## Sub-agent dispatch prompt — template

Every Agent invocation prompt the orchestrator sends must follow this shape:

```
You are `<sub-agent-name>`.

Context:
  <one paragraph: what the user asked, what has already been produced
   by prior phases (paste paths or short summaries), what surface this
   subtask owns>

Inputs to read:
  - <absolute or repo-relative path>
  - <prior-phase artefact path, if any>

Task:
  <single concrete deliverable — one sentence>

Output:
  - <expected file path(s) or response shape>

Constraints:
  - In scope: <surfaces this sub-agent owns>
  - Out of scope: <surfaces another sub-agent owns or that the user excluded>
  - <hard rules: stack-agnostic, no Flyway, strict AS-IS, etc.>
```

Rules:

- **Self-contained.** The sub-agent has no access to the orchestration
  conversation. Brief it like a smart colleague who just walked into the room.
- **Specific.** Include exact file paths, prior phase outputs (paste them or
  reference paths), constraints, and the expected output format.
- **Bounded.** State clearly what is in scope and what is not. Specialists
  expand scope if you don't constrain them.

## Parallel vs sequential dispatch — mechanics

- **Parallel phases**: launch all agents in that phase **in a single message
  with multiple Agent tool calls**. This is the only way they actually run in
  parallel. Multiple sequential messages = sequential execution, not parallel.
- **Sequential phases**: launch one Agent at a time, wait for completion, pass
  its output as context to the next.

### Worktree isolation (`isolation: "worktree"`)

Use it when:

- Multiple parallel agents touch git-tracked files that might collide.
- Long-running parallel work should not contaminate the main branch.
- Agents produce PRs independently.

Skip it for read-only or non-conflicting parallel work — the worktree overhead
is not free.

## Output — final response skeleton

For non-trivial orchestrations, structure the final response like this:

```
## Plan
<the decomposition + phase plan, briefly stated>

## Execution
- Phase 1: <agent> — <one-line outcome>
- Phase 2: <agent A> + <agent B> in parallel — <outcomes>
- Phase 3: <agent> — <integration outcome>

## Synthesis
<unified deliverable summary, organised by output not by agent>

## Notes
<conflicts resolved, gaps identified, decisions made, follow-ups recommended>
```

For simple two-agent orchestrations, compress to a single coherent paragraph
followed by the synthesis section only.

## Synthesis rules (Step 6 expanded)

1. **Collect every agent's output** — record what each one produced (file
   paths created/modified, content summaries, decisions made).
2. **Detect conflicts**: did two agents produce contradictory recommendations?
   Inconsistent type names? Misaligned API contracts? Different naming
   conventions? Address each conflict explicitly — either resolve it (one
   wins) or surface it to the user with a recommendation.
3. **Detect gaps**: did anything fall between agents? Cross-cutting concerns
   that no single agent owned (logging, error handling, security,
   observability)? Either dispatch a follow-up agent or note the gap in the
   synthesis.
4. **Produce the unified response**: organise the synthesis by **deliverable**,
   not by agent. The user does not care which agent produced what — they care
   what was delivered, what changed, and what remains.

Synthesis is the part that distinguishes orchestration from delegation. Without
it, the orchestrator has just been a routing table. Do not skip this step
under any circumstances.

## Stop conditions

- **Stop and ask the user** before dispatching if the plan involves
  destructive operations (deletions, rewrites of large surfaces, force-pushes).
- **Stop and ask the user** if a sub-agent reports a blocking conflict that
  cannot be resolved without a product-level decision.
- Otherwise continue automatically through the phases.
