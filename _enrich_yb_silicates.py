"""Phase 3.1: enrich Yb2SiO5 and Yb2Si2O7 stubs with literature metadata.

These are X2-type Yb2SiO5 (monoclinic B2/b, ICSD 281135) and β-Yb2Si2O7
(monoclinic C2/m, ICSD 24430). Too complex for procedural prototyping but
we can ship the lattice parameters and structural notes in info[].
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data" / "crystal_vr.json"

ENRICH = {
    "Ytterbium Silicate": {
        "system": "Monoclinic B2/b (X2-Yb2SiO5)",
        "info": [
            "Environmental Barrier Coating (EBC) topcoat for SiC-based CMC",
            "Two distinct Yb sites (6-fold + 7-fold) with isolated [SiO4] tetrahedra",
            "Lattice: a=12.40 Å, b=6.71 Å, c=10.30 Å, β=102.4° (X2 polymorph)",
            "Stable to ~1700 °C; low CTE matches SiC (4.4 vs 4.5 ×10⁻⁶/K)",
            "Resists CMAS attack and steam-water corrosion above 1300 °C",
            "Atomic coordinates pending Phase 3.2 (Materials Project ingest)",
        ],
        "uncertainty_notes": "Lattice from literature (Felsche 1973); full atom coords deferred to Phase 3.2.",
    },
    "Ytterbium Disilicate": {
        "system": "Monoclinic C2/m (β-Yb2Si2O7)",
        "info": [
            "Primary EBC layer for SiC/SiC CMCs in next-gen turbines",
            "Pyrosilicate: corner-shared [Si2O7] dimers with Yb in 6-fold coordination",
            "Lattice (β): a=6.80 Å, b=8.88 Å, c=4.70 Å, β=102.1°",
            "CTE 3.6–4.0 ×10⁻⁶/K — best match to SiC of any rare-earth silicate",
            "α↔β transition near 1225 °C; β phase preferred for service",
            "Atomic coordinates pending Phase 3.2 (Materials Project ingest)",
        ],
        "uncertainty_notes": "Lattice from literature (Liddell & Thompson 1986); full atom coords deferred to Phase 3.2.",
    },
}

def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    for s in data["structures"]:
        patch = ENRICH.get(s.get("name"))
        if not patch:
            continue
        for k, v in patch.items():
            s[k] = v
        changed += 1
    if changed != len(ENRICH):
        print(f"WARN: enriched {changed} of {len(ENRICH)} expected stubs", file=sys.stderr)
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: enriched {changed} Yb-silicate stubs with crystallographic metadata")
    return 0

if __name__ == "__main__":
    sys.exit(main())
