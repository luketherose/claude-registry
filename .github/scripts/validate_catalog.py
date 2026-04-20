#!/usr/bin/env python3
"""
Validates Claude Code subagent files in claude-catalog/agents/ and claude-catalog/skills/.

Exit codes:
  0 — no errors (warnings may be present)
  1 — one or more errors found

Usage:
  python3 validate_catalog.py
  python3 validate_catalog.py --changed-files claude-catalog/agents/foo.md
  python3 validate_catalog.py --output-file /tmp/comment.md
"""

import sys
import re
import yaml
import argparse
from pathlib import Path
from dataclasses import dataclass


KNOWN_TOOLS = {
    "Read", "Edit", "Write", "Bash", "Glob", "Grep", "Agent",
    "WebFetch", "WebSearch", "LSP", "NotebookEdit", "TodoWrite",
}
VALID_MODELS = {"sonnet", "opus", "haiku"}
VALID_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
KNOWN_FRONTMATTER_KEYS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "color", "initialPrompt", "background", "effort", "isolation",
    "skills", "mcpServers", "hooks", "memory",
}

# Tools that skill agents should not have (they are knowledge providers, not actors)
SKILL_DISALLOWED_TOOLS = {"Edit", "Write", "Bash", "Agent"}


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    location: str
    message: str


def parse_frontmatter(content: str):
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm or {}, content[match.end():]
    except yaml.YAMLError as exc:
        return {"_parse_error": str(exc)}, content


def validate_agent_file(filepath: Path, file_type: str = "agent") -> list[Finding]:
    """Validate a single subagent or skill file."""
    findings = []
    content = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    expected_name = filepath.stem

    if fm is None:
        findings.append(Finding("error", str(filepath),
            "No YAML frontmatter found. File must start with `---`."))
        return findings

    if "_parse_error" in fm:
        findings.append(Finding("error", str(filepath),
            f"YAML frontmatter parse error: {fm['_parse_error']}"))
        return findings

    # --- name ---
    if "name" not in fm:
        findings.append(Finding("error", str(filepath),
            "Missing required frontmatter field: `name`"))
    else:
        name = str(fm["name"])
        if name != expected_name:
            findings.append(Finding("error", str(filepath),
                f"`name: {name}` does not match filename. Expected `{expected_name}`."))
        if not re.match(r"^[a-z][a-z0-9-]*$", name):
            findings.append(Finding("error", str(filepath),
                f"`name: {name}` must be lowercase letters, digits, and hyphens only."))

    # --- description ---
    if "description" not in fm:
        findings.append(Finding("error", str(filepath),
            "Missing required frontmatter field: `description`"))
    else:
        desc = str(fm["description"]).strip()
        if not desc:
            findings.append(Finding("error", str(filepath),
                "`description` is empty."))
        elif not re.match(r"^Use (when|for|to)\b", desc, re.IGNORECASE):
            findings.append(Finding("warning", str(filepath),
                f"`description` should start with \"Use when\", \"Use for\", or \"Use to\". "
                f"Got: \"{desc[:80]}\""))
        if 0 < len(desc) < 40:
            findings.append(Finding("warning", str(filepath),
                f"`description` is very short ({len(desc)} chars). "
                "A precise description is critical for automatic delegation."))

    # --- tools ---
    tools_used = set()
    if "tools" in fm:
        raw = str(fm["tools"])
        for tool in [t.strip() for t in raw.split(",") if t.strip()]:
            tools_used.add(tool)
            if tool not in KNOWN_TOOLS:
                findings.append(Finding("warning", str(filepath),
                    f"Unknown tool `{tool}` in `tools` field. "
                    f"Known tools: {', '.join(sorted(KNOWN_TOOLS))}"))

    # --- skill-specific tool checks ---
    if file_type == "skill":
        bad_tools = tools_used & SKILL_DISALLOWED_TOOLS
        if bad_tools:
            findings.append(Finding("warning", str(filepath),
                f"Skill has tools that knowledge providers should not need: "
                f"{', '.join(sorted(bad_tools))}. "
                "Skills should only use `Read`. Add a comment in the PR explaining why."))
        if "Agent" in tools_used:
            findings.append(Finding("error", str(filepath),
                "Skill uses the `Agent` tool. Skills must not spawn subagents — "
                "they are leaf knowledge providers."))

    # --- model ---
    if "model" in fm:
        model = str(fm["model"])
        if model not in VALID_MODELS and not model.startswith("claude-"):
            findings.append(Finding("warning", str(filepath),
                f"`model: {model}` is not a recognized shorthand. "
                f"Expected one of: {', '.join(sorted(VALID_MODELS))}, or a full claude-* model ID."))
        if file_type == "skill" and model in ("sonnet", "opus"):
            findings.append(Finding("warning", str(filepath),
                f"Skill uses `model: {model}`. Skills are knowledge retrieval — "
                "`model: haiku` is recommended unless reasoning depth requires more."))

    # --- color ---
    if "color" in fm:
        color = str(fm["color"])
        if color not in VALID_COLORS:
            findings.append(Finding("warning", str(filepath),
                f"`color: {color}` is not valid. "
                f"Expected one of: {', '.join(sorted(VALID_COLORS))}"))

    # --- unknown keys ---
    for key in fm:
        if not key.startswith("_") and key not in KNOWN_FRONTMATTER_KEYS:
            findings.append(Finding("warning", str(filepath),
                f"Unknown frontmatter key `{key}`. Check for typos. "
                f"Known keys: {', '.join(sorted(KNOWN_FRONTMATTER_KEYS))}"))

    # --- body ---
    stripped_body = body.strip()
    if not stripped_body:
        findings.append(Finding("error", str(filepath),
            "System prompt body is empty. A subagent without a system prompt has no defined behavior."))
    elif len(stripped_body) < 80:
        findings.append(Finding("warning", str(filepath),
            f"System prompt body is very short ({len(stripped_body)} chars). "
            "A useful subagent needs a substantive system prompt."))
    else:
        body_lower = stripped_body.lower()
        has_role = "you are" in body_lower or "## role" in body_lower
        if not has_role:
            findings.append(Finding("warning", str(filepath),
                "System prompt does not define a role. "
                "Consider adding a '## Role' section or 'You are...' opening."))

    return findings


def check_supporting_files(catalog_root: Path) -> list[Finding]:
    findings = []
    examples_dir = catalog_root / "examples"
    evals_dir = catalog_root / "evals"
    agents_dir = catalog_root / "agents"
    skills_dir = catalog_root / "skills"

    for agent_file in sorted(agents_dir.glob("*.md")):
        name = agent_file.stem
        if not (examples_dir / f"{name}-example.md").exists():
            findings.append(Finding("warning", f"examples/{name}-example.md",
                f"No example file for agent `{name}`. "
                "Add `examples/{name}-example.md` before promoting to stable."))
        if not (evals_dir / f"{name}-eval.md").exists():
            findings.append(Finding("warning", f"evals/{name}-eval.md",
                f"No eval file for agent `{name}`. "
                "Add `evals/{name}-eval.md` before promoting to stable."))

    if skills_dir.exists():
        for skill_file in sorted(skills_dir.glob("*.md")):
            name = skill_file.stem
            if not (examples_dir / f"{name}-example.md").exists():
                findings.append(Finding("warning", f"examples/{name}-example.md",
                    f"No example file for skill `{name}`. "
                    "Consider adding `examples/{name}-example.md`."))
            if not (evals_dir / f"{name}-eval.md").exists():
                findings.append(Finding("warning", f"evals/{name}-eval.md",
                    f"No eval file for skill `{name}`. "
                    "Consider adding `evals/{name}-eval.md`."))

    return findings


def check_changelog(catalog_root: Path) -> list[Finding]:
    changelog = catalog_root / "CHANGELOG.md"
    if not changelog.exists():
        return [Finding("error", "CHANGELOG.md", "CHANGELOG.md not found.")]
    content = changelog.read_text(encoding="utf-8")
    if "[Unreleased]" not in content:
        return [Finding("warning", "CHANGELOG.md",
            "No `[Unreleased]` section found in CHANGELOG.md. "
            "PRs that add or modify capabilities should include a changelog entry.")]
    return []


def format_comment(findings: list[Finding], validated_files: list[str]) -> str:
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines = ["<!-- claude-catalog-validation -->"]
    lines.append("## Catalog Validation Report")
    lines.append("")

    if validated_files:
        files_str = ", ".join(f"`{f}`" for f in validated_files[:10])
        if len(validated_files) > 10:
            files_str += f" … (+{len(validated_files) - 10} more)"
        lines.append(f"**Validated**: {files_str}")
        lines.append("")

    if not findings:
        lines.append("### ✅ All checks passed")
        lines.append("")
        lines.append("No errors or warnings. This PR is ready for manual review.")
        return "\n".join(lines)

    if errors:
        lines.append(f"### ❌ Errors — must fix before merge ({len(errors)})")
        lines.append("")
        for f in errors:
            lines.append(f"- **`{f.location}`** — {f.message}")
        lines.append("")

    if warnings:
        lines.append(f"### ⚠️ Warnings — review before approving ({len(warnings)})")
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
    parser.add_argument("--changed-files", nargs="*", default=None)
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    catalog_root = repo_root / "claude-catalog"
    agents_dir = catalog_root / "agents"
    skills_dir = catalog_root / "skills"

    all_findings: list[Finding] = []
    validated_files: list[str] = []

    if args.changed_files:
        for path_str in args.changed_files:
            filepath = repo_root / path_str
            if filepath.exists() and filepath.suffix == ".md":
                if "agents" in filepath.parts:
                    all_findings.extend(validate_agent_file(filepath, file_type="agent"))
                    validated_files.append(path_str)
                elif "skills" in filepath.parts:
                    all_findings.extend(validate_agent_file(filepath, file_type="skill"))
                    validated_files.append(path_str)
    else:
        for filepath in sorted(agents_dir.glob("*.md")):
            all_findings.extend(validate_agent_file(filepath, file_type="agent"))
            validated_files.append(str(filepath.relative_to(repo_root)))
        if skills_dir.exists():
            for filepath in sorted(skills_dir.glob("*.md")):
                all_findings.extend(validate_agent_file(filepath, file_type="skill"))
                validated_files.append(str(filepath.relative_to(repo_root)))

    all_findings.extend(check_changelog(catalog_root))
    all_findings.extend(check_supporting_files(catalog_root))

    comment = format_comment(all_findings, validated_files)

    if args.output_file:
        Path(args.output_file).write_text(comment, encoding="utf-8")
    else:
        print(comment)

    if any(f.severity == "error" for f in all_findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
