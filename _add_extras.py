#!/usr/bin/env python3
"""2026-10-26 extras (Ryan: 'would it be hard to add...?'):
  1. SrZrO3   mp-aaaaafjm Cmcm  — full DFT entry
  2. CaZrO3   mp-aaaaagtv Pnma  — full DFT entry (ehull 0)
  3. (Hf,Zr,Ti,Ta,Nb)N   — high-entropy nitride, rocksalt_mix prototype (load-time)
  4. (Hf,Zr,Ti,Ta,Nb)B2  — high-entropy diboride, AlB2_mix prototype (load-time)
Answer: no, not hard — 1/2 are the same MP-ingest path as BaZrO3; 3 reuses the
existing rocksalt_mix DEF; 4 needed one 20-line AlB2_mix DEF (done in
index.html) + a stub. Gates identical for the full entries."""
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

FULL = [
    ("Strontium Zirconate", "SrZrO₃", "mp-aaaaafjm", (3, 3, 3),
     "Orthorhombic Cmcm (perovskite)",
     "refractory_oxide", 1400, 2600,
     ["high-temperature-ceramic", "perovskite", "zirconate", "refractory"],
     ["Strontium zirconate — orthorhombic perovskite (Cmcm); refractory dielectric with low thermal expansion.",
      "Service temperature: 1400°C", "Melting point: ~2600°C", "Thermal shock risk: low"],
     {"Sr-O": (2.50, 2.90), "Zr-O": (2.05, 2.25)},
    ),
    ("Calcium Zirconate", "CaZrO₃", "mp-aaaaagtv", (3, 3, 3),
     "Orthorhombic Pnma (perovskite)",
     "refractory_oxide", 1450, 2400,
     ["high-temperature-ceramic", "perovskite", "zirconate", "refractory"],
     ["Calcium zirconate — orthorhombic perovskite (Pnma, ehull 0); the classic CaO-ZrO₂ refractory reaction product.",
      "Service temperature: 1450°C", "Melting point: ~2400°C", "Thermal shock risk: medium"],
     {"Ca-O": (2.25, 2.65), "Zr-O": (2.05, 2.30)},
    ),
]

STUBS = [
    ("High-Entropy Nitride (Hf,Zr,Ti,Ta,Nb)N", "(HfZrTiTaNb)N",
     "Cubic Fm-3m (rock-salt, 5-cation solid solution)",
     "high_entropy", 1300, 3000,
     ["high-temperature-ceramic", "high-entropy-ceramic", "nitride", "hard-coating", "next-gen-thermal-protection"],
     ["Equimolar 5-cation rock-salt nitride (Hf,Zr,Ti,Ta,Nb)N — HEN archetype.",
      "Procedural mixed-cation lattice (cations cycled over sites); a true DFT supercell is a Phase 3.5+ task.",
      "Service temperature: 1300°C (air)", "Melting/decomposition: ~3000°C (est.)"]),
    ("High-Entropy Boride (Hf,Zr,Ti,Ta,Nb)B₂", "(HfZrTiTaNb)B2",
     "Hexagonal P6/mmm (AlB₂-type, 5-cation solid solution)",
     "high_entropy", 1800, 3300,
     ["high-temperature-ceramic", "high-entropy-ceramic", "boride", "UHTC", "thermo-structural"],
     ["Equimolar 5-cation diboride (Hf,Zr,Ti,Ta,Nb)B₂ — HEB archetype; the UHTC extension of ZrB₂/HfB₂.",
      "Procedural mixed-cation lattice (cations cycled on the metal site, B honeycomb); a true DFT supercell is Phase 3.5+.",
      "Service temperature: 1800°C", "Melting/decomposition: ~3300°C (est.)"]),
]

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(formula):
    f = formula.translate(_SUB).replace("ₓ", "x").replace("₋", "-").replace("·", " ")
    counts = Counter()
    for g, gm, el, em in re.findall(r"\(([A-Za-z0-9]+)\)([0-9.]*)|([A-Z][a-z]?)([0-9.]*)", f):
        if g:
            mul = float(gm) if gm else 1.0
            for x in re.finditer(r"([A-Z][a-z]?)([0-9.]*)", g):
                counts[x.group(1)] += mul * (float(x.group(2)) if x.group(2) else 1.0)
        elif el and el.isalpha() and el != "x":
            counts[el] += float(em) if em else 1.0
    return counts


def bmean(bmeans, pair):
    return bmeans.get("-".join(sorted(pair.split("-"))))
def main():
    write = "--write" in sys.argv[1:]
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr); return 2
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    names = {s["name"] for s in doc["structures"]}
    added = []

    for (name, formula, mp_id, sc, system, mclass, service, mp_temp, tags, info, exp) in FULL:
        if name in names:
            print(f"SKIP {name}: already present"); continue
        payload = _mp_fetch(mp_id, api_key)
        sg = (payload.get("symmetry") or {}).get("symbol", "?")
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)
        f = formula_counts(formula); a = Counter(x["e"] for x in atoms)
        stoich = all(abs(f[el] / sum(f.values()) - a[el] / len(atoms)) <= 0.02
                     for el in set(f) | set(a))
        means = {p: bmean(stats.get("bondLengths") or {}, p) for p in exp}
        ok = stoich and all(m is not None and lo <= m <= hi
                            for m, (lo, hi) in zip(means.values(), exp.values()))
        print(f"## {name} [{mp_id}] {sg} {len(atoms)} at  means={means}")
        if not ok:
            print("   GATE FAIL — skipped"); continue
        entry = {
            "name": name, "formula": formula, "system": system, "material_class": mclass,
            "service_temp_c": service, "melting_point_c": mp_temp, "application_tags": tags,
            "info": info + [f"Source: Materials Project {mp_id}. DFT-relaxed coordinates."],
            "supercell": scl, "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). 2026-10-26 extras pass.",
        }
        doc["structures"].append(entry); added.append(name)

    for (name, formula, system, mclass, service, mp_temp, tags, info) in STUBS:
        if name in names:
            print(f"SKIP {name}: already present"); continue
        entry = {
            "name": name, "formula": formula, "system": system, "material_class": mclass,
            "service_temp_c": service, "melting_point_c": mp_temp, "application_tags": tags,
            "info": info, "isStub": True, "bound_type": "melts",
            "atoms": [], "bonds": [], "bondTypes": [], "cellVectors": [], "supercell": None,
            "stats": {"bondLengths": {}, "coordDist": {}},
        }
        doc["structures"].append(entry); added.append(name)

    if added:
        doc["structureCount"] = doc.get("structureCount", 0) + len(added)
        doc["renderableCount"] = doc.get("renderableCount", 0) + len(FULL)
    print("\nADDED:", added or "(none)")
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} (+{len(added)}).")


if __name__ == "__main__":
    main()