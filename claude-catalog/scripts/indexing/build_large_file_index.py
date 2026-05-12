#!/usr/bin/env python3
"""Build bronze/large-files.jsonl and bronze/large-file-chunks.jsonl — large file analysis for Phase 0 indexing."""
import argparse, ast, csv, hashlib, io, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

# Size thresholds
THRESHOLD_LARGE = (800, 150_000)      # (lines, bytes)
THRESHOLD_HUGE  = (2000, 500_000)
THRESHOLD_GIANT = (5000, 1_000_000)

# Chunk parameters
CHUNK_WINDOW  = 200
CHUNK_OVERLAP = 20

DATA_EXTS   = {'.json', '.csv', '.xml', '.ndjson', '.jsonl'}
SOURCE_EXTS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs',
               '.rb', '.php', '.cs', '.cpp', '.cc', '.c', '.h', '.hpp',
               '.kt', '.swift'}


def sha256_str(text: str) -> str:
    return 'sha256:' + hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()


def safe_path_id(rel_str: str) -> str:
    """Convert a relative path to a safe ID component."""
    return re.sub(r'[^a-zA-Z0-9]', '-', rel_str)


def size_tier(line_count: int, size_bytes: int) -> str:
    if line_count >= THRESHOLD_GIANT[0] or size_bytes >= THRESHOLD_GIANT[1]:
        return 'giant'
    if line_count >= THRESHOLD_HUGE[0] or size_bytes >= THRESHOLD_HUGE[1]:
        return 'huge'
    if line_count >= THRESHOLD_LARGE[0] or size_bytes >= THRESHOLD_LARGE[1]:
        return 'large'
    return 'normal'


def has_generated_marker(text: str) -> bool:
    head = text[:2000].lower()
    return 'do not edit' in head or '# generated' in head or '// generated' in head


def is_minified(text: str, size_bytes: int) -> bool:
    """Single long line heuristic."""
    if size_bytes < 10_000:
        return False
    lines = text.splitlines()
    if not lines:
        return False
    max_len = max(len(l) for l in lines)
    return max_len > 10_000


def classify_large_file(rel: Path, text: str, size_bytes: int, category: str) -> str:
    """Return: generated | minified | data | vendor | source."""
    parts = rel.parts
    if any(p in ('vendor', 'node_modules', '__pycache__') for p in parts):
        return 'vendor'
    if category in ('vendor',):
        return 'vendor'
    if rel.suffix.lower() in DATA_EXTS:
        return 'data'
    if is_minified(text, size_bytes):
        return 'minified'
    if has_generated_marker(text):
        return 'generated'
    return 'source'


def profile_json(text: str) -> dict:
    """Return top-level keys count for JSON."""
    try:
        obj = json.loads(text[:500_000])  # limit to avoid giant parse
        if isinstance(obj, dict):
            return {"type": "object", "top_level_keys": list(obj.keys())[:20]}
        if isinstance(obj, list):
            return {"type": "array", "length": len(obj)}
    except Exception:
        pass
    return {"type": "unknown"}


def profile_csv(text: str) -> dict:
    """Return columns and row count estimate."""
    try:
        reader = csv.reader(io.StringIO(text[:100_000]))
        rows = list(reader)
        if rows:
            return {"columns": rows[0], "sample_rows": len(rows) - 1}
    except Exception:
        pass
    return {"columns": [], "sample_rows": 0}


def chunk_python_ast(source: str, rel_str: str, safe_id: str) -> list:
    """Create semantic chunks for Python: one chunk per top-level class/function."""
    chunks = []
    seq = 0

    try:
        tree = ast.parse(source)
    except SyntaxError:
        raise ValueError("Python SyntaxError")

    lines = source.splitlines()

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            line_start = node.lineno
            line_end   = getattr(node, 'end_lineno', node.lineno)
            chunk_text = '\n'.join(lines[line_start - 1:line_end])
            kind = 'class' if isinstance(node, ast.ClassDef) else 'function'
            seq += 1
            chunks.append({
                "chunk_id":   f"CHUNK-{safe_id}-{seq:04d}",
                "file":       rel_str,
                "lines":      f"{line_start}-{line_end}",
                "kind":       kind,
                "symbols":    [node.name],
                "hash":       sha256_str(chunk_text),
                "summary":    f"{kind} {node.name} ({line_end - line_start + 1} lines)",
                "evidence_id": None,
            })

    return chunks


def chunk_line_windows(source: str, rel_str: str, safe_id: str) -> list:
    """Create line-window chunks with overlap."""
    chunks = []
    lines = source.splitlines()
    total = len(lines)
    seq = 0
    pos = 0

    while pos < total:
        end = min(pos + CHUNK_WINDOW, total)
        chunk_lines = lines[pos:end]
        chunk_text = '\n'.join(chunk_lines)
        seq += 1
        chunks.append({
            "chunk_id":   f"CHUNK-{safe_id}-{seq:04d}",
            "file":       rel_str,
            "lines":      f"{pos + 1}-{end}",
            "kind":       "line_window",
            "symbols":    [],
            "hash":       sha256_str(chunk_text),
            "summary":    f"Lines {pos + 1}-{end} of {total}",
            "evidence_id": None,
        })
        # advance with overlap
        pos = end - CHUNK_OVERLAP
        if pos >= total or end == total:
            break

    return chunks


def chunk_data_profile(source: str, rel_str: str, safe_id: str, ext: str) -> list:
    """Produce a single data profile chunk."""
    if ext == '.json':
        profile = profile_json(source)
    elif ext == '.csv':
        profile = profile_csv(source)
    else:
        profile = {"type": ext.lstrip('.')}

    return [{
        "chunk_id":   f"CHUNK-{safe_id}-0001",
        "file":       rel_str,
        "lines":      f"1-{source.count(chr(10)) + 1}",
        "kind":       "data_sample",
        "symbols":    [],
        "hash":       sha256_str(source[:1024]),
        "summary":    f"Data file profile: {json.dumps(profile)}",
        "evidence_id": None,
    }]


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


def main():
    parser = argparse.ArgumentParser(description="Build bronze/large-files.jsonl and bronze/large-file-chunks.jsonl")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    lf_path     = bronze_dir / "large-files.jsonl"
    chunks_path = bronze_dir / "large-file-chunks.jsonl"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    large_count = 0
    chunk_count = 0
    error_count = 0
    parse_errors = []

    with open(lf_path, 'w') as lf_f, open(chunks_path, 'w') as ch_f:
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
            line_count = inv_rec.get("line_count", 0)
            size_bytes = inv_rec.get("size_bytes", abs_path.stat().st_size)

            tier = size_tier(line_count, size_bytes)
            if tier == 'normal':
                continue

            large_count += 1
            safe_id = safe_path_id(rel_str)

            # Build the large-file record skeleton
            lf_rec = {
                "file":           rel_str,
                "size_bytes":     size_bytes,
                "line_count":     line_count,
                "tier":           tier,
                "language":       language,
                "category":       category,
                "file_type":      None,
                "parse_strategy": None,
                "status":         "ok",
                "excluded_reason": None,
            }

            try:
                source = abs_path.read_text(errors='replace')
                file_type = classify_large_file(rel, source, size_bytes, category)
                lf_rec["file_type"] = file_type

                if file_type in ('generated', 'minified', 'vendor'):
                    lf_rec["parse_strategy"] = "excluded_" + file_type
                    lf_rec["status"] = "excluded_with_reason"
                    lf_rec["excluded_reason"] = file_type
                    # Still emit a chunk record to mark it excluded
                    chunk_rec = {
                        "chunk_id":   f"CHUNK-{safe_id}-0001",
                        "file":       rel_str,
                        "lines":      f"1-{line_count}",
                        "kind":       "excluded",
                        "symbols":    [],
                        "hash":       None,
                        "summary":    f"Excluded: {file_type}",
                        "evidence_id": None,
                        "status":     "excluded_with_reason",
                    }
                    ch_f.write(json.dumps(chunk_rec) + '\n')
                    chunk_count += 1

                elif file_type == 'data':
                    lf_rec["parse_strategy"] = "data_profile"
                    chunks = chunk_data_profile(source, rel_str, safe_id, rel.suffix.lower())
                    for c in chunks:
                        ch_f.write(json.dumps(c) + '\n')
                    chunk_count += len(chunks)

                elif file_type == 'source' and language == 'python':
                    lf_rec["parse_strategy"] = "ast_semantic"
                    try:
                        chunks = chunk_python_ast(source, rel_str, safe_id)
                        if not chunks:
                            # Fall back to line windows if no top-level items found
                            chunks = chunk_line_windows(source, rel_str, safe_id)
                            lf_rec["parse_strategy"] = "line_window_fallback"
                    except ValueError:
                        chunks = chunk_line_windows(source, rel_str, safe_id)
                        lf_rec["parse_strategy"] = "line_window_fallback"

                    for c in chunks:
                        ch_f.write(json.dumps(c) + '\n')
                    chunk_count += len(chunks)

                else:
                    lf_rec["parse_strategy"] = "line_window"
                    chunks = chunk_line_windows(source, rel_str, safe_id)
                    for c in chunks:
                        ch_f.write(json.dumps(c) + '\n')
                    chunk_count += len(chunks)

                if args.verbose:
                    print(f"  {rel_str} [{tier}] {lf_rec['parse_strategy']} -> {chunk_count} chunks so far", file=sys.stderr)

            except Exception as e:
                error_count += 1
                lf_rec["status"] = "parse_failed"
                lf_rec["excluded_reason"] = str(e)
                err = {"script": "build_large_file_index", "file": rel_str, "error": str(e)}
                parse_errors.append(err)
                if args.verbose:
                    print(f"  ERROR {rel_str}: {e}", file=sys.stderr)

            lf_f.write(json.dumps(lf_rec) + '\n')

    if parse_errors:
        with open(errors_path, 'a') as ef:
            for err in parse_errors:
                ef.write(json.dumps(err) + '\n')

    print(f"Wrote {lf_path} ({large_count} large files)", file=sys.stderr)
    print(f"Wrote {chunks_path} ({chunk_count} chunks, {error_count} errors)", file=sys.stderr)
    return 2 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
