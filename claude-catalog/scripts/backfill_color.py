#!/usr/bin/env python3
"""One-off: backfill `color:` frontmatter on agents that omit it.

Each missing agent inherits the colour already adopted by its topic's
supervisor, so the topic stays visually coherent.
"""
from pathlib import Path
import re

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/agents")

TOPIC_COLOR = {
    "baseline-testing":    "green",
    "functional-analysis": "cyan",
    "indexing":            "magenta",
    "refactoring-tobe":    "red",
    "technical-analysis":  "yellow",
}


def has_color(frontmatter: str) -> bool:
    return re.search(r"^color:\s*\S+\s*$", frontmatter, re.MULTILINE) is not None


def insert_color(text: str, color: str) -> str | None:
    m = re.search(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not m:
        return None
    fm = m.group(1)
    if has_color(fm):
        return None
    # Insert `color: <c>` as the last frontmatter line, before the closing ---
    new_fm = fm.rstrip() + f"\ncolor: {color}\n"
    return text[: m.start(1)] + new_fm + text[m.end(1):]


def main() -> None:
    inserted = 0
    skipped = []
    for p in sorted(ROOT.rglob("*.md")):
        topic = p.parent.name
        if topic not in TOPIC_COLOR:
            continue
        color = TOPIC_COLOR[topic]
        text = p.read_text(encoding="utf-8")
        new = insert_color(text, color)
        if new is None:
            skipped.append((p.relative_to(ROOT), "color already present or no frontmatter"))
            continue
        p.write_text(new, encoding="utf-8")
        print(f"  ✓ {p.relative_to(ROOT)} ← color: {color}")
        inserted += 1
    print(f"\nDone: {inserted} agents updated, {len(skipped)} skipped")


if __name__ == "__main__":
    main()
