#!/usr/bin/env python3
"""
Validates claude-marketplace/ structure and catalog.json consistency.

Exit codes:
  0 — no errors (warnings may be present)
  1 — one or more errors found

Usage:
  python3 validate_marketplace.py
  python3 validate_marketplace.py --output-file /tmp/comment.md
"""

import sys
import json
import re
import yaml
import argparse
from pathlib import Path
from dataclasses import dataclass


SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
VALID_TIERS = {"stable", "beta"}
VALID_STATUSES = {"active", "deprecated"}
REQUIRED_CAP_FIELDS = {"name", "version", "tier", "status", "description", "file"}


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    location: str
    message: str


def parse_frontmatter(content: str):
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None


def validate_catalog_json(catalog_path: Path) -> tuple[list[Finding], dict]:
    findings = []

    if not catalog_path.exists():
        return [Finding("error", "catalog.json", "catalog.json not found.")], {}

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Finding("error", "catalog.json", f"Invalid JSON: {exc}")], {}

    if "capabilities" not in catalog:
        findings.append(Finding("error", "catalog.json",
            "Missing required top-level key: `capabilities`"))
        return findings, catalog

    if not isinstance(catalog["capabilities"], list):
        findings.append(Finding("error", "catalog.json",
            "`capabilities` must be a JSON array"))
        return findings, catalog

    names_seen: set[str] = set()

    for i, cap in enumerate(catalog["capabilities"]):
        if not isinstance(cap, dict):
            findings.append(Finding("error", f"catalog.json[{i}]",
                "Entry must be a JSON object"))
            continue

        # Skip internal comment entries (keys starting with _)
        if any(k.startswith("_") for k in cap):
            continue

        loc = f"catalog.json › {cap.get('name', f'[{i}]')}"

        # Required fields
        for field in REQUIRED_CAP_FIELDS:
            if field not in cap:
                findings.append(Finding("error", loc,
                    f"Missing required field: `{field}`"))

        name = cap.get("name", "")
        if not name:
            continue

        if name in names_seen:
            findings.append(Finding("error", loc,
                f"Duplicate capability name: `{name}`"))
        names_seen.add(name)

        # version semver
        version = cap.get("version", "")
        if version and not SEMVER.match(str(version)):
            findings.append(Finding("error", loc,
                f"`version: {version}` does not follow semver (MAJOR.MINOR.PATCH)"))

        # tier
        tier = cap.get("tier", "")
        if tier and tier not in VALID_TIERS:
            findings.append(Finding("error", loc,
                f"`tier: {tier}` is not valid. Expected: {', '.join(sorted(VALID_TIERS))}"))

        # status
        status = cap.get("status", "")
        if status and status not in VALID_STATUSES:
            findings.append(Finding("error", loc,
                f"`status: {status}` is not valid. "
                f"Expected: {', '.join(sorted(VALID_STATUSES))}"))

        # referenced file exists
        file_field = cap.get("file", "")
        if file_field:
            full_path = catalog_path.parent / file_field
            if not full_path.exists():
                findings.append(Finding("error", loc,
                    f"Referenced file `{file_field}` does not exist in the marketplace directory."))
            else:
                # Check that the .md file has valid frontmatter with matching name
                fm = parse_frontmatter(full_path.read_text(encoding="utf-8"))
                if fm is None:
                    findings.append(Finding("warning", loc,
                        f"`{file_field}` has no parseable YAML frontmatter."))
                elif fm.get("name") != name:
                    findings.append(Finding("error", loc,
                        f"`{file_field}` has `name: {fm.get('name')}` "
                        f"but catalog entry is `{name}`. They must match."))

            # Check file path convention: {tier}/{name}.md
            if tier and name:
                expected = f"{tier}/{name}.md"
                if file_field != expected:
                    findings.append(Finding("warning", loc,
                        f"`file: {file_field}` — expected `{expected}` "
                        f"based on tier and name."))

    return findings, catalog


def check_orphan_files(marketplace_root: Path, catalog: dict) -> list[Finding]:
    """Warn about .md files in stable/ or beta/ with no catalog.json entry."""
    findings = []
    catalog_files = {
        cap.get("file")
        for cap in catalog.get("capabilities", [])
        if isinstance(cap, dict) and not any(k.startswith("_") for k in cap)
    }
    for tier in ("stable", "beta"):
        tier_dir = marketplace_root / tier
        if not tier_dir.exists():
            continue
        for md_file in sorted(tier_dir.glob("*.md")):
            rel = f"{tier}/{md_file.name}"
            if rel not in catalog_files:
                findings.append(Finding("warning", rel,
                    f"`{rel}` has no entry in catalog.json. "
                    "Run the publish script to register it, or delete the file."))
    return findings


def format_comment(findings: list[Finding]) -> str:
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines = ["<!-- claude-marketplace-validation -->"]
    lines.append("## Marketplace Validation Report")
    lines.append("")

    if not findings:
        lines.append("### ✅ All checks passed")
        lines.append("")
        lines.append("`catalog.json` is valid and all files are consistent.")
        return "\n".join(lines)

    if errors:
        lines.append(f"### ❌ Errors — must fix before merge ({len(errors)})")
        lines.append("")
        for f in errors:
            lines.append(f"- **`{f.location}`** — {f.message}")
        lines.append("")

    if warnings:
        lines.append(f"### ⚠️ Warnings ({len(warnings)})")
        lines.append("")
        for f in warnings:
            lines.append(f"- `{f.location}` — {f.message}")
        lines.append("")

    lines.append("---")
    if errors:
        lines.append("**Status: BLOCKED** — resolve all errors before this PR can be merged.")
    else:
        lines.append("**Status: WARNINGS** — no blocking errors. Review warnings before approving.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    marketplace_root = repo_root / "claude-marketplace"
    catalog_path = marketplace_root / "catalog.json"

    findings, catalog = validate_catalog_json(catalog_path)

    if catalog:
        findings.extend(check_orphan_files(marketplace_root, catalog))

    comment = format_comment(findings)

    if args.output_file:
        Path(args.output_file).write_text(comment, encoding="utf-8")
    else:
        print(comment)

    if any(f.severity == "error" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
