#!/usr/bin/env python3
"""Build bronze/import-graph.json — inter-file dependency graph for Phase 0 indexing."""
import argparse, ast, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

SKIP_CATEGORIES = {'generated', 'vendor', 'build_artifact'}

# JS/TS: import ... from '...' or require('...')
RE_JS_IMPORT_FROM = re.compile(r"""import\s+.*?from\s+['"]([^'"]+)['"]""")
RE_JS_REQUIRE     = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")
RE_JS_DYNAMIC     = re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""")

# Java: import org.foo.Bar;
RE_JAVA_IMPORT = re.compile(r'^\s*import\s+([\w.]+)\s*;')

# Go: import "pkg" or "pkg/sub"
RE_GO_IMPORT_SINGLE = re.compile(r'^\s*import\s+"([^"]+)"')
RE_GO_IMPORT_BLOCK  = re.compile(r'"([^"]+)"')

# Generic: #include <foo> or #include "foo"
RE_C_INCLUDE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]')


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


def parse_python_imports(source: str) -> tuple:
    """Return (imports, from_imports) lists. imports = module names. from_imports = 'module:symbol'."""
    imports = []
    from_imports = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise ValueError("Python SyntaxError")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            if node.names:
                for alias in node.names:
                    from_imports.append(f"{module}:{alias.name}")
            else:
                imports.append(module)

    return imports, from_imports


def parse_js_imports(source: str, language: str) -> tuple:
    imports = []
    from_imports = []

    for m in RE_JS_IMPORT_FROM.finditer(source):
        imports.append(m.group(1))
    for m in RE_JS_REQUIRE.finditer(source):
        imports.append(m.group(1))
    for m in RE_JS_DYNAMIC.finditer(source):
        imports.append(m.group(1))

    return imports, from_imports


def parse_java_imports(source: str) -> tuple:
    imports = []
    from_imports = []
    for line in source.splitlines():
        m = RE_JAVA_IMPORT.match(line)
        if m:
            full = m.group(1)
            # last component might be a class name
            parts = full.rsplit('.', 1)
            if len(parts) == 2 and parts[1][0].isupper():
                from_imports.append(f"{parts[0]}:{parts[1]}")
            else:
                imports.append(full)
    return imports, from_imports


def parse_go_imports(source: str) -> tuple:
    imports = []
    from_imports = []
    in_block = False
    for line in source.splitlines():
        if RE_GO_IMPORT_SINGLE.match(line):
            m = RE_GO_IMPORT_SINGLE.match(line)
            imports.append(m.group(1))
            continue
        stripped = line.strip()
        if stripped == 'import (':
            in_block = True
            continue
        if in_block:
            if stripped == ')':
                in_block = False
                continue
            m = RE_GO_IMPORT_BLOCK.search(stripped)
            if m:
                imports.append(m.group(1))
    return imports, from_imports


def parse_c_imports(source: str) -> tuple:
    imports = []
    from_imports = []
    for line in source.splitlines():
        m = RE_C_INCLUDE.match(line)
        if m:
            imports.append(m.group(1))
    return imports, from_imports


def extract_imports(source: str, language: str) -> tuple:
    if language == 'python':
        return parse_python_imports(source)
    elif language in ('javascript', 'typescript'):
        return parse_js_imports(source, language)
    elif language == 'java':
        return parse_java_imports(source)
    elif language == 'go':
        return parse_go_imports(source)
    elif language in ('c', 'cpp'):
        return parse_c_imports(source)
    else:
        return [], []


def main():
    parser = argparse.ArgumentParser(description="Build bronze/import-graph.json")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    output_path = bronze_dir / "import-graph.json"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    files_data = {}
    parse_error_count = 0
    parse_errors = []

    PARSEABLE_LANGUAGES = {
        'python', 'javascript', 'typescript', 'java', 'go', 'c', 'cpp'
    }

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

        if language not in PARSEABLE_LANGUAGES:
            continue

        try:
            source = abs_path.read_text(errors='replace')
            imports, from_imports = extract_imports(source, language)
            files_data[rel_str] = {
                "imports":      imports,
                "from_imports": from_imports,
            }
            if args.verbose:
                print(f"  {rel_str} [{language}] {len(imports)+len(from_imports)} imports", file=sys.stderr)

        except Exception as e:
            parse_error_count += 1
            files_data[rel_str] = {"imports": [], "from_imports": []}
            err = {"script": "build_import_graph", "file": rel_str, "error": str(e)}
            parse_errors.append(err)
            if args.verbose:
                print(f"  ERROR {rel_str}: {e}", file=sys.stderr)

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    result = {
        "files":   files_data,
        "summary": {
            "total_files":  len(files_data),
            "parse_errors": parse_error_count,
        }
    }

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Wrote {output_path} ({len(files_data)} files, {parse_error_count} errors)", file=sys.stderr)
    return 2 if parse_error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
