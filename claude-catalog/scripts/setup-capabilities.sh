#!/usr/bin/env bash
# setup-capabilities.sh
# Installa capability dal claude-registry nel tuo progetto Claude Code.
#
# Utilizzo:
#   ./setup-capabilities.sh                      # installa in $(pwd)
#   ./setup-capabilities.sh /path/to/my-project  # installa nel progetto indicato
#   ./setup-capabilities.sh /path/to/project all # installa tutte le stable senza interazione

set -euo pipefail

# ── Colori ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
RED='\033[0;31m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

# ── Percorsi ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MARKETPLACE_ROOT="$REGISTRY_ROOT/claude-marketplace"
CATALOG="$MARKETPLACE_ROOT/catalog.json"

PROJECT_DIR="${1:-$(pwd)}"
SELECTION="${2:-}"

AGENTS_DIR="$PROJECT_DIR/.claude/agents"
SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"

# ── Controlli preliminari ────────────────────────────────────────────────────
if [[ ! -f "$CATALOG" ]]; then
  echo -e "${RED}Errore:${RESET} catalog.json non trovato: $CATALOG"
  exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo -e "${RED}Errore:${RESET} directory progetto non trovata: $PROJECT_DIR"
  exit 1
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     Claude Registry — Setup Capabilities     ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Registry:  ${DIM}$REGISTRY_ROOT${RESET}"
echo -e "  Progetto:  ${CYAN}$PROJECT_DIR${RESET}"
echo ""

# ── Leggi catalog.json (scrivi su file temporaneo per evitare quoting issues) ──
CATALOG_TMP=$(mktemp /tmp/claude-catalog-XXXXXX.json)
python3 -c "
import json
with open('$CATALOG') as f:
    data = json.load(f)
# Escludi campi interni e le skill (installate come dipendenze, non come scelte primarie)
caps = [c for c in data.get('capabilities', [])
        if not any(k.startswith('_') for k in c)
        and c.get('type', 'agent') == 'agent']
with open('$CATALOG_TMP', 'w') as out:
    json.dump(caps, out)
"
trap "rm -f $CATALOG_TMP" EXIT

N=$(python3 -c "import json; print(len(json.load(open('$CATALOG_TMP'))))")

if [[ "$N" -eq 0 ]]; then
  echo -e "${YELLOW}Nessuna capability trovata nel catalog.${RESET}"
  exit 0
fi

# ── Mostra lista ──────────────────────────────────────────────────────────────
echo -e "${BOLD}Capability disponibili:${RESET}"
echo ""
echo -e "  ${DIM}Num  Tier    Nome                           Descrizione${RESET}"
echo -e "  ${DIM}───  ──────  ─────────────────────────────  ────────────────────────────────────────${RESET}"

python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for i, c in enumerate(caps, 1):
    tier = c.get('tier','?')
    name = c.get('name','?')
    desc = c.get('description','')
    desc = ' '.join(desc.split())[:55]
    deps = c.get('dependencies', [])
    tier_color = '\033[0;32m' if tier == 'stable' else '\033[1;33m'
    reset = '\033[0m'
    dep_str = f' \033[2m[uses: {chr(44).join(deps)}]\033[0m' if deps else ''
    print(f'  {i:3}  {tier_color}{tier:<6}{reset}  {name:<29}  {desc}...{dep_str}')
"

echo ""
echo -e "  ${DIM}Digita i numeri separati da spazio, oppure:${RESET}"
echo -e "  ${CYAN}all${RESET}  — installa tutte le ${GREEN}stable${RESET}"
echo -e "  ${CYAN}q${RESET}    — esci"
echo ""

if [[ -n "$SELECTION" ]]; then
  echo -e "  Selezione automatica: ${CYAN}$SELECTION${RESET}"
else
  read -rp "  Selezione: " SELECTION
fi

if [[ "$SELECTION" == "q" || -z "$SELECTION" ]]; then
  echo "Uscita."
  exit 0
fi

# ── Crea directory ────────────────────────────────────────────────────────────
mkdir -p "$AGENTS_DIR"

INSTALLED=()

# ── Installa capability selezionate ──────────────────────────────────────────
echo ""
echo -e "${BOLD}Installazione:${RESET}"
echo ""

install_capability() {
  local name="$1" tier="$2" is_dep="${3:-}"
  local src

  # Skill: cercano in marketplace/skills/, agenti in marketplace/{tier}/
  if [[ "$tier" == "skill" ]]; then
    src="$MARKETPLACE_ROOT/skills/$name.md"
  else
    src="$MARKETPLACE_ROOT/$tier/$name.md"
  fi

  local dst="$AGENTS_DIR/$name.md"

  if [[ ! -f "$src" ]]; then
    echo -e "  ${RED}✗${RESET} $name — file sorgente non trovato ($src)"
    return 1
  fi

  if [[ -f "$dst" ]]; then
    [[ -z "$is_dep" ]] && echo -e "  ${YELLOW}↺${RESET} $name — già presente, sovrascritto" || true
  else
    if [[ -n "$is_dep" ]]; then
      echo -e "  ${CYAN}↳${RESET} $name ${DIM}[skill — dipendenza]${RESET}"
    else
      echo -e "  ${GREEN}✓${RESET} $name ${DIM}[$tier]${RESET}"
    fi
  fi

  cp "$src" "$dst"
  INSTALLED+=("$name")

  # ── Risolvi dipendenze ───────────────────────────────────────────────────────
  python3 - "$name" "$CATALOG" <<'DEPEOF'
import json, sys
name = sys.argv[1]
catalog_path = sys.argv[2]
all_caps = json.load(open(catalog_path)).get('capabilities', [])
cap = next((c for c in all_caps if c.get('name') == name), None)
if cap:
    for dep in cap.get('dependencies', []):
        dep_cap = next((c for c in all_caps if c.get('name') == dep), None)
        if dep_cap:
            tier = dep_cap.get('tier', 'skill') if dep_cap.get('type') == 'skill' else dep_cap.get('tier', 'beta')
            print(f"{dep}|{tier}")
DEPEOF
  while IFS='|' read -r dep_name dep_tier; do
    [[ -z "$dep_name" ]] && continue
    if [[ ! -f "$AGENTS_DIR/$dep_name.md" ]]; then
      install_capability "$dep_name" "$dep_tier" "dep"
    fi
  done < <(python3 - "$name" "$CATALOG" <<'DEPEOF2'
import json, sys
name = sys.argv[1]
catalog_path = sys.argv[2]
all_caps = json.load(open(catalog_path)).get('capabilities', [])
cap = next((c for c in all_caps if c.get('name') == name), None)
if cap:
    for dep in cap.get('dependencies', []):
        dep_cap = next((c for c in all_caps if c.get('name') == dep), None)
        if dep_cap:
            t = 'skill' if dep_cap.get('type') == 'skill' else dep_cap.get('tier', 'beta')
            print(f"{dep}|{t}")
DEPEOF2
)
}

if [[ "$SELECTION" == "all" ]]; then
  while IFS='|' read -r name tier; do
    [[ "$tier" == "stable" ]] && install_capability "$name" "$tier"
  done < <(python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for c in caps:
    print(c['name'] + '|' + c['tier'])
")
else
  # Scrivi la mappa num→name|tier su un file temporaneo
  CAPMAP_TMP=$(mktemp /tmp/claude-capmap-XXXXXX.sh)
  python3 -c "
import json
caps = json.load(open('$CATALOG_TMP'))
for i, c in enumerate(caps, 1):
    name = c['name'].replace(\"'\", '')
    tier = c['tier'].replace(\"'\", '')
    print(f\"CAP_{i}_NAME='{name}'\")
    print(f\"CAP_{i}_TIER='{tier}'\")
print(f'CAP_TOTAL={len(caps)}')
" > "$CAPMAP_TMP"
  # shellcheck source=/dev/null
  source "$CAPMAP_TMP"
  rm -f "$CAPMAP_TMP"

  for num in $SELECTION; do
    name_var="CAP_${num}_NAME"
    tier_var="CAP_${num}_TIER"
    if [[ -n "${!name_var:-}" ]]; then
      install_capability "${!name_var}" "${!tier_var}"
    else
      echo -e "  ${RED}✗${RESET} Numero non valido: $num (max: $CAP_TOTAL)"
    fi
  done
fi

# ── Aggiorna settings.json ────────────────────────────────────────────────────
if [[ ${#INSTALLED[@]} -gt 0 ]]; then
  echo ""
  echo -e "${BOLD}Aggiornamento .claude/settings.json:${RESET}"

  python3 - "$SETTINGS_FILE" "${INSTALLED[@]}" <<'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
new_agents = sys.argv[2:]

if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

perms = settings.setdefault("permissions", {})
allow = perms.setdefault("allow", [])

added = []
for agent in new_agents:
    rule = f"Agent({agent})"
    if rule not in allow:
        allow.append(rule)
        added.append(rule)

settings_path.parent.mkdir(parents=True, exist_ok=True)
settings_path.write_text(json.dumps(settings, indent=2) + "\n")

if added:
    print(f"  Aggiunte {len(added)} regole Agent a settings.json")
else:
    print("  settings.json già aggiornato — nessuna modifica necessaria")
PYEOF
fi

# ── Riepilogo ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  Completato: ${#INSTALLED[@]} capability installate${RESET}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Directory: ${CYAN}$AGENTS_DIR${RESET}"
echo ""
echo -e "${BOLD}Prossimi passi:${RESET}"
echo ""
echo -e "  1. Aggiungi le capability a git del tuo progetto:"
echo -e "     ${DIM}cd $PROJECT_DIR${RESET}"
echo -e "     ${DIM}git add .claude/ && git commit -m 'add: claude capabilities'${RESET}"
echo ""
echo -e "  2. Apri Claude Code nella directory del progetto"
echo ""
echo -e "  3. Verifica con ${CYAN}/agents${RESET} che le capability siano visibili"
echo ""
