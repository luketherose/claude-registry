---
name: capability-parity-sync
description: "This skill should be used when a capability is added, changed or retired in one of the two registries and the twin must be brought back into step: deciding whether the change is portable, producing the mirrored file, recording the divergence when it is not portable, and running the drift check that proves the two sides still match. Trigger phrases: \"mirror this skill\", \"sync the registries\", \"keep the twin in step\", \"parity drift\", \"is the twin up to date\", \"propagate this to the other registry\". Covers the procedure and its ledger. It does not cover the host mapping itself (that is `cross-host-parity`)."
---

# Keeping two registries in step

Two registries hold the same capabilities for two hosts. Without a procedure they drift
within weeks: an edit lands on one side, the other keeps an older answer, and nobody
notices because both still pass their own gate.

The property to preserve: **a capability added or changed on either side appears on the
other, adapted, or is recorded as a deliberate divergence with a reason.** Silence is
the failure mode, so the ledger has an entry either way.

## One source of truth per capability

Every capability names one side as its source. The other side holds a derived copy.
Nothing is edited on both sides.

The source is declared in the ledger, not inferred from timestamps. Inferring it from
which file changed last turns a hotfix on the derived side into a new source of truth,
and then the real source is silently reverted on the next sync.

## The four cases

Decide which one applies before touching anything.

### 1. Portable as is

A skill with no host-specific content. The overwhelming majority of skills, because the
Agent Skills standard is shared. Copy, apply the mechanical substitutions, done.

### 2. Portable with adaptation

Host-specific strings, tool names, path variables. Mechanical, checkable, and it is where
the substitution table earns its place.

### 3. Portable only after restructuring

A supervisor that dispatches other agents. Gemini CLI blocks agent-to-agent dispatch, so
the shape has to change before the content can move. Do not attempt this as part of a
sync: raise it as its own piece of work.

### 4. Not portable

The capability depends on something the other host does not have. Record it as a
divergence with a reason and a re-check date. It is not a failure, it is a fact that has
to stay visible.

## The mechanical substitutions

Applied in this order when moving toward Gemini CLI. Reverse them coming back.

1. A Claude Code plugin-root path becomes a plain relative path in `SKILL.md`. The
   Gemini extension-path variable is substituted only inside `gemini-extension.json`
   and `hooks/hooks.json`, so it is wrong anywhere else.
2. Claude Code tool names become Gemini tool names.
3. `CLAUDE.md` becomes `GEMINI.md`.
4. Hook `timeout` seconds become milliseconds.
5. Command frontmatter and body become TOML `description` and `prompt`; `$ARGUMENTS`
   becomes `{{args}}`.
6. Model class names are resolved through the host's own policy, never hardcoded.

Substitution 4 is the one that silently survives review. A number that changes meaning
between hosts looks correct in a diff on either side.

## The procedure

1. **Classify** the change against the four cases above.
2. **Check the ledger** for an existing divergence covering this capability. An open
   divergence means the sync is already known not to apply; extend it rather than
   reopening the argument.
3. **Produce the mirror.** Apply the substitutions. Do not translate prose that names the
   host to a user; rewrite it.
4. **Port the eval corpus, not the harness.** The queries, the should-trigger flags and
   the expected behaviours are facts about the capability and belong to both sides. The
   harnesses do not converge and should not be made to.
5. **Run both gates.** A mirrored capability that passes only its own side is not synced.
6. **Update the ledger** in the same commit as the mirror. A ledger updated later is a
   ledger that will be updated never.
7. **Run the drift check.**

## The ledger

One row per capability, in a file both registries carry identically.

| Field | Meaning |
|---|---|
| `capability` | the name, identical on both sides |
| `kind` | skill, agent, command or hook |
| `source` | which registry is authoritative |
| `status` | `mirrored`, `diverged` or `pending` |
| `reason` | required when `diverged`, empty otherwise |
| `source_sha` | the commit the mirror was derived from |
| `recheck` | a date, required when `diverged` |

`source_sha` is what makes the drift check possible: the mirror is stale exactly when the
source has moved past the recorded SHA.

## The drift check

It must fail the build, or it is documentation.

Three properties, each one a real failure that has happened in registries like this:

1. **Presence.** Every capability with `status: mirrored` exists on both sides. Catches a
   capability added on one side and forgotten.
2. **Freshness.** For every mirrored capability, the source has not moved past
   `source_sha`. Catches an edit on the source side that never propagated.
3. **Justification.** Every `diverged` row has a non-empty `reason` and a `recheck` date
   that has not passed. Catches a divergence recorded once and then left to rot, which is
   how a temporary exception becomes permanent.

Report the failing capability by name. A drift check that says "the registries differ"
without saying where is a check people learn to ignore.

## What not to automate

Generating the mirror automatically is tempting and wrong for prose. The substitutions
are mechanical; deciding that a paragraph about Claude Code's approval flow should become
a paragraph about consent prompts is not. Automate the substitutions, the ledger checks
and the drift check. Leave the judgement to a review that a human signs.
