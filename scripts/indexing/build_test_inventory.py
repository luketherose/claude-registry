#!/usr/bin/env python3
"""Build bronze/test-inventory.jsonl — test catalogue for Phase 0 indexing."""
import argparse, ast, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

SKIP_CATEGORIES = {'generated', 'vendor', 'build_artifact'}

# ----- Jest patterns -----
RE_JEST_DESCRIBE = re.compile(r"""^\s*describe\s*\(\s*['"`]([^'"`]*)['"`]""")
RE_JEST_IT       = re.compile(r"""^\s*(?:it|test)\s*\(\s*['"`]([^'"`]*)['"`]""")

# ----- JUnit patterns -----
RE_JUNIT_TEST    = re.compile(r"""^\s*@Test\b""")
RE_JAVA_METHOD   = re.compile(r"""^\s*(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(""")

# ----- unittest.TestCase -----
RE_UNITTEST_CLASS = re.compile(r"""class\s+(\w+)\s*\(.*unittest\.TestCase""")


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


def is_test_file_python(rel: Path) -> bool:
    name = rel.name.lower()
    parts = rel.parts
    return (
        name.startswith('test_') or name.endswith('_test.py') or
        any(p in ('test', 'tests', 'spec', 'specs') for p in parts)
    )


def is_test_file_js(rel: Path) -> bool:
    name = rel.name.lower()
    return (
        name.endswith('.test.js') or name.endswith('.spec.js') or
        name.endswith('.test.ts') or name.endswith('.spec.ts') or
        name.endswith('.test.jsx') or name.endswith('.spec.jsx') or
        name.endswith('.test.tsx') or name.endswith('.spec.tsx')
    )


def is_test_file_java(rel: Path) -> bool:
    name = rel.name.lower()
    parts = rel.parts
    return (
        name.endswith('test.java') or name.endswith('tests.java') or
        'test' in name or
        any(p in ('test', 'tests') for p in parts)
    )


def extract_python_tests(source: str, rel_str: str, counter: list) -> list:
    """Extract pytest and unittest test items from Python source."""
    records = []

    # File-level record if this looks like a test file
    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise ValueError("Python SyntaxError during AST parse")

    for node in ast.iter_child_nodes(tree):
        # unittest.TestCase classes
        if isinstance(node, ast.ClassDef):
            # Check base classes for unittest.TestCase
            is_unittest = any(
                (isinstance(b, ast.Attribute) and b.attr == 'TestCase') or
                (isinstance(b, ast.Name) and b.id == 'TestCase')
                for b in node.bases
            )
            framework = 'unittest' if is_unittest else 'pytest'
            if node.name.startswith('Test') or is_unittest:
                counter[0] += 1
                records.append({
                    "test_id":   f"TEST-{counter[0]:06d}",
                    "file":      rel_str,
                    "framework": framework,
                    "kind":      "class",
                    "name":      node.name,
                    "line":      node.lineno,
                })
                # Methods inside test class
                for item in ast.iter_child_nodes(node):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name.startswith('test'):
                            counter[0] += 1
                            records.append({
                                "test_id":   f"TEST-{counter[0]:06d}",
                                "file":      rel_str,
                                "framework": framework,
                                "kind":      "function",
                                "name":      item.name,
                                "line":      item.lineno,
                            })

        # Top-level test functions (pytest style)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_') or node.name.startswith('test'):
                counter[0] += 1
                records.append({
                    "test_id":   f"TEST-{counter[0]:06d}",
                    "file":      rel_str,
                    "framework": "pytest",
                    "kind":      "function",
                    "name":      node.name,
                    "line":      node.lineno,
                })

    return records


def extract_js_tests(source: str, rel_str: str, counter: list) -> list:
    """Extract Jest test items from JS/TS source using regex."""
    records = []
    lines = source.splitlines()

    for lineno, line in enumerate(lines, 1):
        m = RE_JEST_DESCRIBE.match(line)
        if m:
            counter[0] += 1
            records.append({
                "test_id":   f"TEST-{counter[0]:06d}",
                "file":      rel_str,
                "framework": "jest",
                "kind":      "class",
                "name":      m.group(1),
                "line":      lineno,
            })
            continue

        m = RE_JEST_IT.match(line)
        if m:
            counter[0] += 1
            records.append({
                "test_id":   f"TEST-{counter[0]:06d}",
                "file":      rel_str,
                "framework": "jest",
                "kind":      "function",
                "name":      m.group(1),
                "line":      lineno,
            })

    return records


def extract_java_tests(source: str, rel_str: str, counter: list) -> list:
    """Extract JUnit test methods from Java source using regex."""
    records = []
    lines = source.splitlines()
    next_is_test = False

    for lineno, line in enumerate(lines, 1):
        if RE_JUNIT_TEST.match(line):
            next_is_test = True
            continue
        if next_is_test:
            m = RE_JAVA_METHOD.match(line)
            if m:
                counter[0] += 1
                records.append({
                    "test_id":   f"TEST-{counter[0]:06d}",
                    "file":      rel_str,
                    "framework": "junit",
                    "kind":      "function",
                    "name":      m.group(1),
                    "line":      lineno,
                })
            next_is_test = False

    return records


def main():
    parser = argparse.ArgumentParser(description="Build bronze/test-inventory.jsonl")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    output_path = bronze_dir / "test-inventory.jsonl"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    counter = [0]
    total_records = 0
    error_count = 0
    parse_errors = []
    framework_counts: dict = {}
    test_file_count = 0

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

            # Determine if this is a test file at all
            is_test = False
            if language == 'python' and is_test_file_python(rel):
                is_test = True
            elif language in ('javascript', 'typescript') and is_test_file_js(rel):
                is_test = True
            elif language == 'java' and is_test_file_java(rel):
                is_test = True

            if not is_test:
                continue

            test_file_count += 1
            # Emit a file-level record
            file_framework = (
                'pytest' if language == 'python' else
                'jest'   if language in ('javascript', 'typescript') else
                'junit'  if language == 'java' else
                'unknown'
            )
            counter[0] += 1
            file_rec = {
                "test_id":   f"TEST-{counter[0]:06d}",
                "file":      rel_str,
                "framework": file_framework,
                "kind":      "file",
                "name":      abs_path.name,
                "line":      1,
            }
            out_f.write(json.dumps(file_rec) + '\n')
            total_records += 1
            framework_counts[file_framework] = framework_counts.get(file_framework, 0) + 1

            try:
                source = abs_path.read_text(errors='replace')

                if language == 'python':
                    records = extract_python_tests(source, rel_str, counter)
                elif language in ('javascript', 'typescript'):
                    records = extract_js_tests(source, rel_str, counter)
                elif language == 'java':
                    records = extract_java_tests(source, rel_str, counter)
                else:
                    records = []

                for rec in records:
                    out_f.write(json.dumps(rec) + '\n')
                total_records += len(records)

                if args.verbose:
                    print(f"  {rel_str} [{file_framework}] {len(records)} test items", file=sys.stderr)

            except Exception as e:
                error_count += 1
                err = {"script": "build_test_inventory", "file": rel_str, "error": str(e)}
                parse_errors.append(err)
                if args.verbose:
                    print(f"  ERROR {rel_str}: {e}", file=sys.stderr)

        # Write summary record
        summary_rec = {
            "test_id":        "SUMMARY",
            "kind":           "summary",
            "total_test_files": test_file_count,
            "total_records":  total_records,
            "by_framework":   framework_counts,
        }
        out_f.write(json.dumps(summary_rec) + '\n')

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    print(f"Wrote {output_path} ({total_records} records across {test_file_count} test files, {error_count} errors)", file=sys.stderr)
    return 2 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
