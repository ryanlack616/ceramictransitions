#!/usr/bin/env python3
"""Backfill conservative, structured provenance labels in the catalog.

This migration classifies existing records from fields already present in the
repository. It does not invent literature citations or upgrade an analogue to
an exact composition claim.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from validate_crystal_vr import PROCEDURAL_FORMULAS, _normalize_formula


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crystal_vr.json"
ANALOGUE_NAMES = {
    "Ytterbium Silicate",  # Lu2SiO5 MP structure with conservative Yb substitution.
    "Reaction-Bonded Silicon Carbide",  # Processing variant using the SiC crystal model.
    "Sintered Silicon Carbide",           # Processing variant using the SiC crystal model.
    "Sintered Silicon Nitride",            # Processing variant using the beta-Si3N4 model.
}


def classify(entry: dict) -> str:
    if entry.get("entry_type") == "system":
        return "illustrative-system"
    if entry.get("isStub") and _normalize_formula((entry.get("formula") or "").strip()) in PROCEDURAL_FORMULAS:
        return "procedural-prototype"
    if entry.get("name") in ANALOGUE_NAMES:
        return "mp-analogue"
    if entry.get("mp_id"):
        return "mp-exact"
    if entry.get("isStub"):
        return "metadata-only"
    return "literature-reference"


def source_record(entry: dict, status: str) -> list[dict]:
    existing = entry.get("sources")
    sources = list(existing) if isinstance(existing, list) else []
    mp_id = entry.get("mp_id")
    if mp_id and not any(source.get("id") == mp_id for source in sources if isinstance(source, dict)):
        sources.append({
            "kind": "materials-project",
            "id": mp_id,
            "title": "Materials Project structure record",
            "url": f"https://materialsproject.org/materials/{mp_id}",
        })
    return sources


def quality_for(status: str) -> str:
    return {
        "mp-exact": "materials-project",
        "mp-analogue": "materials-project-analogue",
        "procedural-prototype": "canonical-prototype",
        "illustrative-system": "illustrative-architecture",
        "literature-reference": "literature-reference",
        "metadata-only": "metadata-only",
    }[status]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the migration; default is a report")
    args = parser.parse_args()
    document = json.loads(DATA.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    changed = 0
    for entry in document["structures"]:
        status = classify(entry)
        counts[status] = counts.get(status, 0) + 1
        if entry.get("source_status") != status:
            entry["source_status"] = status
            changed += 1
        quality = quality_for(status)
        if entry.get("source_quality") != quality:
            entry["source_quality"] = quality
            changed += 1
        sources = source_record(entry, status)
        if sources != entry.get("sources"):
            entry["sources"] = sources
            changed += 1
        if not entry.get("uncertainty_notes"):
            if status == "mp-analogue":
                entry["uncertainty_notes"] = "MP-sourced analogue or processing variant; the displayed crystal structure is not a full process-specific microstructure model."
            elif status == "procedural-prototype":
                entry["uncertainty_notes"] = "Canonical prototype geometry for visual exploration; not simulation-derived for this material record."
            elif status == "illustrative-system":
                entry["uncertainty_notes"] = "Illustrative layered architecture; layer thicknesses and geometry vary by process and application."
            elif status == "literature-reference":
                entry["uncertainty_notes"] = "Reference structure record; consult the cited crystallographic source before using it for quantitative analysis."
            changed += 1

    print(f"provenance statuses: {counts}")
    print(f"fields changed: {changed}")
    if not args.write:
        print("DRY-RUN: no catalog changes written")
        return 0

    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, DATA)
    print(f"Wrote {DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
