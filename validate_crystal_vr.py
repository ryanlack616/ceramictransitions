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
REQUIRED_SYSTEM = {"name", "formula", "system", "layers", "material_class", "service_temp_c"}

# Phase 3.3 (May 27 2026): HT-focus rule — every non-precursor/carbonate/hydroxide/mineral
# entry must carry material_class and service_temp_c so the filter UI can reason about it.
HT_CLASSIFICATION_REQUIRED = True
NON_HT_CLASSES = {"precursor", "carbonate", "hydroxide", "mineral"}

# Phase 2.5.1: stub formulas the viewer can synthesize procedurally at load
# time from canonical structure prototypes (kept in sync with PROTOTYPE_TABLE
# in index.html / lattice.html).
PROCEDURAL_FORMULAS = {
    "ZrC", "HfC", "TaC",
    "HfO2", "ZrO2", "ZrO2-3Y2O3", "ZrO2-8Y2O3", "ZrO2-CeO2", "La2Zr2O7",
    "ZrB2", "HfB2",
    "AlN", "BN",
    "SiC", "SiC (fiber-reinforced)", "SiC (reaction-bonded)", "SiC (sintered)",
    # Phase 3.1 (May 16, 2026) — β-Si3N4 family
    "Si3N4", "Si6-xAlxOxN8-x",
}

_SUBSCRIPT_MAP = str.maketrans(
    "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089\u2093\u208B",
    "0123456789x-",
)


def _normalize_formula(f: str) -> str:
    return (f or "").translate(_SUBSCRIPT_MAP)


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
        entry_type = s.get("entry_type", "crystal")
        if entry_type == "system":
            missing = REQUIRED_SYSTEM - set(s.keys())
            if missing:
                errors.append(f"[{i}] {s.get('name', '?')}: system entry missing keys {missing}")
            layers = s.get("layers") or []
            if not isinstance(layers, list) or not layers:
                errors.append(f"[{i}] {s.get('name', '?')}: system entry has empty layers[]")
            continue

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

        # Phase 3.3 HT-classification rule.
        if HT_CLASSIFICATION_REQUIRED:
            mc = s.get("material_class")
            st = s.get("service_temp_c")
            if mc is None:
                errors.append(f"[{i}] {s.get('name', '?')}: missing material_class (Phase 3.3 P0 rule)")
            elif mc not in NON_HT_CLASSES and st is None:
                errors.append(
                    f"[{i}] {s.get('name', '?')}: missing service_temp_c "
                    f"(material_class={mc!r} is HT-relevant)"
                )

    # Header count consistency (Phase 3.3 drift guard, added 2026-06-17).
    # The top-level header counts must mirror the array exactly, matching how the
    # frontend recomputes them at load time (index.html:
    #   structureCount  = data.structures.length
    #   renderableCount = data.structures.filter(s => !s.isStub).length
    # ). Append scripts grew the array 60->83 but left the header at 60/55 — a
    # silent drift that fooled a downstream audit into reporting a phantom gap.
    hdr_sc = root.get("structureCount")
    if hdr_sc != len(structs):
        errors.append(
            f"header structureCount={hdr_sc} != actual array length {len(structs)} "
            f"(update the header when you grow structures[])"
        )
    hdr_rc = root.get("renderableCount")
    actual_native = sum(1 for s in structs if not s.get("isStub"))
    if hdr_rc != actual_native:
        errors.append(
            f"header renderableCount={hdr_rc} != actual non-stub count {actual_native}"
        )

    # Optional JSON Schema validation (skipped silently if jsonschema not installed)
    schema_path = HERE / "data" / "crystal_vr.schema.json"
    if schema_path.exists():
        try:
            from jsonschema import Draft202012Validator  # type: ignore
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            for err in list(Draft202012Validator(schema).iter_errors(root))[:50]:
                errors.append(f"[schema] {list(err.absolute_path)}: {err.message}")
        except ImportError:
            print("note: jsonschema not installed, skipping schema check (pip install jsonschema)")

    if errors:
        print(f"FAIL: {len(errors)} issues")
        for e in errors:
            print(f"  - {e}")
        return 1

    renderable = sum(1 for s in structs if not s.get("isStub"))
    stubs = [s for s in structs if s.get("isStub")]
    procedural = sum(1 for s in stubs if _normalize_formula((s.get("formula") or "").strip()) in PROCEDURAL_FORMULAS)
    remaining = len(stubs) - procedural
    print(
        f"OK: {len(structs)} structures \u00b7 "
        f"{renderable} native + {procedural} procedural = {renderable + procedural} renderable in viewer \u00b7 "
        f"{remaining} metadata-only stubs"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
