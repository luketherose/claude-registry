#!/usr/bin/env bash
# Sincronizza le skill dei plugin (la fonte) verso il twin tree Gemini committato
# in questo stesso repository (il derivato), in gemini/extensions/<plugin>/skills/.
#
# Sostituisce i symlink, che sull'host di consegna (VDI Windows, Git Bash) non
# esistono: ln -s produce una copia silenziosa. Topologia e razionale in
# docs/gemini-twin/twin-registry-plan.md sezione 3.
#
#   sync-gemini-extension.sh                  sincronizza i plugin in scope
#   sync-gemini-extension.sh --check          non scrive, esce 1 se divergono
#   sync-gemini-extension.sh --prune          rimuove anche le skill orfane
#   sync-gemini-extension.sh --init           crea il manifest per un plugin che non ce l'ha
#   sync-gemini-extension.sh --plugins a,b    sottoinsieme di plugin
#
# Non tocca MAI agents/: quelli passano dal porter, non da qui.

set -euo pipefail

R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGINS="dev-standards docs-branding analysis-architecture deliberation"
MODE="sync"; PRUNE=0; INIT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --check)   MODE="check" ;;
    --prune)   PRUNE=1 ;;
    --init)    INIT=1 ;;
    --plugins) PLUGINS="$(printf '%s' "$2" | tr ',' ' ')"; shift ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "opzione non riconosciuta: $1" >&2; exit 2 ;;
  esac
  shift
done

diverged=0; t_ok=0; t_upd=0; t_new=0; t_orph=0

for p in $PLUGINS; do
  src_dir="$R/plugins/$p/skills"
  ext_dir="$R/gemini/extensions/$p"
  [ -d "$src_dir" ] || { echo "[$p] nessuna skill nella fonte, salto"; continue; }

  if [ ! -f "$ext_dir/gemini-extension.json" ]; then
    if [ "$INIT" -eq 1 ] && [ "$MODE" != "check" ]; then
      mkdir -p "$ext_dir"
      printf '{\n  "name": "%s",\n  "version": "0.1.0",\n  "description": "Gemini CLI twin of the %s plugin"\n}\n' "$p" "$p" > "$ext_dir/gemini-extension.json"
      echo "[$p] manifest creato (name uguale al nome directory, come richiede il manifest)"
    else
      echo "[$p] ERRORE: manca gemini-extension.json. Il manifest e materiale di fonte gemini,"
      echo "     non lo genero di nascosto: rilancia con --init, o crealo con 'gemini extensions new'."
      diverged=1; continue
    fi
  fi

  dst_dir="$ext_dir/skills"
  mkdir -p "$dst_dir"
  declare -a seen=()

  while IFS= read -r src; do
    name="$(basename "$src")"; [ -n "$name" ] || continue
    seen+=("$name"); dst="$dst_dir/$name"

    if find "$src" -name 'GEMINI.user.md' -o -name '.env' | grep -q .; then
      echo "[$p] RIFIUTATA  $name (contiene un file che non va distribuito)"; diverged=1; continue
    fi

    if [ ! -d "$dst" ]; then
      if [ "$MODE" = "check" ]; then echo "[$p] ASSENTE    $name"; diverged=1
      else cp -R "$src" "$dst"; echo "[$p] NUOVA      $name"; fi
      t_new=$((t_new+1))
    elif diff -r -q "$src" "$dst" >/dev/null 2>&1; then
      t_ok=$((t_ok+1))
    else
      if [ "$MODE" = "check" ]; then echo "[$p] DIVERGE    $name"; diverged=1
      else
        case "$dst" in "$dst_dir"/?*) rm -rf "$dst" ;; *) echo "path sospetto: $dst" >&2; exit 2 ;; esac
        cp -R "$src" "$dst"; echo "[$p] AGGIORNATA $name"
      fi
      t_upd=$((t_upd+1))
    fi
  done < <(find "$src_dir" -mindepth 1 -maxdepth 1 -type d | sort)

  while IFS= read -r d; do
    name="$(basename "$d")"; found=0
    for s in ${seen[@]+"${seen[@]}"}; do [ "$s" = "$name" ] && found=1 && break; done
    if [ "$found" -eq 0 ]; then
      t_orph=$((t_orph+1))
      if [ "$PRUNE" -eq 1 ] && [ "$MODE" != "check" ]; then
        case "$d" in "$dst_dir"/?*) rm -rf "$d"; echo "[$p] RIMOSSA    $name (orfana)" ;; esac
      else
        echo "[$p] ORFANA     $name (non e piu nella fonte; --prune per rimuoverla)"; diverged=1
      fi
    fi
  done < <(find "$dst_dir" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
  unset seen
done

echo "---"
echo "fonte:  $R/plugins  (plugin: $PLUGINS)"
echo "twin:   $R/gemini/extensions/<plugin>/skills"
echo "modo:   $MODE"
printf "allineate %s, aggiornate %s, nuove %s, orfane %s\n" "$t_ok" "$t_upd" "$t_new" "$t_orph"
echo "skill nel twin: $(find "$R/gemini/extensions" -mindepth 3 -maxdepth 3 -type d -path '*/skills/*' 2>/dev/null | wc -l | tr -d ' ')"
echo "agents/ non toccata: $(find "$R/gemini/extensions" -path '*/agents/*.md' 2>/dev/null | wc -l | tr -d ' ') file"

if [ "$MODE" = "check" ] && [ "$diverged" -ne 0 ]; then echo "ESITO: DIVERGENTI"; exit 1; fi
echo "ESITO: allineati"
