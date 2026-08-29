#!/usr/bin/env python3
"""Build bronze/config-env-index.jsonl — env var and config access catalogue for Phase 0 indexing."""
import argparse, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

SKIP_CATEGORIES = {'generated', 'vendor', 'build_artifact'}

# ----- Env-var patterns -----

# os.environ.get('KEY', default) or os.environ.get("KEY")
RE_ENV_GET = re.compile(r"""os\.environ\.get\(\s*['"](\w+)['"]\s*(?:,\s*([^)]+))?\)""")
# os.environ['KEY'] or os.environ["KEY"]
RE_ENV_BRACKET = re.compile(r"""os\.environ\[\s*['"](\w+)['"]\s*\]""")
# os.getenv('KEY', default)
RE_GETENV = re.compile(r"""os\.getenv\(\s*['"](\w+)['"]\s*(?:,\s*([^)]+))?\)""")
# process.env.KEY  (JS/TS)
RE_PROCESS_ENV = re.compile(r"""process\.env\.(\w+)""")
# process.env['KEY'] (JS/TS)
RE_PROCESS_ENV_BRACKET = re.compile(r"""process\.env\[\s*['"](\w+)['"]\s*\]""")
# System.getenv("KEY") (Java)
RE_JAVA_GETENV = re.compile(r"""System\.getenv\(\s*"(\w+)"\s*\)""")
# os.environ["KEY"] = value (write)
RE_ENV_WRITE = re.compile(r"""os\.environ\[\s*['"](\w+)['"]\s*\]\s*=""")

# load_dotenv / dotenv usage
RE_DOTENV = re.compile(r"""(?:load_dotenv|dotenv\.config|require\s*\(.*dotenv.*\))""")

# ----- Config patterns -----

# settings.SOMETHING or config.SOMETHING
RE_SETTINGS_ACCESS = re.compile(r"""\b(?:settings|config)\s*\.\s*(\w+)""")
# app.config['KEY'] (Flask) or app.config.get('KEY')
RE_APP_CONFIG = re.compile(r"""app\.config(?:\[['"](\w+)['"]\]|\.get\(\s*['"](\w+)['"]\s*\))""")
# @Value("${key}") Spring
RE_SPRING_VALUE = re.compile(r"""@Value\s*\(\s*"\$\{([^}]+)\}"\s*\)""")
# application.properties / application.yml key = value  (config file itself)
RE_PROPS_KEY = re.compile(r"""^([\w.\-]+)\s*[=:]""")


def should_skip_path(rel: Path) -> bool:
    return any(part in IGNORE_DIRS for part in rel.parts)


def load_inventory(bronze_dir: Path) -> dict:
    inv = {}
    inventory_path = bronze_dir / "file-inventory.jsonl"
    if inventory_path.exists():
        with open(inventory_path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    inv[rec["file"]] = rec
                except json.JSONDecodeError:
                    pass
    return inv


def scan_source_file(source: str, rel_str: str, counter: list) -> list:
    """Scan a source file for env var and config accesses. Returns list of records."""
    records = []
    lines = source.splitlines()

    for lineno, line in enumerate(lines, 1):
        # ENV reads: os.environ.get(...)
        for m in RE_ENV_GET.finditer(line):
            counter[0] += 1
            default = m.group(2).strip() if m.group(2) else None
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": default,
                "evidence_id":  None,
            })

        # ENV reads: os.environ[...]
        for m in RE_ENV_BRACKET.finditer(line):
            # check if it's a write (followed by =)
            is_write = bool(RE_ENV_WRITE.search(line))
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "write" if is_write else "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # ENV reads: os.getenv(...)
        for m in RE_GETENV.finditer(line):
            counter[0] += 1
            default = m.group(2).strip() if m.group(2) else None
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": default,
                "evidence_id":  None,
            })

        # JS/TS: process.env.KEY
        for m in RE_PROCESS_ENV.finditer(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # JS/TS: process.env['KEY']
        for m in RE_PROCESS_ENV_BRACKET.finditer(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # Java: System.getenv("KEY")
        for m in RE_JAVA_GETENV.finditer(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # Config access: settings.KEY or config.KEY
        for m in RE_SETTINGS_ACCESS.finditer(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "config_key",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # Flask app.config access
        for m in RE_APP_CONFIG.finditer(line):
            name = m.group(1) or m.group(2)
            if name:
                counter[0] += 1
                records.append({
                    "key_id":       f"ENV-{counter[0]:06d}",
                    "kind":         "config_key",
                    "name":         name,
                    "file":         rel_str,
                    "line":         lineno,
                    "access_type":  "read",
                    "default_value": None,
                    "evidence_id":  None,
                })

        # Spring @Value("${key}")
        for m in RE_SPRING_VALUE.finditer(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "config_key",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

        # dotenv detection
        if RE_DOTENV.search(line):
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "env_var",
                "name":         "dotenv_load",
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })

    return records


def scan_properties_file(source: str, rel_str: str, counter: list) -> list:
    """Scan a .properties or application.yml file for config keys."""
    records = []
    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('!'):
            continue
        m = RE_PROPS_KEY.match(stripped)
        if m:
            counter[0] += 1
            records.append({
                "key_id":       f"ENV-{counter[0]:06d}",
                "kind":         "config_key",
                "name":         m.group(1),
                "file":         rel_str,
                "line":         lineno,
                "access_type":  "read",
                "default_value": None,
                "evidence_id":  None,
            })
    return records


SOURCE_LANGS = {
    'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp',
    'ruby', 'kotlin', 'swift', 'php', 'cpp', 'c', 'shell'
}
CONFIG_LANGS = {'properties', 'yaml', 'ini', 'cfg', 'env', 'toml'}


def main():
    parser = argparse.ArgumentParser(description="Build bronze/config-env-index.jsonl")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    output_path = bronze_dir / "config-env-index.jsonl"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    counter = [0]  # mutable counter shared across scan functions
    total_records = 0
    error_count = 0
    parse_errors = []

    with open(output_path, 'w') as out_f:
        for abs_path in sorted(repo_root.rglob('*')):
            if not abs_path.is_file():
                continue

            try:
                rel = abs_path.relative_to(repo_root)
            except ValueError:
                continue

            if should_skip_path(rel):
                continue

            rel_str = str(rel)
            inv_rec = inventory.get(rel_str, {})
            category = inv_rec.get("category", "unknown")
            language = inv_rec.get("language", "unknown")

            if category in SKIP_CATEGORIES:
                continue

            try:
                source = abs_path.read_text(errors='replace')

                records = []
                if language in SOURCE_LANGS:
                    records = scan_source_file(source, rel_str, counter)
                elif language in CONFIG_LANGS:
                    records = scan_properties_file(source, rel_str, counter)
                elif abs_path.name.lower().startswith('.env'):
                    records = scan_properties_file(source, rel_str, counter)

                for rec in records:
                    out_f.write(json.dumps(rec) + '\n')
                total_records += len(records)

                if args.verbose and records:
                    print(f"  {rel_str} [{language}] {len(records)} env/config refs", file=sys.stderr)

            except Exception as e:
                error_count += 1
                err = {"script": "build_config_env_index", "file": rel_str, "error": str(e)}
                parse_errors.append(err)
                if args.verbose:
                    print(f"  ERROR {rel_str}: {e}", file=sys.stderr)

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    print(f"Wrote {output_path} ({total_records} records, {error_count} errors)", file=sys.stderr)
    return 2 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
