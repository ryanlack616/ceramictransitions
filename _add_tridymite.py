#!/usr/bin/env python3
"""2026-10-26 — add Tridymite using the genuine OP polytype from Materials
Project (mp-aaabewzm, P2_12_12_1, 72 atoms, ehull 0.0075), cross-checked
against Deer et al. 2004 (Ryan-supplied polytype table: OP = orthorhombic
primitive P2_12_12_1, stable ~155 deg C).

Also enriches the alpha-Quartz D.3 transition row for Tridymite with the
alkali-stabilization nuance (tridymite rarely forms from pure quartz; without
alkalis quartz -> cristobalite directly ~1050 deg C).

Gates (same as _rebuild_deviants): exact formula stoichiometry + Si-O mean in
[1.55, 1.70] — crystalline SiO2 frameworks sit ~1.60-1.62.
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

MP_ID = "mp-aaabewzm"

POLYTYPE_INFO = [
    "SiO₂ polymorph — orthorhombic β-tridymite is the most stable form above ~870°C and converts to β-cristobalite above 1470°C.",
    "This entry: OP (low) tridymite, orthorhombic P2₁2₁2₁ (72-atom cell) — the classic room-temperature structure.",
    "Seven tridymite polytypes (Deer et al. 2004): HP β (P6₃/mmm, 460°C) · LHP (P6₃22, 400°C) · OC α (C222₁, 220°C) · OS (100–200°C) · OP (P2₁2₁2₁, 155°C) · MC (Cc, 22°C) · MX (C1, 22°C). Interconversions are complex and sample-dependent; all forms can coexist at ambient.",
    "Mineralogy handbooks often assign tridymite to the triclinic system yet use hexagonal Miller indices (hexagonal crystal shape).",
    "Nuance: tridymite does NOT usually form from pure β-quartz — it is generally stabilized by alkali metals; otherwise β-quartz transitions directly to cristobalite at ~1050°C without the tridymite phase (Deer et al. 2004).",
    "Service temperature: 1470°C (β-tridymite upper stability)", "Melting (metastable): ~1670°C", "Thermal shock risk: low",
]

ENTRY = {
    "name": "Tridymite", "formula": "SiO₂",
    "system": "Orthorhombic P2₁2₁2₁ (tridymite OP, low form)",
    "material_class": "polymorph_silica",
    "service_temp_c": 1470, "melting_point_c": 1670,
    "application_tags": ["high-temperature-ceramic", "polymorph-of:SiO2", "silica",
                         "refractory", "alkali-stabilized"],
    "info": POLYTYPE_INFO,
}


def formula_counts(formula):
    counts = Counter()
    for el, cnt in re.findall(r"([A-Z][a-z]?)([0-9.]*)", formula):
        counts[el] += float(cnt) if cnt else 1.0
    return counts


def main():
    args = sys.argv[1:]
    write = "--write" in args

    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr); return 2

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    entry = next((s for s in doc["structures"] if s["name"] == "Tridymite"), None)
    if entry is None:
        print("ERROR: Tridymite entry not found — abort (cannot add a second one)", file=sys.stderr)
        return 1
    old_n = len(entry.get("atoms", []))
    print(f"REBUILD in place: Tridymite (was {old_n}-atom approximate pedagogical model)")

    payload = _mp_fetch(MP_ID, api_key)
    sg = (payload.get("symmetry") or {}).get("symbol", "?")
    atoms, M, scl = _build_supercell(payload["structure"], (1, 1, 1))
    bonds, bondTypes, stats = _compute_bonds(atoms)

    f = formula_counts("SiO2")
    a = Counter(x["e"] for x in atoms)
    stoich = all(abs(f[el] / sum(f.values()) - a[el] / len(atoms)) <= 0.02
                 for el in set(f) | set(a))
    sio = stats.get("bondLengths", {}).get("O-Si") or stats.get("bondLengths", {}).get("Si-O")
    print(f"## Tridymite [{MP_ID}] {sg}  {len(atoms)} atoms")
    print(f"   bond means (Å): {stats.get('bondLengths')}")
    if not (stoich and sio and 1.55 <= sio <= 1.70):
        print(f"   GATE FAIL stoich={stoich} Si-O={sio} — abort"); return 1

    composed = {
        "system": ENTRY["system"],
        "info": ["Intermediate silica polymorph between quartz and cristobalite"]
                + POLYTYPE_INFO
                + [f"Source: Materials Project {MP_ID}. DFT-relaxed tridymite OP (P2₁2₁2₁); polytype table Deer et al. 2004."],
        "supercell": scl,
        "cellVectors": [[round(v, 4) for v in row] for row in M],
        "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
        "isStub": False, "mp_id": MP_ID,
        "uncertainty_notes": (
            f"Atomic coordinates from Materials Project {MP_ID} (DFT-relaxed tridymite OP). "
            "Tridymite is metastable vs quartz; this is the room-T structural polytype. "
            "The α-Quartz transitions chain's [573–1470 °C] Tridymite window is the textbook "
            "scheme — see its note for the alkali-stabilization caveat."
        ),
    }
    for fld in ("name", "formula", "material_class", "service_temp_c", "melting_point_c",
                "application_tags", "bound_type", "oxidation_temp_c"):
        if fld in entry:
            composed[fld] = entry[fld]
    entry.clear(); entry.update(composed)

    # enrich the α-Quartz Tridymite transition row with the nuance
    for s in doc["structures"]:
        if s["name"] == "α-Quartz":
            for row in s.get("transitions", []):
                if row.get("structure") == "Tridymite":
                    row["note"] = ("Tridymite is alkali-stabilized — it rarely forms from pure β-quartz; "
                                   "without alkalis β-quartz → β-cristobalite directly ~1050°C. "
                                   "Orthorhombic β-tridymite stable >870°C; → β-cristobalite >1470°C (Deer et al. 2004).")
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} (Tridymite rebuilt; structureCount unchanged at {doc['structureCount']}).")


if __name__ == "__main__":
    main()