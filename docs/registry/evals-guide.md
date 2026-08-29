# Evaluations

An evaluation is a documented test case: given a specific prompt and context, what must the
capability do? Evaluations serve two purposes.

1. **Validation before release.** Confirm a new or changed capability behaves as intended.
2. **Regression detection.** After a change, re-run them to confirm existing behaviour
   survived.

Write them **before** the capability. Written afterwards, they document what you built
rather than the problem you set out to solve.

---

## Where they live

```
plugins/<plugin>/evals/<capability-name>/evals.json
plugins/<plugin>/evals/<capability-name>/triggers.json
```

`<capability-name>` is the agent filename without `.md`, or the skill directory name.

Agents carry both files. Skills carry `triggers.json` only: a skill has no behaviour of its
own to score, so the only thing worth testing is whether the right prompt activates it.
The repository currently holds 27 `evals.json` files, all for agents, and 73
`triggers.json` files, 27 for agents and 46 for skills.

---

## `evals.json`

A flat JSON list. One object per scenario, exactly these four keys.

```json
[
  {
    "agent": "developer-java",
    "query": "This repository method triggers an N+1 on order lines. Fix it.",
    "files": ["fixtures/OrderRepository.java"],
    "expected_behavior": [
      "Identifies the lazy association responsible for the N+1",
      "Applies a fetch join or an entity graph rather than switching to EAGER",
      "Keeps the existing method signature and adds a regression test"
    ]
  }
]
```

| Key | Content |
|---|---|
| `agent` | The capability under test. Equals the eval directory name |
| `query` | The exact prompt to send, phrased the way a user would actually phrase it |
| `files` | Context files to place in the working directory. `[]` when the prompt is self-contained |
| `expected_behavior` | Observable behaviours, one per string. Each must be checkable by reading the output |

Write `expected_behavior` entries an independent reader could score without asking you what
you meant. "Handles the error properly" is not checkable. "Returns 404 with an RFC 7807
body when the order does not exist" is.

Nothing in CI validates this schema, so a scenario written to the wrong shape passes review
and then fails when the suite is run. Copy the shape above.

---

## `triggers.json`

A flat JSON list of three-key objects. This is the half that catches a description edit
which quietly breaks routing, and it is the more valuable of the two files.

```json
[
  {
    "query": "Write an ADR for the decision to use event sourcing in the order service",
    "should_trigger": true,
    "description": "Primary invocation"
  },
  {
    "query": "Produce a CVE inventory for our third-party dependencies",
    "should_trigger": false,
    "description": "Dependency vulnerability audit, should route to `technical-analyst`"
  }
]
```

| Key | Content |
|---|---|
| `query` | The prompt |
| `should_trigger` | `true` if this prompt must activate the capability, `false` if it must not |
| `description` | Why. For a negative case, name the sibling that should handle it instead |

Rules that make the negative cases worth having:

- Write one negative case per sibling a reader could plausibly confuse with this
  capability. A negative case against something unrelated proves nothing.
- Check every negative case against the capability's own `description` before committing
  it. A prompt the description claims the capability handles cannot be a valid negative
  case. This is exactly the error that put "What are the security risks in this codebase?"
  in `software-architect` as a must-not-trigger, while its description lists security among
  the non-functional requirements it assesses.
- Vary the phrasing across positive cases, including the languages the team actually uses.

---

## Coverage expectations

Before a capability ships in a minor or major plugin release:

- At least three scenarios in `evals.json` for an agent: the happy path, an edge case, and
  one that would catch a likely regression, such as a required output section going missing
- At least two positive and two negative cases in `triggers.json`
- Every negative case names the sibling it should route to

---

## Running them

Execution is manual. There is no automated harness.

1. Add this clone as a marketplace: `claude plugin marketplace add .`
2. Enable the plugin under test, then open Claude Code in a scratch directory rather than
   in the registry, so `${CLAUDE_PLUGIN_ROOT}` paths resolve the way a consumer sees them
3. Place the `files` from the scenario
4. Send the `query` and score the output against `expected_behavior`
5. For `triggers.json`, send the query with no explicit delegation and record whether
   Claude routed to the capability on its description alone

Test against Haiku, Sonnet and Opus. What reads as sufficient guidance on Opus is often too
terse for Haiku.
