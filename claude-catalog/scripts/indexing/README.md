# Bronze KB Builder Scripts

Eight deterministic Python scripts that produce the `bronze/` KB artifacts for Phase 0 indexing. All scripts use only Python standard library modules (`ast`, `os`, `sys`, `json`, `hashlib`, `pathlib`, `re`, `argparse`, `datetime`, `subprocess`, `csv`, `io`).

---

## Purpose

Each script crawls the target repository and writes one or more JSON/JSONL output files into the `bronze/` directory. The outputs feed downstream agents (codebase-mapper, silver-layer builders, etc.) with structured, machine-readable facts about the codebase.

---

## Scripts

### 1. `build_file_inventory.py`

Crawls every file in the repository, skipping ignored directories, and records metadata for each file.

**Outputs:** `bronze/file-inventory.jsonl`, `bronze/file-hashes.json`

**Usage:**
```bash
python3 build_file_inventory.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Record fields:** `file`, `size_bytes`, `line_count`, `language`, `category`, `hash`

---

### 2. `build_symbol_index.py`

Extracts symbols (classes, functions, methods, constants) from source files. Uses the `ast` module for Python; regex heuristics for all other languages.

**Outputs:** `bronze/symbol-index.jsonl`

**Usage:**
```bash
python3 build_symbol_index.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Record fields:** `symbol_id`, `file`, `line_start`, `line_end`, `kind`, `name`, `visibility`, `parent`, `language`

**Requires:** `file-inventory.jsonl` must exist (reads language/category from it).

---

### 3. `build_import_graph.py`

Parses import statements to build a dependency graph across files. Handles Python (`ast`), JS/TS (regex), Java, Go, and C/C++.

**Outputs:** `bronze/import-graph.json`

**Usage:**
```bash
python3 build_import_graph.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Output shape:** `{"files": {"rel/path.py": {"imports": [...], "from_imports": [...]}}, "summary": {...}}`

**Requires:** `file-inventory.jsonl` must exist.

---

### 4. `build_config_env_index.py`

Detects environment variable reads and config key accesses across all source files, plus scans `.properties`, `.yml`, `.env` config files directly.

**Outputs:** `bronze/config-env-index.jsonl`

**Usage:**
```bash
python3 build_config_env_index.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Record fields:** `key_id`, `kind`, `name`, `file`, `line`, `access_type`, `default_value`, `evidence_id`

**Note on `evidence_id`:** Always `null` in this script. The downstream codebase-mapper agent fills it when emitting `evidence-ledger.jsonl`.

---

### 5. `build_io_boundaries.py`

Detects I/O boundaries: HTTP client calls, database connections, file I/O, subprocess calls, and socket usage.

**Outputs:** `bronze/io-boundaries.jsonl`

**Usage:**
```bash
python3 build_io_boundaries.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Record fields:** `boundary_id`, `kind`, `direction`, `file`, `line`, `target`, `evidence_id`

**Note on `evidence_id`:** Always `null` in this script; filled by codebase-mapper.

---

### 6. `build_test_inventory.py`

Discovers test files, classes, and functions across pytest, unittest, Jest, and JUnit.

**Outputs:** `bronze/test-inventory.jsonl`

**Usage:**
```bash
python3 build_test_inventory.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Record fields:** `test_id`, `file`, `framework`, `kind`, `name`, `line`

The last record is always a `SUMMARY` with aggregated counts per framework.

---

### 7. `build_large_file_index.py`

Identifies large files (>800 lines or >150 KB), classifies them, and produces semantic or line-window chunks for downstream analysis.

**Outputs:** `bronze/large-files.jsonl`, `bronze/large-file-chunks.jsonl`

**Usage:**
```bash
python3 build_large_file_index.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Thresholds:** large (>800 lines / >150 KB), huge (>2000 / >500 KB), giant (>5000 / >1 MB).

**Parse strategies:**
- `ast_semantic` — Python source: one chunk per top-level class or function
- `line_window` — other source: 200-line windows with 20-line overlap
- `data_profile` — data files: keys/columns profile only
- `excluded_generated / excluded_minified / excluded_vendor` — excluded with reason

---

### 8. `build_index_manifest.py`

Reads the outputs of all other scripts and writes a run manifest. Run this **last**.

**Outputs:** `bronze/manifest.json`

**Usage:**
```bash
python3 build_index_manifest.py --repo-root /path/to/repo --output /path/to/.indexing-kb/bronze/
```

**Content:** schema version, script version, run ID, git commit, file counts by category, list of bronze output files.

---

## Recommended run order

```bash
REPO=/path/to/target
OUT=/path/to/.indexing-kb/bronze

python3 build_file_inventory.py    --repo-root $REPO --output $OUT
python3 build_symbol_index.py      --repo-root $REPO --output $OUT
python3 build_import_graph.py      --repo-root $REPO --output $OUT
python3 build_config_env_index.py  --repo-root $REPO --output $OUT
python3 build_io_boundaries.py     --repo-root $REPO --output $OUT
python3 build_test_inventory.py    --repo-root $REPO --output $OUT
python3 build_large_file_index.py  --repo-root $REPO --output $OUT
python3 build_index_manifest.py    --repo-root $REPO --output $OUT   # always last
```

`build_index_manifest.py` must run last because it reads the counts and file list produced by all other scripts.

Scripts 2–7 read `file-inventory.jsonl` produced by script 1 to get language and category metadata. Run `build_file_inventory.py` first.

---

## parse-errors.jsonl

Every script appends parse errors to `bronze/parse-errors.jsonl` rather than crashing. Each record contains:

```json
{"script": "build_symbol_index", "file": "rel/path.py", "error": "Python SyntaxError"}
```

Exit codes:
- `0` — success, no errors
- `1` — fatal error (script could not start or write output)
- `2` — parse errors logged; output was still written

---

## evidence_id fields

The `evidence_id` field in `config-env-index.jsonl` and `io-boundaries.jsonl` records is always `null` when produced by these scripts. It is filled by the downstream **codebase-mapper** agent when it emits `evidence-ledger.jsonl`, linking each env/IO record back to the precise code evidence that justifies it.
