# Parity ledger

## Purpose

One row per capability that exists, or deliberately does not exist, on both the Claude Code
side and the Gemini CLI side. A capability added or changed on either side either appears on
the other, adapted, or carries a `diverged` row with a reason and a recheck date. Silence is
the failure mode this file exists to prevent.

## Format

`parity/ledger.json`, one JSON array, one object per capability, as specified by
`docs/gemini-twin/twin-registry-plan.md` section 4: JSON rather than JSONL or YAML because CI is
already Python and already gates JSON in this repository. A port and its ledger row land in the
same change; a row is never added later.

An earlier revision of this file used append-only JSONL. It was converted when the twin tree moved
into this repository, and the conversion is the reason the two formats are mentioned at all.

## Single source of truth

Every capability names one side as its source, in the `source` field. The other side holds a
derived copy and is never edited directly. The source is read from this file, never inferred
from which copy changed last: inferring it turns a hotfix on the derived side into a new source
of truth, and the real source is then silently reverted on the next sync.

## Schema

Fields 1 to 7 are the ledger schema defined in the `capability-parity-sync` skill, section
"The ledger". Field 8 is an addition, justified below.

| Field | Meaning |
|---|---|
| `capability` | the name, identical on both sides |
| `kind` | skill, agent, command or hook |
| `source` | which registry is authoritative |
| `status` | `mirrored`, `diverged` or `pending` |
| `reason` | required when `diverged`, empty otherwise |
| `source_sha` | the commit the mirror was derived from |
| `recheck` | a date, required when `diverged` |
| `published_ref` | the git ref the Gemini side was published and installed at, empty when the capability is not delivered as an extension |

### Two local conventions, stated so they are not mistaken for the schema

`kind` carries the value `context` for a host context file (`CLAUDE.md`, `GEMINI.md`). The
schema enumeration covers skill, agent, command and hook only, and a context file is none of
those. Labelling it as one of the four to stay inside the enumeration would be worse.

`source` may name a repository that is neither registry, when the capability originates
outside them. `claude-config` is the private personal-configuration repository; the two
registries are `claude-registry` and its Gemini twin.

### Why `published_ref` was added

This is an eighth field, one more than the seven the plan's section 4 specifies. The addition is
deliberate and recorded here rather than made silently, because a schema change nobody declared is
the same class of failure the ledger exists to prevent.

`source_sha` makes freshness checkable inside the repository: the mirror is stale exactly when
the source has moved past the recorded SHA. It says nothing about what a user is running.
`gemini extensions install` copies rather than symlinks, accepts a `--ref`, and detects updates
from tags, so an installed extension stays at the revision it was installed from until
`gemini extensions update` runs. A mirror can therefore be fresh in the repository and absent
from every machine. `published_ref` records the revision the Gemini side was actually published
and installed at, so that gap is visible instead of assumed closed.

Leave it empty for a capability delivered by file copy rather than by extension install. An
empty value means "not delivered as an extension", not "unknown".

## Drift check

Three properties, each of which must fail a build rather than a report:

1. **Presence.** Every `mirrored` capability exists on both sides.
2. **Freshness.** For every `mirrored` capability, the source has not moved past `source_sha`.
   Where `published_ref` is set, the published revision has not fallen behind it either.
3. **Justification.** Every `diverged` row has a non-empty `reason` and a `recheck` date that
   has not passed.

Report the failing capability by name. "The registries differ" is a report people learn to
ignore.

## Client material

`unicredit-design-system` carries a client design system (component catalogue, design tokens), and
`developer-frontend` names client subsidiaries in its detection signals. Decision of 2026-09-10,
answering Q5(a) of `docs/gemini-twin/twin-registry-plan.md`: this material mirrors into the twin
tree of this repository, which already governs it and already contains it on `origin/main`, and
never into a separately publishable extension.

The constraint is recorded here rather than in a ledger `reason`, because the schema requires
`reason` to be empty unless `status` is `diverged`, and this material is mirrored, not diverged.
Section 6 of the plan expects a client-material denylist check in CI: this is the list it reads.

- `unicredit-design-system` (skill, dev-standards)
- `developer-frontend` (agent, dev-standards): 8 lines naming client entities
