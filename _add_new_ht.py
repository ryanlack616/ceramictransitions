"""Phase 3.3 P2: append NEW HT-ceramic entries to crystal_vr.json.

Adds materials that were entirely missing from the catalog:
  Real (MP ingest):
    Ti₃SiC₂        mp-5659    P6₃/mmc   MAX phase (M=Ti, A=Si, X=C, n=2)
    Ti₃AlC₂        mp-3747    P6₃/mmc   MAX phase (M=Ti, A=Al, X=C, n=2)
    B₄C            mp-696746  R-3m      Boron carbide
    TiB₂           mp-1145    P6/mmm    Titanium diboride (UHTC)
    TiC            mp-631     Fm-3m     Titanium carbide
    NbC            mp-910     Fm-3m     Niobium carbide
    Cr₃C₂          mp-20937   Pnma      Chromium carbide
    WC             mp-1894    P-6m2     Tungsten carbide
    TiN            mp-492     Fm-3m     Titanium nitride
    Y₂Si₂O₇        mp-5652    C2/m      Yttrium disilicate (EBC)
    Y₂SiO₅         mp-554420  P2₁/c     Yttrium silicate (EBC)
    Lu₂Si₂O₇       mp-18385   P4₁2₁2    Lutetium disilicate (EBC)
    Gd₂Zr₂O₇       mp-757233  Fd-3m     Gadolinium zirconate pyrochlore (TBC)
    MoSi₂          mp-8938    P6₂22     Molybdenum disilicide (heater)
    Graphite       mp-48      P6₃/mmc   Reference layered carbon

  Stubs (no clean MP entry):
    Cr₂AlC                              MAX phase (M=Cr, A=Al, X=C, n=1)
    c-BN                                Cubic boron nitride
    ZrN                                 Zirconium nitride
    Lu₂SiO₅                             Lutetium silicate (EBC)
    (Hf,Zr,Ti,Ta,Nb)C HEC              High-entropy carbide
"""
from __future__ import annotations
import json, os, sys, urllib.parse, urllib.request, urllib.error, math
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"
CACHE = HERE / "data" / ".mp_cache"
MP_BASE = "https://api.materialsproject.org/materials/summary/"
UA = "ceramictransitions-mp-ingest/0.2 (+https://ceramictransitions.com)"

# reuse helpers from _ingest_mp by import
sys.path.insert(0, str(HERE))
from _ingest_mp import (
    _mp_fetch, _build_supercell, _compute_bonds, BOND_CUTOFFS, RADIUS,
)

# Each spec produces ONE new entry appended to crystal_vr.json.
NEW_REAL = [
    dict(name="Ti₃SiC₂", formula="Ti₃SiC₂", mp_id="mp-5659", supercell=(2,2,1),
         system="Hexagonal P6₃/mmc (MAX phase, M₂AX with n=2)",
         note="Ti₃SiC₂ MAX phase. Layered Ti₃C₂ slabs interleaved with Si planes; machinable yet refractory.",
         material_class="max_phase", service_temp_c=1400, melting_point_c=3000,
         application_tags=["max-phase","damage-tolerant","machinable-ceramic","oxidation-resistant","high-temperature-ceramic"],
         info=["Mₙ₊₁AXₙ MAX phase; M=Ti (transition metal), A=Si (group-A), X=C.",
               "Combines metallic conductivity with ceramic stiffness.",
               "Oxidation forms protective SiO₂+TiO₂ scale above 1000°C."]),
    dict(name="Ti₃AlC₂", formula="Ti₃AlC₂", mp_id="mp-3747", supercell=(2,2,1),
         system="Hexagonal P6₃/mmc (MAX phase, n=2)",
         note="Ti₃AlC₂ MAX phase. Etched form yields Ti₃C₂ MXene.",
         material_class="max_phase", service_temp_c=1300, melting_point_c=2100,
         application_tags=["max-phase","mxene-precursor","damage-tolerant","high-temperature-ceramic"],
         info=["Precursor for Ti₃C₂ MXene (HF or LiF/HCl etch removes Al layer).",
               "Forms protective Al₂O₃ scale on oxidation."]),
    dict(name="Boron Carbide", formula="B₄C", mp_id="mp-696746", supercell=(1,1,1),
         system="Rhombohedral R-3m (B₁₂ icosahedra + C-B-C chain)",
         note="B₄C: icosahedral boron clusters bridged by C-B-C linear chains.",
         material_class="carbide", service_temp_c=1400, melting_point_c=2450,
         application_tags=["armor","neutron-absorber","abrasive","low-density-uhtc-companion","high-temperature-ceramic"],
         info=["Third-hardest known material (Mohs ≈9.5).",
               "B₁₂ icosahedra share edges; C-B-C chain along c-axis."]),
    dict(name="Titanium Diboride", formula="TiB₂", mp_id="mp-1145", supercell=(2,2,2),
         system="Hexagonal P6/mmm (AlB₂-type)",
         note="TiB₂ AlB₂-type. Lower-cost UHTC analog of ZrB₂/HfB₂.",
         material_class="UHTC", service_temp_c=1800, melting_point_c=3225,
         application_tags=["uhtc","boride","electrode","wear-resistant","high-temperature-ceramic"],
         info=["Conductive ceramic; used as cathode in Hall-Héroult aluminium cells.",
               "Cheaper than ZrB₂/HfB₂; gateway boride for AlB₂-family kinetics."]),
    dict(name="Titanium Carbide", formula="TiC", mp_id="mp-631", supercell=(2,2,2),
         system="Cubic Fm-3m (rock-salt)",
         note="TiC rock-salt. Wear-resistant cutting tool ceramic.",
         material_class="carbide", service_temp_c=1800, melting_point_c=3160,
         application_tags=["cutting-tool","wear-resistant","cermet-base","high-temperature-ceramic"],
         info=["Common cermet phase (TiC+Ni/Co binder).",
               "Forms continuous solid solution with TiN."]),
    dict(name="Niobium Carbide", formula="NbC", mp_id="mp-910", supercell=(2,2,2),
         system="Cubic Fm-3m (rock-salt)",
         note="NbC rock-salt. Grain-refiner in WC-Co.",
         material_class="carbide", service_temp_c=1800, melting_point_c=3490,
         application_tags=["cutting-tool","grain-refiner","high-temperature-ceramic"],
         info=["Used as grain-growth inhibitor in cemented carbides.",
               "Forms solid solutions with TiC, TaC, HfC."]),
    dict(name="Chromium Carbide", formula="Cr₃C₂", mp_id="mp-20937", supercell=(1,1,1),
         system="Orthorhombic Pnma",
         note="Cr₃C₂ orthorhombic. HVOF coating base.",
         material_class="carbide", service_temp_c=900, melting_point_c=1895,
         application_tags=["wear-coating","hvof-thermal-spray","oxidation-resistant","high-temperature-ceramic"],
         info=["Cr₃C₂-NiCr is the standard HVOF wear-and-corrosion coating below 900°C.",
               "Lower max-T than other carbides (Cr₂O₃ scale)."]),
    dict(name="Tungsten Carbide", formula="WC", mp_id="mp-1894", supercell=(2,2,2),
         system="Hexagonal P-6m2",
         note="WC simple-hexagonal. Cemented-carbide cutting tool base.",
         material_class="carbide", service_temp_c=1100, melting_point_c=2870,
         application_tags=["cutting-tool","cemented-carbide","wear-resistant","high-temperature-ceramic"],
         info=["Most common cermet phase (WC-Co); H_v ≈22 GPa.",
               "Loses creep resistance via Co binder above ~1100°C."]),
    dict(name="Titanium Nitride", formula="TiN", mp_id="mp-492", supercell=(2,2,2),
         system="Cubic Fm-3m (rock-salt)",
         note="TiN rock-salt. Hard gold-coloured tool coating.",
         material_class="nitride", service_temp_c=600, melting_point_c=2930,
         application_tags=["tool-coating","decorative","diffusion-barrier","high-temperature-ceramic"],
         info=["Common PVD coating on cutting tools (golden colour).",
               "Oxidation-limited above 600°C in air."]),
    dict(name="Yttrium Disilicate", formula="Y₂Si₂O₇", mp_id="mp-5652", supercell=(2,2,2),
         system="Monoclinic C2/m (γ-Y₂Si₂O₇)",
         note="Y₂Si₂O₇ EBC topcoat. CTE-matched to SiC-CMC.",
         material_class="EBC", service_temp_c=1500, melting_point_c=1775,
         application_tags=["ebc","cmas-resistant","cte-match-sic","high-temperature-ceramic"],
         info=["Standard EBC topcoat for SiC/SiC turbine hot section.",
               "CTE ≈3.9×10⁻⁶/K matches SiC.",
               "Multiple polymorphs (α,β,γ,δ); γ stable 1225-1535°C."]),
    dict(name="Yttrium Silicate", formula="Y₂SiO₅", mp_id="mp-554420", supercell=(1,1,1),
         system="Monoclinic P2₁/c (X2-Y₂SiO₅)",
         note="Y₂SiO₅ EBC. Used as interlayer for steam-environment durability.",
         material_class="EBC", service_temp_c=1450, melting_point_c=1980,
         application_tags=["ebc","steam-resistant","high-temperature-ceramic"],
         info=["Monosilicate counterpart to Y₂Si₂O₇.",
               "Higher CTE than disilicate (~7×10⁻⁶/K) — limits direct CMC bonding."]),
    dict(name="Lutetium Disilicate", formula="Lu₂Si₂O₇", mp_id="mp-18385", supercell=(1,1,1),
         system="Tetragonal P4₁2₁2 (Lu₂Si₂O₇)",
         note="Lu₂Si₂O₇ EBC. Best CMAS resistance in the RE-disilicate family.",
         material_class="EBC", service_temp_c=1500, melting_point_c=1800,
         application_tags=["ebc","cmas-resistant","cte-match-sic","high-temperature-ceramic"],
         info=["Among the most CMAS-resistant RE-disilicates.",
               "Slightly higher cost vs Yb/Y analogs."]),
    dict(name="Gadolinium Zirconate", formula="Gd₂Zr₂O₇", mp_id="mp-757233", supercell=(1,1,1),
         system="Cubic Fd-3m (pyrochlore A₂B₂O₇)",
         note="Gd₂Zr₂O₇ pyrochlore TBC. Lower thermal conductivity than YSZ; higher T cap.",
         material_class="TBC", service_temp_c=1500, melting_point_c=2570,
         application_tags=["tbc","next-gen-tbc","low-thermal-conductivity","cmas-resistant","high-temperature-ceramic"],
         info=["Thermal conductivity ≈1.6 W/m·K vs YSZ ≈2.2.",
               "Resists CMAS attack via Gd-apatite formation.",
               "Sintering-resistant; T cap ~1500°C vs YSZ ~1200°C."]),
    dict(name="Molybdenum Disilicide", formula="MoSi₂", mp_id="mp-8938", supercell=(2,2,1),
         system="Hexagonal P6₂22 (high-T β polymorph)",
         note="MoSi₂ disilicide. Furnace heating element.",
         material_class="disilicide", service_temp_c=1700, melting_point_c=2030,
         application_tags=["heating-element","conductive-ceramic","oxidation-resistant","high-temperature-ceramic"],
         info=["Standard high-T furnace element (Kanthal Super).",
               "Self-protecting via SiO₂ passivation; 'pest' oxidation at 400-600°C."]),
    dict(name="Graphite", formula="C", mp_id="mp-48", supercell=(2,2,1),
         system="Hexagonal P6₃/mmc (graphite-2H)",
         note="Reference layered carbon for MAX-phase + BN intercomparison.",
         material_class="carbide", service_temp_c=3000, melting_point_c=3650,
         application_tags=["refractory","reference-structure","anisotropic-conductor","high-temperature-ceramic"],
         info=["Reference for layered structures (MAX phases, h-BN).",
               "Sublimes near 3650°C; oxidises above 500°C in air."]),
]

NEW_STUBS = [
    dict(name="Cr₂AlC", formula="Cr₂AlC",
         system="Hexagonal P6₃/mmc (MAX phase n=1)",
         material_class="max_phase", service_temp_c=1300, melting_point_c=1500,
         application_tags=["max-phase","damage-tolerant","high-temperature-ceramic"],
         info=["Mₙ₊₁AXₙ MAX phase; M=Cr, A=Al, X=C, n=1.",
               "Forms protective Al₂O₃ scale above 1100°C.",
               "Procedural placeholder — not yet ingested from MP."]),
    dict(name="Cubic Boron Nitride", formula="c-BN",
         system="Cubic F-43m (zinc-blende)",
         material_class="nitride", service_temp_c=1400, melting_point_c=2973,
         application_tags=["superhard","abrasive","cutting-tool","high-temperature-ceramic"],
         info=["Second-hardest material after diamond (H_v ≈45 GPa).",
               "Stable in steel-machining where diamond is not (no Fe-C reaction).",
               "Procedural placeholder — not yet ingested from MP."]),
    dict(name="Zirconium Nitride", formula="ZrN",
         system="Cubic Fm-3m (rock-salt)",
         material_class="nitride", service_temp_c=1100, melting_point_c=2980,
         application_tags=["tool-coating","conductive-ceramic","high-temperature-ceramic"],
         info=["Hard gold-coloured PVD coating, harder than TiN.",
               "Conductive (metallic resistivity).",
               "Procedural placeholder — not yet ingested from MP."]),
    dict(name="Lutetium Silicate", formula="Lu₂SiO₅",
         system="Monoclinic C2/c (X2-Lu₂SiO₅)",
         material_class="EBC", service_temp_c=1450, melting_point_c=2050,
         application_tags=["ebc","steam-resistant","high-temperature-ceramic"],
         info=["Monosilicate counterpart to Lu₂Si₂O₇.",
               "X2 polymorph isostructural with Yb₂SiO₅ (Felsche 1973).",
               "Procedural placeholder — not yet ingested from MP."]),
    dict(name="High-Entropy Carbide (Hf,Zr,Ti,Ta,Nb)C", formula="(HfZrTiTaNb)C",
         system="Cubic Fm-3m (random rock-salt solid solution)",
         material_class="high_entropy", service_temp_c=2000, melting_point_c=3800,
         application_tags=["uhtc","high-entropy-ceramic","next-gen-thermal-protection","high-temperature-ceramic"],
         info=["Equimolar 5-cation rock-salt solid solution; HEC archetype.",
               "Sluggish diffusion + lattice distortion → improved oxidation resistance vs single carbides.",
               "Procedural placeholder — single-cell random solid solution not represented atomistically."]),
]


def _build_real(spec):
    payload = _mp_fetch(spec["mp_id"], os.environ["MP_API_KEY"])
    structure = payload["structure"]
    atoms, M, sc = _build_supercell(structure, spec["supercell"])
    bonds, bondTypes, stats = _compute_bonds(atoms)
    cell_vectors = [[round(v, 4) for v in row] for row in M]
    return {
        "name": spec["name"],
        "formula": spec["formula"],
        "system": spec["system"],
        "info": list(spec["info"]) + [f"Source: Materials Project {spec['mp_id']}. {spec['note']}"],
        "supercell": sc,
        "cellVectors": cell_vectors,
        "atoms": atoms,
        "bonds": bonds,
        "bondTypes": bondTypes,
        "stats": stats,
        "isStub": False,
        "mp_id": spec["mp_id"],
        "uncertainty_notes": f"Atomic coordinates from Materials Project {spec['mp_id']} (DFT-relaxed). Phase 3.3 P2 ingest May 27 2026.",
        "material_class": spec["material_class"],
        "service_temp_c": spec["service_temp_c"],
        "melting_point_c": spec["melting_point_c"],
        "application_tags": list(spec["application_tags"]),
    }


def _build_stub(spec):
    return {
        "name": spec["name"],
        "formula": spec["formula"],
        "system": spec["system"],
        "info": list(spec["info"]),
        "isStub": True,
        "atoms": [],
        "bonds": [],
        "bondTypes": [],
        "cellVectors": [],
        "supercell": [],
        "stats": {"bondLengths": {}, "coordDist": {}},
        "material_class": spec["material_class"],
        "service_temp_c": spec["service_temp_c"],
        "melting_point_c": spec["melting_point_c"],
        "application_tags": list(spec["application_tags"]),
        "uncertainty_notes": "Procedural stub entry — viewer renders via FALLBACK_ELEMENT_META; atomic coordinates not baked. Phase 3.3 P2.",
    }


def main():
    if "MP_API_KEY" not in os.environ:
        print("ERROR: MP_API_KEY required", file=sys.stderr)
        return 2
    root = json.loads(DATA.read_text(encoding="utf-8"))
    existing = {s["name"] for s in root["structures"]}
    added = 0
    for spec in NEW_REAL:
        if spec["name"] in existing:
            print(f"SKIP existing: {spec['name']}")
            continue
        try:
            entry = _build_real(spec)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            print(f"ERROR {spec['mp_id']} ({spec['name']}): {e}", file=sys.stderr)
            continue
        root["structures"].append(entry)
        added += 1
        bl = entry["stats"]["bondLengths"]
        print(f"  + {spec['mp_id']:<10} {spec['name']:<35} atoms={len(entry['atoms']):>4} bonds={len(entry['bonds']):>4} bondL={bl}")
    for spec in NEW_STUBS:
        if spec["name"] in existing:
            print(f"SKIP existing stub: {spec['name']}")
            continue
        root["structures"].append(_build_stub(spec))
        added += 1
        print(f"  + STUB        {spec['name']}")
    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(root, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, DATA)
    print(f"OK: appended {added} new HT-ceramic entries. total={len(root['structures'])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
