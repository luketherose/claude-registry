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

Every agent and every skill in the registry has a `triggers.json`. `evals.json` exists for
agents only, and not yet for all of them. Count the corpus rather than trusting a figure
written here, because it moves with every capability added:

```bash
ls plugins/*/evals/*/triggers.json | wc -l
ls plugins/*/evals/*/evals.json | wc -l
```

---

## `evals.json`

A flat JSON list. One object per scenario, exactly these four keys.

Abridged from `plugins/dev-standards/evals/developer-java/evals.json`:

```json
[
  {
    "agent": "developer-java",
    "query": "Review this Spring Boot controller",
    "files": ["fixtures/OrderController.java"],
    "expected_behavior": [
      "Flags the discount computation inside create, and the @Autowired field injection into the controller, as layering violations, quoting the offending lines",
      "Flags the empty catch (Exception) that returns null and requires an RFC 7807 ProblemDetail response in place of the RuntimeException",
      "Reports the hardcoded STRIPE_KEY constant and the log statement that writes customer email and card number, each with its line"
    ]
  }
]
```

| Key | Content |
|---|---|
| `agent` | The capability under test. Equals the eval directory name |
| `query` | The exact prompt to send, phrased the way a user would actually phrase it |
| `files` | Context files to place in the working directory, written relative to the eval directory. `[]` when the prompt is self-contained |
| `expected_behavior` | Observable behaviours, one per string. Each must be checkable by reading the output |

Write `expected_behavior` entries an independent reader could score without asking you what
you meant. "Handles the error properly" is not checkable. "Returns 404 with an RFC 7807
body when the order does not exist" is.

`validate_evals()` in `.github/scripts/validate_registry.py` gates this file, so a scenario
written to the wrong shape fails CI rather than passing review. It checks three things:

- the file parses as JSON
- every scenario's key set is exactly `agent`, `query`, `files`, `expected_behavior`, with
  no extra key and none missing
- every path in `files` resolves, joined against the directory the `evals.json` lives in

The convention that `agent` equals the eval directory name holds across the corpus and is
what the trigger gate keys on, but nothing asserts it for `evals.json`. Getting it wrong
costs you a scenario that names the wrong capability, silently.

---

## `triggers.json`

A flat JSON list of three-key objects. This is the half that catches a description edit
which quietly breaks routing, and it is the more valuable of the two files.

Two cases from `plugins/analysis-architecture/evals/software-architect/triggers.json`:

```json
[
  {
    "query": "Write an ADR for the decision to use event sourcing in the order management system",
    "should_trigger": true,
    "description": "ADR for adopting event sourcing"
  },
  {
    "query": "Produce a CVE inventory for our third-party dependencies",
    "should_trigger": false,
    "description": "CVE inventory for third-party dependencies"
  }
]
```

| Key | Content |
|---|---|
| `query` | The prompt |
| `should_trigger` | `true` if this prompt must activate the capability, `false` if it must not |
| `description` | A restatement of what the query is about. It never says which capability wins and never says whether the case triggers |

### The description restates the query and nothing else

This is the rule the validator is strictest about, and the one contributors get wrong,
because the older corpus taught the opposite habit. `validate_evals()` rejects a
`description` on two grounds:

- it matches a verdict phrasing. The gate is case-insensitive and looks for
  `primary invocation`, `should activate`, `should not activate`, `route to` in any of its
  `route`, `routes` and `routed` spellings, `belongs to`, and `use <word> instead`
- it names any agent or skill in the registry that the `query` does not already mention

The second rule allows a description to repeat a subject the query names. A query about
TanStack Start may be described as being about TanStack Start, because that tells a grader
nothing it could not read off the query itself. Naming a capability the query never
mentions is what hands over the answer.

The reason is measured. An earlier corpus named the routing winner in 364 of 365
descriptions, and a nine-line keyword table then scored 232 of 232 on it without reading a
single capability. A suite that a keyword table passes is not testing routing.

Practical consequence: a description reading "Dependency vulnerability audit, should route
to technical-analyst" fails CI twice over, on the verdict phrasing and on the capability
name. Write "CVE inventory for third-party dependencies" and let the grader do the routing.

Rules that make the negative cases worth having:

- Write one negative case per sibling a reader could plausibly confuse with this
  capability. A negative case against something unrelated proves nothing. Pick the sibling
  when you choose the query, then leave it out of the description.
- Check every negative case against the capability's own `description` before committing
  it. A prompt the description claims the capability handles cannot be a valid negative
  case. That error once listed "What are the security risks in this codebase?" as a
  must-not-trigger for `software-architect`, whose description names security among the
  non-functional requirements it assesses. It is now a dependency-CVE query instead.
- Vary the phrasing across positive cases, including the languages the team actually uses.

---

## Coverage expectations

Before a capability ships in a minor or major plugin release:

- At least three scenarios in `evals.json` for an agent: the happy path, an edge case, and
  one that would catch a likely regression, such as a required output section going missing
- At least two positive and two negative cases in `triggers.json`
- Every negative case is aimed at a specific sibling, and no description names it

---

## Running them

Execution is manual. This repository ships no eval harness.

1. Add this clone as a marketplace: `claude plugin marketplace add .`
2. Enable the plugin under test, then open Claude Code in a scratch directory rather than
   in the registry, so `${CLAUDE_PLUGIN_ROOT}` paths resolve the way a consumer sees them
3. Place the `files` from the scenario
4. Send the `query` and score the output against `expected_behavior`
5. For `triggers.json`, send the query with no explicit delegation and record whether
   Claude routed to the capability on its description alone

Test against Haiku, Sonnet and Opus. What reads as sufficient guidance on Opus is often too
terse for Haiku.
