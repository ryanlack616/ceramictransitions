#!/usr/bin/env python3
"""2026-10-26 (CH-261026-6) — add the 7 deferred-but-real materials from
Materials Project (PLANS.md Open Operational Threads #2). Tridymite is
deliberately NOT in this pass: MP has no clean on-topic phase (its top SiO2
entries are other polymorphs at low ehull), so it is documented as needing a
specialist source instead of risking a mislabeled structure.

Additions (87 -> 94 structures; renderable 84 -> 91):
  Yttrium Oxide (Y2O3)     mp-aaaaadya Ia-3        [2,2,2]  yttria: zirconia's stabilizer
  Yttrium Aluminum Garnet  mp-aaaaaeni Ia-3d       [1,1,1]  YAG transparent ceramic
  Hafnon (HfSiO4)          mp-aaaaagvh I41/amd     [3,3,3]  zircon-analog
  Celsian (BaAl2Si2O8)     mp-aaaabapn C2/c        [2,2,1]  barium feldspar
  Vanadium Carbide (VC)    mp-aaaaabxi Fm-3m       [4,4,4]  rock-salt
  Molybdenum Carbide       mp-aaaaachs Pbcn        [3,3,3]  alpha-Mo2C
  6H-SiC                   mp-aaaaalhn P63mc       [3,3,1]  the alpha polytype

Same gates as the 7-model rebuild: exact formula stoichiometry + mean bond
lengths inside crystallographic ranges, verified per entry before write.

Usage:
  python _add_deferred.py            # dry run
  python _add_deferred.py --write    # append to data/crystal_vr.json
"""
import argparse
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

# name, formula, mp_id, supercell, system, material_class, service_temp_c,
# melting_point_c, application_tags, info, expected-bond ranges
ADD_SPECS = [
    (
        "Yttrium Oxide", "Y₂O₃", "mp-aaaaadya", (2, 2, 2),
        "Cubic Ia-3 (bixbyite)",
        "refractory_oxide", 1800, 2425,
        ["high-temperature-ceramic", "refractory", "yttria", "transparent-ceramic",
         "zirconia-stabilizer"],
        ["Cubic bixbyite (Ia-3) yttria — zirconia's stabilizer and the host of the Y-silicate EBC family.",
         "Service temperature: 1800°C", "Thermal expansion: 8.1 × 10⁻⁶/°C", "Thermal shock risk: medium"],
        {"Y-O": (2.15, 2.55)},
    ),
    (
        "Yttrium Aluminum Garnet", "Y₃Al₅O₁₂", "mp-aaaaaeni", (1, 1, 1),
        "Cubic Ia-3d (garnet)",
        "oxide", 1650, 1970,
        ["high-temperature-ceramic", "transparent-ceramic", "laser-host",
         "scintillator", "refractory"],
        ["Yttrium aluminum garnet (cubic Ia-3d) — synthetic gem, laser host, creep-resistant optic/refractory.",
         "Service temperature: 1650°C", "Thermal expansion: 7.8 × 10⁻⁶/°C", "Thermal shock risk: low"],
        {"Y-O": (2.20, 2.50), "Al-O": (1.75, 2.05)},
    ),
    (
        "Hafnon", "HfSiO₄", "mp-aaaaagvh", (3, 3, 3),
        "Tetragonal I4₁/amd (zircon-type)",
        "silicate", 1400, 1900,
        ["high-temperature-ceramic", "silicate", "hafnon", "nuclear-applications", "refractory"],
        ["Hafnon — the Hf-analog of zircon (I4₁/amd, isostructural); relevant for hafnia-rich nuclear/furnace ceramics.",
         "Service temperature: 1400°C", "Decomposes HfO₂+SiO₂ well above service range", "Thermal shock risk: medium"],
        {"Hf-O": (2.05, 2.45), "Si-O": (1.55, 1.75)},
    ),
    (
        "Celsian", "BaAl₂Si₂O₈", "mp-aaaabapn", (2, 2, 1),
        "Monoclinic C2/c (barium feldspar)",
        "silicate", 1250, 1760,
        ["high-temperature-ceramic", "silicate", "feldspar", "cmc-matrix",
         "low-thermal-expansion", "refractory"],
        ["Barium feldspar (monoclinic C2/c) — the lowest-CTE feldspar; the stable phase in BaAl₂Si₂O₈ glass-ceramics and oxide-CMC matrices.",
         "Service temperature: 1250°C", "Thermal expansion: 2.7 × 10⁻⁶/°C (very low)", "Thermal shock risk: low"],
        {"Ba-O": (2.65, 3.25), "Al-O": (1.68, 1.95), "Si-O": (1.55, 1.78)},
    ),
    (
        "Vanadium Carbide", "VC", "mp-aaaaabxi", (4, 4, 4),
        "Cubic Fm-3m (rock-salt)",
        "carbide", 700, 2650,
        ["high-temperature-ceramic", "carbide", "wear-resistant", "hardness"],
        ["Rock-salt VC — very hard and refractory. Stoichiometric VC sits ~0.09 eV/atom above the C-deficient MP ground states (V₆C₅/V₈C₇), so this is the ideal ordered cell.",
         "Service temperature: 700°C (air)", "Thermal expansion: 7.2 × 10⁻⁶/°C", "Thermal shock risk: medium"],
        {"V-C": (1.95, 2.30)},
    ),
    (
        "Molybdenum Carbide", "Mo₂C", "mp-aaaaachs", (3, 3, 3),
        "Orthorhombic Pbcn (α-Mo₂C)",
        "carbide", 800, 2520,
        ["high-temperature-ceramic", "carbide", "catalyst-support", "refractory"],
        ["α-Mo₂C (ordered orthorhombic Pbcn) — a refractory carbide for inert/reducing service; oxidation-limited in air above ~700-800°C.",
         "Service temperature: 800°C (air)", "Thermal expansion: 5.6 × 10⁻⁶/°C", "Thermal shock risk: medium"],
        {"Mo-C": (2.05, 2.50)},
    ),
    (
        "6H-SiC (α)", "SiC", "mp-aaaaalhn", (3, 3, 1),
        "Hexagonal P6₃mc (6H-SiC)",
        "carbide", 1600, 2730,
        ["high-temperature-ceramic", "carbide", "sic", "polytype", "abrasive", "kiln-furniture"],
        ["α-SiC 6H polytype (hexagonal P6₃mc, 12-atom cell) — the dominant engineering polytype; the D.3 transition chain names it as the β→α (3C→6H) product above ~2000°C.",
         "Service temperature: 1600°C", "Thermal expansion: 4.5 × 10⁻⁶/°C", "Thermal shock risk: low"],
        {"Si-C": (1.80, 2.00)},
    ),
]

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(formula):
    f = formula.translate(_SUB).replace("ₓ", "x").replace("₋", "-").replace("·", " ")
    # Drop a leading polytype label like "6H-" (6H-SiC) — not part of chemistry.
    f = re.sub(r"^\d+H-", "", f)
    counts = Counter()
    for group, gmul, el, emul in re.findall(r"\(([A-Za-z0-9]+)\)([0-9.]*)|([A-Z][a-z]?)([0-9.]*)", f):
        if group:
            mul = float(gmul) if gmul else 1.0
            for m in re.finditer(r"([A-Z][a-z]?)([0-9.]*)", group):
                counts[m.group(1)] += mul * (float(m.group(2)) if m.group(2) else 1.0)
        elif el and el.isalpha() and el != "x":
            counts[el] += float(emul) if emul else 1.0
    return counts


def bmean_for(bmeans, pair):
    """Look up a mean bond length regardless of element ordering in the key."""
    canon = "-".join(sorted(pair.split("-")))
    return bmeans.get(canon)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr)
        return 2

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    names = {s["name"] for s in doc["structures"]}
    added = []
    for spec in ADD_SPECS:
        (name, formula, mp_id, sc, system, mclass, service, mp_temp,
         tags, info, expected) = spec
        if name in names:
            print(f"SKIP {name}: already present"); continue
        payload = _mp_fetch(mp_id, api_key)
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)

        # gate A — stoichiometry
        f = formula_counts(formula)
        a = Counter(x["e"] for x in atoms)
        ft = sum(f.values())
        stoich_ok = all(abs(f[el] / ft - a[el] / len(atoms)) <= 0.02
                        for el in set(f) | set(a))
        # gate B — expected bond lengths
        bmeans = stats.get("bondLengths") or {}
        bond_means = [bmean_for(bmeans, pair) for pair in expected]
        bonds_ok = all(m is not None and lo <= m <= hi
                       for m, (lo, hi) in zip(bond_means, expected.values()))
        print(f"\n## {name}  [{mp_id}]  {len(atoms)} atoms  {system}")
        print(f"   bond means (Å): {dict(bmeans)}")
        if not (stoich_ok and bonds_ok):
            print(f"   GATE FAIL stoich={stoich_ok} bonds={bonds_ok} — skipped")
            continue

        entry = {
            "name": name, "formula": formula, "system": system,
            "material_class": mclass, "service_temp_c": service,
            "melting_point_c": mp_temp, "application_tags": tags,
            "info": info + [f"Source: Materials Project {mp_id}. DFT-relaxed coordinates."],
            "supercell": scl,
            "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": (
                f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). "
                f"2026-10-26 deferred-additions pass; supercell {scl[0]}×{scl[1]}×{scl[2]} "
                f"of the primitive cell, centred at origin."
            ),
        }
        doc["structures"].append(entry)
        added.append(name)

    if added:
        old_sc = doc.get("structureCount")
        doc["structureCount"] = old_sc + len(added)
        doc["renderableCount"] = doc.get("renderableCount", 0) + len(added)
        print(f"\nstructureCount {old_sc} -> {doc['structureCount']}; "
              f"renderableCount -> {doc['renderableCount']}")

    print("\nADDED:", added or "(none)")
    if not args.write:
        print("\n(dry run — rerun with --write to apply.)")
        return

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} (+{len(added)} entries). Run validator + schema + smoke.")


if __name__ == "__main__":
    main()