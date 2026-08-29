#!/usr/bin/env python3
"""Build bronze/symbol-index.jsonl — symbol catalogue extracted from source files."""
import argparse, ast, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

SKIP_CATEGORIES = {'generated', 'vendor', 'build_artifact'}

# Regex patterns for non-Python languages
RE_PATTERNS = {
    'javascript': [
        (r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)', 'function'),
        (r'^(?:export\s+)?class\s+(\w+)', 'class'),
        (r'^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(', 'function'),
    ],
    'typescript': [
        (r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)', 'function'),
        (r'^(?:export\s+)?class\s+(\w+)', 'class'),
        (r'^(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\(', 'function'),
        (r'^(?:export\s+)?interface\s+(\w+)', 'class'),
        (r'^(?:export\s+)?type\s+(\w+)\s*=', 'constant'),
    ],
    'java': [
        (r'^\s*(?:public|private|protected)?\s*(?:static\s+)?class\s+(\w+)', 'class'),
        (r'^\s*(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]*>)?)\s+(\w+)\s*\(', 'function'),
    ],
    'go': [
        (r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(', 'function'),
        (r'^type\s+(\w+)\s+struct', 'class'),
        (r'^type\s+(\w+)\s+interface', 'class'),
    ],
    'rust': [
        (r'^pub(?:\(.*?\))?\s+fn\s+(\w+)', 'function'),
        (r'^fn\s+(\w+)', 'function'),
        (r'^pub(?:\(.*?\))?\s+struct\s+(\w+)', 'class'),
        (r'^pub(?:\(.*?\))?\s+enum\s+(\w+)', 'class'),
        (r'^pub(?:\(.*?\))?\s+trait\s+(\w+)', 'class'),
    ],
    'csharp': [
        (r'^\s*(?:public|private|protected|internal)?\s*(?:static\s+)?class\s+(\w+)', 'class'),
        (r'^\s*(?:public|private|protected|internal)\s+(?:static\s+)?(?:\w+)\s+(\w+)\s*\(', 'function'),
    ],
    'ruby': [
        (r'^class\s+(\w+)', 'class'),
        (r'^\s*def\s+(\w+)', 'function'),
    ],
    'kotlin': [
        (r'^(?:data\s+)?class\s+(\w+)', 'class'),
        (r'^(?:fun\s+)(\w+)\s*\(', 'function'),
    ],
}


def visibility(name: str, language: str) -> str:
    if language == 'python':
        return 'private' if name.startswith('_') else 'public'
    if language == 'go':
        # Unexported symbols start with lowercase
        return 'public' if name and name[0].isupper() else 'private'
    return 'public'


def extract_python_symbols(source: str, rel_path: str) -> list:
    """Extract symbols from Python source using ast."""
    symbols = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return symbols

    for node in ast.iter_child_nodes(tree):
        # Top-level classes
        if isinstance(node, ast.ClassDef):
            end = getattr(node, 'end_lineno', node.lineno)
            symbols.append({
                "_name": node.name,
                "_kind": "class",
                "_line_start": node.lineno,
                "_line_end": end,
                "_parent": None,
            })
            # Methods
            for item in ast.iter_child_nodes(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    mend = getattr(item, 'end_lineno', item.lineno)
                    symbols.append({
                        "_name": item.name,
                        "_kind": "method",
                        "_line_start": item.lineno,
                        "_line_end": mend,
                        "_parent": node.name,
                    })

        # Top-level functions
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, 'end_lineno', node.lineno)
            symbols.append({
                "_name": node.name,
                "_kind": "function",
                "_line_start": node.lineno,
                "_line_end": end,
                "_parent": None,
            })

        # Module-level constants (UPPER_CASE assignments)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    symbols.append({
                        "_name": target.id,
                        "_kind": "constant",
                        "_line_start": node.lineno,
                        "_line_end": node.lineno,
                        "_parent": None,
                    })

    return symbols


def extract_regex_symbols(source: str, language: str) -> list:
    """Extract symbols from non-Python source using regex."""
    symbols = []
    patterns = RE_PATTERNS.get(language, [])
    if not patterns:
        return symbols

    lines = source.splitlines()
    for lineno, line in enumerate(lines, 1):
        for pattern, kind in patterns:
            m = re.match(pattern, line)
            if m:
                symbols.append({
                    "_name": m.group(1),
                    "_kind": kind,
                    "_line_start": lineno,
                    "_line_end": lineno,
                    "_parent": None,
                })
                break  # one match per line is enough
    return symbols


def load_inventory(bronze_dir: Path) -> dict:
    """Load file-inventory.jsonl to get language/category info."""
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


def should_skip_path(rel: Path) -> bool:
    return any(part in IGNORE_DIRS for part in rel.parts)


def main():
    parser = argparse.ArgumentParser(description="Build bronze/symbol-index.jsonl")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    output_path = bronze_dir / "symbol-index.jsonl"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    symbol_counter = 0
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

            # Only process known source-like languages
            if language not in {
                'python', 'javascript', 'typescript', 'java', 'go',
                'rust', 'csharp', 'ruby', 'kotlin', 'swift', 'php', 'cpp', 'c'
            }:
                continue

            try:
                source = abs_path.read_text(errors='replace')

                if language == 'python':
                    raw_symbols = extract_python_symbols(source, rel_str)
                else:
                    raw_symbols = extract_regex_symbols(source, language)

                if not raw_symbols:
                    # Emit a single module-level record
                    symbol_counter += 1
                    rec = {
                        "symbol_id":   f"SYM-{symbol_counter:06d}",
                        "file":        rel_str,
                        "line_start":  1,
                        "line_end":    source.count('\n') + 1,
                        "kind":        "module",
                        "name":        abs_path.stem,
                        "visibility":  "public",
                        "parent":      None,
                        "language":    language,
                    }
                    out_f.write(json.dumps(rec) + '\n')
                else:
                    for sym in raw_symbols:
                        symbol_counter += 1
                        rec = {
                            "symbol_id":   f"SYM-{symbol_counter:06d}",
                            "file":        rel_str,
                            "line_start":  sym["_line_start"],
                            "line_end":    sym["_line_end"],
                            "kind":        sym["_kind"],
                            "name":        sym["_name"],
                            "visibility":  visibility(sym["_name"], language),
                            "parent":      sym["_parent"],
                            "language":    language,
                        }
                        out_f.write(json.dumps(rec) + '\n')

                if args.verbose:
                    print(f"  {rel_str} [{language}] {len(raw_symbols)} symbols", file=sys.stderr)

            except Exception as e:
                error_count += 1
                err = {"script": "build_symbol_index", "file": rel_str, "error": str(e)}
                parse_errors.append(err)
                if args.verbose:
                    print(f"  ERROR {rel_str}: {e}", file=sys.stderr)

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    print(f"Wrote {output_path} ({symbol_counter} symbols, {error_count} errors)", file=sys.stderr)
    return 2 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
