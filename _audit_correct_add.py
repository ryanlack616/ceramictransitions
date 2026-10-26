#!/usr/bin/env python3
"""2026-10-26 structure audit — correct + add (dry-run default).

Corrections / additions to data/crystal_vr.json based on the full-structure
audit (validate_crystal_vr.py + stoichiometry + cell sanity):

A. DOCUMENT (not silently fix) the 7 hand-built pedagogical models whose atom
   counts deviate from exact formula stoichiometry:
     Zircon (O halved), Leucite (K doubled), Willemite, Enstatite, Anorthite,
     Kaolinite, Talc.
   These need a crystallographic source (MP/ICSD, no API key in .env) to
   rebuild properly. We append an honest "model note" to info[].

B. ADD 5 genuinely missing high-temp ceramics as prototype-stubs that promote
   to procedural 3D lattices at load (they need matching PROTOTYPE_TABLE keys
   added to index.html):
     Calcium Oxide  (CaO,  rocksalt)        a=4.811
     Beryllium Oxide(BeO,  wurtzite)        a=2.698, c=4.377
     Tantalum Diboride (TaB2, AlB2-type)    a=3.098, c=3.227
     Hafnium Nitride (HfN, rocksalt)        a=4.525
     High-Entropy Carbide (Hf,Zr,Ti,Ta,Nb)C — mixed-cation rocksalt, a=4.46
   These complete canonical UHTC sets: the diboride trio (ZrB2/HfB2/TaB2),
   late-transition-metal nitrides (TiN/ZrN/HfN) and calcite's oxide product.

Usage:
  python _audit_correct_add.py            # dry run
  python _audit_correct_add.py --write    # apply
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"

MODEL_NOTE = ("Structural note (2026-10 audit): this lattice is a pedagogical "
              "rendering; atom counts approximate the formula but are not exact "
              "crystallography. Rebuild in progress from a cited coordinate source.")

MODEL_NOTE_NAMES = ["Zircon", "Leucite", "Willemite", "Enstatite", "Anorthite",
                    "Kaolinite", "Talc"]

NEW_ENTRIES = [
    {
        "name": "Calcium Oxide", "formula": "CaO",
        "system": "Cubic Fm-3m (rock-salt)",
        "material_class": "refractory_oxide",
        "service_temp_c": 1800, "melting_point_c": 2570,
        "application_tags": ["high-temperature-ceramic", "refractory", "lime",
                             "decomposition-product-of:Calcite"],
        "info": ["Common lime refractory. Forms by calcite decomposition (see Calcite transitions, CaO+CO2 @825°C).",
                 "Service temperature: 1800°C", "Thermal expansion: 13.4 × 10⁻⁶/°C", "Thermal shock risk: medium"],
        "isStub": True,
    },
    {
        "name": "Beryllium Oxide", "formula": "BeO",
        "system": "Hexagonal P6₃mc (wurtzite)",
        "material_class": "refractory_oxide",
        "service_temp_c": 1800, "melting_point_c": 2530,
        "application_tags": ["high-temperature-ceramic", "refractory", "high-thermal-conductivity",
                             "nuclear-applications", "electronics-thermal-management"],
        "info": ["Outstanding thermal conductivity for an electrical insulator (~300 W/m·K, second to diamond among oxides).",
                 "Service temperature: 1800°C", "Thermal expansion: 7.5 × 10⁻⁶/°C",
                 "Toxicity hazard: dust is a serious inhalation risk — handled with containment"],
        "isStub": True,
    },
    {
        "name": "Tantalum Diboride", "formula": "TaB₂",
        "system": "Hexagonal P6/mmm (AlB₂-type)",
        "material_class": "UHTC",
        "service_temp_c": 1800, "melting_point_c": 3040,
        "application_tags": ["high-temperature-ceramic", "UHTC", "thermal-protection-system",
                             "rocket-nozzle", "leading-edge"],
        "info": ["Completes the canonical UHTC diboride trio with ZrB₂ and HfB₂.",
                 "Service temperature: 1800°C", "Thermal expansion: 5.6 × 10⁻⁶/°C", "Thermal shock risk: low-medium"],
        "isStub": True,
    },
    {
        "name": "Hafnium Nitride", "formula": "HfN",
        "system": "Cubic Fm-3m (rock-salt)",
        "material_class": "nitride",
        "service_temp_c": 2000, "melting_point_c": 3310,
        "application_tags": ["high-temperature-ceramic", "nitride", "UHTC", "wear-resistant",
                             "nuclear-cladding-candidate"],
        "info": ["Rock-salt hafnium nitride; pairs with TiN and ZrN in the late-transition-metal nitride set.",
                 "Service temperature: 2000°C", "Thermal expansion: 6.9 × 10⁻⁶/°C", "Thermal shock risk: low"],
        "isStub": True,
    },
    {
        "name": "High-Entropy Carbide (Hf,Zr,Ti,Ta,Nb)C", "formula": "(HfZrTiTaNb)C",
        "system": "Cubic Fm-3m (rock-salt, 5-cation solid solution)",
        "material_class": "high_entropy",
        "service_temp_c": 2000, "melting_point_c": 3500,
        "application_tags": ["uhtc", "high-entropy-ceramic", "next-gen-thermal-protection",
                             "rocket-nozzle"],
        "info": ["Equimolar 5-cation rock-salt solid solution; HEC archetype.",
                 "Procedural mixed-cation lattice (cations cycled over sites) — a true DFT supercell is a Phase 3.5+ task.",
                 "Service temperature: 2000°C", "Thermal expansion: ~7 × 10⁻⁶/°C",
                 "Note: precise lattice parameter depends on the cation mix; ~4.46 Å used here."],
        "isStub": True,
    },
]

def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    doc = load()
    names = {s["name"] for s in doc["structures"]}

    add = [e for e in NEW_ENTRIES if e["name"] not in names]
    print("ADD %d missing entries:" % len(add))
    for e in add:
        print("  + %-42s %-12s | %s" % (e["name"], e["formula"], e["system"]))

    noted = 0
    for s in doc["structures"]:
        if s["name"] in MODEL_NOTE_NAMES and not any(
                "Structural note (2026-10 audit)" in (i or "") for i in (s.get("info") or [])):
            noted += 1
    print("APPEND model-note to %d deviant pedagogical entries." % noted)

    old_count = doc.get("structureCount")
    new_count = old_count + len(add)
    print("structureCount header: %s -> %s" % (old_count, new_count))

    if not args.write:
        print("\n(dry run — rerun with --write to apply.)")
        return

    for e in add:
        # House style: even metadata-only stubs carry empty lattice placeholders
        # (the JSON Schema requires these keys; the viewer fills them at load via
        # prototype promotion, or leaves the stub overlay).
        e.setdefault("atoms", [])
        e.setdefault("bonds", [])
        e.setdefault("bondTypes", [])
        e.setdefault("cellVectors", [])
        e.setdefault("supercell", None)
        e.setdefault("stats", {"bondLengths": {}, "coordDist": {}})
        e.setdefault("bound_type", "melts")
        doc["structures"].append(e)
    for s in doc["structures"]:
        if s["name"] in MODEL_NOTE_NAMES and not any(
                "Structural note (2026-10 audit)" in (i or "") for i in (s.get("info") or [])):
            s.setdefault("info", []).append(MODEL_NOTE)
    doc["structureCount"] = old_count + len(add)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("\nWrote %s (+%d entries, %d model notes). Run validate_crystal_vr.py + smoke." % (DATA, len(add), noted))


if __name__ == "__main__":
    main()