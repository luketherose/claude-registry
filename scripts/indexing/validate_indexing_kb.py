#!/usr/bin/env python3
"""
validate_indexing_kb.py — validates Phase 0 output quality.

Exit codes:
  0 = PASS
  1 = FAIL
  2 = PASS_WITH_GAPS

Usage:
  python3 validate_indexing_kb.py --kb-root /path/to/.indexing-kb/ [--strict]
"""

import argparse
import json
import sys
from pathlib import Path


FORBIDDEN_TOBE_TOKENS = [
    "Spring Boot",
    "Angular",
    "migrate to",
    "replatform",
    "target architecture",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_jsonl(path: Path) -> list:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


class Report:
    def __init__(self, strict: bool):
        self.strict = strict
        self.lines = []
        self._verdict = "PASS"  # PASS < PASS_WITH_GAPS < FAIL

    def _escalate(self, level: str) -> None:
        order = {"PASS": 0, "PASS_WITH_GAPS": 1, "FAIL": 2}
        if order.get(level, 0) > order.get(self._verdict, 0):
            self._verdict = level

    def ok(self, msg: str) -> None:
        self.lines.append(f"- [OK]   {msg}")

    def warn(self, msg: str, escalate_to: str = "PASS_WITH_GAPS") -> None:
        self.lines.append(f"- [WARN] {msg}")
        self._escalate(escalate_to)

    def fail(self, msg: str) -> None:
        self.lines.append(f"- [FAIL] {msg}")
        self._escalate("FAIL")

    def info(self, msg: str) -> None:
        self.lines.append(f"- [INFO] {msg}")

    def section(self, title: str) -> None:
        self.lines.append(f"\n## {title}")

    def render(self) -> str:
        out = ["# Phase 0 KB Validation Report", ""]
        out.extend(self.lines)
        out.append("")
        out.append(f"VERDICT: {self._verdict}")
        return "\n".join(out) + "\n"

    @property
    def verdict(self) -> str:
        return self._verdict


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_required_files(kb_root: Path, report: Report) -> None:
    report.section("Required files")
    required = [
        "bronze/manifest.json",
        "bronze/stack.json",
    ]
    for rel in required:
        p = kb_root / rel
        if p.exists():
            report.ok(f"{rel} exists")
        else:
            report.fail(f"{rel} is missing")


def check_file_inventory(kb_root: Path, report: Report) -> None:
    report.section("File inventory")
    p = kb_root / "bronze" / "file-inventory.jsonl"
    if not p.exists():
        report.fail("bronze/file-inventory.jsonl is missing")
        return
    records = _read_jsonl(p)
    if len(records) >= 1:
        report.ok(f"bronze/file-inventory.jsonl has {len(records)} records")
    else:
        report.fail("bronze/file-inventory.jsonl exists but has 0 records")


def check_gold_overview(kb_root: Path, report: Report) -> None:
    report.section("Gold synthesis")
    p = kb_root / "gold" / "system-overview.md"
    if p.exists():
        report.ok("gold/system-overview.md exists")
    else:
        report.fail("gold/system-overview.md is missing")


def check_evidence_ledger(kb_root: Path, report: Report, strict: bool) -> None:
    report.section("Evidence ledger")
    ledger = kb_root / "evidence-ledger.jsonl"
    if not ledger.exists():
        if strict:
            report.fail("evidence-ledger.jsonl is missing (strict mode)")
        else:
            report.warn("evidence-ledger.jsonl is missing — evidence grounding cannot be verified")
        return

    records = _read_jsonl(ledger)
    report.ok(f"evidence-ledger.jsonl exists with {len(records)} records")

    # Check for duplicate evidence_id values
    seen_ids: dict = {}
    duplicates = []
    for rec in records:
        eid = rec.get("evidence_id")
        if eid:
            if eid in seen_ids:
                duplicates.append(eid)
            else:
                seen_ids[eid] = True

    if duplicates:
        report.fail(f"Duplicate evidence_ids found ({len(duplicates)}): {duplicates[:5]}")
    else:
        report.ok(f"No duplicate evidence_ids ({len(seen_ids)} unique IDs)")


def check_large_files(kb_root: Path, report: Report) -> None:
    report.section("Large files")
    p = kb_root / "bronze" / "large-files.jsonl"
    if not p.exists():
        report.info("bronze/large-files.jsonl not present — skipping")
        return
    records = _read_jsonl(p)
    null_status = [r for r in records if not r.get("status")]
    if null_status:
        report.fail(
            f"bronze/large-files.jsonl: {len(null_status)} records have null/missing 'status' field"
        )
    else:
        report.ok(f"bronze/large-files.jsonl: all {len(records)} records have a 'status' field")


def check_business_rules_evidence(kb_root: Path, report: Report) -> None:
    report.section("Business rules evidence grounding")
    p = kb_root / "silver" / "business-rules.jsonl"
    if not p.exists():
        report.info("silver/business-rules.jsonl not present — skipping")
        return
    records = _read_jsonl(p)
    if not records:
        report.info("silver/business-rules.jsonl is empty — skipping")
        return
    without_evidence = [r for r in records if not r.get("evidence_ids")]
    pct = 100.0 * len(without_evidence) / len(records)
    if pct > 10:
        report.fail(
            f"silver/business-rules.jsonl: {len(without_evidence)}/{len(records)} "
            f"({pct:.1f}%) records have no evidence_ids (threshold: 10%)"
        )
    else:
        report.ok(
            f"silver/business-rules.jsonl: evidence coverage OK "
            f"({len(without_evidence)}/{len(records)} without evidence_ids)"
        )


def check_tobe_tokens(kb_root: Path, report: Report) -> None:
    report.section("AS-IS purity (forbidden TO-BE tokens in gold/)")
    gold_dir = kb_root / "gold"
    if not gold_dir.exists():
        report.info("gold/ directory not present — skipping TO-BE token check")
        return

    violations = []
    for md_file in gold_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for token in FORBIDDEN_TOBE_TOKENS:
            if token.lower() in content.lower():
                violations.append(f"{md_file.relative_to(kb_root)}: contains '{token}'")

    if violations:
        for v in violations:
            report.fail(f"TO-BE token found: {v}")
    else:
        report.ok("No forbidden TO-BE tokens found in gold/ markdown files")


def check_graph_quality(kb_root: Path, report: Report) -> None:
    report.section("Graph quality report")
    p = kb_root / "graph" / "graph-quality-report.md"
    if not p.exists():
        report.info("graph/graph-quality-report.md not present — run build_context_graph.py to generate")
        return

    content = p.read_text(encoding="utf-8", errors="replace")
    verdict_line = None
    for line in content.splitlines():
        if line.startswith("## Verdict:"):
            verdict_line = line
            break

    if verdict_line:
        report.info(f"Graph quality: {verdict_line}")
        if "FAIL" in verdict_line:
            report.warn("Graph quality report verdict is FAIL — review graph-quality-report.md")
        elif "PASS_WITH_GAPS" in verdict_line:
            report.warn("Graph quality report verdict is PASS_WITH_GAPS")
        else:
            report.ok("Graph quality report verdict is PASS")
    else:
        report.warn("graph-quality-report.md exists but no verdict line found")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate Phase 0 (.indexing-kb/) output quality."
    )
    parser.add_argument("--kb-root", required=True, help="Path to .indexing-kb/ directory")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat PASS_WITH_GAPS conditions as FAIL",
    )
    args = parser.parse_args()

    kb_root = Path(args.kb_root).resolve()
    if not kb_root.exists():
        print(f"ERROR: kb-root not found: {kb_root}", file=sys.stderr)
        sys.exit(1)

    report = Report(strict=args.strict)

    check_required_files(kb_root, report)
    check_file_inventory(kb_root, report)
    check_gold_overview(kb_root, report)
    check_evidence_ledger(kb_root, report, strict=args.strict)
    check_large_files(kb_root, report)
    check_business_rules_evidence(kb_root, report)
    check_tobe_tokens(kb_root, report)
    check_graph_quality(kb_root, report)

    print(report.render())

    verdict = report.verdict
    if args.strict and verdict == "PASS_WITH_GAPS":
        verdict = "FAIL"

    if verdict == "PASS":
        sys.exit(0)
    elif verdict == "PASS_WITH_GAPS":
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
