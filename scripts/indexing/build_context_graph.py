#!/usr/bin/env python3
"""
build_context_graph.py — builds the evidence-backed context graph in .indexing-kb/graph/.

Reads bronze/, silver/, evidence-ledger.jsonl and produces:
  graph/nodes.jsonl
  graph/edges.jsonl
  graph/aliases.jsonl
  graph/retrieval-index.json
  graph/graph-quality-report.md

Usage:
  python3 build_context_graph.py --kb-root /path/to/.indexing-kb/ [--verbose]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node_id(node_type: str, label: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_\-./]", "-", label)
    return f"{node_type}-{safe}"


def _edge_id(counter: list) -> str:
    counter[0] += 1
    return f"EDGE-{counter[0]:06d}"


def _make_node(node_type: str, label: str, **kwargs) -> dict:
    node = {
        "node_id": _node_id(node_type, label),
        "type": node_type,
        "label": label,
        "file": kwargs.get("file"),
        "lines": kwargs.get("lines"),
        "evidence_ids": kwargs.get("evidence_ids", []),
        "tags": kwargs.get("tags", []),
        "confidence": kwargs.get("confidence", "high"),
        "origin": kwargs.get("origin", "deterministic_scan"),
    }
    return node


def _make_edge(counter: list, source: str, target: str, edge_type: str, **kwargs) -> dict:
    return {
        "edge_id": _edge_id(counter),
        "source": source,
        "target": target,
        "type": edge_type,
        "evidence_ids": kwargs.get("evidence_ids", []),
        "confidence": kwargs.get("confidence", "high"),
        "origin": kwargs.get("origin", "deterministic_scan"),
        "status": kwargs.get("status", "confirmed"),
        "inference_level": kwargs.get("inference_level", "direct"),
    }


def _read_jsonl(path: Path) -> list:
    records = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def _read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return default


def _write_jsonl(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Build nodes from bronze sources
# ---------------------------------------------------------------------------

def build_file_nodes(bronze: Path, verbose: bool) -> dict:
    """Return {node_id: node} for every file in file-inventory.jsonl."""
    nodes = {}
    for rec in _read_jsonl(bronze / "file-inventory.jsonl"):
        rel = rec.get("path") or rec.get("file") or rec.get("rel_path")
        if not rel:
            continue
        evidence_ids = rec.get("evidence_ids", [])
        if rec.get("evidence_id"):
            evidence_ids = [rec["evidence_id"]] + evidence_ids
        n = _make_node(
            "File",
            rel,
            file=rel,
            lines=rec.get("lines") or rec.get("line_count"),
            evidence_ids=evidence_ids,
            tags=rec.get("tags", []),
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  File nodes: {len(nodes)}")
    return nodes


def build_symbol_nodes(bronze: Path, verbose: bool) -> dict:
    """Return {node_id: node} for every symbol in symbol-index.jsonl."""
    nodes = {}
    for rec in _read_jsonl(bronze / "symbol-index.jsonl"):
        name = rec.get("name") or rec.get("symbol")
        if not name:
            continue
        file_path = rec.get("file") or rec.get("path")
        label = f"{file_path}::{name}" if file_path else name
        evidence_ids = rec.get("evidence_ids", [])
        if rec.get("evidence_id"):
            evidence_ids = [rec["evidence_id"]] + evidence_ids
        n = _make_node(
            "SYM",
            label,
            file=file_path,
            lines=rec.get("line") or rec.get("lineno"),
            evidence_ids=evidence_ids,
            tags=rec.get("tags", []) + ([rec["kind"]] if rec.get("kind") else []),
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  Symbol nodes: {len(nodes)}")
    return nodes


def build_package_nodes(bronze: Path, verbose: bool) -> dict:
    nodes = {}
    dep_locks = _read_json(bronze / "dependency-locks.json", default={})
    for pkg_name, pkg_info in (dep_locks.get("packages") or {}).items():
        if not pkg_name:
            continue
        n = _make_node(
            "PKG",
            pkg_name,
            tags=["external"],
            confidence="high",
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  Package nodes: {len(nodes)}")
    return nodes


def build_route_nodes(bronze: Path, verbose: bool) -> dict:
    nodes = {}
    routes_data = _read_json(bronze / "routes.json", default=None)
    if routes_data is None:
        return nodes
    items = routes_data if isinstance(routes_data, list) else routes_data.get("routes", [])
    for rec in items:
        path = rec.get("path") or rec.get("route")
        if not path:
            continue
        n = _make_node(
            "Route",
            path,
            file=rec.get("file"),
            evidence_ids=rec.get("evidence_ids", []),
            tags=[rec["method"]] if rec.get("method") else [],
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  Route nodes: {len(nodes)}")
    return nodes


def build_ui_surface_nodes(bronze: Path, verbose: bool) -> dict:
    nodes = {}
    ui_data = _read_json(bronze / "ui-surfaces.json", default=None)
    if ui_data is None:
        return nodes
    items = ui_data if isinstance(ui_data, list) else ui_data.get("surfaces", [])
    for rec in items:
        label = rec.get("name") or rec.get("page") or rec.get("surface")
        if not label:
            continue
        n = _make_node(
            "UISurface",
            label,
            file=rec.get("file"),
            evidence_ids=rec.get("evidence_ids", []),
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  UISurface nodes: {len(nodes)}")
    return nodes


def build_env_var_nodes(bronze: Path, verbose: bool) -> dict:
    nodes = {}
    for rec in _read_jsonl(bronze / "config-env-index.jsonl"):
        var_name = rec.get("name") or rec.get("key") or rec.get("env_var")
        if not var_name:
            continue
        n = _make_node(
            "EnvVar",
            var_name,
            file=rec.get("file"),
            evidence_ids=rec.get("evidence_ids", []),
            tags=["env"],
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  EnvVar nodes: {len(nodes)}")
    return nodes


def build_io_boundary_nodes(bronze: Path, verbose: bool) -> dict:
    nodes = {}
    for rec in _read_jsonl(bronze / "io-boundaries.jsonl"):
        label = rec.get("target") or rec.get("endpoint") or rec.get("name")
        if not label:
            continue
        n = _make_node(
            "IOBoundary",
            label,
            file=rec.get("file"),
            evidence_ids=rec.get("evidence_ids", []),
            tags=[rec["direction"]] if rec.get("direction") else [],
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  IOBoundary nodes: {len(nodes)}")
    return nodes


def build_evidence_nodes(ledger_path: Path, verbose: bool) -> dict:
    nodes = {}
    for rec in _read_jsonl(ledger_path):
        eid = rec.get("evidence_id")
        if not eid:
            continue
        n = _make_node(
            "Evidence",
            eid,
            file=rec.get("file") or rec.get("source_file"),
            evidence_ids=[eid],
            tags=[rec["kind"]] if rec.get("kind") else [],
            confidence=rec.get("confidence", "high"),
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  Evidence nodes: {len(nodes)}")
    return nodes


def build_business_rule_nodes(silver_path: Path, verbose: bool) -> dict:
    nodes = {}
    for rec in _read_jsonl(silver_path / "business-rules.jsonl"):
        label = rec.get("rule_id") or rec.get("id") or rec.get("name")
        if not label:
            continue
        n = _make_node(
            "BusinessRule",
            label,
            file=rec.get("file"),
            evidence_ids=rec.get("evidence_ids", []),
            confidence=rec.get("confidence", "medium"),
        )
        nodes[n["node_id"]] = n
    if verbose:
        print(f"  BusinessRule nodes: {len(nodes)}")
    return nodes


# ---------------------------------------------------------------------------
# Build edges
# ---------------------------------------------------------------------------

def build_contains_edges(file_nodes: dict, symbol_nodes: dict, counter: list) -> list:
    """CONTAINS: File → Symbol based on matching file path."""
    edges = []
    # Build a map: file_label -> file_node_id
    file_label_map = {n["label"]: nid for nid, n in file_nodes.items()}

    for nid, sym in symbol_nodes.items():
        file_path = sym.get("file")
        if not file_path:
            continue
        file_nid = file_label_map.get(file_path)
        if not file_nid:
            file_nid = f"FILE-{re.sub(r'[^a-zA-Z0-9_\\-./]', '-', file_path)}"
            if file_nid not in file_nodes:
                continue
        edges.append(_make_edge(counter, file_nid, nid, "CONTAINS"))
    return edges


def build_import_edges(bronze: Path, file_nodes: dict, counter: list) -> list:
    """IMPORTS: File → File from import-graph.json."""
    edges = []
    import_graph = _read_json(bronze / "import-graph.json", default=None)
    if import_graph is None:
        return edges

    # Support both dict-of-lists and list-of-dicts formats
    if isinstance(import_graph, dict):
        items = import_graph.get("imports") or import_graph
        if isinstance(items, dict):
            for src_file, targets in items.items():
                src_nid = _node_id("FILE", src_file)
                if src_nid not in file_nodes:
                    continue
                if isinstance(targets, list):
                    for tgt in targets:
                        tgt_file = tgt if isinstance(tgt, str) else tgt.get("file") or tgt.get("path")
                        if not tgt_file:
                            continue
                        tgt_nid = _node_id("FILE", tgt_file)
                        if tgt_nid not in file_nodes:
                            continue
                        edges.append(_make_edge(counter, src_nid, tgt_nid, "IMPORTS"))
    elif isinstance(import_graph, list):
        for rec in import_graph:
            src = rec.get("source") or rec.get("file")
            tgt = rec.get("target") or rec.get("imports")
            if not src or not tgt:
                continue
            if isinstance(tgt, str):
                targets = [tgt]
            elif isinstance(tgt, list):
                targets = tgt
            else:
                continue
            src_nid = _node_id("FILE", src)
            if src_nid not in file_nodes:
                continue
            for t in targets:
                tgt_file = t if isinstance(t, str) else t.get("file") or t.get("path")
                if not tgt_file:
                    continue
                tgt_nid = _node_id("FILE", tgt_file)
                if tgt_nid not in file_nodes:
                    continue
                edges.append(_make_edge(counter, src_nid, tgt_nid, "IMPORTS"))
    return edges


def build_reads_env_edges(bronze: Path, symbol_nodes: dict, env_var_nodes: dict, counter: list) -> list:
    """READS_ENV: Symbol → EnvVar from config-env-index.jsonl."""
    edges = []
    for rec in _read_jsonl(bronze / "config-env-index.jsonl"):
        var_name = rec.get("name") or rec.get("key") or rec.get("env_var")
        reader_sym = rec.get("reader") or rec.get("symbol") or rec.get("used_by")
        if not var_name or not reader_sym:
            continue
        tgt_nid = _node_id("EnvVar", var_name)
        if tgt_nid not in env_var_nodes:
            continue
        # Try to find the symbol
        for snid in symbol_nodes:
            if reader_sym in snid:
                edges.append(_make_edge(counter, snid, tgt_nid, "READS_ENV"))
                break
    return edges


def build_calls_external_edges(bronze: Path, symbol_nodes: dict, io_nodes: dict, counter: list) -> list:
    """CALLS_EXTERNAL: Symbol → IOBoundary from io-boundaries.jsonl."""
    edges = []
    for rec in _read_jsonl(bronze / "io-boundaries.jsonl"):
        target = rec.get("target") or rec.get("endpoint") or rec.get("name")
        caller = rec.get("caller") or rec.get("symbol") or rec.get("function")
        if not target:
            continue
        tgt_nid = _node_id("IOBoundary", target)
        if tgt_nid not in io_nodes:
            continue
        if caller:
            for snid in symbol_nodes:
                if caller in snid:
                    edges.append(_make_edge(counter, snid, tgt_nid, "CALLS_EXTERNAL"))
                    break
        else:
            # fallback: link source file node if file is known
            file_path = rec.get("file")
            if file_path:
                file_nid = _node_id("FILE", file_path)
                edges.append(_make_edge(counter, file_nid, tgt_nid, "CALLS_EXTERNAL",
                                        inference_level="inferred"))
    return edges


def build_exposes_route_edges(bronze: Path, file_nodes: dict, route_nodes: dict, counter: list) -> list:
    """EXPOSES_ROUTE: File → Route from routes.json."""
    edges = []
    routes_data = _read_json(bronze / "routes.json", default=None)
    if routes_data is None:
        return edges
    items = routes_data if isinstance(routes_data, list) else routes_data.get("routes", [])
    for rec in items:
        route_path = rec.get("path") or rec.get("route")
        file_path = rec.get("file")
        if not route_path or not file_path:
            continue
        src_nid = _node_id("FILE", file_path)
        tgt_nid = _node_id("Route", route_path)
        if src_nid in file_nodes and tgt_nid in route_nodes:
            edges.append(_make_edge(counter, src_nid, tgt_nid, "EXPOSES_ROUTE"))
    return edges


def build_renders_ui_edges(bronze: Path, file_nodes: dict, ui_nodes: dict, counter: list) -> list:
    """RENDERS_UI: File → UISurface from ui-surfaces.json."""
    edges = []
    ui_data = _read_json(bronze / "ui-surfaces.json", default=None)
    if ui_data is None:
        return edges
    items = ui_data if isinstance(ui_data, list) else ui_data.get("surfaces", [])
    for rec in items:
        label = rec.get("name") or rec.get("page") or rec.get("surface")
        file_path = rec.get("file")
        if not label or not file_path:
            continue
        src_nid = _node_id("FILE", file_path)
        tgt_nid = _node_id("UISurface", label)
        if src_nid in file_nodes and tgt_nid in ui_nodes:
            edges.append(_make_edge(counter, src_nid, tgt_nid, "RENDERS_UI"))
    return edges


def build_cites_evidence_edges(symbol_nodes: dict, evidence_nodes: dict, counter: list) -> list:
    """CITES_EVIDENCE: Symbol → Evidence via evidence_ids on symbol records."""
    edges = []
    for snid, sym in symbol_nodes.items():
        for eid in sym.get("evidence_ids", []):
            tgt_nid = _node_id("Evidence", eid)
            if tgt_nid in evidence_nodes:
                edges.append(_make_edge(counter, snid, tgt_nid, "CITES_EVIDENCE",
                                        inference_level="direct"))
    return edges


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------

def build_aliases(all_nodes: dict) -> list:
    """Build short-name aliases for common lookups."""
    aliases = []
    for nid, node in all_nodes.items():
        label = node.get("label", "")
        if node["type"] == "File":
            # basename alias
            basename = Path(label).name
            if basename and basename != label:
                aliases.append({"alias": basename, "node_id": nid, "source": "basename"})
        elif node["type"] == "SYM":
            # symbol name alias (strip file prefix)
            if "::" in label:
                sym_name = label.split("::")[-1]
                aliases.append({"alias": sym_name, "node_id": nid, "source": "symbol_name"})
    return aliases


# ---------------------------------------------------------------------------
# Retrieval index
# ---------------------------------------------------------------------------

def build_retrieval_index(all_nodes: dict, all_edges: list) -> dict:
    """Build a simple retrieval index: type → [node_ids], node_id → neighbour_ids."""
    type_index: dict = defaultdict(list)
    adjacency: dict = defaultdict(list)

    for nid, node in all_nodes.items():
        type_index[node["type"]].append(nid)

    for edge in all_edges:
        adjacency[edge["source"]].append(edge["target"])
        adjacency[edge["target"]].append(edge["source"])

    return {
        "by_type": dict(type_index),
        "adjacency": {k: list(set(v)) for k, v in adjacency.items()},
    }


# ---------------------------------------------------------------------------
# Quality report
# ---------------------------------------------------------------------------

def build_quality_report(all_nodes: dict, all_edges: list, file_nodes: dict) -> str:
    node_type_counts: dict = defaultdict(int)
    for n in all_nodes.values():
        node_type_counts[n["type"]] += 1

    edge_type_counts: dict = defaultdict(int)
    for e in all_edges:
        edge_type_counts[e["type"]] += 1

    # Orphan nodes: nodes with no edges
    connected = set()
    for e in all_edges:
        connected.add(e["source"])
        connected.add(e["target"])
    orphans = [nid for nid in all_nodes if nid not in connected]

    # Verdict: fraction of files that have at least 1 node (a File node IS the file)
    total_files = len(file_nodes)
    if total_files == 0:
        verdict = "FAIL"
        coverage_pct = 0.0
    else:
        coverage_pct = 100.0 * len(file_nodes) / total_files
        if coverage_pct >= 80:
            verdict = "PASS"
        elif coverage_pct >= 50:
            verdict = "PASS_WITH_GAPS"
        else:
            verdict = "FAIL"

    lines = [
        "# Graph Quality Report",
        "",
        "## Node counts by type",
        "",
    ]
    for ntype, cnt in sorted(node_type_counts.items()):
        lines.append(f"- **{ntype}**: {cnt}")

    lines += [
        "",
        "## Edge counts by type",
        "",
    ]
    for etype, cnt in sorted(edge_type_counts.items()):
        lines.append(f"- **{etype}**: {cnt}")

    lines += [
        "",
        "## Summary",
        "",
        f"- Total nodes: {len(all_nodes)}",
        f"- Total edges: {len(all_edges)}",
        f"- Orphan nodes (no edges): {len(orphans)}",
        f"- File coverage: {coverage_pct:.1f}% ({len(file_nodes)}/{total_files} files have a node)",
        "",
        f"## Verdict: {verdict}",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build the evidence-backed context graph from .indexing-kb/ bronze/silver data."
    )
    parser.add_argument("--kb-root", required=True, help="Path to .indexing-kb/ directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    kb_root = Path(args.kb_root).resolve()
    bronze = kb_root / "bronze"
    silver = kb_root / "silver"
    graph_dir = kb_root / "graph"
    ledger_path = kb_root / "evidence-ledger.jsonl"
    verbose = args.verbose

    if not kb_root.exists():
        print(f"ERROR: kb-root not found: {kb_root}", file=sys.stderr)
        sys.exit(1)

    if not bronze.exists():
        print(f"ERROR: bronze/ not found under {kb_root}", file=sys.stderr)
        sys.exit(1)

    print("Building context graph...")
    edge_counter = [0]

    # --- Nodes ---
    if verbose:
        print("Loading nodes...")
    file_nodes = build_file_nodes(bronze, verbose)
    symbol_nodes = build_symbol_nodes(bronze, verbose)
    package_nodes = build_package_nodes(bronze, verbose)
    route_nodes = build_route_nodes(bronze, verbose)
    ui_nodes = build_ui_surface_nodes(bronze, verbose)
    env_nodes = build_env_var_nodes(bronze, verbose)
    io_nodes = build_io_boundary_nodes(bronze, verbose)
    evidence_nodes = build_evidence_nodes(ledger_path, verbose)
    br_nodes = build_business_rule_nodes(silver, verbose)

    all_nodes: dict = {}
    for d in [file_nodes, symbol_nodes, package_nodes, route_nodes,
              ui_nodes, env_nodes, io_nodes, evidence_nodes, br_nodes]:
        all_nodes.update(d)

    if verbose:
        print(f"  Total nodes: {len(all_nodes)}")

    # --- Edges ---
    if verbose:
        print("Building edges...")
    all_edges: list = []
    all_edges.extend(build_contains_edges(file_nodes, symbol_nodes, edge_counter))
    all_edges.extend(build_import_edges(bronze, file_nodes, edge_counter))
    all_edges.extend(build_reads_env_edges(bronze, symbol_nodes, env_nodes, edge_counter))
    all_edges.extend(build_calls_external_edges(bronze, symbol_nodes, io_nodes, edge_counter))
    all_edges.extend(build_exposes_route_edges(bronze, file_nodes, route_nodes, edge_counter))
    all_edges.extend(build_renders_ui_edges(bronze, file_nodes, ui_nodes, edge_counter))
    all_edges.extend(build_cites_evidence_edges(symbol_nodes, evidence_nodes, edge_counter))

    if verbose:
        print(f"  Total edges: {len(all_edges)}")

    # --- Aliases ---
    aliases = build_aliases(all_nodes)

    # --- Retrieval index ---
    retrieval_index = build_retrieval_index(all_nodes, all_edges)

    # --- Quality report ---
    report = build_quality_report(all_nodes, all_edges, file_nodes)

    # --- Write outputs ---
    graph_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(graph_dir / "nodes.jsonl", list(all_nodes.values()))
    _write_jsonl(graph_dir / "edges.jsonl", all_edges)
    _write_jsonl(graph_dir / "aliases.jsonl", aliases)
    _write_json(graph_dir / "retrieval-index.json", retrieval_index)
    (graph_dir / "graph-quality-report.md").write_text(report, encoding="utf-8")

    print(f"Graph written to {graph_dir}")
    print(f"  nodes.jsonl       : {len(all_nodes)} records")
    print(f"  edges.jsonl       : {len(all_edges)} records")
    print(f"  aliases.jsonl     : {len(aliases)} records")
    print(f"  retrieval-index.json: {len(retrieval_index['by_type'])} types indexed")
    print(f"  graph-quality-report.md: written")

    # Print verdict
    for line in report.splitlines():
        if line.startswith("## Verdict:"):
            print(line)
            break


if __name__ == "__main__":
    main()
