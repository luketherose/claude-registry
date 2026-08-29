#!/usr/bin/env python3
"""Build bronze/io-boundaries.jsonl — I/O boundary catalogue for Phase 0 indexing."""
import argparse, json, re, sys
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

IGNORE_DIRS = {
    '.git', 'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
    '__pycache__', 'coverage', '.pytest_cache', '.mypy_cache', '.ruff_cache',
    '.next', '.angular', 'out', 'bin', 'obj', 'vendor', 'tmp', 'logs'
}

SKIP_CATEGORIES = {'generated', 'vendor', 'build_artifact'}

# ----- HTTP client patterns -----
RE_HTTP_PATTERNS = [
    # Python requests / httpx
    (re.compile(r"""\brequests\.(get|post|put|delete|patch|head|options)\s*\(\s*['"]([^'"]+)['"]"""), 'http_client', 'outbound'),
    (re.compile(r"""\brequests\.(get|post|put|delete|patch|head|options)\s*\("""),                     'http_client', 'outbound'),
    (re.compile(r"""\bhttpx\.(get|post|put|delete|patch|head|options)\s*\(\s*['"]([^'"]+)['"]"""),     'http_client', 'outbound'),
    (re.compile(r"""\bhttpx\.(get|post|put|delete|patch|head|options)\s*\("""),                        'http_client', 'outbound'),
    (re.compile(r"""\burllib\.request\.(urlopen|urlretrieve)\s*\("""),                                 'http_client', 'outbound'),
    # JS/TS fetch
    (re.compile(r"""\bfetch\s*\(\s*['"]([^'"]+)['"]"""),                                              'http_client', 'outbound'),
    (re.compile(r"""\bfetch\s*\("""),                                                                   'http_client', 'outbound'),
    # axios
    (re.compile(r"""\baxios\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]"""),                 'http_client', 'outbound'),
    (re.compile(r"""\baxios\.(get|post|put|delete|patch)\s*\("""),                                     'http_client', 'outbound'),
    # Java HttpClient / RestTemplate / WebClient
    (re.compile(r"""\bHttpClient\b|\bRestTemplate\b|\bWebClient\b"""),                                 'http_client', 'outbound'),
]

# ----- DB patterns -----
RE_DB_PATTERNS = [
    (re.compile(r"""\bpsycopg2\.connect\s*\("""),                                                      'database', 'outbound'),
    (re.compile(r"""\bsqlite3\.connect\s*\("""),                                                       'database', 'outbound'),
    (re.compile(r"""\bpymongo\.MongoClient\s*\("""),                                                   'database', 'outbound'),
    (re.compile(r"""\bsqlalchemy\.\w+|create_engine\s*\("""),                                          'database', 'outbound'),
    (re.compile(r"""\bconnect\s*\([^)]*(?:host|dbname|database|server)\s*="""),                        'database', 'outbound'),
    (re.compile(r"""\.execute\s*\(\s*['"](?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)""", re.IGNORECASE), 'database', 'outbound'),
    (re.compile(r"""\bcursor\s*\(\s*\)"""),                                                             'database', 'outbound'),
    # Java: DataSource, JdbcTemplate, EntityManager
    (re.compile(r"""\bDataSource\b|\bJdbcTemplate\b|\bEntityManager\b|\bHibernate\b"""),               'database', 'outbound'),
    # JS: mongoose, sequelize, knex, pg
    (re.compile(r"""\bmongoose\.connect\s*\(|\bsequelize\b|\bknex\s*\(|\bnew Pool\s*\("""),            'database', 'outbound'),
]

# ----- File I/O patterns -----
RE_FILE_PATTERNS = [
    (re.compile(r"""\bopen\s*\(\s*['"]([^'"]+)['"]"""),                                                'file_io', 'bidirectional'),
    (re.compile(r"""\bopen\s*\("""),                                                                    'file_io', 'bidirectional'),
    (re.compile(r"""Path\s*\([^)]*\)\.(read_text|read_bytes)\s*\("""),                                 'file_io', 'inbound'),
    (re.compile(r"""Path\s*\([^)]*\)\.(write_text|write_bytes)\s*\("""),                               'file_io', 'outbound'),
    (re.compile(r"""\.(read_text|read_bytes)\s*\(\s*\)"""),                                            'file_io', 'inbound'),
    (re.compile(r"""\.(write_text|write_bytes)\s*\("""),                                               'file_io', 'outbound'),
    (re.compile(r"""\bwith\s+open\s*\("""),                                                             'file_io', 'bidirectional'),
    # JS/TS fs
    (re.compile(r"""\bfs\.(readFile|readFileSync|writeFile|writeFileSync|createReadStream|createWriteStream)\s*\("""), 'file_io', 'bidirectional'),
]

# ----- Subprocess patterns -----
RE_SUBPROCESS_PATTERNS = [
    (re.compile(r"""\bsubprocess\.(run|Popen|call|check_output|check_call)\s*\("""),                   'subprocess', 'outbound'),
    (re.compile(r"""\bos\.system\s*\("""),                                                              'subprocess', 'outbound'),
    (re.compile(r"""\bos\.popen\s*\("""),                                                               'subprocess', 'outbound'),
    # JS
    (re.compile(r"""\bchild_process\.(exec|spawn|execSync|spawnSync)\s*\("""),                         'subprocess', 'outbound'),
    (re.compile(r"""\bexecSync\s*\(|\bspawn\s*\("""),                                                  'subprocess', 'outbound'),
]

# ----- Socket patterns -----
RE_SOCKET_PATTERNS = [
    (re.compile(r"""\bsocket\.connect\s*\("""),                                                        'socket', 'outbound'),
    (re.compile(r"""\bsocket\.bind\s*\("""),                                                           'socket', 'inbound'),
    (re.compile(r"""\bsocket\.socket\s*\("""),                                                         'socket', 'bidirectional'),
]

ALL_PATTERN_GROUPS = (
    RE_HTTP_PATTERNS,
    RE_DB_PATTERNS,
    RE_FILE_PATTERNS,
    RE_SUBPROCESS_PATTERNS,
    RE_SOCKET_PATTERNS,
)


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


def extract_target(m: re.Match) -> str | None:
    """Try to extract a URL or DB name from the first captured group."""
    try:
        grp = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
        if grp and len(grp) > 1:
            return grp
    except IndexError:
        pass
    return None


def scan_file(source: str, rel_str: str, counter: list) -> list:
    records = []
    lines = source.splitlines()
    seen = set()  # avoid duplicate records for the same (kind, line)

    for lineno, line in enumerate(lines, 1):
        for group in ALL_PATTERN_GROUPS:
            for pattern_tuple in group:
                regex, kind, direction = pattern_tuple
                m = regex.search(line)
                if m:
                    key = (kind, lineno, m.start())
                    if key in seen:
                        continue
                    seen.add(key)

                    target = extract_target(m)
                    counter[0] += 1
                    records.append({
                        "boundary_id": f"IO-{counter[0]:06d}",
                        "kind":        kind,
                        "direction":   direction,
                        "file":        rel_str,
                        "line":        lineno,
                        "target":      target,
                        "evidence_id": None,
                    })
    return records


SOURCE_LANGS = {
    'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'csharp',
    'ruby', 'kotlin', 'swift', 'php', 'cpp', 'c', 'shell'
}


def main():
    parser = argparse.ArgumentParser(description="Build bronze/io-boundaries.jsonl")
    parser.add_argument("--repo-root", required=True, help="Path to target repository")
    parser.add_argument("--output", required=True, help="Path to .indexing-kb/bronze/")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    bronze_dir = Path(args.output).resolve()
    bronze_dir.mkdir(parents=True, exist_ok=True)

    output_path = bronze_dir / "io-boundaries.jsonl"
    errors_path = bronze_dir / "parse-errors.jsonl"

    inventory = load_inventory(bronze_dir)
    counter = [0]
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

            if language not in SOURCE_LANGS:
                continue

            try:
                source = abs_path.read_text(errors='replace')
                records = scan_file(source, rel_str, counter)

                for rec in records:
                    out_f.write(json.dumps(rec) + '\n')
                total_records += len(records)

                if args.verbose and records:
                    print(f"  {rel_str} [{language}] {len(records)} I/O boundaries", file=sys.stderr)

            except Exception as e:
                error_count += 1
                err = {"script": "build_io_boundaries", "file": rel_str, "error": str(e)}
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
