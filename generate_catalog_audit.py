#!/usr/bin/env python3
"""Generate a reviewable per-entry catalog audit report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crystal_vr.json"


def audit_entry(entry: dict) -> dict:
    atoms = entry.get("atoms") or []
    bonds = entry.get("bonds") or []
    invalid_bonds = [
        bond for bond in bonds
        if not isinstance(bond, list)
        or len(bond) != 2
        or not all(isinstance(index, int) and 0 <= index < len(atoms) for index in bond)
    ]
    return {
        "id": f"{entry.get('name', '')}|{entry.get('formula', '')}".lower(),
        "name": entry.get("name"),
        "formula": entry.get("formula"),
        "entry_type": entry.get("entry_type", "crystal"),
        "source_status": entry.get("source_status", "unclassified"),
        "source_quality": entry.get("source_quality", "unknown"),
        "mp_id": entry.get("mp_id"),
        "renderable_in_catalog": not bool(entry.get("isStub")),
        "runtime_procedural_candidate": bool(entry.get("isStub")) and entry.get("source_status") == "procedural-prototype",
        "atom_count": len(atoms),
        "bond_count": len(bonds),
        "invalid_bond_count": len(invalid_bonds),
        "transition_count": len(entry.get("transitions") or []),
        "application_count": len(entry.get("application_tags") or []),
        "has_uncertainty_notes": bool(entry.get("uncertainty_notes")),
        "has_sources": bool(entry.get("sources")),
        "caveat": entry.get("uncertainty_notes"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "catalog-audit.json")
    args = parser.parse_args()
    document = json.loads(DATA.read_text(encoding="utf-8"))
    report = {
        "catalog_version": document.get("version"),
        "structure_count": len(document["structures"]),
        "entries": [audit_entry(entry) for entry in document["structures"]],
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({len(report['entries'])} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
