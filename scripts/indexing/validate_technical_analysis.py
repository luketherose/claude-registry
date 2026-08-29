#!/usr/bin/env python3
"""
validate_technical_analysis.py — validates Phase 2 technical analysis outputs.

Exit codes:
  0 = PASS
  1 = FAIL
  2 = PASS_WITH_GAPS

Usage:
  python3 validate_technical_analysis.py \
    --analysis-dir /path/to/docs/analysis/02-technical/ \
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

FORBIDDEN_PRESCRIPTIVE_LANGUAGE = [
    "should use",
    "must migrate",
    "replace with",
    "upgrade to",
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
        out = ["# Phase 2 Technical Analysis Validation Report", ""]
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

def check_technical_findings(analysis_dir: Path, report: Report, strict: bool) -> None:
    report.section("Technical findings")
    p = analysis_dir / "normalized" / "technical-findings.jsonl"
    if not p.exists():
        report.fail("normalized/technical-findings.jsonl is missing")
        return

    records = _read_jsonl(p)
    report.ok(f"normalized/technical-findings.jsonl exists with {len(records)} records")

    # All findings must have non-empty evidence_ids
    without_evidence = [r for r in records if not r.get("evidence_ids")]
    if without_evidence:
        report.fail(
            f"{len(without_evidence)}/{len(records)} findings have no evidence_ids"
        )
    else:
        report.ok(f"All {len(records)} findings have evidence_ids")

    # High/critical findings without validation.status
    high_critical = [
        r for r in records
        if str(r.get("severity", "")).lower() in ("high", "critical")
        or str(r.get("risk_level", "")).lower() in ("high", "critical")
    ]
    unvalidated = []
    for r in high_critical:
        validation = r.get("validation") or {}
        if isinstance(validation, dict):
            status = validation.get("status")
        else:
            status = None
        if not status:
            unvalidated.append(r)

    if unvalidated:
        finding_ids = [
            r.get("finding_id") or r.get("id") or "?" for r in unvalidated[:5]
        ]
        if strict:
            report.fail(
                f"{len(unvalidated)} high/critical finding(s) have no validation.status (strict mode): "
                + ", ".join(finding_ids)
            )
        else:
            report.warn(
                f"{len(unvalidated)} high/critical finding(s) have no validation.status: "
                + ", ".join(finding_ids)
            )
    else:
        report.ok(f"All {len(high_critical)} high/critical findings have validation.status")


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


def check_evidence_audit(analysis_dir: Path, report: Report) -> None:
    report.section("Technical evidence audit")
    p = analysis_dir / "normalized" / "technical-evidence-audit.json"
    if not p.exists():
        report.info("normalized/technical-evidence-audit.json not present — skipping")
        return

    data = _read_json(p)
    if data is None:
        report.warn("technical-evidence-audit.json could not be parsed")
        return

    verdict = data.get("verdict") or data.get("status") or data.get("result")
    if verdict:
        report.info(f"Evidence audit verdict: {verdict}")
        if str(verdict).upper() == "FAIL":
            report.fail("Evidence audit verdict is FAIL — review technical-evidence-audit.json")
        elif str(verdict).upper() == "PASS_WITH_GAPS":
            report.warn("Evidence audit verdict is PASS_WITH_GAPS")
        else:
            report.ok("Evidence audit verdict is PASS")
    else:
        report.warn("technical-evidence-audit.json exists but no 'verdict' field found")


def check_prescriptive_language(analysis_dir: Path, report: Report) -> None:
    report.section("Prescriptive language in findings")
    p = analysis_dir / "normalized" / "technical-findings.jsonl"
    if not p.exists():
        report.info("normalized/technical-findings.jsonl not present — skipping prescriptive check")
        return

    records = _read_jsonl(p)
    offenders = []
    for rec in records:
        statement = rec.get("statement") or rec.get("description") or ""
        if not isinstance(statement, str):
            continue
        matched = [tok for tok in FORBIDDEN_PRESCRIPTIVE_LANGUAGE if tok.lower() in statement.lower()]
        if matched:
            fid = rec.get("finding_id") or rec.get("id") or "?"
            offenders.append(f"{fid}: {matched}")

    if offenders:
        report.warn(
            f"{len(offenders)} finding(s) contain prescriptive language (recommend review): "
            + "; ".join(offenders[:5])
        )
    else:
        report.ok("No prescriptive language found in finding statements")


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
        description="Validate Phase 2 technical analysis outputs."
    )
    parser.add_argument(
        "--analysis-dir",
        required=True,
        help="Path to docs/analysis/02-technical/ directory",
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

    check_technical_findings(analysis_dir, report, strict=args.strict)
    check_tobe_tokens(analysis_dir, report)
    check_evidence_audit(analysis_dir, report)
    check_prescriptive_language(analysis_dir, report)
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
