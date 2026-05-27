"""Phase 3.3 P3: append layered SYSTEM entries to crystal_vr.json.

These are not single crystals — they document multi-layer architectures
that are the actual deployment form of HT ceramics:

  TBC stack:  Superalloy / NiCoCrAlY bond / TGO α-Al₂O₃ / 7YSZ topcoat
  EBC stack:  SiC-CMC / Si bond coat / Mullite or Yb₂SiO₅ interlayer / Yb₂Si₂O₇ topcoat
  CMC:        SiC fibers / pyC or BN interphase / SiC matrix (CVI or PIP)

Stored with `entry_type="system"` and `layers[]` describing each layer's
material, thickness, role, and a cross-reference to the single-crystal
entry (by `name`) where applicable.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

DATA = Path(__file__).parent / "data" / "crystal_vr.json"

SYSTEMS = [
    {
        "name": "TBC System (7YSZ on Superalloy)",        "formula": "Ni-base / NiCoCrAlY / α-Al₂O₃(TGO) / ZrO₂-8Y₂O₃",
        "entry_type": "system",
        "isStub": True,
        "system": "Multi-layer thermal barrier coating stack",
        "material_class": "TBC",
        "service_temp_c": 1200,
        "melting_point_c": None,
        "application_tags": ["tbc","turbine-hot-section","system-architecture","high-temperature-ceramic"],
        "layers": [
            {"role": "substrate", "material": "Ni-base superalloy (CMSX-4 / René N5)", "thickness_um": 1000, "purpose": "Load-bearing component"},
            {"role": "bond coat", "material": "NiCoCrAlY (HVOF or LPPS)", "thickness_um": 150, "purpose": "Bonds topcoat, supplies Al for TGO; CTE bridge"},
            {"role": "TGO", "material": "α-Al₂O₃", "thickness_um": 5, "purpose": "Thermally grown oxide; oxygen barrier; CTE mismatch source", "xref": "Corundum"},
            {"role": "topcoat", "material": "ZrO₂-8mol%Y₂O₃ (EB-PVD or APS)", "thickness_um": 250, "purpose": "Thermal insulator; strain-tolerant columnar microstructure", "xref": "Yttria-Stabilized Zirconia (8 mol% Y₂O₃)"},
        ],
        "info": [
            "Standard turbine blade TBC architecture (since ~1990s).",
            "Failure mode: TGO growth + thermal-cycle stress drives topcoat spallation.",
            "T cap ~1200°C; sintering + phase destabilisation above this.",
            "CMAS infiltration is dominant degradation above 1240°C.",
        ],
        "uncertainty_notes": "System entry — illustrative architecture only. Layer thicknesses are representative; actual coatings vary by OEM/application.",
    },
    {
        "name": "EBC System (Yb₂Si₂O₇ on SiC-CMC)",
        "formula": "SiC-SiC CMC / Si / Yb₂SiO₅ / Yb₂Si₂O₇",
        "entry_type": "system",
        "isStub": True,
        "system": "Multi-layer environmental barrier coating stack",
        "material_class": "EBC",
        "service_temp_c": 1480,
        "melting_point_c": None,
        "application_tags": ["ebc","steam-water-vapor-protection","sic-cmc-protection","system-architecture","high-temperature-ceramic"],
        "layers": [
            {"role": "substrate", "material": "SiC/SiC ceramic matrix composite", "thickness_um": 2000, "purpose": "Load-bearing hot-section component", "xref": "SiC-SiC Ceramic Matrix Composite"},
            {"role": "bond coat", "material": "Silicon (HVOF or slurry)", "thickness_um": 75, "purpose": "Bonds EBC to CMC; oxidises to SiO₂ at interface"},
            {"role": "intermediate", "material": "Yb₂SiO₅ (or mullite)", "thickness_um": 75, "purpose": "CTE grading; reduces stress between Si and topcoat", "xref": "Ytterbium Silicate"},
            {"role": "topcoat", "material": "Yb₂Si₂O₇", "thickness_um": 125, "purpose": "Water-vapor and CMAS barrier; CTE-matched to SiC (~3.9×10⁻⁶/K)", "xref": "Ytterbium Disilicate"},
        ],
        "info": [
            "Current generation EBC (GEN-II/III) for SiC-CMC turbine combustors and shrouds.",
            "Protects against Si-OH₄ volatilization in steam (~1300°C+ combustion environment).",
            "T cap ~1480°C (steam stability of disilicate).",
            "Yb chosen for lowest Si-OH₄ recession rate among RE family.",
        ],
        "uncertainty_notes": "System entry — architecture and thicknesses are representative of GE/Rolls-Royce GEN-II EBC designs in public literature.",
    },
    {
        "name": "CMC Architecture (SiC/BN/SiC)",
        "formula": "SiC fiber / BN interphase / SiC matrix (CVI)",
        "entry_type": "system",
        "isStub": True,
        "system": "Ceramic matrix composite micro-architecture",
        "material_class": "CMC",
        "service_temp_c": 1315,
        "melting_point_c": None,
        "application_tags": ["cmc","fiber-reinforced","damage-tolerant","aerospace-structural","high-temperature-ceramic"],
        "layers": [
            {"role": "fiber", "material": "SiC (Hi-Nicalon Type S or Tyranno SA3)", "thickness_um": 10, "purpose": "Load transfer; near-stoichiometric SiC for creep resistance"},
            {"role": "interphase", "material": "h-BN (CVI, 0.3–0.8 μm)", "thickness_um": 0.5, "purpose": "Crack deflection; debonding for damage tolerance", "xref": "Boron Nitride (Hexagonal)"},
            {"role": "matrix", "material": "SiC (CVI + melt-infiltrated Si or PIP)", "thickness_um": 0, "purpose": "Continuous load path; oxidation barrier", "xref": "Silicon Carbide"},
        ],
        "info": [
            "Standard CMC microstructure for turbine shroud and combustor liner.",
            "BN interphase chosen over pyC for steam stability (pyC oxidises at >450°C).",
            "T cap set by SiC fiber creep (~1315°C continuous in oxidising environments).",
            "Always overcoated with an EBC stack (see 'EBC System' entry).",
        ],
        "uncertainty_notes": "Architecture entry — geometry is representative. Fiber arrangement (2D/3D weave) and interphase chemistry vary by manufacturer.",
    },
]


def main():
    root = json.loads(DATA.read_text(encoding="utf-8"))
    existing = {s["name"] for s in root["structures"]}
    added = 0
    for sys_entry in SYSTEMS:
        if sys_entry["name"] in existing:
            print(f"SKIP existing: {sys_entry['name']}")
            continue
        # Satisfy crystal-shaped schema/validator with empty arrays.
        sys_entry.setdefault("atoms", [])
        sys_entry.setdefault("bonds", [])
        sys_entry.setdefault("bondTypes", [])
        sys_entry.setdefault("cellVectors", [])
        sys_entry.setdefault("supercell", [])
        sys_entry.setdefault("stats", {"bondLengths": {}, "coordDist": {}})
        root["structures"].append(sys_entry)
        added += 1
        layers = len(sys_entry["layers"])
        print(f"  + SYSTEM {sys_entry['name']:<40} layers={layers}")
    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(root, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, DATA)
    print(f"OK: appended {added} system entries. total={len(root['structures'])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
