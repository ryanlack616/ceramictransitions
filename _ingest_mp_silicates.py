"""Phase 3.2: ingest Yb-silicate atomic coordinates from Materials Project.

Bakes atom coordinates + bonds directly into `data/crystal_vr.json` for:
  - Ytterbium Disilicate (Yb2Si2O7, β polymorph, monoclinic C2/m)
        source = MP `mp-4300` (real Yb2Si2O7 entry, stable, ehull=0)
  - Ytterbium Silicate (Yb2SiO5, X2 polymorph, monoclinic C2/c ≡ B2/b setting)
        source = MP `mp-16969` (Lu2SiO5, X2 polymorph, stable, ehull=0)
                 then Lu → Yb element substitution. Lu³⁺ (0.861 Å, 6-coord) and
                 Yb³⁺ (0.868 Å, 6-coord) differ by <1% in ionic radius and X2
                 RE-monosilicates are isostructural across the late lanthanides,
                 so the Lu primitive cell is the correct topology for visualisation.

Strategy:
  1. Pull MP `materials/summary/` JSON (cached to `data/.mp_cache/`).
  2. Build a small supercell (Cartesian, centred at origin) from the primitive cell.
  3. Compute Yb-O and Si-O bonds via element-pair cutoffs.
  4. Replace the stub entry in `data/crystal_vr.json` while preserving `info[]`
     and the literature `uncertainty_notes` (rewritten to credit MP).

Usage:
  MP_API_KEY=xxx python _ingest_mp_silicates.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "crystal_vr.json"
CACHE = HERE / "data" / ".mp_cache"

MP_BASE = "https://api.materialsproject.org/materials/summary/"
USER_AGENT = "ceramictransitions-mp-ingest/0.1 (+https://ceramictransitions.com)"

# --- bond cutoffs (Å) for the silicate chemistry we care about ---
BOND_CUTOFFS = {
    frozenset(("Si", "O")): 2.00,   # Si-O ~1.55-1.70
    frozenset(("Yb", "O")): 3.10,   # Yb-O 2.20-2.85 across 6- and 7-fold sites
}

# --- ingest targets ---
TARGETS = [
    {
        "name": "Ytterbium Disilicate",
        "mp_id": "mp-4300",
        "element_subs": None,                              # real Yb compound
        "supercell": (2, 2, 2),
        "system": "Monoclinic C2/m (β-Yb₂Si₂O₇)",
        "source_note": (
            "Atomic coordinates from Materials Project mp-4300 "
            "(β-Yb₂Si₂O₇, sg C2/m, ehull=0). Phase 3.2 ingest May 27 2026."
        ),
    },
    {
        "name": "Ytterbium Silicate",
        "mp_id": "mp-16969",
        "element_subs": {"Lu": "Yb"},
        "supercell": (1, 1, 1),
        "system": "Monoclinic C2/c (X2-Yb₂SiO₅, isostructural with X2-Lu₂SiO₅)",
        "source_note": (
            "Atomic coordinates from Materials Project mp-16969 (X2-Lu₂SiO₅, "
            "sg C2/c, ehull=0) with Lu→Yb element substitution. Lu³⁺ and Yb³⁺ "
            "differ <1% in ionic radius and X2 RE-monosilicates are isostructural "
            "across the late lanthanides (Felsche 1973). Phase 3.2 ingest May 27 2026."
        ),
    },
]


# ─────────────────────────── MP fetch (cached) ───────────────────────────

def _mp_fetch(mp_id: str, api_key: str) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE / f"{mp_id}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    params = {
        "material_ids": mp_id,
        "_fields": "material_id,formula_pretty,symmetry,nsites,structure,energy_above_hull",
    }
    url = MP_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "X-API-KEY": api_key,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.loads(r.read())
    rows = body.get("data") or []
    if not rows:
        raise RuntimeError(f"MP returned no data for {mp_id}")
    payload = rows[0]
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


# ─────────────────────────── geometry helpers ───────────────────────────

def _mat_vec(M: list[list[float]], v: list[float]) -> list[float]:
    # Pymatgen lattice matrix is row-major: lattice_row_i = a_i vector.
    # Cartesian = sum_i frac_i * a_i   (so x = frac @ M, NOT M @ frac).
    out = [0.0, 0.0, 0.0]
    for i in range(3):
        for j in range(3):
            out[j] += v[i] * M[i][j]
    return out


def _build_supercell(structure: dict, supercell: tuple[int, int, int],
                     subs: dict | None) -> tuple[list[dict], list[list[float]], list[int]]:
    """Return (atoms_cartesian_centred, primitive_cell_vectors, [Nx,Ny,Nz])."""
    M = structure["lattice"]["matrix"]
    sites = structure["sites"]
    Nx, Ny, Nz = supercell

    # Origin offset so centre of supercell lands at origin (matches Periclase style).
    centre = [
        0.5 * Nx * M[0][0] + 0.5 * Ny * M[1][0] + 0.5 * Nz * M[2][0],
        0.5 * Nx * M[0][1] + 0.5 * Ny * M[1][1] + 0.5 * Nz * M[2][1],
        0.5 * Nx * M[0][2] + 0.5 * Ny * M[1][2] + 0.5 * Nz * M[2][2],
    ]

    atoms: list[dict] = []
    for ix in range(Nx):
        for iy in range(Ny):
            for iz in range(Nz):
                shift_frac = [ix, iy, iz]
                shift_cart = _mat_vec(M, [float(s) for s in shift_frac])
                for s in sites:
                    sp = s["species"][0]["element"]
                    el = subs.get(sp, sp) if subs else sp
                    frac = s["abc"]
                    xyz = _mat_vec(M, list(frac))
                    atoms.append({
                        "e": el,
                        "x": round(xyz[0] + shift_cart[0] - centre[0], 4),
                        "y": round(xyz[1] + shift_cart[1] - centre[1], 4),
                        "z": round(xyz[2] + shift_cart[2] - centre[2], 4),
                    })
    return atoms, M, [Nx, Ny, Nz]


# ─────────────────────────── bond computation ───────────────────────────

# Default radii used when the JSON viewer's FALLBACK_ELEMENT_META kicks in
# (kept here so the baked-in `r` field matches what the renderer would assign).
RADIUS = {"Yb": 1.75, "Si": 1.10, "O": 0.60, "Lu": 1.75}


def _pair_key(a: str, b: str) -> str:
    return "-".join(sorted((a, b)))


def _compute_bonds(atoms: list[dict]) -> tuple[list[list[int]], list[str], dict]:
    bonds: list[list[int]] = []
    bondTypes: list[str] = []
    length_sums: dict[str, list[float]] = {}

    n = len(atoms)
    for i in range(n):
        ai = atoms[i]
        for j in range(i + 1, n):
            aj = atoms[j]
            pair = frozenset((ai["e"], aj["e"]))
            cutoff = BOND_CUTOFFS.get(pair)
            if cutoff is None:
                continue
            dx = ai["x"] - aj["x"]
            dy = ai["y"] - aj["y"]
            dz = ai["z"] - aj["z"]
            d2 = dx * dx + dy * dy + dz * dz
            if d2 > cutoff * cutoff:
                continue
            d = math.sqrt(d2)
            if d < 0.5:
                continue  # numerical/self pathological
            bonds.append([i, j])
            ptype = _pair_key(ai["e"], aj["e"])
            bondTypes.append(ptype)
            length_sums.setdefault(ptype, []).append(d)

    # CN per atom + per-pair mean length
    cn = [0] * n
    for i, j in bonds:
        cn[i] += 1
        cn[j] += 1

    bond_lengths = {p: round(sum(v) / len(v), 3) for p, v in length_sums.items()}
    cn_hist: dict[str, int] = {}
    for c in cn:
        key = str(c)
        cn_hist[key] = cn_hist.get(key, 0) + 1

    # Attach r + cn to atoms
    for idx, a in enumerate(atoms):
        a["r"] = RADIUS.get(a["e"], 0.8)
        a["cn"] = cn[idx]

    return bonds, bondTypes, {"bondLengths": bond_lengths, "coordDist": cn_hist}


# ─────────────────────────── crystal_vr.json patcher ───────────────────────────

def _build_entry(target: dict, mp_payload: dict, existing: dict) -> dict:
    structure = mp_payload["structure"]
    atoms, M, sc = _build_supercell(structure, target["supercell"], target["element_subs"])
    bonds, bondTypes, stats = _compute_bonds(atoms)

    # Round cellVectors to 4 dp for readability.
    cell_vectors = [[round(v, 4) for v in row] for row in M]

    # Preserve original info[] but rewrite the stale "pending Phase 3.2" line.
    info = [
        line for line in (existing.get("info") or [])
        if "Phase 3.2" not in line
    ]
    info.append(target["source_note"])

    return {
        "name": existing["name"],
        "formula": existing["formula"],
        "system": target["system"],
        "info": info,
        "supercell": sc,
        "cellVectors": cell_vectors,
        "atoms": atoms,
        "bonds": bonds,
        "bondTypes": bondTypes,
        "stats": stats,
        "isStub": False,
        "uncertainty_notes": (
            target["source_note"] +
            " Lattice + atom positions are DFT-relaxed; literature comparison "
            "for Yb₂Si₂O₇: a=6.80 Å, b=8.88 Å, c=4.70 Å, β=102.1° "
            "(Liddell & Thompson 1986). For Yb₂SiO₅ X2: a=12.40 Å, b=6.71 Å, "
            "c=10.30 Å, β=102.4° (Felsche 1973). MP primitive cells differ from "
            "the conventional setting; cellVectors above is the primitive lattice."
        ),
        "mp_id": target["mp_id"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Fetch + build but do not write data/crystal_vr.json")
    args = ap.parse_args()

    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: set MP_API_KEY env var with your Materials Project API key.",
              file=sys.stderr)
        return 2

    root = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: idx for idx, s in enumerate(root["structures"])}

    changed = 0
    for target in TARGETS:
        if target["name"] not in by_name:
            print(f"WARN: stub for {target['name']!r} not found in crystal_vr.json",
                  file=sys.stderr)
            continue
        try:
            payload = _mp_fetch(target["mp_id"], api_key)
        except urllib.error.HTTPError as e:
            print(f"ERROR fetching {target['mp_id']}: HTTP {e.code} {e.reason}",
                  file=sys.stderr)
            return 3

        idx = by_name[target["name"]]
        existing = root["structures"][idx]
        new_entry = _build_entry(target, payload, existing)

        nb = len(new_entry["bonds"])
        na = len(new_entry["atoms"])
        sym = payload.get("symmetry") or {}
        print(
            f"  {target['mp_id']} → {target['name']:<22}  "
            f"sg={sym.get('number')} {sym.get('symbol'):<8}  "
            f"atoms={na:>4}  bonds={nb:>4}  "
            f"bondLengths={new_entry['stats']['bondLengths']}"
        )
        root["structures"][idx] = new_entry
        changed += 1

    if args.dry_run:
        print(f"DRY-RUN: would update {changed} entries (no write)")
        return 0

    DATA.write_text(json.dumps(root, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"OK: ingested {changed} Yb-silicate structures from Materials Project")
    return 0


if __name__ == "__main__":
    sys.exit(main())
