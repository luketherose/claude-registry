#!/usr/bin/env bash
# present.sh
# CLI shortcut to invoke presentation-creator or document-creator via Claude Code.
#
# Usage:
#   ./present.sh [OPTIONS] [DOCS...]
#
# Options:
#   --type  pptx|pdf|docx   Output format (default: pptx)
#   --audience  biz|tech    Target audience (default: biz)
#   --project   NAME        Project name (inferred from dir if omitted)
#   --output    FILE        Output file path (default: ./output/<project>.<type>)
#
# Examples:
#   ./present.sh ./estimation/
#   ./present.sh --type pdf --audience tech ./estimation/
#   ./present.sh --type pptx --audience biz --project "Portal Modernization" --output ~/Desktop/deck.pptx ./docs/

set -euo pipefail

GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

# ── Defaults ──────────────────────────────────────────────────────────────────
TYPE="pptx"
AUDIENCE="biz"
PROJECT=""
OUTPUT=""
DOCS=()

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --type)      TYPE="$2";      shift 2 ;;
    --audience)  AUDIENCE="$2";  shift 2 ;;
    --project)   PROJECT="$2";   shift 2 ;;
    --output)    OUTPUT="$2";    shift 2 ;;
    --help|-h)
      sed -n '2,20p' "$0" | grep '^#' | sed 's/^# \?//'
      exit 0
      ;;
    *)
      DOCS+=("$1")
      shift
      ;;
  esac
done

# ── Validate ──────────────────────────────────────────────────────────────────
if [[ ${#DOCS[@]} -eq 0 ]]; then
  echo "Error: specify at least one document file or directory."
  echo "  Usage: $0 [--type pptx|pdf|docx] [--audience biz|tech] <docs...>"
  exit 1
fi

case "$TYPE" in
  pptx|pdf|docx) ;;
  *) echo "Error: --type must be pptx, pdf, or docx. Got: $TYPE"; exit 1 ;;
esac

case "$AUDIENCE" in
  biz|tech) ;;
  *) echo "Error: --audience must be biz or tech. Got: $AUDIENCE"; exit 1 ;;
esac

# ── Infer project name if not provided ────────────────────────────────────────
if [[ -z "$PROJECT" ]]; then
  # use the first doc's parent dir name
  FIRST_DOC="${DOCS[0]}"
  if [[ -d "$FIRST_DOC" ]]; then
    PROJECT="$(basename "$(realpath "$FIRST_DOC")")"
  else
    PROJECT="$(basename "$(dirname "$(realpath "$FIRST_DOC")")")"
  fi
fi

# ── Default output path ───────────────────────────────────────────────────────
if [[ -z "$OUTPUT" ]]; then
  mkdir -p "./output"
  SAFE_NAME="${PROJECT// /-}"
  OUTPUT="./output/${SAFE_NAME}.${TYPE}"
fi

OUTPUT="$(realpath -m "$OUTPUT")"

# ── Build docs list string ────────────────────────────────────────────────────
DOCS_STR=""
for d in "${DOCS[@]}"; do
  DOCS_STR+="$(realpath "$d") "
done
DOCS_STR="${DOCS_STR% }"

# ── Select agent ─────────────────────────────────────────────────────────────
if [[ "$TYPE" == "pptx" ]]; then
  AGENT="presentation-creator"
else
  AGENT="document-creator"
fi

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║     Claude Registry — Present               ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Agent:    ${CYAN}$AGENT${RESET}"
echo -e "  Type:     ${CYAN}$TYPE${RESET}"
echo -e "  Audience: ${CYAN}$AUDIENCE${RESET}"
echo -e "  Project:  ${CYAN}$PROJECT${RESET}"
echo -e "  Output:   ${CYAN}$OUTPUT${RESET}"
echo -e "  Sources:  ${DIM}$DOCS_STR${RESET}"
echo ""

# ── Build Claude prompt ───────────────────────────────────────────────────────
PROMPT="Use the ${AGENT} agent.

Project name: ${PROJECT}
Target audience: ${AUDIENCE} ($([ "$AUDIENCE" = "biz" ] && echo "business — concise, minimal jargon" || echo "technical — full architecture and patterns"))
Output type: ${TYPE}
Output path: ${OUTPUT}

Source documents to read:
${DOCS_STR}

Read all the source documents listed above, then produce the ${TYPE} output at ${OUTPUT}.
Follow the Accenture brand standard (colors, fonts, layouts) as defined in claude-catalog/policies/accenture-branding.md.
$([ "$TYPE" = "pptx" ] && echo "Include standard slides: Cover, Agenda, Context & Problem, Proposed Solution, Architecture, Dependencies, Timeline, Risks, Next Steps." || echo "Include standard sections: Cover, Executive Summary, Context & Problem, Proposed Solution, Architecture, Component Inventory, Implementation Plan, Effort Estimate, Risks, Next Steps.")"

# ── Run Claude ────────────────────────────────────────────────────────────────
echo -e "${BOLD}Running Claude Code...${RESET}"
echo ""

# claude CLI: non-interactive mode with -p
claude -p "$PROMPT" \
  --allowedTools "Read,Write,Bash,Grep,Glob,Agent" \
  --output-format text

echo ""
if [[ -f "$OUTPUT" ]]; then
  SIZE=$(du -sh "$OUTPUT" | cut -f1)
  echo -e "${GREEN}✓ Output ready:${RESET} $OUTPUT (${SIZE})"
else
  echo -e "Note: output file not found at $OUTPUT — check Claude's output above."
fi
echo ""
