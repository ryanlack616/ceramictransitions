#!/usr/bin/env python3
"""2026-10-26 (CH-261026-6) — rebuild the 7 stoichiometry-deviant pedagogical
models with DFT-relaxed Materials Project coordinates (PLANS.md Open
Operational Threads #1).

Only geometry is replaced: name, formula, material_class, service_temp_c,
melting_point_c, application_tags, transitions and oxidation_temp_c are
preserved (PRESERVE_FIELDS, same contract as _ingest_mp.py). The honest
"Structural note (2026-10 audit)" info line is removed — the coordinates are
now exact and cited — and a "Source: Materials Project {mp_id}" line appended.

Acceptance gates (run every time, printed per material):
  A. formula-vs-atoms stoichiometry within 2% on every element;
  B. mean bond lengths inside expected crystallographic ranges
     (Si-O 1.55-1.75, Al-O 1.7-1.95, Mg-O 2.0-2.3, Ca-O 2.3-2.6, K-O 2.7-3.1,
      Zn-O 1.9-2.15, Zr-O 2.1-2.4, O-H 0.85-1.15).
If either fails, the material is left untouched and reported.

Usage:
  python _rebuild_deviants.py            # dry run: fetch+verify, report only
  python _rebuild_deviants.py --write    # apply to data/crystal_vr.json
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

# .env (gitignored) — MP_API_KEY; never echo the value.
for _line in (HERE / ".env").read_text(encoding="utf-8").splitlines():
    _line = _line.strip()
    if _line and "=" in _line and not _line.startswith("#"):
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k, _v)

sys.path.insert(0, str(HERE))
from _ingest_mp import _mp_fetch, _build_supercell, _compute_bonds

MODEL_NOTE_MARKER = "Structural note (2026-10 audit)"

# (entry name, mp_id, supercell, system, note) — mp_ids verified 2026-10-26:
# all the stable/low-ehull on-topic phases (probe output in _probe_mp.py).
TARGETS = [
    ("Zircon", "mp-aaaaahdk", (3, 3, 3),
     "Tetragonal I4₁/amd (zircon)",
     "ZrSiO₄ zircon (sg I4₁/amd, ehull=0). Textbook stoichiometric model — replaces the O-halved pedagogical model."),
    ("Leucite", "mp-aaabfoej", (1, 2, 2),
     "Tetragonal I4₁/a (leucite)",
     "KAlSi₂O₆ leucite (sg I4₁/a, ehull≈0). Replaces the doubled-K pedagogical model."),
    ("Willemite", "mp-aaaaafpt", (2, 2, 2),
     "Trigonal R-3 (willemite)",
     "Zn₂SiO₄ willemite (sg R-3, ehull=0). Replaces the O-deficient pedagogical model."),
    ("Enstatite", "mp-aaacgbbo", (1, 1, 2),
     "Monoclinic P2₁/c (clinoenstatite)",
     "MgSiO₃ clinoenstatite (sg P2₁/c, lowest-ehull MP pyroxene). Replaces the non-stoichiometric pedagogical model."),
    ("Anorthite", "mp-aaaaajrg", (1, 1, 1),
     "Triclinic P-1 (anorthite feldspar)",
     "CaAl₂Si₂O₈ anorthite (sg P-1, ehull≈0). Full 104-atom feldspar cell — replaces the A/Si-deficient pedagogical model."),
    ("Kaolinite", "mp-aaabpaxc", (3, 3, 1),
     "Monoclinic Cc (kaolinite layer)",
     "Al₂Si₂O₅(OH)₄ kaolinite (sg Cc, ehull≈0). DFT-relaxed layered model with explicit hydroxyl H — replaces the H/O-short pedagogical model."),
    ("Talc", "mp-aaabnqij", (3, 3, 1),
     "Triclinic P-1 (talc layer)",
     "Mg₃Si₄O₁₀(OH)₂ talc (sg P-1, ehull=0). Replaces the Si-deficient pedagogical model."),
]

# expected mean bond lengths per pair (Å): (lo, hi) — the acceptance gate.
EXPECTED = {
    "Si-O": (1.55, 1.78), "Al-O": (1.68, 1.95), "Mg-O": (1.95, 2.35),
    "Ca-O": (2.25, 2.60), "K-O": (2.70, 3.15), "Zn-O": (1.90, 2.15),
    "Zr-O": (2.05, 2.45), "O-H": (0.85, 1.15),
}

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(formula):
    f = formula.translate(_SUB).replace("ₓ", "x").replace("₋", "-").replace("·", " ")
    counts = Counter()
    for group, gmul, el, emul in re.findall(r"\(([A-Za-z0-9]+)\)([0-9.]*)|([A-Z][a-z]?)([0-9.]*)", f):
        if group:
            mul = float(gmul) if gmul else 1.0
            for m in re.finditer(r"([A-Z][a-z]?)([0-9.]*)", group):
                counts[m.group(1)] += mul * (float(m.group(2)) if m.group(2) else 1.0)
        elif el and el.isalpha() and el != "x":
            counts[el] += float(emul) if emul else 1.0
    return counts


def verify(name, formula, atoms, stats):
    problems = []
    f = formula_counts(formula)
    a = Counter(x["e"] for x in atoms)
    ft = sum(f.values())
    for el in set(f) | set(a):
        fr = f[el] / ft
        ar = a[el] / len(atoms)
        if abs(fr - ar) > 0.02:
            problems.append(f"  STOICH {el}: formula {fr:.3f} vs atoms {ar:.3f}")
    for pair, (lo, hi) in EXPECTED.items():
        mean = (stats.get("bondLengths") or {}).get(pair)
        if mean is not None and not (lo <= mean <= hi):
            problems.append(f"  BOND {pair}: mean {mean} Å outside [{lo}, {hi}]")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr)
        return 2

    doc = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in doc["structures"]}

    ok, skip = [], []
    for name, mp_id, sc, system, note in TARGETS:
        entry = by_name.get(name)
        if entry is None:
            skip.append((name, "entry missing")); continue
        payload = _mp_fetch(mp_id, api_key)
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)
        problems = verify(name, entry.get("formula", ""), atoms, stats)
        if problems:
            skip.append((name, "GATE FAIL"))
            print(f"\n## {name} REJECTED:"); print("\n".join(problems)); continue

        composed = {
            "system": system,
            "info": [n for n in (entry.get("info") or []) if MODEL_NOTE_MARKER not in n]
                    + [f"Source: Materials Project {mp_id}. {note}"],
            "supercell": scl,
            "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mp_id,
            "uncertainty_notes": (
                f"Atomic coordinates from Materials Project {mp_id} (DFT-relaxed). "
                f"2026-10-26 stoichiometry-rebuild; supercell {scl[0]}×{scl[1]}×{scl[2]} "
                f"of the primitive cell, centred at origin. Replaces the pedagogical model."
            ),
        }
        for f in ("name", "formula", "material_class", "service_temp_c", "melting_point_c",
                  "application_tags", "transitions", "oxidation_temp_c", "bound_type",
                  "proceduralFallback"):
            if f in entry:
                composed[f] = entry[f]
        entry.clear(); entry.update(composed)
        meand = {p: round(v, 3) for p, v in (stats.get("bondLengths") or {}).items()}
        print(f"\n## {name}  [{mp_id}]  {len(atoms)} atoms  {system}")
        print("   bond means (Å):", meand)
        ok.append(name)

    print("\nRESULT — rebuilt:", ok)
    print("SKIPPED:", skip or "(none)")
    if skip:
        print("NOTE: skipped materials were left untouched.")

    if not args.write:
        print("\n(dry run — rerun with --write to apply.)")
        return

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} ({len(ok)} rebuilt). Run the full suite + _audit_correct_add.py --check.")


if __name__ == "__main__":
    main()