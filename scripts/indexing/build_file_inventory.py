#!/usr/bin/env python3
"""Build bronze/file-inventory.jsonl and bronze/file-hashes.json — file catalogue for Phase 0 indexing."""
import argparse, hashlib, json, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

LANGUAGE_MAP = {
    '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'typescript',
    '.jsx': 'javascript', '.java': 'java', '.go': 'go', '.rs': 'rust',
    '.rb': 'ruby', '.php': 'php', '.cs': 'csharp', '.cpp': 'cpp', '.cc': 'cpp',
    '.c': 'c', '.h': 'c', '.hpp': 'cpp', '.kt': 'kotlin', '.swift': 'swift',
    '.sh': 'shell', '.bash': 'shell', '.zsh': 'shell',
    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.toml': 'toml',
    '.ini': 'ini', '.cfg': 'cfg', '.env': 'env', '.properties': 'properties',
    '.md': 'markdown', '.rst': 'rst', '.txt': 'text', '.pdf': 'pdf',
    '.html': 'html', '.css': 'css', '.scss': 'scss', '.sql': 'sql',
    '.xml': 'xml', '.proto': 'protobuf',
}

SOURCE_EXTS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs',
               '.rb', '.php', '.cs', '.cpp', '.cc', '.c', '.h', '.hpp',
               '.kt', '.swift'}
CONFIG_EXTS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.properties'}
DOCS_EXTS   = {'.md', '.rst', '.txt', '.pdf'}
BUILD_EXTS  = {'.pyc', '.class', '.o', '.so', '.a', '.dll', '.exe', '.pdb'}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return 'sha256:' + h.hexdigest()


def has_generated_header(path: Path) -> bool:
    """Check first 5 lines for generated markers."""
    try:
        with open(path, 'r', errors='replace') as f:
            head = ''.join(f.readline() for _ in range(5)).lower()
        return 'do not edit' in head or 'generated' in head
    except Exception:
        return False


def classify(path: Path, rel: Path) -> str:
    parts = rel.parts
    ext = path.suffix.lower()

    # vendor / build artifacts by extension
    if ext in BUILD_EXTS:
        return 'build_artifact'

    # vendor dirs already filtered by IGNORE_DIRS but handle in-tree vendor
    if any(p in ('vendor', 'node_modules', '__pycache__') for p in parts):
        return 'vendor'

    # generated dirs or generated header
    if any(p in ('generated', 'build', 'dist') for p in parts):
        if ext not in DOCS_EXTS:
            return 'generated'
    if ext in SOURCE_EXTS and has_generated_header(path):
        return 'generated'

    # test detection: name contains test/spec or is in test/tests dir
    name_lower = path.stem.lower()
    if ('test' in name_lower or 'spec' in name_lower or
            any(p in ('test', 'tests', 'spec', 'specs', '__tests__') for p in parts)):
        if ext in SOURCE_EXTS:
            return 'test'

    # config files
    if ext in CONFIG_EXTS:
        return 'config'
    name_full = path.name.lower()
    if name_full.startswith('.env') or name_full in ('dockerfile', 'makefile', 'justfile'):
        return 'config'

    # docs
    if ext in DOCS_EXTS:
        return 'docs'

    # source
    if ext in SOURCE_EXTS:
        return 'source'

    return 'unknown'


def count_lines(path: Path) -> int:
    try:
        with open(path, 'r', errors='replace') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def main():
    parser = argparse.ArgumentParser(description="Build bronze/file-inventory.jsonl and bronze/file-hashes.json")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    inventory_path = bronze_dir / "file-inventory.jsonl"
    hashes_path    = bronze_dir / "file-hashes.json"
    errors_path    = bronze_dir / "parse-errors.jsonl"

    file_hashes = {}
    parse_errors = []
    total = 0
    error_count = 0

    with open(inventory_path, 'w') as inv_f:
        for abs_path in sorted(repo_root.rglob('*')):
            if not abs_path.is_file():
                continue

            try:
                rel = abs_path.relative_to(repo_root)
            except ValueError:
                continue

            if should_skip(rel):
                continue

            try:
                size = abs_path.stat().st_size
                line_count = count_lines(abs_path)
                file_hash  = sha256_file(abs_path)
                language   = LANGUAGE_MAP.get(abs_path.suffix.lower(), 'unknown')
                category   = classify(abs_path, rel)

                record = {
                    "file":        str(rel),
                    "size_bytes":  size,
                    "line_count":  line_count,
                    "language":    language,
                    "category":    category,
                    "hash":        file_hash,
                }
                inv_f.write(json.dumps(record) + '\n')
                file_hashes[str(rel)] = file_hash
                total += 1

                if args.verbose:
                    print(f"  {rel} [{category}]", file=sys.stderr)

            except Exception as e:
                error_count += 1
                err = {"script": "build_file_inventory", "file": str(rel), "error": str(e)}
                parse_errors.append(err)
                if args.verbose:
                    print(f"  ERROR {rel}: {e}", file=sys.stderr)

    with open(hashes_path, 'w') as hf:
        json.dump(file_hashes, hf, indent=2)

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    print(f"Wrote {inventory_path} ({total} files, {error_count} errors)", file=sys.stderr)
    print(f"Wrote {hashes_path}", file=sys.stderr)

    return 2 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
