#!/usr/bin/env python3
"""
validate_functional_analysis.py — validates Phase 1 functional analysis outputs.

Exit codes:
  0 = PASS
  1 = FAIL
  2 = PASS_WITH_GAPS

Usage:
  python3 validate_functional_analysis.py \
    --analysis-dir /path/to/docs/analysis/01-functional/ \
    [--kb-root /path/to/.indexing-kb/] \
    [--strict]
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
    "TO-BE architecture",
    "target stack",
    "will be replaced",
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


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return default


class Report:
    def __init__(self, strict: bool):
        self.strict = strict
        self.lines = []
        self._verdict = "PASS"

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
        out = ["# Phase 1 Functional Analysis Validation Report", ""]
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

def check_use_case_candidates(analysis_dir: Path, report: Report, strict: bool) -> None:
    report.section("Use case candidates")
    p = analysis_dir / "normalized" / "use-case-candidates.jsonl"
    if not p.exists():
        report.fail("normalized/use-case-candidates.jsonl is missing")
        return

    records = _read_jsonl(p)
    report.ok(f"normalized/use-case-candidates.jsonl exists with {len(records)} records")

    # Check confirmed UCs for evidence_ids
    confirmed = [r for r in records if r.get("status", "").lower() == "confirmed"]
    without_evidence = [r for r in confirmed if not r.get("evidence_ids")]

    if without_evidence:
        if strict:
            report.fail(
                f"{len(without_evidence)} confirmed UC(s) have no evidence_ids (strict mode): "
                + ", ".join(r.get("uc_id") or r.get("id") or "?" for r in without_evidence[:5])
            )
        else:
            report.warn(
                f"{len(without_evidence)}/{len(confirmed)} confirmed UC(s) have no evidence_ids"
            )
    else:
        report.ok(
            f"All {len(confirmed)} confirmed UC(s) have evidence_ids"
        )


def check_functional_gaps(analysis_dir: Path, report: Report) -> None:
    report.section("Functional gaps")
    p = analysis_dir / "normalized" / "functional-gaps.jsonl"
    if not p.exists():
        report.warn("normalized/functional-gaps.jsonl is missing — gap coverage unknown")
    else:
        records = _read_jsonl(p)
        report.ok(f"normalized/functional-gaps.jsonl exists with {len(records)} records")


def check_tobe_tokens(analysis_dir: Path, report: Report) -> None:
    report.section("AS-IS purity (forbidden TO-BE tokens)")
    violations = []
    for md_file in analysis_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for token in FORBIDDEN_TOBE_TOKENS:
            if token.lower() in content.lower():
                violations.append(f"{md_file}: contains '{token}'")

    if violations:
        for v in violations:
            report.fail(f"TO-BE token found: {v}")
    else:
        report.ok("No forbidden TO-BE tokens found in any .md files")


def check_traceability_audit(analysis_dir: Path, report: Report) -> None:
    report.section("Functional traceability audit")
    p = analysis_dir / "normalized" / "functional-traceability-audit.json"
    if not p.exists():
        report.info("normalized/functional-traceability-audit.json not present — skipping")
        return

    data = _read_json(p)
    if data is None:
        report.warn("functional-traceability-audit.json could not be parsed")
        return

    verdict = data.get("verdict") or data.get("status") or data.get("result")
    if verdict:
        report.info(f"Traceability audit verdict: {verdict}")
        if str(verdict).upper() == "FAIL":
            report.fail("Traceability audit verdict is FAIL — review functional-traceability-audit.json")
        elif str(verdict).upper() == "PASS_WITH_GAPS":
            report.warn("Traceability audit verdict is PASS_WITH_GAPS")
        else:
            report.ok("Traceability audit verdict is PASS")
    else:
        report.warn("functional-traceability-audit.json exists but no 'verdict' field found")


def check_meta_manifest(analysis_dir: Path, report: Report) -> None:
    report.section("Phase manifest")
    p = analysis_dir / "_meta" / "manifest.json"
    if p.exists():
        report.ok("_meta/manifest.json exists")
    else:
        report.fail("_meta/manifest.json is missing")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate Phase 1 functional analysis outputs."
    )
    parser.add_argument(
        "--analysis-dir",
        required=True,
        help="Path to docs/analysis/01-functional/ directory",
    )
    parser.add_argument(
        "--kb-root",
        help="Path to .indexing-kb/ directory (optional, for cross-checks)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat PASS_WITH_GAPS conditions as FAIL",
    )
    args = parser.parse_args()

    analysis_dir = Path(args.analysis_dir).resolve()
    if not analysis_dir.exists():
        print(f"ERROR: analysis-dir not found: {analysis_dir}", file=sys.stderr)
        sys.exit(1)

    report = Report(strict=args.strict)

    check_use_case_candidates(analysis_dir, report, strict=args.strict)
    check_functional_gaps(analysis_dir, report)
    check_tobe_tokens(analysis_dir, report)
    check_traceability_audit(analysis_dir, report)
    check_meta_manifest(analysis_dir, report)

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
