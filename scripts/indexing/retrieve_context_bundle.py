#!/usr/bin/env python3
"""
retrieve_context_bundle.py — BFS traversal to build context bundles for a given seed node.

Reads graph/nodes.jsonl and graph/edges.jsonl, performs BFS from the seed node,
collects all nodes and edges in the subgraph, resolves evidence records, and
writes the bundle to the output directory.

Usage:
  python3 retrieve_context_bundle.py \
    --kb-root /path/to/.indexing-kb/ \
    --seed <node_id> \
    --hops 2 \
    --purpose functional \
    --output .indexing-kb/graph/context-bundles/
"""

import argparse
import json
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

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


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

def load_graph(graph_dir: Path):
    """Load nodes and edges, return (nodes_by_id, adjacency, edges_by_pair)."""
    nodes_by_id = {}
    for rec in _read_jsonl(graph_dir / "nodes.jsonl"):
        nid = rec.get("node_id")
        if nid:
            nodes_by_id[nid] = rec

    # adjacency: node_id -> set of (neighbour_id, edge)
    adjacency: dict = {nid: [] for nid in nodes_by_id}
    all_edges = _read_jsonl(graph_dir / "edges.jsonl")
    for edge in all_edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src and tgt:
            if src in adjacency:
                adjacency[src].append((tgt, edge))
            if tgt in adjacency:
                adjacency[tgt].append((src, edge))

    return nodes_by_id, adjacency, all_edges


# ---------------------------------------------------------------------------
# BFS
# ---------------------------------------------------------------------------

def bfs_subgraph(seed_id: str, nodes_by_id: dict, adjacency: dict, max_hops: int):
    """Return (visited_node_ids, visited_edge_ids, included_edges)."""
    if seed_id not in nodes_by_id:
        return set(), set(), []

    visited_nodes = set()
    visited_edge_ids = set()
    included_edges = []

    queue = deque()
    queue.append((seed_id, 0))
    visited_nodes.add(seed_id)

    while queue:
        current_id, depth = queue.popleft()
        if depth >= max_hops:
            continue
        for neighbour_id, edge in adjacency.get(current_id, []):
            edge_id = edge.get("edge_id", "")
            if edge_id not in visited_edge_ids:
                visited_edge_ids.add(edge_id)
                included_edges.append(edge)
            if neighbour_id not in visited_nodes:
                visited_nodes.add(neighbour_id)
                queue.append((neighbour_id, depth + 1))

    return visited_nodes, visited_edge_ids, included_edges


# ---------------------------------------------------------------------------
# Evidence resolution
# ---------------------------------------------------------------------------

def resolve_evidence(node_ids: set, nodes_by_id: dict, ledger_path: Path) -> list:
    """Collect all evidence_ids referenced by included nodes."""
    all_eids = set()
    for nid in node_ids:
        node = nodes_by_id.get(nid, {})
        for eid in node.get("evidence_ids", []):
            all_eids.add(eid)

    if not ledger_path.exists() or not all_eids:
        return list(all_eids)

    # Return the list of resolved evidence_ids (full records could be large;
    # consumers can look them up in the ledger by id)
    resolved = []
    for rec in _read_jsonl(ledger_path):
        eid = rec.get("evidence_id")
        if eid and eid in all_eids:
            resolved.append(eid)

    # Include any that weren't found in the ledger (still valid IDs)
    found = set(resolved)
    for eid in all_eids:
        if eid not in found:
            resolved.append(eid)

    return resolved


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="BFS traversal to build a targeted context bundle from the KB graph."
    )
    parser.add_argument("--kb-root", required=True, help="Path to .indexing-kb/ directory")
    parser.add_argument("--seed", required=True, help="Seed node_id to start BFS from")
    parser.add_argument("--hops", type=int, default=2, help="Maximum BFS hops (default: 2)")
    parser.add_argument(
        "--purpose",
        choices=["functional", "technical", "security", "general"],
        default="general",
        help="Bundle purpose tag",
    )
    parser.add_argument(
        "--output",
        help="Output directory for the bundle JSON (default: <kb-root>/graph/context-bundles/)",
    )
    args = parser.parse_args()

    kb_root = Path(args.kb_root).resolve()
    graph_dir = kb_root / "graph"
    ledger_path = kb_root / "evidence-ledger.jsonl"
    output_dir = Path(args.output).resolve() if args.output else graph_dir / "context-bundles"

    if not kb_root.exists():
        print(f"ERROR: kb-root not found: {kb_root}", file=sys.stderr)
        sys.exit(1)

    if not (graph_dir / "nodes.jsonl").exists():
        print(f"ERROR: graph/nodes.jsonl not found — run build_context_graph.py first", file=sys.stderr)
        sys.exit(1)

    print(f"Loading graph from {graph_dir}...")
    nodes_by_id, adjacency, _ = load_graph(graph_dir)

    seed_id = args.seed
    if seed_id not in nodes_by_id:
        # Try alias resolution
        aliases = _read_jsonl(graph_dir / "aliases.jsonl")
        alias_map = {a["alias"]: a["node_id"] for a in aliases if "alias" in a and "node_id" in a}
        if seed_id in alias_map:
            seed_id = alias_map[seed_id]
            print(f"Resolved alias '{args.seed}' -> '{seed_id}'")
        else:
            print(f"ERROR: seed node '{args.seed}' not found in graph", file=sys.stderr)
            sys.exit(1)

    print(f"Running BFS from '{seed_id}', max hops={args.hops}...")
    visited_nodes, _, included_edges = bfs_subgraph(seed_id, nodes_by_id, adjacency, args.hops)

    included_node_records = [nodes_by_id[nid] for nid in visited_nodes if nid in nodes_by_id]
    evidence_ids = resolve_evidence(visited_nodes, nodes_by_id, ledger_path)

    # Bundle ID and filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Sanitize seed_id for filename
    safe_seed = seed_id.replace("/", "-").replace("\\", "-")
    bundle_id = f"CTX-{safe_seed}-{timestamp}"
    filename = f"{bundle_id}.json"

    bundle = {
        "bundle_id": bundle_id,
        "seed_node_id": seed_id,
        "purpose": args.purpose,
        "hops": args.hops,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "included_nodes": included_node_records,
        "included_edges": included_edges,
        "included_evidence_ids": evidence_ids,
        "summary": (
            f"BFS bundle from {seed_id} with {len(included_node_records)} nodes, "
            f"{len(included_edges)} edges, {len(evidence_ids)} evidence records"
        ),
    }

    output_path = output_dir / filename
    _write_json(output_path, bundle)

    print(f"Bundle written: {output_path}")
    print(f"  Nodes    : {len(included_node_records)}")
    print(f"  Edges    : {len(included_edges)}")
    print(f"  Evidence : {len(evidence_ids)}")
    print(f"  Summary  : {bundle['summary']}")


if __name__ == "__main__":
    main()
