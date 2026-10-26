#!/usr/bin/env python3
"""2026-10-26 deep-correctness: rebuild the remaining 27 native pedagogical
models from Materials Project (the last non-DFT tier).

Per-target gates before write:
  A. the chosen MP phase's space group matches the entry's known structure
     (SET of accepted settings per formula, so we can never silently swap a
     polymorph — e.g. coesite for alpha-quartz);
  B. exact formula stoichiometry (with a per-target override where the
     catalog formula carries stoichiometric coefficients, e.g. mullite);
  C. mean bond lengths inside expected crystallographic ranges for the pairs
     that arise (a range table for this chemistry set; unknown pairs WARN).

Entries that fail any gate are SKIPPED and listed — never forced.

Usage:
  python _rebuild_natives.py            # dry run
  python _rebuild_natives.py --write    # apply geometry in place
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
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

MP_BASE = "https://api.materialsproject.org/materials/summary/"
UA = "ceramictransitions-mp-ingest/0.2 (+https://ceramictransitions.com)"


def _mp_search(formula, api_key):
    params = {"formula": formula, "_limit": 100,
              "_fields": "material_id,formula_pretty,nsites,energy_above_hull,symmetry"}
    url = MP_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-API-KEY": api_key, "Accept": "application/json",
                                               "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = json.loads(r.read())
    rows = body.get("data") or []
    out = []
    for row in rows:
        sg = (row.get("symmetry") or {}).get("symbol", "?")
        out.append((row.get("energy_above_hull", 9e9), row.get("material_id"),
                    row.get("formula_pretty"), sg, row.get("nsites")))
    return sorted(out)


def _norm_sg(sg):
    return (sg or "").replace("_", "").replace("(", "").replace(")", "").replace(" ", "").upper()


# name, mp-search formula (elements only, e.g. 'Al2O3'), accepted space groups
# (normalized), optional stoichiometry override (gate uses entry formula unless set)
TARGETS = [
    ("Periclase", "MgO", ["FM-3M"]),
    ("Cuprite", "Cu2O", ["PN-3M"]),
    ("Rutile", "TiO2", ["P42/MNM"]),
    ("Corundum", "Al2O3", ["R-3C", "R3C"]),
    ("Hematite", "Fe2O3", ["R-3C", "R3C"]),
    ("Cassiterite", "SnO2", ["P42/MNM"]),
    ("Magnetite", "Fe3O4", ["FD-3M", "FDM"]),
    ("α-Quartz", "SiO2", ["P3121", "P3221"]),
    ("β-Cristobalite", "SiO2", ["FD-3M", "FDM", "PN-3M"]),
    ("Forsterite", "Mg2SiO4", ["PNMA", "PBNM"]),
    ("Diopside", "CaMgSi2O6", ["C2/C"]),
    ("Spodumene", "LiAlSi2O6", ["C2/C"]),
    ("Wollastonite", "CaSiO3", ["P-1"]),
    ("Albite", "NaAlSi3O8", ["C-1", "P-1"]),
    ("Orthoclase", "KAlSi3O8", ["C2/M", "C2/C", "P-1"]),
    ("Nepheline", "NaAlSiO4", ["P63", "P6.3"]),
    ("Akermanite", "Ca2MgSi2O7", ["P-421M", "P-42(1)M"]),
    ("Gehlenite", "Ca2Al2SiO7", ["P-421M", "P-42(1)M"]),
    ("Andalusite", "Al2SiO5", ["PNNM"]),
    ("Kyanite", "Al2SiO5", ["P-1"]),
    ("Sillimanite", "Al2SiO5", ["PNMA", "PBNM"]),
    ("Spinel", "MgAl2O4", ["FD-3M", "FDM"]),
    ("Mullite", "Al6Si2O13", ["PNMA", "PBNM", "PBAM"], "Al₆Si₂O₁₃"),
    ("Brucite", "MgH2O2", ["P-3M1", "P3M1"]),
    ("Calcite", "CaCO3", ["R-3C", "R3C"]),
    ("Dolomite", "CaMgC2O6", ["R-3"]),
    ("Cordierite", "Mg2Al4Si5O18", ["CCCM", "P6/MCC"]),
]

# mean bond-length ranges (Å) for this chemistry set — the acceptance table.
EXPECTED = {
    "Si-O": (1.52, 1.80), "Al-O": (1.68, 2.00), "Mg-O": (1.90, 2.30),
    "Ca-O": (2.25, 2.65), "Na-O": (2.25, 2.80), "K-O": (2.65, 3.15),
    "Li-O": (1.88, 2.35), "Fe-O": (1.85, 2.25), "Cu-O": (1.75, 2.05),
    "Sn-O": (1.95, 2.30), "Ti-O": (1.88, 2.25), "C-O": (1.18, 1.40),
    "O-H": (0.85, 1.20),
}

# Entries deliberately kept native (MP has no clean on-topic phase / the
# catalog's teaching model is the better representation). Reason shown in the
# skip list and recorded in PLANS.
KEEP_NATIVE = {
    "Mullite": "Mullite is intrinsically non-stoichiometric (3Al₂O₃·2SiO₂ ↔ 2Al₂O₃·SiO₂); MP has no ordered 3:2 phase — native teaching model retained.",
}

_SUB = str.maketrans({"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
                      "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"})


def formula_counts(formula):
    f = formula.translate(_SUB).replace("ₓ", "x").replace("₋", "-").replace("·", " ")
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


def counts_of(search_formula):
    c = Counter()
    for el, n in re.findall(r"([A-Z][a-z]?)([0-9.]*)", search_formula):
        c[el] += float(n) if n else 1.0
    return c


def auto_supercell(nsites, lo=140, hi=400):
    best = None
    for x in range(1, 5):
        for y in range(1, 7):
            for z in range(1, 5):
                t = nsites * x * y * z
                if lo <= t <= hi and (best is None or t > best[0]):
                    best = (t, (x, y, z))
    return best[1] if best else (2, 2, 2)


def bmean(means, pair):
    return means.get("-".join(sorted(pair.split("-"))))


EXTRA_NOTE = {
    "β-Cristobalite": "β-cristobalite is the high-T polymorph (no DFT ground state); MP's Pn-3m phase is its average aristotype structure.",
    "Orthoclase": "MP ground state of K-feldspar is the ordered triclinic P-1 (microcline-type); the monoclinic C2/m orthoclase is the Al/Si-disordered variant. This entry carries the DFT structure with that caveat.",
}


def main():
    write = "--write" in sys.argv[1:]
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: MP_API_KEY not in .env", file=sys.stderr); return 2
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in doc["structures"]}
    rebuilt, skipped = [], []

    for (name, search_f, sgs, *rest) in TARGETS:
        override = rest[0] if rest else None
        if name in KEEP_NATIVE:
            skipped.append((name, "KEEP_NATIVE: " + KEEP_NATIVE[name])); continue
        entry = by_name.get(name)
        if entry is None:
            skipped.append((name, "no entry")); continue
        if entry.get("mp_id"):
            print(f"SKIP {name}: already has mp_id"); continue
        want = counts_of(search_f)
        rows = _mp_search(search_f, api_key)
        cand = None
        for eh, mid, fp, sg, ns in rows:
            try:
                c2 = formula_counts(fp or "")
            except Exception:
                continue
            if dict(c2) != dict(want):
                continue
            if _norm_sg(sg) in {_norm_sg(s) for s in sgs}:
                cand = (mid, sg, ns)
                break
        if cand is None:
            skipped.append((name, f"no SG match for {sgs}")); continue
        mid, sg, ns = cand
        payload = _mp_fetch(mid, api_key)
        sc = auto_supercell(ns)
        atoms, M, scl = _build_supercell(payload["structure"], sc)
        bonds, bondTypes, stats = _compute_bonds(atoms)

        f = formula_counts(override or entry.get("formula", ""))
        a = Counter(x["e"] for x in atoms)
        stoich = all(abs(f[el] / sum(f.values()) - a[el] / len(atoms)) <= 0.02
                     for el in set(f) | set(a))
        means = stats.get("bondLengths") or {}
        problems = []
        for pair, (lo, hi) in EXPECTED.items():
            m = bmean(means, pair)
            if m is not None and not (lo <= m <= hi):
                problems.append(f"{pair}={m:.3f}")
        unknown = sorted(set(means) - set("-".join(sorted(p.split("-"))) for p in EXPECTED))
        if not (stoich and not problems):
            skipped.append((name, f"gate: stoich={stoich} bonds={problems}"))
            print(f"REJECT {name}: stoich={stoich} bonds={problems} unknown={unknown}")
            continue
        print(f"OK {name}: [{mid}] {sg} {len(atoms)} at  supercell={scl}  means={dict(means)}")
        new_system = f"{sg} (from Materials Project {mid}, DFT-relaxed)"
        info = [i for i in (entry.get("info") or [])
                if "approx" not in i and "model" not in i.lower() and "Source: Mater" not in i and "Structural note" not in i]
        if name in EXTRA_NOTE:
            info.append(EXTRA_NOTE[name])
        info.append(f"Source: Materials Project {mid}. DFT-relaxed {search_f}; replaces the pedagogical model.")
        composed = {
            "system": new_system, "info": info,
            "supercell": scl, "cellVectors": [[round(v, 4) for v in row] for row in M],
            "atoms": atoms, "bonds": bonds, "bondTypes": bondTypes, "stats": stats,
            "isStub": False, "mp_id": mid,
            "uncertainty_notes": f"Atomic coordinates from Materials Project {mid} (DFT-relaxed). 2026-10-26 native-tier rebuild; supercell {scl[0]}×{scl[1]}×{scl[2]}, centred at origin.",
        }
        for k in ("name", "formula", "material_class", "service_temp_c", "melting_point_c",
                  "application_tags", "transitions", "bound_type", "oxidation_temp_c"):
            if k in entry:
                composed[k] = entry[k]
        entry.clear(); entry.update(composed)
        rebuilt.append(name)

    print("\nREBUILT (%d):" % len(rebuilt), rebuilt)
    print("SKIPPED (%d):" % len(skipped))
    for n, why in skipped:
        print("   -", n, "::", why)
    if not write:
        print("\n(dry run — rerun with --write to apply.)"); return 0
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} ({len(rebuilt)} rebuilt).")


if __name__ == "__main__":
    main()