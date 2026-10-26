#!/usr/bin/env python3
"""2026-10-26 round-4 deep pass: Ti2AlN (MAX nitride), SrHfO3, CaHfO3,
La2Hf2O7, Gd2Hf2O7 (hafnate TBC perovskites/pyrochlores), NbN (rock-salt,
caveated), TaN (hexagonal eps) + two CMC system architectures (C/C and
Oxide-Oxide). Gates as in every pass: exact stoichiometry + crystallographic
bond means, per entry."""
import json, os, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent; DATA = HERE / "data" / "crystal_vr.json"
for _l in (HERE / ".env").read_text(encoding="utf-8").splitlines():
    _l = _l.strip()
    if _l and "=" in _l and not _l.startswith("#"):
        k, v = _l.split("=", 1); os.environ.setdefault(k, v)
sys.path.insert(0, str(HERE))
from _ingest_mp import _mp_fetch, _build_supercell, _compute_bonds

FULL = [
    ("Ti₂AlN (MAX nitride)", "Ti₂AlN", "mp-aaaaahjm", (4, 4, 2),
     "Hexagonal P6₃/mmc (MAX nitride, n=1)", "max_phase", 1000, 1700,
     ["high-temperature-ceramic", "max-phase", "nitride", "nanolaminate", "machinable"],
     ["Ti₂AlN — the archetypal nitride MAX phase (n=1): Ti-N octahedral sheets with Al monolayers.",
      "Service temperature: 1000°C", "Melts/decomposes: ~1700°C", "Thermal shock risk: low"],
     {"Ti-N": (1.95, 2.30), "Ti-Al": (2.60, 3.00)},
    ),
    ("Strontium Hafnate", "SrHfO₃", "mp-aaaaaezy", (3, 3, 3),
     "Orthorhombic Pnma (perovskite)", "refractory_oxide", 1400, 2650,
     ["high-temperature-ceramic", "perovskite", "hafnate", "refractory", "tbc"],
     ["Strontium hafnate — orthorhombic perovskite (Pnma, ehull 0); TBC/refractory candidate with very low thermal expansion.",
      "Service temperature: 1400°C", "Melting point: ~2650°C", "Thermal shock risk: low"],
     {"Sr-O": (2.50, 2.90), "Hf-O": (2.05, 2.40)},
    ),
    ("Calcium Hafnate", "CaHfO₃", "mp-aaabqyqv", (3, 3, 3),
     "Orthorhombic Pnma (perovskite)", "refractory_oxide", 1450, 2490,
     ["high-temperature-ceramic", "perovskite", "hafnate", "refractory", "tbc"],
     ["Calcium hafnate — orthorhombic perovskite (Pnma, ehull 0); refractory with high melting point.",
      "Service temperature: 1450°C", "Melting point: ~2490°C", "Thermal shock risk: medium"],
     {"Ca-O": (2.25, 2.65), "Hf-O": (2.05, 2.40)},
    ),
    ("Lanthanum Hafnate", "La₂Hf₂O₇", "mp-aaaaasob", (3, 3, 2),
     "Cubic Fd-3m (pyrochlore)", "TBC", 1400, 2400,
     ["high-temperature-ceramic", "tbc", "pyrochlore", "hafnate", "next-gen-thermal-barrier"],
     ["Lanthanum hafnate — cubic pyrochlore (Fd-3m, ehull 0); next-gen TBC beyond the zirconate pyrochlores.",
      "Service temperature: 1400°C", "Melting point: ~2400°C", "Thermal shock risk: low"],
     {"La-O": (2.35, 2.65), "Hf-O": (2.05, 2.40)},
    ),
    ("Gadolinium Hafnate", "Gd₂Hf₂O₇", "mp-aaacpssr", (3, 3, 2),
     "Cubic Fd-3m (pyrochlore)", "TBC", 1400, 2350,
     ["high-temperature-ceramic", "tbc", "pyrochlore", "hafnate", "next-gen-thermal-barrier"],
     ["Gadolinium hafnate — cubic pyrochlore (Fd-3m, ehull 0); low-thermal-conductivity TBC candidate.",
      "Service temperature: 1400°C", "Melting point: ~2350°C", "Thermal shock risk: low"],
     {"Gd-O": (2.30, 2.60), "Hf-O": (2.05, 2.40)},
    ),
    ("Niobium Nitride", "NbN", "mp-aaaaaciu", (5, 5, 5),
     "Cubic Fm-3m (rock-salt δ′-NbN)", "nitride", 600, 2200,
     ["high-temperature-ceramic", "nitride", "hard-coating", "superconductor", "wear-resistant"],
     ["Rock-salt δ′-NbN — the classic hard nitride / superconducting phase.",
      "Caveat: sits ~0.20 eV/atom above MP's hexagonal δ-NbN ground state — this is the ordered NaCl cell.",
      "Service temperature: 600°C (air)", "Melting/decomposition: ~2200°C", "Thermal shock risk: medium"],
     {"Nb-N": (2.00, 2.30)},
    ),
    ("Tantalum Nitride", "TaN", "mp-aaaaabxf", (4, 4, 3),
     "Hexagonal P-62m (ε-TaN)", "nitride", 600, 2950,
     ["high-temperature-ceramic", "nitride", "hard-coating", "wear-resistant"],
     ["ε-TaN — hexagonal tantalum nitride (P-62m, ehull 0, the MP ground state); very hard and refractory.",
      "Service temperature: 600°C (air)", "Melting point: ~2950°C", "Thermal shock risk: medium"],
     {"Ta-N": (2.00, 2.35)},
    ),
]

SYSTEMS = [
    dict(name="C/C Composite (Carbon-Carbon)", formula="PAN fiber / pyrocarbon / CVI matrix (+SiC coating optional)",
         system="Multi-layer carbon/carbon composite architecture", entry_type="system", isStub=True,
         material_class="CMC", service_temp_c=1650, melting_point_c=None,
         application_tags=["cmc", "fiber-reinforced", "re-entry", "thermal-protection-system", "high-temperature-ceramic"],
         info=["Carbon/carbon CMC — the re-entry heat-shield mainstay (PAN fiber + pyrocarbon interphase + CVD/CVI carbon matrix).",
               "Service temperature: 1650°C in air (≥2800°C inert); oxidation is the life limit.",
               "Layers: PAN-derived carbon fiber / pyrocarbon interphase / CVI carbon matrix / optional SiC coating (xref Silicon Carbide)."],
         layers=[
             {"role": "fiber", "material": "PAN-based carbon fiber (T300/T700 class)", "thickness_um": 7, "purpose": "Reinforcement", "xref": "Graphite"},
             {"role": "interphase", "material": "Pyrolytic carbon coating", "thickness_um": 0.5, "purpose": "Crack deflection, load transfer"},
             {"role": "matrix", "material": "Pyrolytic carbon (CVD/CVI)", "thickness_um": None, "purpose": "Consolidation matrix", "xref": "Graphite"},
             {"role": "coating", "material": "SiC oxidation shield (optional)", "thickness_um": 100, "purpose": "Oxidation protection above 1650°C", "xref": "Silicon Carbide"},
         ]),
    dict(name="Oxide-Oxide CMC (Nextel 610 / α-Al₂O₃ + BAS)", formula="Al₂O₃ fiber / porous Al₂O₃ matrix (± Celsian sealant)",
         system="Multi-layer oxide/oxide CMC architecture", entry_type="system", isStub=True,
         material_class="CMC", service_temp_c=1000, melting_point_c=None,
         application_tags=["cmc", "fiber-reinforced", "oxide-oxide", "engine-liner", "high-temperature-ceramic"],
         info=["Oxide-oxide CMC — damage-tolerant and oxidation-immune by construction (Nextel 610 alumina fibers in a porous alumina/BAS matrix).",
               "Service temperature: 1000°C", "No BN interphase needed — inherently oxidation-stable.",
               "Layers: α-Al₂O₃ fiber (xref Corundum) / porous α-Al₂O₃ matrix (xref Corundum) / optional Celsian seal coat (xref Celsian)."],
         layers=[
             {"role": "fiber", "material": "Nextel 610 α-Al₂O₃ fiber", "thickness_um": 12, "purpose": "Reinforcement", "xref": "Corundum"},
             {"role": "matrix", "material": "Porous α-Al₂O₃ matrix", "thickness_um": None, "purpose": "Crack-impregnable porous matrix", "xref": "Corundum"},
             {"role": "sealant", "material": "Celsian (BaAl₂Si₂O₈) BAS seal coat", "thickness_um": 50, "purpose": "Environmental barrier / densification", "xref": "Celsian"},
         ]),
]

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(f0):
    f = f0.translate(_SUB).replace("ₓ", "x").replace("₋", "-").replace("·", " ")
    c = Counter()
    for g, gm, el, em in re.findall(r"\(([A-Za-z0-9]+)\)([0-9.]*)|([A-Z][a-z]?)([0-9.]*)", f):
        if g:
            m = float(gm) if gm else 1.0
            for x in re.finditer(r"([A-Z][a-z]?)([0-9.]*)", g):
                c[x.group(1)] += m * (float(x.group(2)) if x.group(2) else 1.0)
        elif el and el.isalpha() and el != "x":
            c[el] += float(em) if em else 1.0
    return c


def bmean(bm, pair):
    return bm.get("-".join(sorted(pair.split("-"))))


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
            "uncertainty_notes": f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). 2026-10-26 round-4 pass.",
        }
        doc["structures"].append(entry); added.append(name)

    for sysdef in SYSTEMS:
        name = sysdef["name"]
        if name in names:
            print(f"SKIP {name}: already present"); continue
        entry = dict(sysdef)
        entry.setdefault("atoms", []); entry.setdefault("bonds", [])
        entry.setdefault("bondTypes", []); entry.setdefault("cellVectors", [])
        entry.setdefault("supercell", None)
        entry.setdefault("stats", {"bondLengths": {}, "coordDist": {}})
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