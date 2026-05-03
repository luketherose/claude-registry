# Logic-translator — output / reporting templates

> Reference doc for `logic-translator`. Read at runtime when assembling
> the supervisor-facing report. The agent body keeps the canonical list
> of paths under `## Outputs`; this doc holds the full markdown reporting
> skeleton.

## Reporting skeleton

```markdown
## Files written / edited
- <backend-dir>/src/main/java/.../<bc>/application/<Aggregate>Service.java
  (filled <N> method bodies for UC-NN)
- <backend-dir>/src/main/java/.../<bc>/domain/<Entity>.java
  (added <N> state-transition methods)

## Translation summary
- UC handled:        UC-NN
- Mode:              full | scaffold-todo | structural
- AS-IS source(s):   <list of files:lines read>
- Methods filled:    <N>
- TODO markers left: <N>  (in scaffold-todo mode)
- State transitions: <N>
- Validation rules from implicit-logic translated: <N> (IL-NN refs)
- Phase 3 baseline test: green-expected | xfail-expected (BUG-NN)

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- ...
```
