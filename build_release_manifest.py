#!/usr/bin/env python3
"""Generate the public release manifest from the canonical catalog."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from validate_crystal_vr import PROCEDURAL_FORMULAS, _normalize_formula


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crystal_vr.json"


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "working-tree"


def build_manifest() -> dict:
    document = json.loads(DATA.read_text(encoding="utf-8"))
    structures = document["structures"]
    systems = [s for s in structures if s.get("entry_type") == "system"]
    stubs = [s for s in structures if s.get("isStub")]
    transitions = [s for s in structures if s.get("transitions")]
    procedural = sum(
        bool(s.get("isStub"))
        and _normalize_formula((s.get("formula") or "").strip()) in PROCEDURAL_FORMULAS
        for s in structures
    )
    return {
        "manifest_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_revision": git_revision(),
        "deployment_target": "github-pages",
        "build": {
            "validation_required": True,
            "generated_bundle": "data/crystal_vr.js",
            "artifact_staging": "release/",
        },
        "catalog": {
            "version": document.get("version"),
            "entries": len(structures),
            "baked_renderable": sum(1 for s in structures if not s.get("isStub")),
            "procedural_candidates": procedural,
            "system_entries": len(systems),
            "metadata_only_after_promotion": len(stubs) - procedural,
            "materials_project_records": sum(1 for s in structures if s.get("mp_id")),
            "transition_entries": len(transitions),
            "transition_rows": sum(len(s.get("transitions", [])) for s in transitions),
        },
        "public_files": [
            "index.html",
            "lattice.html",
            "CNAME",
            "data/crystal_vr.json",
            "data/crystal_vr.js",
            "data/crystal_vr.schema.json",
            "release-manifest.json",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "release-manifest.json")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_manifest(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
