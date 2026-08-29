# Deliberation — trigger lexicon

Authoritative lexicon used by `deliberative-decision-engine` Step 0 to
detect whether the user is explicitly asking for multi-agent
deliberation. Conservative by design: false negatives cost the user
one extra utterance ("decidi con dibattito"); false positives degrade
trust by hijacking routine answers.

The detector returns:

```json
{
  "deliberativeModeRequested": true,
  "matchedTriggers": ["dibattito", "critica"],
  "confidence": 0.92,
  "source": "user_prose"
}
```

`confidence < 0.7` ⇒ ask one focused clarifying question, do not
auto-trigger.

## Italian triggers (high signal)

Match the **stem** as a whole word; match exact phrase where listed.

| Trigger | Type | Notes |
|---|---|---|
| `decidi con dibattito` | exact phrase | Strongest signal. |
| `usa il dibattito` / `usa modalità dibattito` | exact phrase | Strong. |
| `usa multi-agente` / `multi agente` / `multi-agente` | substring | Strong. |
| `più agenti` | substring (whole word) | Strong when paired with a decision verb (decidi, scegli, valuta). |
| `fai criticare la decisione` / `critica questa decisione` | exact phrase | Strong. |
| `challenge` / `rebuttal` | substring | Strong (English loan, common in IT IT teams). |
| `red team` / `red-team` | substring | Strong. |
| `fammi una decisione robusta` / `decisione robusta` | substring | Strong. |
| `valuta pro e contro` | substring | Medium-strong (paired with a decision verb is strong). |
| `fammi decidere con più prospettive` / `con più prospettive` | substring | Strong. |
| `discuti pro e contro` | substring | Medium. |
| `simula un dibattito` | substring | Strong. |
| `fai un dibattito` | substring | Strong. |

## English triggers (high signal)

| Trigger | Type | Notes |
|---|---|---|
| `debate mode` | exact phrase | Strongest. |
| `multi-agent debate` / `multi agent debate` | substring | Strongest. |
| `deliberative decision` | substring | Strong. |
| `critic` (with decision verb) | substring | Medium — must co-occur with "decision" / "choice" / "recommendation". |
| `challenge` / `rebuttal` (with decision verb) | substring | Medium-strong. |
| `red team` / `red-team` (with decision verb) | substring | Strong. |
| `decision review` | substring | Strong. |
| `robust decision` | substring | Strong. |
| `do a debate` / `run a debate` / `have a debate` | substring | Strong. |
| `peer review my decision` / `pressure-test this decision` | substring | Strong. |

## Programmatic flag

If the dispatch JSON contains any of the following, skip prose
detection and treat as confirmed:

```json
{ "decisionMode": "deliberative" }
{ "useDeliberativeDecision": true }
{ "deliberationPolicy": { "enabled": true, ... } }
```

## False-positive guards (do NOT auto-trigger)

These phrases contain trigger lemmas but are NOT decision requests:

| Utterance | Why it is not a trigger |
|---|---|
| "the team is critical of the design" | "critical" used as adjective, not request |
| "we should debate this later" | future-tense planning, not a current request |
| "she's a critic of monoliths" | descriptive, not directive |
| "let me play devil's advocate for a sec" | informal, single-speaker |
| "what's the rebuttal to this argument?" | asking for a rebuttal text, not a deliberation |
| "the multi-agent system we built last quarter" | descriptive reference to a prior system |
| "il dibattito politico" / "il critico letterario" | unrelated semantic field |

## Confidence scoring

Start at 0.0. Add per match:

- exact-phrase match from the strongest list (`decidi con dibattito`,
  `debate mode`, `multi-agent debate`, `deliberative decision`,
  `decision review`, `robust decision`, `fammi una decisione robusta`):
  +0.7
- exact-phrase match from medium list: +0.4
- substring match from medium list co-occurring with a decision verb
  (`decidi`, `scegli`, `valuta`, `decide`, `choose`, `evaluate`): +0.4
- substring match without a decision verb: +0.2
- a false-positive-guard phrase containing the same lemma: −0.5
- programmatic flag in dispatch JSON: set confidence = 1.0

Cap at 1.0. Decision threshold: `>= 0.7` ⇒ auto-trigger; `0.4–0.7` ⇒
ask one focused clarifying question; `< 0.4` ⇒ standard answer.

## Examples

| Utterance | Match | Confidence | Action |
|---|---|---|---|
| "Decidi con dibattito quale strategia di migrazione usare." | `decidi con dibattito` (0.7) + `decidi` decision verb implicit | 0.9 | trigger |
| "Use multi-agent debate before selecting the target architecture." | `multi-agent debate` (0.7) + `selecting` decision verb | 0.95 | trigger |
| "fai criticare la decisione prima di finalizzarla" | `fai criticare la decisione` (0.7) + `decisione` decision verb | 0.9 | trigger |
| "debate this with the team please" | `debate` substring, no decision verb, single-speaker context | 0.2 | standard |
| "The critic in our last review caught a bug" | descriptive, false-positive guard | 0.0 | standard |
| `decisionMode: deliberative` in dispatch JSON | programmatic flag | 1.0 | trigger |
| "valuta pro e contro tra Kafka e RabbitMQ" | `valuta pro e contro` (0.4) + `valuta` decision verb (0.4) | 0.8 | trigger |
| "vorrei pesare i pro e contro di Kafka, ma non ora" | matches `pro e contro` but future-conditional reduces confidence | 0.4 | clarify |
