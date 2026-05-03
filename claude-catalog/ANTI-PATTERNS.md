# Anti-Patterns

This file is the registry's institutional memory of what has **failed**.

Every time a capability is deprecated, retired, or substantially rewritten because the
underlying approach did not work, an entry is added here describing **what was tried,
why it failed, and what replaced it**. The deprecated `.md` file is removed from the
marketplace 90 days after deprecation (per `GOVERNANCE.md`), but the lesson stays here
indefinitely so the next contributor proposing a similar capability can see we already
tried it.

This is the analogue of `CHANGELOG.md` for **negative knowledge**: changelog records
what works and ships; anti-patterns record what didn't and why.

---

## When to add an entry

Add an entry here when **any** of the following happens:

- A capability is deprecated (`status: deprecated`) — the deprecation reason becomes the
  anti-pattern reason. Adding the entry is part of the deprecation PR, not a follow-up.
- A capability is renamed/restructured because the original framing was wrong (not just
  cosmetic). Record the original framing and why it didn't work.
- A proposed capability is rejected during PR review for a structural reason (overlap,
  scope creep, wrong abstraction). Record it so the next person proposing the same
  thing finds the precedent.
- An internal pattern is intentionally banned (e.g. "skills must not delegate via
  `Agent` tool"). Record the rule and the incident that produced it.

Do **not** add entries for:

- Bug fixes or behavior tweaks — those are `CHANGELOG.md` material.
- One-off mistakes corrected in the same PR — no precedent value.
- Personal preferences without a concrete failure mode behind them.

---

## Entry format

Each entry is one section. Keep it short — a future reader should be able to skim 50
entries in a few minutes.

```markdown
## <name-or-pattern> — <one-line summary>

- **Tried**: 2026-MM-DD (catalog version `name@x.y.z` if applicable)
- **Failure mode**: One or two sentences. Be concrete — what broke, what users hit, what
  the metric was if any.
- **Replaced by**: The capability or pattern that now covers the use case. If nothing
  replaced it, say "Removed; the use case is no longer in scope" and explain why.
- **Do not retry unless**: Conditions that would make this approach worth re-trying.
  If there are no such conditions, write "Do not retry."
```

The **Do not retry unless** clause is the most important field. Without it, future
contributors will assume the entry just describes a mistake and may re-propose the same
thing under a different name. With it, they have a concrete signal — either the
preconditions for a retry are met (and the proposal is valid), or they are not (and the
proposal is dead on arrival).

---

## How to use this file during review

The PR review checklist (`review-checklist.md`, section 10) requires reviewers to
**search this file** for the proposed capability's role keywords before approving a new
capability. A hit is not an automatic block — a deprecated capability may have failed
for reasons that no longer apply — but the reviewer must explicitly confirm in the PR
discussion that the **Do not retry unless** clause is satisfied.

Search examples:

```bash
# Looking at adding a "java-microservices-developer" — search for similar past attempts
grep -i 'microservices\|developer-java' claude-catalog/ANTI-PATTERNS.md

# Looking at adding a doc-generation skill — search the doc topic
grep -i 'doc\|documentation' claude-catalog/ANTI-PATTERNS.md
```

---

## Entries

<!--
No entries yet. The first deprecation after this file is introduced will populate it.

When you add the first entry, remove this comment and start the list directly below.
Keep the most recent entry at the top so a future reader sees the latest precedent first.
-->

_(empty — populated as capabilities are deprecated or rejected for structural reasons)_
