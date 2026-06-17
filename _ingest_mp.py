"""Phase 3.3 P1: generalized Materials Project ingest for HT-ceramic stubs.

Replaces stub entries in `data/crystal_vr.json` with DFT-relaxed atomic
coordinates pulled from the Materials Project REST API. Pure stdlib (urllib),
no pymatgen/mp_api dependency.

Targets (11 stubs):
  Silicon Carbide              (β-SiC, 3C, F-43m)            mp-8062
  Silicon Nitride              (β-Si₃N₄, P6₃/m)              mp-988
  Zirconium Diboride           (ZrB₂, P6/mmm, AlB₂-type)     mp-1788
  Hafnium Diboride             (HfB₂, P6/mmm, AlB₂-type)     mp-2311
  Zirconium Carbide            (ZrC, Fm-3m, rock-salt)       mp-2795
  Hafnium Carbide              (HfC, Fm-3m, rock-salt)       mp-2496
  Tantalum Carbide             (TaC, Fm-3m, rock-salt)       mp-7088
  Aluminum Nitride             (AlN, P6₃mc, wurtzite)        mp-661
  Boron Nitride (Hexagonal)    (h-BN, P6₃/mmc)               mp-984
  Hafnium Oxide                (m-HfO₂, P2₁/c, baddeleyite)  mp-352
  Lanthanum Zirconate          (La₂Zr₂O₇, Fd-3m, pyrochlore) mp-8821

Existing classification fields (material_class, service_temp_c,
melting_point_c, application_tags, transitions) are preserved verbatim.

Usage:
  MP_API_KEY=xxx python _ingest_mp.py [--dry-run] [--only mp-661,mp-984]
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
USER_AGENT = "ceramictransitions-mp-ingest/0.2 (+https://ceramictransitions.com)"

# Visible-radius (Å) used by viewer's FALLBACK_ELEMENT_META — kept consistent
# so baked-in `r` matches renderer.
RADIUS = {
    "O": 0.60, "N": 0.65, "C": 0.70, "B": 0.85, "Si": 1.10, "Al": 1.25,
    "Mg": 1.50, "Ca": 1.80, "Ti": 1.40, "Zr": 1.55, "Hf": 1.55, "Ta": 1.45,
    "Yb": 1.75, "Lu": 1.75, "Y": 1.80, "La": 1.95, "Ce": 1.85, "Gd": 1.80,
    "Cr": 1.40, "Fe": 1.40, "Ni": 1.35, "Mo": 1.45, "W": 1.50, "Nb": 1.45,
}

# Bond cutoffs (Å) — covalent/ionic upper bounds for renderable bonds.
# Tuned from Pauling/Shannon radii + 0.25-0.4 Å buffer to capture full
# coordination shell. Frozenset key is symmetric.
BOND_CUTOFFS = {
    # silicate chemistry (kept from Phase 3.2 ingest)
    frozenset(("Si", "O")): 2.00,
    frozenset(("Yb", "O")): 3.10,
    frozenset(("Lu", "O")): 3.10,
    # carbides
    frozenset(("Si", "C")): 2.10,
    frozenset(("Zr", "C")): 2.65,
    frozenset(("Hf", "C")): 2.60,
    frozenset(("Ta", "C")): 2.60,
    frozenset(("Ti", "C")): 2.40,
    frozenset(("Nb", "C")): 2.55,
    frozenset(("Cr", "C")): 2.25,
    frozenset(("W",  "C")): 2.40,
    frozenset(("C",  "C")): 1.75,
    # nitrides
    frozenset(("Si", "N")): 2.05,
    frozenset(("Al", "N")): 2.30,
    frozenset(("B", "N")):  1.90,
    frozenset(("Ti", "N")): 2.40,
    frozenset(("Zr", "N")): 2.50,
    # borides
    frozenset(("Zr", "B")): 2.80,
    frozenset(("Hf", "B")): 2.75,
    frozenset(("Ta", "B")): 2.75,
    frozenset(("Ti", "B")): 2.65,
    frozenset(("B",  "B")): 1.95,
    # oxides for HfO₂, La₂Zr₂O₇
    frozenset(("Hf", "O")): 2.60,
    frozenset(("Zr", "O")): 2.65,
    frozenset(("La", "O")): 2.95,
    frozenset(("Gd", "O")): 2.80,
    frozenset(("Y",  "O")): 2.75,
    frozenset(("Ce", "O")): 2.80,
    frozenset(("Ti", "O")): 2.40,
    frozenset(("Al", "O")): 2.20,
    frozenset(("Mg", "O")): 2.45,
    # disilicide / MAX-phase fragments (future use)
    frozenset(("Mo", "Si")): 2.80,
    frozenset(("Ti", "Si")): 2.80,
}

# Match stub `name` in crystal_vr.json → MP ingest config.
TARGETS = [
    {
        "stub_name": "Silicon Carbide",
        "mp_id": "mp-8062",
        "supercell": (2, 2, 2),
        "system": "Cubic F-43m (3C / β-SiC, zinc-blende)",
        "note": "β-SiC (3C polytype, sg F-43m, ehull=0).",
    },
    {
        "stub_name": "Silicon Nitride",
        "mp_id": "mp-988",
        "supercell": (1, 1, 2),
        "system": "Hexagonal P6₃/m (β-Si₃N₄)",
        "note": "β-Si₃N₄ (sg P6₃, ehull≈0). Dominant HT polymorph.",
    },
    {
        "stub_name": "Zirconium Diboride",
        "mp_id": "mp-1472",
        "supercell": (2, 2, 2),
        "system": "Hexagonal P6/mmm (AlB₂-type)",
        "note": "ZrB₂ AlB₂-prototype (sg P6/mmm, ehull=0).",
    },
    {
        "stub_name": "Hafnium Diboride",
        "mp_id": "mp-1994",
        "supercell": (2, 2, 2),
        "system": "Hexagonal P6/mmm (AlB₂-type)",
        "note": "HfB₂ AlB₂-prototype (sg P6/mmm, ehull=0).",
    },
    {
        "stub_name": "Zirconium Carbide",
        "mp_id": "mp-2795",
        "supercell": (2, 2, 2),
        "system": "Cubic Fm-3m (rock-salt)",
        "note": "ZrC rock-salt (sg Fm-3m, ehull=0).",
    },
    {
        "stub_name": "Hafnium Carbide",
        "mp_id": "mp-21075",
        "supercell": (2, 2, 2),
        "system": "Cubic Fm-3m (rock-salt)",
        "note": "HfC rock-salt (sg Fm-3m, ehull=0). Highest melting binary known (~3950°C).",
    },
    {
        "stub_name": "Tantalum Carbide",
        "mp_id": "mp-1086",
        "supercell": (2, 2, 2),
        "system": "Cubic Fm-3m (rock-salt)",
        "note": "TaC rock-salt (sg Fm-3m, ehull=0).",
    },
    {
        "stub_name": "Aluminum Nitride",
        "mp_id": "mp-661",
        "supercell": (2, 2, 2),
        "system": "Hexagonal P6₃mc (wurtzite)",
        "note": "AlN wurtzite (sg P6₃mc, ehull=0). High thermal conductivity electronic ceramic.",
    },
    {
        "stub_name": "Boron Nitride (Hexagonal)",
        "mp_id": "mp-984",
        "supercell": (2, 2, 1),
        "system": "Hexagonal P6₃/mmc (graphitic h-BN)",
        "note": "h-BN graphitic layered (sg P6₃/mmc, ehull=0).",
    },
    {
        "stub_name": "Hafnium Oxide",
        "mp_id": "mp-352",
        "supercell": (1, 1, 2),
        "system": "Monoclinic P2₁/c (baddeleyite-type m-HfO₂)",
        "note": "m-HfO₂ baddeleyite (sg P2₁/c, ehull=0). Tetragonal transition ~1700°C.",
    },
    {
        "stub_name": "Lanthanum Zirconate",
        "mp_id": "mp-4974",
        "supercell": (1, 1, 1),
        "system": "Cubic Fd-3m (pyrochlore A₂B₂O₇)",
        "note": "La₂Zr₂O₇ pyrochlore (sg Fd-3m). Next-gen TBC candidate (lower k, higher T cap than YSZ).",
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

def _mat_vec(M, v):
    out = [0.0, 0.0, 0.0]
    for i in range(3):
        for j in range(3):
            out[j] += v[i] * M[i][j]
    return out


def _build_supercell(structure, supercell, subs=None):
    M = structure["lattice"]["matrix"]
    sites = structure["sites"]
    Nx, Ny, Nz = supercell
    centre = [
        0.5 * Nx * M[0][0] + 0.5 * Ny * M[1][0] + 0.5 * Nz * M[2][0],
        0.5 * Nx * M[0][1] + 0.5 * Ny * M[1][1] + 0.5 * Nz * M[2][1],
        0.5 * Nx * M[0][2] + 0.5 * Ny * M[1][2] + 0.5 * Nz * M[2][2],
    ]
    atoms = []
    for ix in range(Nx):
        for iy in range(Ny):
            for iz in range(Nz):
                shift_cart = _mat_vec(M, [float(ix), float(iy), float(iz)])
                for s in sites:
                    sp = s["species"][0]["element"]
                    el = (subs or {}).get(sp, sp)
                    frac = s["abc"]
                    xyz = _mat_vec(M, list(frac))
                    atoms.append({
                        "e": el,
                        "x": round(xyz[0] + shift_cart[0] - centre[0], 4),
                        "y": round(xyz[1] + shift_cart[1] - centre[1], 4),
                        "z": round(xyz[2] + shift_cart[2] - centre[2], 4),
                    })
    return atoms, M, [Nx, Ny, Nz]


def _pair_key(a, b):
    return "-".join(sorted((a, b)))


def _compute_bonds(atoms):
    bonds, bondTypes = [], []
    length_sums = {}
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
                continue
            bonds.append([i, j])
            ptype = _pair_key(ai["e"], aj["e"])
            bondTypes.append(ptype)
            length_sums.setdefault(ptype, []).append(d)

    cn = [0] * n
    for i, j in bonds:
        cn[i] += 1
        cn[j] += 1
    bond_lengths = {p: round(sum(v) / len(v), 3) for p, v in length_sums.items()}
    cn_hist = {}
    for c in cn:
        key = str(c)
        cn_hist[key] = cn_hist.get(key, 0) + 1
    for idx, a in enumerate(atoms):
        a["r"] = RADIUS.get(a["e"], 0.8)
        a["cn"] = cn[idx]
    return bonds, bondTypes, {"bondLengths": bond_lengths, "coordDist": cn_hist}


# ─────────────────────────── entry builder ───────────────────────────

# Fields that must survive the stub→real rewrite (set by _classify_ht.py).
PRESERVE_FIELDS = (
    "name", "formula", "material_class", "service_temp_c", "melting_point_c",
    "application_tags", "transitions", "oxidation_temp_c",
)


def _build_entry(target, mp_payload, existing):
    structure = mp_payload["structure"]
    atoms, M, sc = _build_supercell(structure, target["supercell"])
    bonds, bondTypes, stats = _compute_bonds(atoms)
    cell_vectors = [[round(v, 4) for v in row] for row in M]

    info = [line for line in (existing.get("info") or []) if "Phase 3.3" not in line]
    info.append(f"Source: Materials Project {target['mp_id']}. {target['note']}")

    entry = {
        "system": target["system"],
        "info": info,
        "supercell": sc,
        "cellVectors": cell_vectors,
        "atoms": atoms,
        "bonds": bonds,
        "bondTypes": bondTypes,
        "stats": stats,
        "isStub": False,
        "mp_id": target["mp_id"],
        "uncertainty_notes": (
            f"Atomic coordinates from Materials Project {target['mp_id']} "
            f"(DFT-relaxed). Phase 3.3 P1 ingest May 27 2026. "
            f"Supercell {sc[0]}×{sc[1]}×{sc[2]} of primitive cell; centred at origin."
        ),
    }
    for f in PRESERVE_FIELDS:
        if f in existing:
            entry[f] = existing[f]
    # ensure name+formula retained
    entry.setdefault("name", existing.get("name"))
    entry.setdefault("formula", existing.get("formula"))
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated mp_ids to ingest")
    args = ap.parse_args()

    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        print("ERROR: set MP_API_KEY env var.", file=sys.stderr)
        return 2

    only = set(x.strip() for x in args.only.split(",") if x.strip())
    root = json.loads(DATA.read_text(encoding="utf-8"))
    by_name = {s["name"]: idx for idx, s in enumerate(root["structures"])}

    changed = 0
    failed = []
    for target in TARGETS:
        if only and target["mp_id"] not in only:
            continue
        name = target["stub_name"]
        if name not in by_name:
            print(f"WARN: stub {name!r} not found in crystal_vr.json", file=sys.stderr)
            continue
        try:
            payload = _mp_fetch(target["mp_id"], api_key)
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            print(f"ERROR {target['mp_id']} ({name}): {e}", file=sys.stderr)
            failed.append(target["mp_id"])
            continue

        idx = by_name[name]
        existing = root["structures"][idx]
        new_entry = _build_entry(target, payload, existing)
        sym = payload.get("symmetry") or {}
        print(
            f"  {target['mp_id']:<8} → {name:<32} sg={sym.get('number'):<4} "
            f"{(sym.get('symbol') or ''):<10} atoms={len(new_entry['atoms']):>4} "
            f"bonds={len(new_entry['bonds']):>4} "
            f"bondL={new_entry['stats']['bondLengths']}"
        )
        root["structures"][idx] = new_entry
        changed += 1

    if args.dry_run:
        print(f"DRY-RUN: would update {changed} entries; failed={failed}")
        return 0

    tmp = DATA.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(root, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    os.replace(tmp, DATA)
    print(f"OK: ingested {changed} HT-ceramic structures from Materials Project.")
    if failed:
        print(f"FAILED ({len(failed)}): {failed}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
