#!/usr/bin/env python3
"""2026-10-26 deep-audit pass 2 — upgrade the flagship ZrO2 trio to DFT-exact
Materials Project structures and fix text bugs:

1. Baddeleyite (m)      <- mp-aaaaaefy P2_1/c  (ehull 0, 12 at)  [3,3,3]
2. Tetragonal Zirconia  <- mp-aaaaadva P4_2/nmc (ehull .027)      [4,4,4]
3. Cubic Zirconia       <- mp-aaaaacif Fm-3m  (ehull .056)       [4,4,4]

These were the last "approx model" entries in the atlas and they carry the
project's namesake t<->m transformation story; now they are exact like
everything else. Gates: exact ZrO2 stoichiometry + mean Zr-O in [2.10, 2.30].
Also: Willemite "900-10500 C" temperature typo -> 900-1050 C, and all
'simplified'/'simplified' info variants normalized to 'simplified'.
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"

for _line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
    _line = _line.strip()
    if _line and "=" in _line and not _line.startswith("#"):
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k, _v)

sys.path.insert(0, str(HERE))
from _ingest_mp import _mp_fetch, _build_supercell, _compute_bonds

UPGRADES = [
    ("Baddeleyite", "mp-aaaaaefy", (3, 3, 3), "Monoclinic P2₁/c (baddeleyite m-ZrO₂, DFT)",
     "m-ZrO₂ baddeleyite (sg P2₁/c, ehull=0). The room-T phase; the t↔m transformation is the PSZ story (see transitions)."),
    ("Tetragonal Zirconia", "mp-aaaaadva", (4, 4, 4), "Tetragonal P4₂/nmc (t-ZrO₂, DFT)",
     "t-ZrO₂ (sg P4₂/nmc, ehull≈0.03 — metastable, the transformation-toughening phase)."),
    ("Cubic Zirconia", "mp-aaaaacif", (4, 4, 4), "Cubic Fm-3m (c-ZrO₂ fluorite, DFT)",
     "c-ZrO₂ fluorite (sg Fm-3m, ehull≈0.06 — high-T phase, stabilized with Y₂O₃ in service)."),
]


def main():
    write = "--write" in sys.argv[1:]
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr); return 2

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in doc["structures"]}

    for name, mp_id, sc, system, note in UPGRADES:
        entry = by_name.get(name)
        if entry is None:
            print(f"SKIP {name}: missing"); continue
        payload = _mp_fetch(mp_id, api_key)
        sg = (payload.get("symmetry") or {}).get("symbol", "?")
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)
        comp = Counter(x["e"] for x in atoms)
        zr_ok = comp["Zr"] / len(atoms), comp["O"] / len(atoms)  # 1:2 fractions
        zr_mean = stats.get("bondLengths", {}).get("O-Zr") or stats.get("bondLengths", {}).get("Zr-O")
        gate = (abs(zr_ok[0] - 1 / 3) < 0.01 and abs(zr_ok[1] - 2 / 3) < 0.01
                and zr_mean and 2.10 <= zr_mean <= 2.30)
        print(f"## {name} [{mp_id}] {sg} {len(atoms)} at  Zr-O mean={zr_mean} gate={gate}")
        if not gate:
            print("   GATE FAIL — skipped"); continue

        old_mp = entry.get("mp_id")
        if old_mp and old_mp != mp_id:
            print(f"   WARN: replacing existing mp_id {old_mp}")

        info = [i for i in (entry.get("info") or [])
                if "simplified" not in i and "approx" not in i and "Source: Materials" not in i]
        if name == "Cubic Zirconia":
            info = [i for i in info if "approximate" not in i]
        info.append(f"Source: Materials Project {mp_id}. {note}")
        composed = {
            "system": system,
            "info": info,
            "supercell": scl,
            "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": (
                f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). "
                f"2026-10-26 zirconia upgrade; supercell {scl[0]}×{scl[1]}×{scl[2]}, centred at origin."
            ),
        }
        for fld in ("name", "formula", "material_class", "service_temp_c", "melting_point_c",
                    "application_tags", "transitions", "bound_type", "oxidation_temp_c"):
            if fld in entry and fld not in composed:
                composed[fld] = entry[fld]
        entry.clear(); entry.update(composed)

    # ---- text fix: Willemite temperature-range typo only ----
    n_fixed = 0
    for s in doc["structures"]:
        info = s.get("info") or []
        for idx, line in enumerate(info):
            if "900–10500°C" in line or "900-10500" in line:
                info[idx] = line.replace("900–10500°C", "900–1050°C").replace("900-10500", "900-1050")
                n_fixed += 1

    print("\ntext fixes (willemite typo):", n_fixed)
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA}.")


if __name__ == "__main__":
    main()