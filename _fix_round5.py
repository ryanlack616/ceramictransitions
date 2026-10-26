#!/usr/bin/env python3
"""2026-10-26 round-5: (1) upgrade the four schematic binaries CaO/BeO/TaB2/HfN
to full DFT (they are plain MP ground states - no reason to stay prototypes);
(2) correct the melting_point_c field where it holds a transformation or
decomposition temperature (textbook values only); (3) clarify the remaining
transform-not-melt entries with info notes; (4) tidy Mullite's system label."""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"

for _l in (HERE / ".env").read_text(encoding="utf-8").splitlines():
    _l = _l.strip()
    if _l and "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1)
        os.environ.setdefault(k, v)
sys.path.insert(0, str(HERE))
from _ingest_mp import _mp_fetch, _build_supercell, _compute_bonds

# name, mp_id, supercell, system, note, expected-bond ranges
UPGRADE = [
    ("Calcium Oxide", "mp-aaaaadwf", (5, 5, 5),
     "Cubic Fm-3m (lime, rock-salt)",
     "CaO lime (sg Fm-3m, ehull=0) - exact DFT replaces the schematic rock-salt prototype.",
     {"Ca-O": (2.30, 2.55)}),
    ("Beryllium Oxide", "mp-aaaaadtu", (4, 4, 3),
     "Hexagonal P6₃mc (beryllia, wurtzite)",
     "BeO beryllia (sg P6₃mc, ehull=0) - exact DFT replaces the schematic wurtzite prototype.",
     {"Be-O": (1.60, 1.72)}),
    ("Tantalum Diboride", "mp-aaaaabqq", (5, 5, 3),
     "Hexagonal P6/mmm (TaB₂, AlB₂-type)",
     "TaB₂ (sg P6/mmm, ehull=0) - exact DFT replaces the schematic AlB₂ prototype.",
     {"B-Ta": (2.25, 2.60), "B-B": (1.72, 1.95)}),
    ("Hafnium Nitride", "mp-aaaaaeeu", (5, 5, 5),
     "Cubic Fm-3m (HfN, rock-salt)",
     "HfN (sg Fm-3m, ehull=0) - exact DFT replaces the schematic rock-salt prototype.",
     {"Hf-N": (2.10, 2.40)}),
]

# melting_point_c corrections (textbook values; the old numbers were
# transformation/decomposition temperatures) + notes for transform-not-melt set.
MELT_FIX = {
    "Kaolinite": (1750, "dehydroxylates ~450-550°C to metakaolin; true melting reported ~1750°C - the 450 figure was the transformation temperature."),
    "Talc": (1470, "dehydroxylates ~800°C to enstatite; melting/incongruent ~1470°C - the 800 figure was the transformation temperature."),
    "Calcite": (1339, "decomposes to CaO+CO₂ from ~825°C; melts 1339°C only under CO₂ pressure - the 825 figure was the decomposition temperature."),
    "Brucite": (None, "no melting point - decomposes to periclase (MgO) + H₂O from ~350°C."),
    "Dolomite": (None, "no congruent melting - decomposes stepwise (to calcite+periclase ~750°C, then CaO)."),
}
TRANSFORM_NOTE = ("listed temperature is the phase transformation/decomposition (not a melting point); "
                  "see bound_type.")


def main():
    write = "--write" in sys.argv[1:]
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr); return 2
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in doc["structures"]}
    upgraded = []

    for (name, mp_id, sc, system, note, exp) in UPGRADE:
        entry = by_name.get(name)
        if entry is None:
            print(f"SKIP {name}: not found"); continue
        if entry.get("mp_id") and entry["mp_id"] == mp_id:
            print(f"SKIP {name}: already upgraded"); continue
        payload = _mp_fetch(mp_id, api_key)
        sg = (payload.get("symmetry") or {}).get("symbol", "?")
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)
        means = stats.get("bondLengths") or {}
        ok = all((lambda m: m is not None and lo <= m <= hi)(means.get("-".join(sorted(p.split("-")))))
                 for p, (lo, hi) in exp.items())
        print(f"## {name} [{mp_id}] {sg} {len(atoms)} at  means={dict(means)}")
        if not ok:
            print("   GATE FAIL — skipped"); continue
        info = [i for i in (entry.get("info") or []) if "Source: Materials" not in i and "Procedural" not in i]
        info.append(f"Source: Materials Project {mp_id}. {note}")
        comp = {
            "system": system, "info": info, "supercell": scl,
            "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": f"2026-10-26 round-5: upgraded from schematic prototype to Materials Project {mp_id} (DFT-relaxed); supercell {scl[0]}×{scl[1]}×{scl[2]}.",
        }
        for k in ("name", "formula", "material_class", "service_temp_c", "melting_point_c",
                  "application_tags", "transitions", "bound_type", "oxidation_temp_c"):
            if k in entry:
                comp[k] = entry[k]
        entry.clear(); entry.update(comp)
        upgraded.append(name)

    # melting-point corrections + transform-not-melt notes
    mel_fixed, noted = [], []
    for s in doc["structures"]:
        if s["name"] in MELT_FIX:
            new_mp, note = MELT_FIX[s["name"]]
            if s.get("melting_point_c") != new_mp:
                mel_fixed.append((s["name"], s.get("melting_point_c"), new_mp))
            s["melting_point_c"] = new_mp
            if note and not any(note[:20] in (i or "") for i in (s.get("info") or [])):
                s.setdefault("info", []).append("Thermal note: " + note)
        elif s["name"] in ("Andalusite", "Kyanite", "Sillimanite", "Spodumene"):
            if not any(TRANSFORM_NOTE[:24] in (i or "") for i in (s.get("info") or [])):
                s.setdefault("info", []).append("Thermal note: " + TRANSFORM_NOTE)
                noted.append(s["name"])

    mull = by_name.get("Mullite")
    if mull and "(approx model)" in (mull.get("system") or ""):
        mull["system"] = "Orthorhombic Pbam (3:2 mullite — teaching model; ordered 3:2 phase does not exist in MP)"

    doc["renderableCount"] = sum(1 for s in doc["structures"] if not s.get("isStub"))

    print("\nUPGRADED:", upgraded)
    print("MELT_FIX:", mel_fixed)
    print("TRANSFORM-NOTE:", noted or "(unchanged)")
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA}.")


if __name__ == "__main__":
    main()