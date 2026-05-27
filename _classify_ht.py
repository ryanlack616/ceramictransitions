#!/usr/bin/env python3
"""
Phase 3.3 P0: classify all entries in data/crystal_vr.json with HT-focused
metadata so the library can be filtered/sorted by service temperature and
material class.

Adds per-entry fields:
  material_class      one of: oxide, refractory_oxide, silicate, UHTC, TBC, EBC,
                              CMC, carbide, nitride, boride, disilicide,
                              precursor, mineral, polymorph_silica, hydroxide,
                              carbonate, max_phase, high_entropy
  service_temp_c      max sustained operating temperature in air, °C
  melting_point_c     melting (or decomposition) point, °C
  application_tags    list of strings — e.g. ["TBC topcoat", "EBC topcoat"]

Idempotent: reads + rewrites data/crystal_vr.json atomically.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
CRYSTAL = REPO / "data" / "crystal_vr.json"

# (material_class, service_temp_c, melting_point_c, application_tags)
# service_temp_c is conservative MAX sustained-air-service temperature.
# melting_point_c uses (m) for melting, (d) for decomposition; numeric only here.
CLASSIFY = {
    # === HT REFRACTORY OXIDES ===
    "Periclase":           ("refractory_oxide", 2200, 2852, ["refractory-brick", "crucible"]),
    "Rutile":              ("oxide",            1500, 1843, ["white-pigment", "photocatalyst"]),
    "Corundum":            ("refractory_oxide", 1800, 2072, ["abrasive", "Nd-YAG-host", "spark-plug", "armor"]),
    "Spinel":              ("refractory_oxide", 1900, 2135, ["transparent-armor", "refractory"]),
    "Mullite":             ("refractory_oxide", 1700, 1840, ["EBC-intermediate", "kiln-furniture", "refractory"]),
    "Baddeleyite":         ("refractory_oxide", 1200, 2715, ["precursor-to:TBC"]),
    "Tetragonal Zirconia": ("refractory_oxide", 1200, 2715, ["TBC-research", "PSZ-component"]),
    "Cubic Zirconia":      ("refractory_oxide", 2400, 2715, ["jewelry", "FSZ"]),
    "Cordierite":          ("refractory_oxide", 1300, 1465, ["catalytic-converter-substrate", "kiln-shelf"]),

    # === HT SILICATES (engineered refractories) ===
    "Forsterite":          ("silicate", 1700, 1890, ["refractory-brick"]),
    "Zircon":              ("silicate", 1500, 1676, ["foundry-mold", "refractory", "decomp-to:ZrO2+SiO2"]),
    "Enstatite":           ("silicate", 1400, 1557, ["refractory-component"]),
    "Diopside":            ("silicate", 1200, 1391, ["glass-ceramic"]),
    "Akermanite":          ("silicate", 1300, 1454, ["slag", "bioceramic"]),
    "Gehlenite":           ("silicate", 1400, 1593, ["cement-clinker-phase"]),
    "Andalusite":          ("silicate", 1380, 1380, ["refractory-precursor", "decomp-to:Mullite+SiO2"]),
    "Kyanite":             ("silicate", 1100, 1100, ["refractory-precursor", "decomp-to:Mullite+SiO2"]),
    "Sillimanite":         ("silicate", 1545, 1545, ["refractory-precursor", "decomp-to:Mullite+SiO2"]),

    # === SiO₂ POLYMORPHS ===
    "α-Quartz":            ("polymorph_silica", 573, 1713, ["polymorph-of:SiO2", "transforms-to:β-Quartz@573C"]),
    "β-Cristobalite":      ("polymorph_silica", 1713, 1713, ["polymorph-of:SiO2", "high-temp-SiO2-form"]),
    "Tridymite":           ("polymorph_silica", 1470, 1670, ["polymorph-of:SiO2"]),

    # === MINERAL / LOW-HT (kept for reference, not HT-engineered) ===
    "Cuprite":             ("mineral", 800, 1235, ["pigment", "p-type-semiconductor"]),
    "Hematite":            ("mineral", 1390, 1539, ["pigment", "iron-ore", "transforms-to:Magnetite>1390C"]),
    "Magnetite":           ("mineral", 1500, 1597, ["magnetic-ceramic", "iron-ore"]),
    "Cassiterite":         ("mineral", 1500, 1630, ["gas-sensor", "tin-ore"]),
    "Willemite":           ("mineral", 1400, 1512, ["green-phosphor"]),

    # === PRECURSORS (clays / carbonates / hydroxides / feldspars / feldspathoids) ===
    "Kaolinite":           ("precursor", 450, 450,  ["precursor-to:Mullite", "decomp-to:Metakaolin@450C"]),
    "Talc":                ("precursor", 800, 800,  ["precursor-to:Enstatite+SiO2", "soft-lubricant"]),
    "Brucite":             ("hydroxide", 350, 350,  ["precursor-to:MgO", "decomp@350C"]),
    "Calcite":             ("carbonate", 825, 825,  ["precursor-to:CaO", "decomp-to:CaO+CO2@825C"]),
    "Dolomite":            ("carbonate", 750, 750,  ["precursor-to:MgO+CaO", "refractory-precursor"]),
    "Albite":              ("precursor", 1118, 1118, ["feldspar", "flux"]),
    "Orthoclase":          ("precursor", 1150, 1150, ["feldspar", "flux"]),
    "Anorthite":           ("precursor", 1553, 1553, ["feldspar", "flux", "porcelain-component"]),
    "Nepheline":           ("precursor", 1257, 1257, ["feldspathoid", "glass-component"]),
    "Leucite":             ("precursor", 1693, 1693, ["feldspathoid", "dental-ceramic"]),
    "Spodumene":           ("precursor", 1380, 1380, ["Li-source", "low-CTE-glass-ceramic"]),
    "Wollastonite":        ("precursor", 1540, 1540, ["filler", "low-loss-microwave"]),

    # === UHTC (Ultra-High Temp Ceramics) ===
    "Zirconium Diboride":  ("UHTC", 1800, 3245, ["hypersonic-leading-edge", "rocket-nozzle"]),
    "Hafnium Diboride":    ("UHTC", 2000, 3380, ["hypersonic-leading-edge", "atmospheric-reentry"]),
    "Zirconium Carbide":   ("UHTC", 1800, 3530, ["rocket-nozzle", "nuclear-fuel-coating"]),
    "Hafnium Carbide":     ("UHTC", 2000, 3958, ["highest-mp-binary", "hypersonic-leading-edge"]),
    "Tantalum Carbide":    ("UHTC", 1900, 3880, ["rocket-nozzle", "cutting-tool"]),

    # === TBC (Thermal Barrier Coatings) ===
    "Stabilized Zirconia":                   ("TBC", 1200, 2700, ["TBC-topcoat-legacy"]),
    "Yttria-Stabilized Zirconia (3 mol% Y₂O₃)": ("TBC", 1100, 2700, ["TBC-topcoat", "structural-tetragonal-PSZ"]),
    "Yttria-Stabilized Zirconia (8 mol% Y₂O₃)": ("TBC", 1200, 2700, ["TBC-topcoat-standard", "turbine-blade"]),
    "Ceria-Stabilized Zirconia":             ("TBC", 1100, 2700, ["TBC-topcoat-research"]),
    "Hafnium Oxide":                         ("TBC", 1500, 2758, ["TBC-next-gen", "high-k-dielectric"]),
    "Lanthanum Zirconate":                   ("TBC", 1300, 2300, ["TBC-topcoat-pyrochlore", "lower-thermal-conductivity"]),

    # === EBC (Environmental Barrier Coatings) ===
    "Ytterbium Silicate":   ("EBC", 1485, 1980, ["EBC-topcoat", "CMC-protection", "low-CTE-match-to-SiC"]),
    "Ytterbium Disilicate": ("EBC", 1485, 1850, ["EBC-topcoat", "CMC-protection", "low-CTE-match-to-SiC"]),

    # === STRUCTURAL HT NON-OXIDES ===
    "Silicon Carbide":           ("carbide", 1600, 2730, ["CMC-fiber-matrix", "kiln-shelf", "armor"]),
    "Reaction-Bonded Silicon Carbide": ("carbide", 1380, 2730, ["near-net-shape", "kiln-furniture"]),
    "Sintered Silicon Carbide":  ("carbide", 1600, 2730, ["pump-seal", "armor", "kiln-furniture"]),
    "Silicon Nitride":           ("nitride", 1400, 1900, ["turbine-rotor", "bearing", "cutting-tool"]),
    "Sintered Silicon Nitride":  ("nitride", 1400, 1900, ["bearing-ball", "turbocharger-rotor"]),
    "Sialon":                    ("nitride", 1400, 1900, ["cutting-tool", "molten-metal-handling"]),
    "Aluminum Nitride":          ("nitride", 1000, 2200, ["electronic-substrate", "thermal-management"]),
    "Boron Nitride (Hexagonal)": ("nitride", 1000, 2973, ["lubricant-HT", "crucible", "breakdown-insulator"]),

    # === CMC ===
    "SiC-SiC Ceramic Matrix Composite": ("CMC", 1300, 2730, ["turbine-shroud", "combustor-liner", "engine-hot-section"]),
}

# Application tags appended to ALL non-precursor entries for global filtering.
HT_GLOBAL_TAGS = ["high-temperature-ceramic"]


def main() -> int:
    if not CRYSTAL.exists():
        print(f"ERROR: {CRYSTAL} not found", file=sys.stderr)
        return 2
    data = json.loads(CRYSTAL.read_text(encoding="utf-8"))
    structs = data if isinstance(data, list) else data.get("structures", [])

    missing: list[str] = []
    updated = 0
    for s in structs:
        name = s.get("name")
        if not name:
            continue
        spec = CLASSIFY.get(name)
        if spec is None:
            missing.append(name)
            continue
        material_class, service_temp_c, melting_point_c, app_tags = spec
        # Append global HT tag for non-precursor entries.
        tags = list(app_tags)
        if material_class not in ("precursor", "carbonate", "hydroxide", "mineral"):
            tags = HT_GLOBAL_TAGS + tags
        s["material_class"] = material_class
        s["service_temp_c"] = service_temp_c
        s["melting_point_c"] = melting_point_c
        s["application_tags"] = tags
        updated += 1

    print(f"Classified {updated}/{len(structs)} entries.")
    if missing:
        print(f"WARN: {len(missing)} entries had no classification entry:")
        for n in missing:
            print(f"  - {n}")
        return 1

    tmp = CRYSTAL.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, CRYSTAL)
    print(f"Wrote {CRYSTAL}.")
    # Distribution summary
    by_class: dict[str, int] = {}
    for s in structs:
        cls = s.get("material_class", "?")
        by_class[cls] = by_class.get(cls, 0) + 1
    print("\nDistribution by material_class:")
    for cls, n in sorted(by_class.items(), key=lambda kv: -kv[1]):
        print(f"  {cls:>20}  {n:>3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
