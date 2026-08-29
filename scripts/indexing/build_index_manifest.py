#!/usr/bin/env python3
"""Build bronze/manifest.json — run metadata for Phase 0 indexing."""
import argparse, datetime, json, os, subprocess, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

def get_git_commit(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"

def count_files_by_category(bronze_dir: Path) -> dict:
    inventory = bronze_dir / "file-inventory.jsonl"
    counts = {"source": 0, "test": 0, "config": 0, "docs": 0, "generated": 0, "vendor": 0, "build_artifact": 0, "unknown": 0}
    if inventory.exists():
        with open(inventory) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    cat = rec.get("category", "unknown")
                    counts[cat] = counts.get(cat, 0) + 1
                except json.JSONDecodeError:
                    pass
    return counts

def main():
    parser = argparse.ArgumentParser(description="Build bronze/manifest.json")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--run-id", help="Override run ID (default: ISO-8601 timestamp)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or datetime.datetime.utcnow().isoformat() + "Z"

    manifest = {
        "schema_version": "1.0",
        "script_version": SCRIPT_VERSION,
        "run_id": run_id,
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "repo_root": str(repo_root),
        "git_commit": get_git_commit(repo_root),
        "file_counts": count_files_by_category(bronze_dir),
        "bronze_outputs": [p.name for p in bronze_dir.glob("*.json") if p.is_file()]
                        + [p.name for p in bronze_dir.glob("*.jsonl") if p.is_file()]
                        + [p.name for p in bronze_dir.glob("*.csv") if p.is_file()]
    }

    output_path = bronze_dir / "manifest.json"
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {output_path}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
