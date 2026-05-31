#!/usr/bin/env python3
"""
Backfills preceded_by, followed_by, workflow, phase, wave fields into
claude-marketplace/catalog.json from bmad/design/workflow-dag-draft.json.
Safe to re-run — idempotent.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CATALOG = ROOT / "claude-marketplace" / "catalog.json"
DAG = ROOT / "bmad" / "design" / "workflow-dag-draft.json"


def main():
    catalog_data = json.loads(CATALOG.read_text())
    dag_data = json.loads(DAG.read_text())

    dag_by_name = {a["name"]: a for a in dag_data["agents"]}

    updated = 0
    for cap in catalog_data["capabilities"]:
        name = cap["name"]
        if name not in dag_by_name:
            continue
        entry = dag_by_name[name]
        cap["bmad"] = {
            "workflow": entry.get("workflow") or entry.get("workflow_id") or (
                dag_data.get("workflow_id") if entry.get("phase") else None
            ),
            "role": entry.get("role"),
            "phase": entry.get("phase"),
            "wave": entry.get("wave"),
            "preceded_by": entry.get("preceded_by", []),
            "followed_by": entry.get("followed_by", []),
        }
        # strip None values
        cap["bmad"] = {k: v for k, v in cap["bmad"].items() if v is not None}
        updated += 1

    CATALOG.write_text(json.dumps(catalog_data, indent=2, ensure_ascii=False) + "\n")
    print(f"Updated {updated}/{len(catalog_data['capabilities'])} capabilities")
    not_found = [a["name"] for a in dag_data["agents"] if a["name"] not in {c["name"] for c in catalog_data["capabilities"]}]
    if not_found:
        print(f"DAG entries not in catalog: {not_found}")


if __name__ == "__main__":
    main()
