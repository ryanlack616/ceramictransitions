#!/usr/bin/env python3
"""2026-10-26 deep-audit additions — six genuinely-missing high-temp ceramics
from Materials Project (94 -> 100 structures). Skipped with documentation
(MgCr2O4, Ta4HfC5) because MP has no clean on-topic phase — same rule as
Tridymite. Gates identical to _add_deferred: exact stoichiometry + expected
bond-length means per entry."""
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

# name, formula, mp_id, supercell, system, class, service, mp, tags, info, expected
ADD_SPECS = [
    ("Ti₂AlC (MAX)", "Ti₂AlC", "mp-aaaaatfq", (3, 3, 2),
     "Hexagonal P6₃/mmc (MAX phase, Ti₂AlC n=1)",
     "max_phase", 1000, 1500,
     ["high-temperature-ceramic", "max-phase", "machinable", "nanolaminate", "tbc-interlayer"],
     ["Ti₂AlC — the canonical n=1 MAX phase: Ti-C edge-sharing octahedral sheets interleaved with Al monolayers.",
      "Machinable and damage-tolerant; decomposes well above its service ceiling.",
      "Service temperature: 1000°C", "Melts/decomposes: ~1500°C", "Thermal shock risk: low"],
     {"Ti-C": (2.00, 2.30), "Ti-Al": (2.60, 2.95)},
    ),
    ("Ceria", "CeO₂", "mp-aaaabdws", (4, 4, 4),
     "Cubic Fm-3m (ceria, fluorite)",
     "refractory_oxide", 1500, 2400,
     ["high-temperature-ceramic", "refractory", "ceria", "fluorite", "zirconia-stabilizer"],
     ["Ceria (fluorite CeO₂) — the stabilizer of ceria-zirconia; redox-active at high temperature (Ce⁴⁺/Ce³⁺) and a refractory oxide in its own right.",
      "Service temperature: 1500°C", "Melting point: 2400°C", "Thermal shock risk: medium"],
     {"Ce-O": (2.25, 2.45)},
    ),
    ("Hibonite", "CaAl₁₂O₁₉", "mp-aaacrvvd", (2, 2, 1),
     "Hexagonal P6₃mc (hibonite CA₆, magnetoplumbite-type)",
     "refractory_oxide", 1500, 1830,
     ["high-temperature-ceramic", "refractory", "hibonite", "calcium-aluminate", "kiln-furniture"],
     ["Hibonite (CA₆ calcium hexaaluminate) — the key aggregate/phase in modern high-alumina refractory castables and CA6-hibonite ceramics.",
      "Service temperature: 1500°C", "Melting point: ~1830°C", "Thermal shock risk: medium"],
     {"Ca-O": (2.30, 2.80), "Al-O": (1.75, 2.05)},
    ),
    ("Lanthanum Hexaboride", "LaB₆", "mp-aaaaadzc", (3, 3, 3),
     "Cubic Pm-3m (lanthanum hexaboride, CaB₆-type)",
     "boride", 1600, 2710,
     ["high-temperature-ceramic", "boride", "electron-emitter", "refractory", "cathode"],
     ["Lanthanum hexaboride — refractory thermionic emitter (cathodes, electron guns) for high-temperature/vacuum service.",
      "Service temperature: 1600°C (vacuum/inert)", "Melting point: 2710°C", "Thermal shock risk: low"],
     {"La-B": (2.80, 3.20)},
    ),
    ("Vanadium Nitride", "VN", "mp-aaaaabjp", (4, 4, 4),
     "Cubic Fm-3m (rock-salt VN)",
     "nitride", 600, 2050,
     ["high-temperature-ceramic", "nitride", "hard-coating", "wear-resistant"],
     ["Rock-salt VN — the classic ordered NaCl cell; hard-coating nitride.",
      "Caveat: stoichiometric VN sits ~0.19 eV/atom above MP's hexagonal VN₁₋ₓ ground state — this is the ideal ordered structure.",
      "Service temperature: 600°C (air)", "Melting/decomposition: ~2050°C", "Thermal shock risk: medium"],
     {"V-N": (2.00, 2.20)},
    ),
    ("Barium Zirconate", "BaZrO₃", "mp-aaaaafrm", (3, 3, 3),
     "Cubic Pm-3m (barium zirconate perovskite)",
     "refractory_oxide", 1200, 2600,
     ["high-temperature-ceramic", "perovskite", "zirconate", "refractory", "proton-conductor"],
     ["Barium zirconate — archetypal cubic perovskite; refractory with very low thermal expansion; high-temperature proton conductor when doped.",
      "Service temperature: 1200°C", "Melting point: ~2600°C", "Thermal shock risk: low"],
     {"Zr-O": (2.00, 2.25), "Ba-O": (2.70, 3.05)},
    ),
]

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(formula):
    f = formula.translate(_SUB).replace("ₓ", "x").replace("·", " ")
    f = re.sub(r"^\d+H-", "", f)
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
    for (name, formula, mp_id, sc, system, mclass, service, mp_temp,
         tags, info, expected) in ADD_SPECS:
        if name in names:
            print(f"SKIP {name}: present"); continue
        payload = _mp_fetch(mp_id, api_key)
        sg = (payload.get("symmetry") or {}).get("symbol", "?")
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)
        f = formula_counts(formula); a = Counter(x["e"] for x in atoms)
        stoich = all(abs(f[el] / sum(f.values()) - a[el] / len(atoms)) <= 0.02
                     for el in set(f) | set(a))
        means = {p: bmean(stats.get("bondLengths") or {}, p) for p in expected}
        bonds_ok = all(m is not None and lo <= m <= hi
                       for m, (lo, hi) in zip(means.values(), expected.values()))
        print(f"## {name} [{mp_id}] {sg} {len(atoms)} at  means={means}")
        if not (stoich and bonds_ok):
            print(f"   GATE FAIL stoich={stoich} bonds={bonds_ok} — skipped"); continue
        entry = {
            "name": name, "formula": formula, "system": system,
            "material_class": mclass, "service_temp_c": service,
            "melting_point_c": mp_temp, "application_tags": tags,
            "info": info + [f"Source: Materials Project {mp_id}. DFT-relaxed coordinates."],
            "supercell": scl, "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). 2026-10-26 deep-audit pass; supercell {scl[0]}×{scl[1]}×{scl[2]}, centred at origin.",
        }
        doc["structures"].append(entry)
        added.append(name)
    if added:
        doc["structureCount"] = doc.get("structureCount", 0) + len(added)
        doc["renderableCount"] = doc.get("renderableCount", 0) + len(added)
        print(f"\nstructureCount -> {doc['structureCount']}; renderableCount -> {doc['renderableCount']}")
    print("\nADDED:", added or "(none)")
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} (+{len(added)} entries).")


if __name__ == "__main__":
    main()