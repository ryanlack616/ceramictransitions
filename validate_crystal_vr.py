#!/usr/bin/env python3
"""
Validate data/crystal_vr.json.

Checks:
  - No duplicate (name, formula) pairs.
  - Every structure has the required keys.
  - Renderable structures have well-formed cellVectors (3×3) and atoms.
  - Stub structures are explicitly flagged with isStub: true.

Exits non-zero on any check failure (suitable for CI / pre-deploy gate).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"
REQUIRED = {"name", "formula", "system", "atoms", "bonds", "cellVectors", "supercell"}


def main() -> int:
    root = json.loads(DATA.read_text(encoding="utf-8"))
    structs = root.get("structures", [])

    errors: list[str] = []

    # Duplicate check
    seen: set[tuple[str, str]] = set()
    for i, s in enumerate(structs):
        key = ((s.get("name") or "").strip(), (s.get("formula") or "").strip())
        if key in seen:
            errors.append(f"[{i}] duplicate (name, formula): {key}")
        seen.add(key)

    # Per-structure checks
    for i, s in enumerate(structs):
        missing = REQUIRED - set(s.keys())
        if missing:
            errors.append(f"[{i}] {s.get('name', '?')}: missing keys {missing}")

        cv = s.get("cellVectors") or []
        atoms = s.get("atoms") or []
        has_cell = (
            isinstance(cv, list)
            and len(cv) == 3
            and all(isinstance(v, list) and len(v) == 3 for v in cv)
        )
        has_atoms = isinstance(atoms, list) and len(atoms) > 0
        renderable = has_cell and has_atoms
        is_stub = bool(s.get("isStub"))

        if renderable and is_stub:
            errors.append(f"[{i}] {s['name']}: isStub=true but data looks renderable")
        if not renderable and not is_stub:
            errors.append(
                f"[{i}] {s.get('name', '?')}: malformed/empty data but isStub not set "
                f"(cellVectors len={len(cv)}, atoms len={len(atoms)})"
            )

    if errors:
        print(f"FAIL: {len(errors)} issues")
        for e in errors:
            print(f"  - {e}")
        return 1

    renderable = sum(1 for s in structs if not s.get("isStub"))
    print(f"OK: {len(structs)} structures · {renderable} renderable · "
          f"{len(structs) - renderable} stubs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
