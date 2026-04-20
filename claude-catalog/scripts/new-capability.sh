#!/usr/bin/env bash
# new-capability.sh
# Scaffolda una nuova capability nel claude-catalog e crea il branch git.
#
# Utilizzo:
#   ./new-capability.sh                           # chiede il nome interattivamente
#   ./new-capability.sh api-security-reviewer     # agente con il nome fornito
#   ./new-capability.sh --type skill skill-name   # skill con il nome fornito

set -euo pipefail

# ── Colori ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

# ── Percorsi ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CATALOG_ROOT="$REGISTRY_ROOT/claude-catalog"

cd "$REGISTRY_ROOT"

# ── Input ────────────────────────────────────────────────────────────────────
TYPE="agent"
NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)
      TYPE="${2:-}"
      shift 2
      ;;
    *)
      NAME="$1"
      shift
      ;;
  esac
done

if [[ "$TYPE" != "agent" && "$TYPE" != "skill" ]]; then
  echo -e "${RED}Errore:${RESET} --type deve essere 'agent' o 'skill'. Ricevuto: '$TYPE'"
  exit 1
fi

echo ""
if [[ "$TYPE" == "skill" ]]; then
  echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}║    Claude Registry — Nuova Skill             ║${RESET}"
  echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
else
  echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}║    Claude Registry — Nuova Capability        ║${RESET}"
  echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
fi
echo ""

if [[ -z "$NAME" ]]; then
  echo -e "  Il nome deve essere: ${CYAN}lowercase${RESET}, solo lettere e trattini."
  if [[ "$TYPE" == "skill" ]]; then
    echo -e "  Esempi: ${DIM}java-spring-standards, rest-api-standards, brand-guidelines${RESET}"
  else
    echo -e "  Esempi: ${DIM}api-security-reviewer, data-migration-specialist, event-designer${RESET}"
  fi
  echo ""
  read -rp "  Nome: " NAME
fi

# ── Validazione nome ──────────────────────────────────────────────────────────
if ! echo "$NAME" | grep -qE '^[a-z][a-z0-9-]+$'; then
  echo -e "${RED}Errore:${RESET} '$NAME' non è valido."
  echo "  Usa solo lettere minuscole, cifre e trattini. Es: api-security-reviewer"
  exit 1
fi

TARGET_DIR="$CATALOG_ROOT/agents"
[[ "$TYPE" == "skill" ]] && TARGET_DIR="$CATALOG_ROOT/skills"

if [[ -f "$TARGET_DIR/$NAME.md" ]]; then
  echo -e "${YELLOW}La capability '$NAME' esiste già in ${TARGET_DIR}.${RESET}"
  echo ""
  echo -e "  Edita direttamente:"
  echo -e "    ${CYAN}\$EDITOR $TARGET_DIR/$NAME.md${RESET}"
  exit 1
fi

BRANCH_NAME="add/$NAME"

echo -e "  Tipo:       ${CYAN}$TYPE${RESET}"
echo -e "  Nome:       ${CYAN}$NAME${RESET}"
echo -e "  Branch:     ${CYAN}$BRANCH_NAME${RESET}"
echo -e "  Directory:  ${DIM}$TARGET_DIR${RESET}"
echo ""

# ── Verifica stato git ────────────────────────────────────────────────────────
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo -e "${YELLOW}Attenzione:${RESET} sei su branch '$CURRENT_BRANCH', non su main."
  read -rp "  Vuoi procedere comunque? [y/N] " CONFIRM
  [[ "$CONFIRM" =~ ^[Yy]$ ]] || exit 0
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  echo -e "${YELLOW}Branch '$BRANCH_NAME' già esistente.${RESET} Faccio checkout."
  git checkout "$BRANCH_NAME"
else
  git checkout -b "$BRANCH_NAME"
fi

echo ""
echo -e "${BOLD}Creazione file:${RESET}"
echo ""

# ── Crea capability file ──────────────────────────────────────────────────────
CAPABILITY_FILE="$TARGET_DIR/$NAME.md"

if [[ "$TYPE" == "skill" ]]; then
  mkdir -p "$TARGET_DIR"
  cat > "$CAPABILITY_FILE" <<SKILLEOF
---
name: $NAME
description: >
  Use to retrieve TODO — descrivi i contenuti della skill in modo preciso.
  Inizia con "Use to retrieve" e elenca i topic coperti.
tools: Read
model: haiku
color: cyan
---

## Role

You are a knowledge provider for [domain] standards. When invoked, return the
complete and authoritative standards relevant to the caller's task.

Do not take any actions. Do not write or modify files. Return knowledge only.

---

## [Topic 1]

TODO — contenuto della prima sezione di standard.

---

## [Topic 2]

TODO — contenuto della seconda sezione.
SKILLEOF

  echo -e "  ${GREEN}✓${RESET} $CAPABILITY_FILE"
else
  cat > "$CAPABILITY_FILE" <<AGENTEOF
---
name: $NAME
description: >
  Use when TODO — descrivi la condizione di trigger in modo preciso.
  Inizia con "Use when" e indica i task specifici che questo subagent gestisce.
  Indica anche cosa NON fa (se c'è un'altra capability per quello).
tools: Read, Grep, Glob
model: sonnet
color: blue
---

## Role

TODO: Definisci il ruolo. Inizia con "You are a senior..."
Chi è questo subagent? Su cosa è autorevole?

---

## What you always do

- TODO: elenca i comportamenti obbligatori (presenti in ogni interazione)
- Leggi i file rilevanti prima di analizzare
- Cita sempre evidence (file:riga, valore di configurazione) per ogni finding
- ...

## What you never do

- TODO: elenca le proibizioni esplicite
- Non scrivere codice implementativo (delega ai developer subagent)
- ...

## Output format

TODO: Definisci il formato di output esatto.
Sii specifico: nomi delle sezioni, colonne delle tabelle, campi obbligatori.

Esempio:

\`\`\`
## Report — {Titolo}

### Findings

| # | Finding | Severity | Evidence |
|---|---------|----------|----------|
| 1 | ... | High | file.java:42 |

### Raccomandazioni
...
\`\`\`

## Quality self-check before responding

Prima di rispondere, verifica:
1. TODO: aggiungi controlli di qualità che il subagent deve fare sul proprio output
2. Ho letto i file rilevanti o sto lavorando da assunzioni?
3. Ogni finding è ancorato a evidence specifica?
AGENTEOF

  echo -e "  ${GREEN}✓${RESET} $CAPABILITY_FILE"
fi

# ── Crea example file ─────────────────────────────────────────────────────────
EXAMPLE_FILE="$CATALOG_ROOT/examples/$NAME-example.md"
cat > "$EXAMPLE_FILE" <<EXEOF
# Example: $NAME

## Scenario 1: TODO — Happy path (scenario tipico)

**Setup**: TODO — descrivi il contesto da fornire (file da leggere, informazioni da dare)

**User prompt**:
> TODO — scrivi il prompt esatto da inviare

**Expected output characteristics**:
- TODO — cosa deve apparire nell'output
- TODO — formato che deve essere rispettato
- TODO — comportamento obbligatorio

**Must NOT contain**:
- TODO — anti-pattern da verificare

---

## Scenario 2: TODO — Edge case o errore

**Setup**: TODO

**User prompt**:
> TODO

**Expected output characteristics**:
- TODO

**Must NOT contain**:
- TODO
EXEOF

echo -e "  ${GREEN}✓${RESET} $EXAMPLE_FILE"

# ── Crea eval file ────────────────────────────────────────────────────────────
EVAL_FILE="$CATALOG_ROOT/evals/$NAME-eval.md"
cat > "$EVAL_FILE" <<EVALEOF
# Evals: $NAME

Usa questi scenari per verificare che la capability si comporti correttamente
prima di aprire una PR e prima di ogni release.

---

## Eval-001: Happy path

**Input context**: TODO — descrivi i file da fornire o il contesto della sessione

**User prompt**: "TODO — prompt esatto"

**Expected output characteristics**:
- TODO
- Il formato di output rispetta quanto definito nella sezione "Output format"
- Tutti i finding sono ancorati a evidence

**Must NOT contain**:
- Raccomandazioni senza evidence
- Codice implementativo (se il subagent non dovrebbe scrivere codice)

**How to run**:
1. Apri Claude Code in una directory di test
2. Copia il file in \`.claude/agents/$NAME.md\`
3. Fornisci il contesto descritto e invia il prompt
4. Verifica che l'output rispetti le caratteristiche attese

---

## Eval-002: Missing context

**Input context**: Nessun file fornito, solo il prompt

**User prompt**: "TODO — stesso prompt del Eval-001"

**Expected behavior**:
- Il subagent chiede il contesto mancante prima di procedere
- Non produce output basato su assunzioni non dichiarate

---

## Eval-003: Edge case — TODO

**Input context**: TODO

**User prompt**: "TODO"

**Expected output characteristics**:
- TODO
EVALEOF

echo -e "  ${GREEN}✓${RESET} $EVAL_FILE"

# ── Aggiorna CHANGELOG.md ─────────────────────────────────────────────────────
CHANGELOG="$CATALOG_ROOT/CHANGELOG.md"
if [[ -f "$CHANGELOG" ]]; then
  # Check if [Unreleased] section already has entries for this capability
  if grep -q "$NAME" "$CHANGELOG" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${RESET} CHANGELOG.md contiene già '$NAME' — non modificato"
  else
    # Aggiungi entry sotto [Unreleased]
    # Usa Python per inserimento preciso
    python3 - "$CHANGELOG" "$NAME" <<'PYEOF'
import sys, re
path = sys.argv[1]
name = sys.argv[2]
content = open(path).read()

# Find [Unreleased] and insert after it
pattern = r'(## \[Unreleased\])'
replacement = f'\\1\n\n### Added\n- `{name}@0.1.0` — TODO: descrizione di una riga (draft)'

# Only add if not already present
if name not in content:
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content != content:
        open(path, 'w').write(new_content)
        print(f"  ✓ CHANGELOG.md aggiornato con voce per '{name}'")
    else:
        print(f"  ⚠ Sezione [Unreleased] non trovata in CHANGELOG.md — aggiorna manualmente")
PYEOF
  fi
fi

# ── Riepilogo e istruzioni ────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  Scaffolding completato per: $NAME ($TYPE)${RESET}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "${BOLD}Prossimi passi:${RESET}"
echo ""
echo -e "  ${BOLD}1. Scrivi il contenuto${RESET}"
echo -e "     ${CYAN}\$EDITOR $CAPABILITY_FILE${RESET}"
echo -e "     ${DIM}Sostituisci tutti i TODO con contenuto reale.${RESET}"
echo -e "     ${DIM}Leggi claude-catalog/how-to-write-a-capability.md per la guida completa.${RESET}"
echo ""
echo -e "  ${BOLD}2. Completa gli eval${RESET}"
echo -e "     ${CYAN}\$EDITOR $EVAL_FILE${RESET}"
echo -e "     ${DIM}Almeno 2 scenari reali prima di aprire la PR.${RESET}"
echo ""
echo -e "  ${BOLD}3. Testa localmente${RESET}"
echo -e "     ${DIM}cp $CAPABILITY_FILE /path/to/project/.claude/agents/${RESET}"
echo -e "     ${DIM}Apri Claude Code e prova il subagent con scenari reali.${RESET}"
echo ""
if [[ "$TYPE" == "skill" ]]; then
  echo -e "  ${BOLD}3b. Aggiorna catalog.json${RESET}"
  echo -e "     ${DIM}Aggiungi la voce skill in claude-marketplace/catalog.json.${RESET}"
  echo -e "     ${DIM}Aggiungi '$NAME' nelle 'dependencies' degli agenti che la useranno.${RESET}"
  echo -e "     ${DIM}Aggiungi una sezione '## Skills' agli agenti che la usano.${RESET}"
  echo ""
fi
echo -e "  ${BOLD}4. Apri la Pull Request${RESET}"
echo -e "     ${DIM}git add -A${RESET}"
echo -e "     ${DIM}git commit -m 'add: $NAME $TYPE (draft)'${RESET}"
echo -e "     ${DIM}git push origin $BRANCH_NAME${RESET}"
echo -e "     ${DIM}gh pr create --title 'add: $NAME' --body 'Aggiunge la $TYPE $NAME'${RESET}"
echo ""
echo -e "  ${BOLD}5. Rispondi alla review automatica${RESET}"
echo -e "     ${DIM}GitHub Actions posterà un commento con eventuali errori da correggere.${RESET}"
echo ""
