# W5 critic review: em dash sweep and agent eval suites

Adversarial review of two unreviewed batches carried by commit `15f4749`.
Everything below was re-derived from the repository. The producing agents' reports were not used as input.

Snapshot: reviewed at `15f4749`; repo HEAD is `a005ee5`, which touches only `scripts/install-local.sh`
and changes nothing under `plugins/`. Working tree was clean at the start of the review. The 42 eval JSON
files under review hash to combined md5 `0d45def108d060a05fcbce35c22cefca`. Read 2026-08-29 23:43 CEST.

**Concurrency note.** While this review was being written, another agent in the same session began
repairing B2-1 in the working tree. `plugins/analysis-architecture/agents/technical-analyst.md`,
`plugins/docs-branding/agents/documentation/wiki-writer.md` and
`plugins/dev-standards/agents/developers/developer-frontend.md` now show uncommitted `description:`
edits that were not made by this review, and the B2-1 detector consequently reports 0 broken files
against the working tree instead of 2. The finding was real at `15f4749`, which is the reviewed commit.
Every B2-1 command below is pinned to `git show 15f4749:<path>` or to the `756f883..15f4749` diff so it
still reproduces. Verify the repair landed with the working-tree form of the detector before closing
B2-1, and re-check that the repaired strings still parse.

`.github/scripts/validate_registry.py` is also being edited concurrently, which is the B2-8 gap. The
`grep -c eval` command in B2-8 returned 0 against `15f4749` and will return a nonzero count once that
edit lands. Confirm against `git show 15f4749:.github/scripts/validate_registry.py | grep -c eval` if the
figure needs checking after the fact.

Reproduce the state:

```
git merge-base --is-ancestor 15f4749 HEAD && echo "review commit is an ancestor"
git diff --stat 15f4749..HEAD -- 'plugins/*/skills/*' 'plugins/*/evals/*' 'plugins/*/agents/*'   # empty
```

---

# Batch 1: the em dash sweep

## Verdict

**Mostly sound. Send back 4 of 626 changed lines (0.6%), and reopen the scope question.**

The mechanical quality is good. Nothing I looked for in the "corrupted a code sample" family actually
happened: no table lost a column, no anchor broke, no YAML frontmatter broke, no numeric range or CLI
flag was touched, and no real filesystem path was mistaken for a capability reference. The four lines I
would send back are three semantic inversions inside negative-instruction lists and one missed path that
also visibly misaligns an ASCII block.

The larger issue is not a defect in what was changed, it is what was declared done. The sweep covered
`plugins/*/skills/*` only. 3063 em dashes and 15 stale capability paths survive elsewhere in `plugins/`,
including inside the exact Quality self-check lines that Batch 2's expectations were derived from.

## How much I actually inspected

The stated scope is 589 replacements. Measured: **593 net em dash removals across 626 changed line pairs
in 60 files**. That reconciles exactly with the claim: 589 prose replacements plus the 4 table cells
rewritten from a bare em dash to `n/a`. No file changed line count, so every hunk is a strict 1:1
substitution and the whole diff is analysable as aligned line pairs.

| Layer | Coverage |
|---|---|
| Programmatic screening of every changed line pair | 626 / 626 (100%) |
| Read individually with surrounding context | 442 / 626 (71%) |
| ... of which: all heading edits | 184 |
| ... all non-mechanical edits (transform other than `' —' -> ':'` or `' —' -> ','`) | 152 |
| ... all edits under a heading matching `never / do not / anti-pattern / forbid / out of scope` | 25 |
| ... all frontmatter edits (57 distinct edit sites on 37 `description:` lines) | 49 lines |
| Random sample of the remaining purely mechanical lines | 60 / 244 (25%), seed 20260829 |

The union of the "read individually" sets is 382 lines; adding the 60-line random sample gives 442.
I did not read the other 184 mechanical lines one by one. They were all screened by the classifier below,
which proved each one is a single `' —'` to `':'` or `','` substitution with no other character changed.

Screening script (regenerates every number in this section):

```
python3 - <<'EOF'
import subprocess, difflib, collections
R="756f883..15f4749"
files=subprocess.run(["git","diff","--name-only",R,"--","plugins/*/skills/*"],capture_output=True,text=True).stdout.split()
h=collections.Counter(); n=0
for f in files:
    o=subprocess.run(["git","show",f"756f883:{f}"],capture_output=True,text=True).stdout.split("\n")
    w=subprocess.run(["git","show",f"15f4749:{f}"],capture_output=True,text=True).stdout.split("\n")
    assert len(o)==len(w), f
    for a,b in zip(o,w):
        if a==b: continue
        n+=1
        sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
        h[tuple((t,repr(a[i:j]),repr(b[k:l])) for t,i,j,k,l in sm.get_opcodes() if t!='equal')]+=1
print("changed line pairs:",n); [print(v,k) for k,v in h.most_common(8)]
EOF
```

## Findings, ranked by whether a real regression gets through

### B1-1. A colon inverts a corrective instruction inside a "never do" list (medium)

`plugins/docs-branding/skills/accenture-branding/SKILL.md:197`

```
-  - Generate output files — provide the constants and rules for the calling agent to use
+  - Generate output files: the constants and rules are provided for the calling agent to use
```

```
sed -n '193,198p' plugins/docs-branding/skills/accenture-branding/SKILL.md
```

The bullet sits under `## What you never do` (line 193). In the original, the em dash split a prohibition
from its remedy: never generate output files, instead provide the constants. The colon now subordinates
the second clause to the first, and the remedy was additionally rewritten from an imperative ("provide")
into a passive statement of fact ("are provided"). A model reading the list top to bottom can now parse
the whole bullet as prohibited, which inverts the skill's actual job: providing the constants is the
only thing this skill does. This is the one edit in the batch where the punctuation change carries
behavioural risk.

### B1-2. Same defect class, two more bullets (low to medium)

`plugins/dev-standards/skills/testing-standards/SKILL.md:315` and `:316`, under `## What good tests do NOT do`:

```
-  - Use `Thread.sleep()` to wait for async operations — use `CompletableFuture`, `awaitility`, or test doubles
+  - Use `Thread.sleep()` to wait for async operations: use `CompletableFuture`, `awaitility`, or test doubles
-  - Assert on log output (fragile) — assert on observable side effects instead
+  - Assert on log output (fragile): assert on observable side effects instead
```

```
sed -n '310,317p' plugins/dev-standards/skills/testing-standards/SKILL.md
```

Same structural risk as B1-1, lower severity because the remedy stayed imperative and the alternatives
named are self-evidently the recommended path. Still: a prohibition list is the wrong place to replace a
clause break with a clause link. The safe rewrite for all three is a full stop plus a capitalised
imperative, which is exactly what the sweep did in the other 8 sites where it produced `. Do not`.

Nothing else in the 25 edits under a negative heading has this shape. I checked all of them; the
`unicredit-design-system` bullets (`Apply Bricks rules to a non-UniCredit project: this skill is
client-scoped`) attach a rationale, not a remedy, and read correctly.

### B1-3. A missed path leaves a visibly broken ASCII block, inside the sweep's own scope (low)

`plugins/dev-standards/skills/frontend-orchestrator/SKILL.md:89`

```
sed -n '87,93p' plugins/dev-standards/skills/frontend-orchestrator/SKILL.md
```

```
1. /refactoring/refactoring-expert     → identify code smells, SOLID violations   <-- arrow at col 39
2. angular-expert    → apply structural corrections                               <-- arrow at col 21
3. rxjs-expert       → correct problematic RxJS patterns                          <-- col 21
4. css-expert        → correct styles (if necessary)                              <-- col 21
```

The normalisation matched `refactoring/refactoring-expert` at line 27 (a table cell) but not the
slash-prefixed form at line 89. The other 27 lines it rewrote inside fenced blocks all preserved column
alignment correctly, so this is the only misaligned block the batch produced. Detector:

```
python3 - <<'EOF'
p="plugins/dev-standards/skills/frontend-orchestrator/SKILL.md"
lines=open(p).read().split("\n"); fence=False; blk=[]; start=0
for i,l in enumerate(lines,1):
    if l.strip().startswith("```"):
        if fence and len({x[1].index("→") for x in blk if "→" in x[1]})>1:
            print("MISALIGNED block at line",start); [print(f"  {a}: {b}") for a,b in blk]
        blk=[]; start=i+1; fence=not fence; continue
    if fence: blk.append((i,l))
EOF
```

### B1-4. The path normalisation missed 13 more references in a file it did edit (medium, scope)

`plugins/dev-standards/skills/backend-orchestrator/references/decision-patterns.md`, lines 26 to 58.

```
git grep -nE '/(backend|database|refactoring)/[a-z0-9-]+' -- 'plugins/*/skills/*'
```

14 hits: 13 in `decision-patterns.md`, plus the one line already reported as B1-3.
This file is inside `plugins/*/skills/*/references/*.md`, it was edited by the sweep (its headings
changed at lines 23, 35, 46, 55), and yet every capability reference in its four decision blocks still
reads `/backend/spring-architecture`, `/database/postgresql-expert`, `/backend/spring-data-jpa`,
`/backend/java-expert`, `/backend/spring-expert`. The normalisation pass matched `frontend/`, `python/`
and one bare `refactoring/`, but not the slash-prefixed `/backend/` and `/database/` forms. 13 lines.

Measured totals for the path pass, against the claimed 26: **52 path prefixes removed across 46 lines**,
distributed `frontend/` 17, `frontend/angular/` 16, `frontend/react/` 12, `frontend/vue/` 2,
`frontend/qwik/` 2, `frontend/vanilla/` 1, `refactoring/` 1, `python/` 1. The "26" figure does not
reconcile with lines, occurrences, or distinct references (16). Worth correcting in whatever ledger tracks it.

### B1-5. The same defect survives in `agents/`, where it actually executes (medium, scope)

```
grep -rnoE '`(api|testing|backend|refactoring|frontend|database|python)/[a-z0-9/-]+`' plugins/*/agents/
```

17 hits, of which 2 are genuine filesystem paths and correctly untouched
(`tobe-testing-challenger.md:108,109`, `backend/src/test/` and `frontend/src/test/`).
The other **15 are stale capability references** naming skills that do not exist under those names:

| File and line | Stale reference | Real skill name |
|---|---|---|
| `plugins/dev-standards/agents/api-designer.md:46` | `api/rest-api-standards` | `rest-api-standards` |
| `plugins/dev-standards/agents/api-designer.md:103` | `api/rest-api-standards` | `rest-api-standards` |
| `plugins/dev-standards/agents/test-writer.md:65,68,77` | `testing/testing-standards` | `testing-standards` |
| `plugins/dev-standards/agents/test-writer.md:66` | `backend/java-spring-standards` | `java-spring-standards` |
| `plugins/dev-standards/agents/test-writer.md:50,54` | `frontend/react/react-expert`, `frontend/angular/angular-expert` | `react-expert`, `angular-expert` |
| `plugins/dev-standards/agents/developers/developer-java.md:93,94` | `backend/java-spring-standards`, `testing/testing-standards` | bare names |
| `plugins/dev-standards/agents/developers/developer-frontend.md:84,88,92,95,98` | `frontend/design-expert`, `frontend/css-expert`, `testing/testing-standards`, `api/rest-api-standards`, `refactoring/refactoring-expert` | bare names |

Plus 11 more in `plugins/dev-standards/references/developers/developer-frontend/per-framework-conventions.md`.
Confirm the real names with `ls plugins/dev-standards/skills/ | grep -E 'rest-api|testing-stand|java-spring|refactoring'`.

`api-designer.md:103` is Quality self-check item 1: *"Did I invoke `api/rest-api-standards` and apply the
returned rules?"*. An agent that follows its own self-check calls a name that does not resolve. This is the
highest-impact instance of the exact class of defect Batch 1 set out to fix, and it was out of scope by
one directory. See B2-2: no eval catches it either.

The em dash coverage has the same shape: 3063 em dashes remain under `plugins/`
(`git grep -c '—' -- 'plugins/**' | awk -F: '{s+=$2} END {print s}'`), the top offenders being
`plugins/replatforming/references/refactoring-workflow/per-phase-protocol.md` (47) and
`plugins/docs-branding/agents/documentation/documentation-writer.md` (32).

## What I checked and found clean

One line each, as instructed.

- **Table integrity.** 0 changed lines altered their pipe count. `python3` diff over all 626 pairs comparing `o.count("|")` to `n.count("|")`.
- **Anchors.** 184 headings changed slug, 0 internal `](#slug)` references to any old slug exist anywhere in the repo's `.md` or `.json` files.
- **YAML frontmatter.** All 37 touched `SKILL.md` frontmatter blocks parse with `yaml.safe_load`; the 57 edit sites on `description:` lines left every `\"` escape nesting intact.
- **Ranges and flags.** 0 changed lines had an em dash adjacent to a digit, a version, a percent sign or a hyphen-flag pattern. Nothing to mutilate.
- **Inline code spans.** 0 em dashes were removed from inside a backtick span; the one surviving instance (`component-catalogue.md:68`, `` `// TODO: bricks-gap — confirm...` ``) was correctly left alone.
- **Fenced code blocks.** 403 em dashes inside fences were deliberately left untouched. 28 in-fence lines were edited: 27 are the path normalisation in `frontend-orchestrator/SKILL.md` (all alignment-preserving except B1-3), and one is a markdown checklist line, `plugins/replatforming/skills/python-to-angular-migration-expert/SKILL.md:43`, which is prose inside a fence and harmless.
- **Real filesystem paths.** `frontend/src/app/` survives intact at `angular-expert/SKILL.md:20` and `css-expert/SKILL.md:78`; the normalisation correctly distinguished it from capability references.
- **The `n/a` cells.** All 4 sit in a "Related skills" column (`frontend-orchestrator/SKILL.md:18,19,20`, `backend-orchestrator/SKILL.md:104`) where "not applicable" is the correct reading.
- **Grammar shape.** 0 new sentence breaks left a lowercase word after the full stop; 0 new doubled colons; 0 changes to `→ ↔ § ≥ ≤ ∥` glyph counts.

The 60-line random sample surfaced one cosmetic weakening worth a sentence and no more,
at `plugins/dev-standards/skills/rest-api-standards/SKILL.md:21`:

```
-  `/orders/{id}/items` ✓ — `/order-items?orderId=` ✗
+  `/orders/{id}/items` ✓, `/order-items?orderId=` ✗
```

A comma is a weaker good-versus-bad separator, but the check and cross glyphs still carry the semantics.

---

# Batch 2: the agent eval suites

## Verdict

**No. Send back roughly a third of the suite, and two agent files that are outright broken.**

Structurally the suite is exactly as specified: 21 agents, 3 scenarios each, 3 expectations each, 189
total, `agent` field matching the directory in all 63 scenarios, 3 positive and 2 negative triggers per
agent, 105 total. The expectations are unusually concrete for hand-written evals: the median expectation
shares 75% of its content tokens with its own agent file, and for `api-designer`, `developer-frontend`,
`developer-java` and `test-writer` the mapping to the agent's own numbered self-check is near one to one.

But the suite cannot gate a real regression, for three independent reasons, and it shipped alongside two
agent files that this same commit rendered unloadable.

Send back: 2 agent files (blocking), 13 of 189 expectations to rewrite, 17 of 63 scenarios to give
fixtures, 9 of 21 trigger sets to extend.

## B2-1. BLOCKER: commit `15f4749` broke the YAML frontmatter of two of the 21 agents

`plugins/analysis-architecture/agents/technical-analyst.md:3`
`plugins/docs-branding/agents/documentation/wiki-writer.md:3`

Pinned to the reviewed commit, so it reproduces regardless of working-tree repairs:

```
python3 -c "
import subprocess,yaml
for p in ['plugins/analysis-architecture/agents/technical-analyst.md','plugins/docs-branding/agents/documentation/wiki-writer.md']:
  for rev in ('756f883','15f4749'):
    t=subprocess.run(['git','show',rev+':'+p],capture_output=True,text=True).stdout
    try: yaml.safe_load(t[4:].split(chr(10)+'---',1)[0]); print('OK    ',rev,p)
    except Exception as e: print('BROKEN',rev,p,'::',str(e).split(chr(10))[0])"
```

Working-tree form, to confirm the repair once it lands:

```
python3 -c "
import glob,yaml
for p in sorted(glob.glob('plugins/*/agents/**/*.md',recursive=True)):
    t=open(p).read()
    try: yaml.safe_load(t[4:].split(chr(10)+'---',1)[0])
    except Exception as e: print('BROKEN:',p,'::',str(e).split(chr(10))[0])"
```

Both files were valid at `756f883` and are invalid at `15f4749`. The mechanism is visible in the diff:

```
git diff 756f883..15f4749 -- plugins/analysis-architecture/agents/technical-analyst.md | grep '^[-+]description'
```

```
- ... delegates to software-architect for that. Typical user phrasings: \"produce a technical health report for this repo\", \", and \"."
+ ... delegates to software-architect for that."produce a technical health report for this repo\", \", and \". Typical user phrasings: \"produce ...
```

A pass that repaired truncated `Typical user phrasings:` tails inserted a raw unescaped `"` at the point
where the old truncated fragment began, terminating the YAML scalar early and leaving the rest of the
line as an unparseable trailing scalar. The old truncated text was not removed, it was demoted into
garbage. The same pass ran on three agents; it succeeded on `developer-ruby.md` (which had no truncated
tail to collide with) and corrupted the two that did.

Consequence: `technical-analyst` and `wiki-writer` will not load. Both have an `evals.json` and a
`triggers.json` written in this same commit, and neither the 9 expectations nor the 5 trigger cases for
either agent can catch it, because both assume the agent loads. This is the single highest-value finding
in either batch and it should block the branch.

## B2-2. Zero of 189 expectations test that an agent loads its declared skills

```
python3 -c "
import json,glob,re
P=[q for b in ('dev-standards','analysis-architecture','docs-branding') for q in glob.glob(f'plugins/{b}/evals/*/evals.json')]
n=[e for p in P for s in json.load(open(p)) for e in s['expected_behavior'] if re.search(r'\binvoke\b|\bskill\b',e,re.I)]
print('files:',len(P),'expectations mentioning skill invocation:',len(n))
[print('  ',e[:90]) for e in n]"
```

2 of 189, and both are `registry-auditor` expectations that mention skills as *subject matter*
(`agent-development`, `skill-development` rubrics), not as something the agent invokes.

Every one of the 21 agents declares a `## Skills` block instructing it to load named skills with the
`Skill` tool. Several put the invocation at the top of their own quality gate:
`api-designer.md:103` (item 1), `test-writer.md:115` (item 5, "Are the returned standards from the skills
actually applied?"), `developer-java.md:93` ("Invoke `backend/java-spring-standards` before writing any
code"). None of that is tested.

Combine with B1-5: 15 of those skill references name paths that do not resolve. An agent whose entire
knowledge-provider wiring is dead still passes all 9 of its expectations, because the expectations only
inspect the shape of the produced text. That is the concrete regression this suite is meant to stop and
does not.

Cheapest repair: one expectation per agent of the form "invokes the `<skill>` skill before producing
output and the returned rule appears in the deliverable", replacing the weakest existing entry.

## B2-3. All 63 scenarios pass `files: []`, while 14 expectations demand a file and line citation

```
python3 -c "
import json,glob,re
P=[q for b in ('dev-standards','analysis-architecture','docs-branding') for q in glob.glob(f'plugins/{b}/evals/*/evals.json')]
S=[s for p in P for s in json.load(open(p))]; E=[e for s in S for e in s['expected_behavior']]
print('scenarios:',len(S),'with a non-empty files list:',sum(1 for s in S if s.get('files')))
print('expectations:',len(E),'demanding file/line:',sum(1 for e in E if re.search(r'file and line|file:line|quoting the offending|quoting the log line',e,re.I)))"
```

63 scenarios, 0 with any fixture. **14 expectations across 13 scenarios** require the agent to cite a
file and a line in material that was never supplied, and a further 4 (`functional-analyst` s2e1,
`technical-analyst` s1e0, `document-creator` s0e0, `presentation-creator` s0e1) require citing a specific
source artefact. 17 scenarios affected in total. 35 of the 63 queries are demonstrative
("Review **this** Spring Boot controller", "Ecco lo stack trace", "Produce a technical health report for
**this** repo") and have nothing to point at.

The worst instances, because the expectation is otherwise excellent and is voided entirely:

- `plugins/dev-standards/evals/developer-java/evals.json` scenario 1, all three expectations. "Flags business logic sitting in the controller ... quoting the offending lines" against `files: []`.
- `plugins/dev-standards/evals/developer-python/evals.json` scenario 1 expectation 0. "each with the file and line".
- `plugins/analysis-architecture/evals/technical-analyst/evals.json` scenario 0 expectation 1. "an Evidence column holding a file:line reference or a measured metric".

This is a regression against the predecessor. `plugins/dev-standards/evals/developer-java-eval.md`
Eval-003 specified the fixture explicitly: *"Input context: Existing controller with violations: business
logic inline, entity returned, missing `@Valid`."* The JSON rewrite dropped that and left the `files`
key present but empty in all 63 cases, which reads as an unfinished migration rather than a decision.
Six such `*-eval.md` predecessors still sit alongside the JSON directories
(`ls plugins/*/evals/*-eval.md`), so the repo now carries two divergent eval sources per agent for six
agents.

## B2-4. The negatives are clean of the parenthetical leak, but a keyword table rejects 18 of 18 developer negatives

The specific defect repaired in the skill evals is absent here.

```
python3 -c "
import json,glob,re,statistics,os
P=[q for b in ('dev-standards','analysis-architecture','docs-branding') for q in glob.glob(f'plugins/{b}/evals/*/evals.json')]
T=[os.path.join(os.path.dirname(p),'triggers.json') for p in P]
rows=[r for t in T for r in json.load(open(t))]
pos=[r for r in rows if r['should_trigger']]; neg=[r for r in rows if not r['should_trigger']]
print('agents:',len(T),'rows:',len(rows),'pos:',len(pos),'neg:',len(neg))
print('neg ending in a parenthetical:',sum(1 for r in neg if re.search(r'\([^)]*\)\s*$',r['query'])))
print('chars  pos %.1f  neg %.1f'%(statistics.mean(len(r['query']) for r in pos),statistics.mean(len(r['query']) for r in neg)))
print('words  pos %.2f  neg %.2f'%(statistics.mean(len(r['query'].split()) for r in pos),statistics.mean(len(r['query'].split()) for r in neg)))
print('descriptions:',set((r['should_trigger'],r['description']) for r in rows))"
```

- Parenthetical annotations on negatives: **0 of 42**. Repaired, or never present.
- Length: positives 61.0 chars / 9.79 words, negatives 59.3 chars / 9.52 words. Matched.
- Language: 71% of positives and 79% of negatives read as Italian. Matched.
- Annotation text: uniform, `"Primary invocation"` on all 63 positives and
  `"Should not activate this capability"` on all 42 negatives. No per-case hint.

So the obvious leaks are gone. The residual one is structural.

**Classifier 1, TF-IDF nearest centroid** built from the 63 positive queries only, leave-one-out on
positives, no access to any agent description. Overall 52/105 = 49.5%, but the split is asymmetric:
positives recalled 11/63 = 17.5%, **negatives rejected 41/42 = 97.6%**. A bag-of-words model that has
never read an agent's job description rejects almost every negative. The single miss is
`registry-auditor`'s "Scrivimi un nuovo agent per il code review dei PR", which is also the best negative
in the whole set.

**Classifier 2, a nine-line keyword table** over the 9 `developer-*` agents. Rule: trigger if and only if
the query names this agent's own technology and names no other developer agent's technology. No agent
description is read, no semantics, no model.

```
python3 /dev/stdin <<'EOF'
import json,glob,os
LANG={'developer-java':['java','spring','junit','jpa','maven'],'developer-python':['python','fastapi','pydantic','pytest','streamlit','django'],
'developer-go':['golang','chi','slog','goroutine',' go '],'developer-rust':['rust','cargo','axum','tokio','thiserror','unwrap'],
'developer-ruby':['ruby','rails','sidekiq','rspec','rubocop','activerecord'],'developer-php':['php','phpstan','symfony','laravel','eloquent'],
'developer-kotlin':['kotlin','ktor','coroutin','ktlint','detekt'],'developer-csharp':['c#','asp.net','xunit','dbcontext','.net'],
'developer-frontend':['angular','react','vue','qwik','tanstack','scss','streamlit']}
rows=[(os.path.basename(os.path.dirname(p)),r) for p in sorted(glob.glob('plugins/dev-standards/evals/developer-*/triggers.json')) for r in json.load(open(p))]
ok=pn=nn=0
for a,r in rows:
    q=' '+r['query'].lower()+' '
    pred=any(k in q for k in LANG[a]) and not any(k in q for b,ks in LANG.items() if b!=a for k in ks)
    if not r['should_trigger']: nn+= (pred==False)
    if pred==r['should_trigger']: ok+=1
    else: print('  MISS',a,'want',r['should_trigger'],'::',r['query'])
print(f"overall {ok}/{len(rows)} = {100*ok/len(rows):.1f}%   negatives rejected {nn}/18")
EOF
```

Result: **41/45 = 91.1% overall, and 18 of 18 negatives rejected**. The four errors are all
false rejections of genuine positives ("Scrivi l'OrderService con la validazione",
"Aggiungi table-driven test per l'order service", "Migra questa UI Streamlit in Angular",
"Converti questo service Java in Kotlin idiomatico"). **The classifier never once accepts a negative.**
That is the finding: the negative half of the developer suite requires no understanding of what any
agent does. A rule that has never read a single agent description scores 100% on it.

The reason is uniform: **every one of the 18 `developer-*` negatives is a cross-language flip.** Each one
names a rival language or framework by name in a single token, and 15 of the 18 name a rival that is
itself one of the 9 developer agents. Not one negative is a query in the agent's *own* language that
belongs to a different agent, which is the discrimination that actually fails in production. Missing
shapes, all of them realistic and all of them absent:

- `developer-java` should reject "Questo `OrderService` lancia una NullPointerException, capisci perche" (`debugger`).
- `developer-java` should reject "Rivedi il contratto REST di questa API Spring prima di implementarla" (`api-designer`).
- `developer-python` should reject "Sistema il bug di `session_state` nella mia dashboard Streamlit", which is the agent's own stated boundary at `developer-python.md:33` and is untested.
- `developer-rust` should reject "Scrivi i test per questo modulo Rust" (`test-writer`).

Only 3 of the 18 developer negatives route outside the developer family at all
(`developer-frontend` to `api-designer`, `developer-kotlin` and `developer-ruby` to `software-architect`),
and none of them routes to `debugger`, `test-writer` or `refactoring-expert`, which are the three agents
a language developer is most often confused with.

**One negative is outright wrong.** `plugins/analysis-architecture/evals/software-architect/triggers.json`
index 4: `"What are the security risks in this codebase?"`, labelled `should_trigger: false`. But
`software-architect.md:3` says the agent is for *"assessing non-functional requirements (performance,
**security**, scalability, reliability, cost, maintainability)"*, `:63` says *"Reason about all six
dimensions: **security**, performance..."*, `:91` says *"Never give security an afterthought status"*, and
its own eval `[138]` demands *"the security dimension is substantive, not a one liner"*. A correct router
answering "trigger" here is marked wrong. This case needs a disambiguator ("...and rank them by
remediation effort" pushes it to `technical-analyst`) or it needs deleting.

## B2-5. 13 of 189 expectations are not checkable from an output

Median lexical grounding of an expectation in its own agent file is 0.75, and only 5 entries fall below
0.35, so invention is rare. The failures are almost all *faithful copies of an agent's own unfalsifiable
self-check*, which is a fidelity pass and a checkability fail at the same time.

Ranked worst first. File is `plugins/<plugin>/evals/<agent>/evals.json`; the index is scenario then
expectation, zero-based.

| # | Location | Text | Why it fails |
|---|---|---|---|
| 1 | `dev-standards/evals/developer-kotlin` s2 e1 | "Does not overuse apply/run blocks to hide sequencing, and **keeps the flow readable**" | Two unbounded qualifiers in one line. This is the "writes idiomatic code" failure mode verbatim. |
| 2 | `docs-branding/evals/documentation-writer` s2 e1 | "**Tone and depth are set for the operator audience**, not for a developer or an architect" | No operational test. Two graders will disagree on any runbook. |
| 3 | `analysis-architecture/evals/technical-analyst` s1 e2 | "The roadmap is **sequenced by risk, not by ease of fixing**" | The output is consistent with both orderings; the grader must infer intent. |
| 4 | `dev-standards/evals/developer-rust` s0 e1 | "any `clone()` added to silence the borrow checker **without re-examining ownership**" | The motive behind a `clone()` is not readable from the code. |
| 5 | `analysis-architecture/evals/registry-auditor` s1 e1 | "quick wins that are **genuinely scriptable** with a mechanical sed or grep pass" | Requires the grader to independently solve the scriptability question. |
| 6 | `analysis-architecture/evals/software-architect` s0 e2 | "the security dimension is **substantive, not a one liner**" | Faithful copy of `software-architect.md:267`. Uncheckable at source. |
| 7 | `dev-standards/evals/developer-go` s0 e0 | "every error discarded with `_` **where the value is not genuinely meaningless**" | Judgment call embedded in the pass condition. |
| 8 | `dev-standards/evals/developer-go` s0 e1 | "`init()` used for anything **beyond trivial registration**" | "trivial" unbounded. |
| 9 | `dev-standards/evals/developer-csharp` s2 e2 | "Does not introduce a repository abstraction over DbContext **for trivial CRUD**" | "trivial" unbounded, and with `files: []` nothing defines the CRUD. |
| 10 | `dev-standards/evals/developer-rust` s0 e2 | "Flags allocation inside **hot loops**" | Requires a profile that the scenario does not provide. |
| 11 | `docs-branding/evals/presentation-creator` s1 e0 | "...no **implementation detail dump**" | Unbounded; the enumerated slide list in the same entry is fine. |
| 12 | `analysis-architecture/evals/technical-analyst` s1 e1 | "Severity is **justified by business risk rather than by code elegance**" | First clause uncheckable; the P1/P2/P3 clause in the same entry is fine. |
| 13 | `analysis-architecture/evals/registry-auditor` s2 e2 | "Keeps the report under **roughly** 800 lines" | "roughly" turns a countable threshold into a judgment. Drop the word and this passes. |

Two more are checkable but vacuous, because they test a self-report rather than the fact:
`developer-kotlin` s2 e2 ("**States that** ktlint and detekt were applied") and `developer-rust` s1 e1
("**States that** cargo fmt and cargo clippy were run"). An agent that emits the sentence and runs nothing
scores full marks. Both agents have `Bash` in their tool list, so the real thing is observable.

That is 13 hard failures (6.9%) and 2 soft ones. The other 174 clear the bar, several of them
handsomely: `functional-analyst` s0 e1 even supplies the negative exemplar
(*"a testable acceptance criterion (no wording like 'responds quickly')"*), which is how the whole set
should read.

## B2-6. The stated derivation method could only have been applied to 10 of 21 agents

```
python3 -c "
import glob,re,os
E=[os.path.basename(os.path.dirname(p)) for b in ('dev-standards','analysis-architecture','docs-branding') for p in glob.glob(f'plugins/{b}/evals/*/evals.json')]
A={os.path.basename(p)[:-3]:p for p in glob.glob('plugins/*/agents/**/*.md',recursive=True)}
n=0
for a in sorted(E):
    h=re.findall(r'^## (.+)\$',open(A[a]).read(),re.M)
    of=any(x.lower().startswith('output format') for x in h); q=any(x.lower().startswith('quality') for x in h)
    if not (of and q): n+=1; print(f'OutputFormat={of!s:5} Quality={q!s:5} {A[a]}')
print('agents missing one or both:',n,'of',len(E))"
```

11 of 21 agents lack `## Output format`, `## Quality...`, or both:

- Missing both: `developer-csharp`, `developer-go`, `developer-kotlin`, `developer-php`, `developer-python`, `developer-ruby`, `developer-rust`, `documentation-writer`, `wiki-writer`.
- Missing quality only: `orchestrator`, `debugger`.

Eight of the nine `developer-*` agents are in that list. The expectations for them are still mostly
well-grounded, because the commitments live in the frontmatter `description` and in inline standards
sections instead, but the claim that they were derived from `## Output format` and `## Quality criteria`
is false for over half the batch. `developer-python.md` is the clearest case: it carries
`## Standards (summary — expand in v1.0)` and closes with `> **Status**: beta`, so nine expectations were
written against an admittedly incomplete contract.

**Commitments the evals ignore**, from the side-by-side reads (12 agents read against their evals:
`api-designer`, `orchestrator`, `technical-analyst`, `software-architect`, `test-writer`, `developer-java`,
`developer-python`, `developer-frontend`, `developer-go`, `developer-csharp`, `developer-kotlin`,
`developer-rust`, plus `document-creator`, `presentation-creator`, `wiki-writer`, `registry-auditor`
checked for specific claims):

- `api-designer.md:103` self-check 1 (invoke the skill) and 5 ("Does the OpenAPI YAML validate against the 3.1 spec?") are both untested. Item 5 is the most mechanically checkable statement in the whole agent and it was skipped.
- `developer-java.md:147` self-check 3 ("every new service method has a unit test, every new `@Query` has an integration test") is untested, as is the Javadoc half of item 8 and the CORS half of item 7.
- `test-writer.md:113,117` self-check 1 ("Does the test file compile/parse without errors?") and 5 (skills applied) are both untested.
- `developer-python.md` commits to `uv` or `pip-tools` with hash-pinned dependencies and to `from __future__ import annotations`. Neither is tested.
- The heredoc discipline is tested for `developer-csharp`, `developer-go`, `developer-kotlin` and `developer-rust` but **not** for `developer-php` or `developer-ruby`, which carry the identical constraint at `developer-php.md:238` and `developer-ruby.md:187`. Asymmetric for no stated reason.

And an internal contradiction the evals do not probe: `developer-python.md:33` says *"Do NOT use this
agent for: Streamlit UI work"* while `developer-python.md:44` instructs it to load the `streamlit-expert`
skill *"when the task involves a Streamlit application"*. The `developer-python` negative
("Rifai questa UI Streamlit in Angular") tests the Angular boundary, not this one.

## B2-7. Coverage: 26 of 36 `developer-*` pairs have no discriminating test

Confusion matrix over the 9 `developer-*` agents. A pair is covered if at least one negative in either
agent's set names a technology owned by the other.

```
python3 /dev/stdin <<'EOF'
import json,glob,os,re,itertools
CLAIM={'developer-java':r'\b(java|spring boot|junit|jpa|maven)\b','developer-kotlin':r'\b(kotlin|ktor|coroutin\w*|ktlint|detekt)\b',
'developer-csharp':r'(\bc#|\.net|asp\.net|xunit|dbcontext)','developer-go':r'\b(golang|log/slog|goroutine|gofmt)\b|\bgo\b(?!ogle)',
'developer-rust':r'\b(rust|cargo|axum|tokio|thiserror|unwrap)\b','developer-python':r'\b(python|fastapi|pydantic|pytest|django)\b',
'developer-ruby':r'\b(ruby|rails|sidekiq|rspec|rubocop|activerecord)\b','developer-php':r'\b(php|phpstan|symfony|laravel|eloquent)\b',
'developer-frontend':r'\b(angular|react|vue|qwik|tanstack|scss|streamlit)\b'}
D=list(CLAIM); cov=set()
for p in glob.glob('plugins/dev-standards/evals/developer-*/triggers.json'):
    a=os.path.basename(os.path.dirname(p))
    for r in json.load(open(p)):
        if r['should_trigger']: continue
        for b in D:
            if b!=a and re.search(CLAIM[b],r['query'].lower()): cov.add(frozenset((a,b)))
allp={frozenset(x) for x in itertools.combinations(D,2)}
print(f"covered {len(cov)}/{len(allp)}")
for x in sorted(tuple(sorted(y)) for y in allp-cov): print("  MISSING",x)
EOF
```

**Covered, 10 of 36:** csharp/java, csharp/kotlin, frontend/php, frontend/python, frontend/rust,
go/python, go/rust, java/kotlin, php/ruby, python/ruby.

**No discriminating test, 26 of 36.** The ones that matter, in priority order, because the two agents
share idioms or a request vocabulary and a router genuinely confuses them:

| Uncovered pair | Why it is a real risk |
|---|---|
| `developer-java` / `developer-python` | Both own "Scrivi l'`OrderService` con la validazione" shaped requests. `developer-java`'s own positive 0 is language-agnostic once you drop the class name. |
| `developer-kotlin` / `developer-csharp` | Both managed runtimes with coroutines/async, data class versus record, sealed class versus discriminated union. |
| `developer-java` / `developer-frontend` | The pairing the `orchestrator` scenarios use twice ("backend Java and Angular frontend"), never tested at the developer level. |
| `developer-go` / `developer-java` | Both "write an HTTP service with structured logging and context/MDC propagation". |
| `developer-php` / `developer-python` | Both dynamic; both have the identical "fat model to service layer" refactor request, which is `developer-php` positive 1 and `developer-ruby` positive 0. |
| `developer-java` / `developer-rust`, `developer-kotlin` / `developer-rust`, `developer-go` / `developer-kotlin` | Lower risk but untested. |

The remaining 18 uncovered pairs are low risk (`developer-ruby` / `developer-rust` and similar).

Minimum repair: raise the developer sets from 2 to 4 negatives, and require that at least one negative
per agent be *in the agent's own language but out of its role* (a debugging task, a test-only task, or an
API design task). That alone would break Classifier 2 and cover the six high-risk pairs.

## B2-8. Nothing validates any of this

```
grep -c eval .github/scripts/validate_registry.py   # 0
```

`.github/workflows/validate-pr.yml` runs `validate_registry.py --only manifests` and
`claude plugin validate .`, and neither reads `evals.json` or `triggers.json`. Nothing checks the 3x3
shape, that `agent` matches the directory, that the target agent file exists, or that the target agent
file parses. A schema check costing about 20 lines would have caught B2-1 at PR time.

## What I checked and found clean

- **Shape.** 21 agents, 63 scenarios, 189 expectations, exactly 3 per scenario, 0 mismatches between the `agent` field and the directory name. 105 trigger entries, exactly 3 positive and 2 negative for every agent.
- **Duplication.** 1 duplicated expectation string ("No source file is modified, deleted or overwritten", correctly shared by `document-creator` and `presentation-creator`). 0 duplicated scenario queries. 1 trigger query used three times ("Scrivi un endpoint FastAPI con validazione Pydantic": `developer-python` positive, `developer-go` negative, `developer-ruby` negative), consistently labelled and a genuinely good reciprocal test.
- **Annotation leakage.** 0 negatives carry a parenthetical, a naming hint, or a distinguishing `description` string. The defect found in the skill evals is not present here in any form I could measure.
- **Language and length balance.** Positives and negatives are statistically indistinguishable on both axes (61.0 versus 59.3 chars, 9.79 versus 9.52 words, 71% versus 79% Italian).
- **Non-developer trigger sets.** The 24 negatives outside the `developer-*` family are the strongest part of the suite: `orchestrator` rejecting a single-domain bugfix, `registry-auditor` rejecting "write me a new agent" and "run validate_registry.py", `debugger` rejecting "refactor this, there is no bug", `test-writer` rejecting "this test fails with a NullPointerException". These require actual role reasoning and none of them is keyword-separable.
- **JSON validity.** All 42 files parse; no trailing commas, no duplicate keys, no encoding damage.

---

## Send-back summary

| Batch | Verdict | Fraction sent back |
|---|---|---|
| 1, em dash sweep | Mostly sound | 4 of 626 changed lines (0.6%) rewritten, plus 13 missed paths in `decision-patterns.md` and a scope decision to reopen for `agents/` and `references/` |
| 2, agent evals | Not fit to gate a regression | 2 agent files (blocking), 13 of 189 expectations, 17 of 63 scenarios, 9 of 21 trigger sets |

Order of work: B2-1 first, alone, because it is a live breakage. Then B1-5 plus B2-2 together, because
they are the same defect seen from two sides. Then B2-3. Everything else is improvement rather than
repair.
