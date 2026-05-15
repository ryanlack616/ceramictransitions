#!/usr/bin/env python3
"""
Dedupe data/crystal_vr.json by (name, formula).

When duplicates exist, prefer the entry with the most atoms (i.e. a real
3D model beats a metadata-only stub). Also rewrites `structureCount` and
flags every entry with an `isStub` boolean for downstream UIs.

Idempotent. Safe to re-run.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"


def is_stub(s: dict) -> bool:
    cv = s.get("cellVectors") or []
    atoms = s.get("atoms") or []
    has_cell = (
        isinstance(cv, list)
        and len(cv) >= 3
        and isinstance(cv[0], list)
        and len(cv[0]) >= 3
    )
    has_atoms = isinstance(atoms, list) and len(atoms) > 0
    return not (has_cell and has_atoms)


def main() -> int:
    root = json.loads(DATA.read_text(encoding="utf-8"))
    structs = root.get("structures", [])

    before = len(structs)
    seen: dict[tuple[str, str], dict] = {}
    for s in structs:
        key = ((s.get("name") or "").strip(), (s.get("formula") or "").strip())
        prev = seen.get(key)
        if prev is None:
            seen[key] = s
            continue
        # Keep whichever has more atoms; tie-break to first.
        a_new = len(s.get("atoms") or [])
        a_prev = len(prev.get("atoms") or [])
        if a_new > a_prev:
            seen[key] = s

    deduped = list(seen.values())
    for s in deduped:
        s["isStub"] = is_stub(s)

    root["structures"] = deduped
    root["structureCount"] = len(deduped)
    root["renderableCount"] = sum(1 for s in deduped if not s["isStub"])

    DATA.write_text(
        json.dumps(root, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    removed = before - len(deduped)
    print(f"crystal_vr.json: {before} → {len(deduped)} structures ({removed} dupes removed)")
    print(f"  renderable (full 3D): {root['renderableCount']}")
    print(f"  stub (Phase-3 pending): {len(deduped) - root['renderableCount']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
