#!/usr/bin/env python3
"""Backfill the rubric-required `Typical triggers include [s1], [s2], [s3].`
   middle clause in agent descriptions. Trigger labels are extracted from the
   bold titles of the bullets in the agent's `## When to invoke` body section.

   Idempotent: if the description already contains `Typical triggers include`,
   skip. Skips `refactoring-supervisor.md` (deferred).
"""
from pathlib import Path
import re

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/agents")
DEFER = {"orchestration/refactoring-supervisor.md"}

# Match the When-to-invoke section and capture each bullet's bold title
SECTION_RE = re.compile(
    r"## When to invoke\n\n(.*?)(?:\n---|\Z)",
    re.DOTALL,
)
BULLET_TITLE_RE = re.compile(r"^- \*\*(.+?)\*\*\.?", re.MULTILINE)


def extract_titles(text: str) -> list[str]:
    m = SECTION_RE.search(text)
    if not m:
        return []
    section = m.group(1)
    titles = BULLET_TITLE_RE.findall(section)
    # Clean trailing punctuation; cap length per title
    cleaned = []
    for t in titles:
        t = t.strip().rstrip(".").strip()
        # Some bullet titles include a period inside (e.g., "Phase 3 dispatch.").
        # Already handled. Cap reasonable length.
        if len(t) > 70:
            t = t[:67].rstrip() + "…"
        if t:
            cleaned.append(t.lower()[0] + t[1:])
    return cleaned


def format_clause(titles: list[str]) -> str:
    if not titles:
        return ""
    if len(titles) == 1:
        body = titles[0]
    elif len(titles) == 2:
        body = f"{titles[0]} and {titles[1]}"
    else:
        body = ", ".join(titles[:-1]) + f", and {titles[-1]}"
    return f"Typical triggers include {body}."


def update_description(text: str, clause: str) -> str | None:
    """Insert the `Typical triggers include …` clause before the rubric pointer
    inside the YAML frontmatter description (single-line, double-quoted)."""
    fm_re = re.compile(r"^(description:\s*\")(.*)(\"\s*$)", re.MULTILINE)
    m = fm_re.search(text)
    if not m:
        return None
    desc = m.group(2)
    if "Typical triggers include" in desc:
        return None
    pointer = ' See \\"When to invoke\\" in the agent body for worked scenarios.'
    if pointer in desc:
        # Insert clause immediately before the pointer
        new_desc = desc.replace(pointer, f" {clause}{pointer}")
    else:
        # No pointer (deferred agent or unusual case) — append clause at end
        new_desc = desc.rstrip().rstrip(".") + f". {clause}"
    if new_desc == desc:
        return None
    return text[: m.start(2)] + new_desc + text[m.end(2):]


def main() -> None:
    updated, skipped_no_section, skipped_already, skipped_defer = 0, [], [], []
    for p in sorted(ROOT.rglob("*.md")):
        rel = str(p.relative_to(ROOT))
        if rel in DEFER:
            skipped_defer.append(rel)
            continue
        text = p.read_text(encoding="utf-8")
        titles = extract_titles(text)
        if not titles:
            skipped_no_section.append(rel)
            continue
        clause = format_clause(titles)
        new_text = update_description(text, clause)
        if new_text is None:
            skipped_already.append(rel)
            continue
        p.write_text(new_text, encoding="utf-8")
        print(f"  ✓ {rel} ← {clause[:80]}{'…' if len(clause) > 80 else ''}")
        updated += 1
    print(f"\nDone: {updated} updated, {len(skipped_already)} already had clause, "
          f"{len(skipped_no_section)} no When-to-invoke, "
          f"{len(skipped_defer)} deferred")


if __name__ == "__main__":
    main()
