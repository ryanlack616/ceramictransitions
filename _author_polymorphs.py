#!/usr/bin/env python3
"""Tier D.3 — author the cited polymorph transition set (report-only by default).

Builds on the D.2 harvest (which mined `application_tags` into the locked
`transitions[]` shape with source="tag:...").  D.3 is DOMAIN AUTHORING:
per the 2026-06-17 think-deep checkpoint, authored claims are paired with a
literature citation and are REPORT-ONLY (--dry-run) until a human reviews them.

Two passes:
  PASS A - RECONCILE the 6 deferred hand-authored window rows (alpha-Quartz x3,
           Baddeleyite x3) into the locked shape: add `to`, `reversible`,
           `volume_change_pct` (where solid), `note`, and `source` without
           overwriting existing values.
  PASS B - AUTHOR new event + window rows for the key high-temp polymorphs:
           beta-SiC -> alpha-SiC, alpha->beta Si3N4, m->t->c HfO2 (with the
           ZrO2 t<->m volume change that makes PSZ work), beta'-sialon
           formation, cristobalite inversion, ZrO2 martensitic events.

Usage:
  python _author_polymorphs.py             # dry run: print the proposal
  python _author_polymorphs.py --write     # apply (idempotent; skips existing)
  python _author_polymorphs.py --check     # after --write: audit the file
"""
import argparse, json, sys

DATA = "data/crystal_vr.json"

# exact string used for all SiO2 polymorph data (alpha-quartz / tridymite / cristobalite)
SIO2_SRC = "SiO2 polymorph data - Deer, Howie & Zussman, Rock-Forming Minerals v4 (1963); R.B. Sosman, The Phases of Silica (1965)"
ZRO2_SRC = "R.H.J. Hannink, P.M. Kelly & B.C. Muddle, Transformation Toughening in Zirconia-Containing Ceramics, J. Am. Ceram. Soc. 83 (2000) 461"

# PASS A: patch legacy window rows (matched by entry + structure + row kind;
# fields merged in, never overwrite an existing value). "row" selects the
# legacy window bucket ("window") vs the harvested point event ("event").
RECONCILE = [
    {
        "entry": "α-Quartz", "structure": "α-Quartz", "row": "window",
        "patch": {
            "to": "β-Quartz", "reversible": True, "volume_change_pct": 0.86,
            "note": "The classic quartz inversion: ~0.86 vol% sudden expansion on heating (α→β).",
            "source": SIO2_SRC,
        },
    },
    {
        "entry": "α-Quartz", "structure": "Tridymite", "row": "window",
        "patch": {
            "to": "β-Cristobalite", "reversible": False,
            "note": "Reconstructive rearrangement of the SiO2 framework at 1470°C; sluggish and hysteretic.",
            "source": SIO2_SRC,
        },
    },
    {
        "entry": "α-Quartz", "structure": "β-Cristobalite", "row": "window",
        "patch": {
            "to": "SiO2 liquid", "reversible": False,
            "note": "β-cristobalite melts incongruently ~1713°C (the silica melting corner).",
            "source": SIO2_SRC,
        },
    },
    {
        "entry": "α-Quartz", "structure": "α-Quartz", "row": "event",
        "patch": {
            "volume_change_pct": 0.86,
            "note": "~0.86 vol% expansion on heating at the α→β inversion (573°C).",
            "source": SIO2_SRC,
        },
    },
    {
        "entry": "Baddeleyite", "structure": "Baddeleyite", "row": "window",
        "patch": {
            "to": "Tetragonal Zirconia", "reversible": True, "volume_change_pct": -4.5,
            "note": "m→t contracts ≈4.5 vol% on heating; the reverse t→m EXPANSION on cooling is what transformation-toughened zirconia (PSZ/TZP) exploits to arrest cracks.",
            "source": ZRO2_SRC,
        },
    },
    {
        "entry": "Baddeleyite", "structure": "Tetragonal Zirconia", "row": "window",
        "patch": {
            "to": "Cubic Zirconia", "reversible": True,
            "note": "t→c displacive step near 2370°C; small volume change (not cited to 1 decimal).",
            "source": ZRO2_SRC,
        },
    },
    {
        "entry": "Baddeleyite", "structure": "Cubic Zirconia", "row": "window",
        "patch": {
            "to": "ZrO2 liquid", "reversible": False,
            "note": "Cubic (fluorite) ZrO2 is the stable form up to the 2715°C melting point.",
            "source": ZRO2_SRC,
        },
    },
]

# PASS B: author new rows. (entry, row). merge key = (structure, to, temp_c).
AUTHOR = [
    # ── Silicon Carbide (β-SiC 3C entry, mp-8062) ────────────────────────
    ("Silicon Carbide", {
        "structure": "Silicon Carbide", "phaseName": "β-SiC (3C, cubic zincblende)",
        "tempRange": [20, 2000], "transformType": "polymorphic", "source":
        "N.W. Jepps & T.F. Page, Polytypic transformations in silicon carbide, Prog. Cryst. Growth Charact. 7 (1983) 259",
    }),
    ("Silicon Carbide", {
        "structure": "Silicon Carbide", "to": "α-SiC (6H)", "temp_c": 2000,
        "temp_qualifier": "above", "transformType": "reconstructive", "reversible": False,
        "volume_change_pct": 0.1,
        "note": "β-SiC (3C) is the low-temperature polytype (the entry's DFT ground state). Slow reconstructive 3C→6H recrystallization only proceeds on extended heating above ~2000°C; effectively irreversible in service.",
        "source": "N.W. Jepps & T.F. Page (1983); Snead et al., Handbook of SiC properties for fuel performance modeling, J. Nucl. Mater. 371 (2007) 329",
    }),
    ("Silicon Carbide", {
        "structure": "α-SiC (6H)", "phaseName": "α-SiC (6H, hexagonal)",
        "tempRange": [2000, 2730], "transformType": "reconstructive", "source":
        "N.W. Jepps & T.F. Page (1983)",
    }),
    # ── Silicon Nitride (β-Si3N4 entry, mp-988) ───────────────────────────
    ("Silicon Nitride", {
        "structure": "α-Si₃N₄", "phaseName": "α-Si₃N₄ (trigonal)",
        "tempRange": [20, 1500], "transformType": "polymorphic", "source":
        "F.L. Riley, Silicon Nitride and Related Materials, J. Am. Ceram. Soc. 83 (2000) 245",
    }),
    ("Silicon Nitride", {
        "structure": "α-Si₃N₄", "to": "β-Si₃N₄", "temp_c": 1500,
        "temp_qualifier": "above", "transformType": "reconstructive", "reversible": False,
        "volume_change_pct": -0.5,
        "note": "α→β proceeds by solution-reprecipitation through the liquid phase during sintering (~1400–1800°C); β is the thermodynamically stable high-temperature form (this entry). Not reversible on cooling under service conditions.",
        "source": "F.L. Riley (2000); Ziegler, Heinrich & Wötting, J. Mater. Sci. 22 (1987) 3041",
    }),
    ("Silicon Nitride", {
        "structure": "β-Si₃N₄", "phaseName": "β-Si₃N₄ (hexagonal, P6₃)",
        "tempRange": [1500, 1900], "transformType": "reconstructive",
        "note": "β-Si₃N₄ decomposes before melting (~1900°C at 1 atm N₂).",
        "source": "F.L. Riley (2000)",
    }),
    # ── Hafnium Oxide (m→t→c; entry info cites m→t near 1770°C) ──────────
    ("Hafnium Oxide", {
        "structure": "Hafnium Oxide", "phaseName": "monoclinic (m)",
        "tempRange": [20, 1700], "transformType": "polymorphic", "source":
        "J. Wang, H.P. Li & R. Stevens, Hafnia and hafnia-based materials, J. Mater. Sci. 27 (1992) 5397",
    }),
    ("Hafnium Oxide", {
        "structure": "Hafnium Oxide", "to": "HfO₂ (t)", "temp_c": 1700,
        "temp_qualifier": "at", "transformType": "martensitic", "reversible": True,
        "volume_change_pct": -3.4,
        "note": "m→t contracts ≈3.4 vol% on heating (slightly less than ZrO₂'s) — among the largest framework inversions in ceramics; hafnia's m↔t history is why HfO₂ is both a TBC candidate and a ferroelectric/memory material.",
        "source": "J. Wang, H.P. Li & R. Stevens (1992)",
    }),
    ("Hafnium Oxide", {
        "structure": "HfO₂ (t)", "phaseName": "tetragonal (t)",
        "tempRange": [1700, 2600], "transformType": "displacive", "source":
        "J. Wang, H.P. Li & R. Stevens (1992)",
    }),
    ("Hafnium Oxide", {
        "structure": "HfO₂ (t)", "to": "HfO₂ (c)", "temp_c": 2600,
        "temp_qualifier": "at", "transformType": "displacive", "reversible": True,
        "note": "t→c near 2600°C completes the m→t→c sequence before melting at 2758°C.",
        "source": "J. Wang, H.P. Li & R. Stevens (1992)",
    }),
    ("Hafnium Oxide", {
        "structure": "HfO₂ (c)", "phaseName": "cubic (c, fluorite)",
        "tempRange": [2600, 2758], "transformType": "displacive", "source":
        "J. Wang, H.P. Li & R. Stevens (1992)",
    }),
    # ── β-Cristobalite: the ~230°C inversion (rows merge with the α-Quartz chain) ──
    ("β-Cristobalite", {
        "structure": "α-Cristobalite", "to": "β-Cristobalite", "temp_c": 230,
        "temp_qualifier": "at", "transformType": "displacive", "reversible": True,
        "volume_change_pct": 2.8,
        "note": "α→β cristobalite inversion (~200–270°C): ≈2.8 vol% expansion on heating, the largest of the SiO2 framework inversions — the reason cristobalite-bearing refractory linings spall if fire-cycled through it.",
        "source": SIO2_SRC,
    }),
    # ── Baddeleyite: ZrO2 martensitic events (the D.4 acceptance element) ──
    ("Baddeleyite", {
        "structure": "Baddeleyite", "to": "Tetragonal Zirconia", "temp_c": 1170,
        "temp_qualifier": "at", "transformType": "martensitic", "reversible": True,
        "volume_change_pct": -4.5,
        "note": "The transformation-toughening event: athermal martensitic m→t at ~1170°C on heating, t→m at ~950°C on cooling, ≈4–5 vol% dilation.",
        "source": ZRO2_SRC,
    }),
    ("Baddeleyite", {
        "structure": "Tetragonal Zirconia", "to": "Cubic Zirconia", "temp_c": 2370,
        "temp_qualifier": "at", "transformType": "displacive", "reversible": True,
        "note": "t→c displacive step near 2370°C.",
        "source": ZRO2_SRC,
    }),
    # ── Sialon: β′-sialon solid-solution formation ──────────────────────────
    ("Sialon", {
        "structure": "Sialon", "phaseName": "β′-Sialon (Si₆₋zAlzOzN₈₋z)",
        "tempRange": [20, 1900], "transformType": "polymorphic", "source":
        "K.H. Jack, Sialons and related nitrogen ceramics, J. Mater. Sci. 11 (1976) 1135",
    }),
    ("Sialon", {
        "structure": "Si₃N₄ + Al₂O₃/AlN", "to": "β′-Sialon", "temp_c": 1600,
        "temp_qualifier": "above", "transformType": "reconstructive", "reversible": False,
        "volume_change_pct": 0.0,
        "note": "β′-sialon (z≈0–4.2) forms by solid-state reaction of Si₃N₄ with Al₂O₃+AlN at ~1500–1750°C; aluminium/oxygen substitute into the β-Si₃N₄ lattice keeping the structure isostructural.",
        "source": "K.H. Jack (1976); Ekström & Nygren, SiAlON ceramics, J. Am. Ceram. Soc. 75 (1992) 259",
    }),
]


def load(data=DATA):
    with open(data, encoding="utf-8") as f:
        return json.load(f)


def find_entry(doc, name):
    for s in doc["structures"]:
        if s.get("name") == name:
            return s
    return None


def merge_key(row):
    return (row.get("structure"), row.get("to"), row.get("temp_c"))


def build_proposal(doc):
    add, patch = [], []
    for item in RECONCILE:
        entry = find_entry(doc, item["entry"])
        if entry is None:
            print(f"!! entry not found: {item['entry']!r}", file=sys.stderr); continue
        wanted = item["row"]
        for row in entry.get("transitions", []):
            if row.get("structure") != item["structure"]:
                continue
            if wanted == "window" and "tempRange" not in row:
                continue
            if wanted == "event" and row.get("temp_c") is None:
                continue
            missing = {k: v for k, v in item["patch"].items() if k not in row or row[k] is None}
            if missing:
                patch.append((entry, row, missing))
    for name, row in AUTHOR:
        entry = find_entry(doc, name)
        if entry is None:
            print(f"!! entry not found: {name!r}", file=sys.stderr); continue
        existing = {merge_key(r) for r in entry.get("transitions", [])}
        if merge_key(row) not in existing:
            add.append((name, row))
    return add, patch


def apply(add, patch):
    for _, row in add:
        pass  # callers attach rows themselves; kept for API symmetry
    for entry, row, fields in patch:
        for k, v in fields.items():
            row[k] = v
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply the proposal to data/crystal_vr.json")
    ap.add_argument("--check", action="store_true", help="audit the data file for schema conformance")
    args = ap.parse_args()
    doc = load()

    if args.check:
        n_mats = n_rows = 0
        for s in doc["structures"]:
            tr = s.get("transitions")
            if tr:
                n_mats += 1; n_rows += len(tr)
                for j, r in enumerate(tr):
                    assert r.get("structure"), (s["name"], j)
                    assert "tempRange" in r or "temp_c" in r, (s["name"], j)
                    if r.get("volume_change_pct") is not None:
                        assert isinstance(r["volume_change_pct"], (int, float)), (s["name"], j)
        print(f"Audit OK: {n_mats} materials carry transitions[] ({n_rows} rows total).")
        for s in doc["structures"]:
            if s.get("transitions"):
                print(f"  {s['name']}: {len(s['transitions'])} rows")
        return

    add, patch = build_proposal(doc)
    print("=" * 72)
    print("TIER D.3 PROPOSAL (report-only; --write to apply)")
    print("=" * 72)
    print(f"\nPASS B — {len(add)} new rows to AUTHOR:")
    for name, r in add:
        if "temp_c" in r:
            t = f"@{r['temp_c']}°C{" ("+str(r['temp_qualifier'])+")" if r.get('temp_qualifier') else ""}"
            print(f"  [{name}] {r['structure']} -> {r.get('to')} {t} ({r['transformType']}) "
                  f"vol={r.get('volume_change_pct','-')} rev={r.get('reversible','-')}")
        else:
            lo, hi = r["tempRange"]
            print(f"  [{name}] window {r['structure']} [{lo}, {hi}]°C ({r['transformType']})")
        print(f"      src: {r.get('source','none')}")
    print(f"\nPASS A — {len(patch)} legacy-row reconciles:")
    for entry, row, fields in patch:
        print(f"  [{entry['name']}] {row.get('structure')}: +{sorted(fields)}")
    if not args.write:
        print("\n(dry run — rerun with --write to apply, then validate.)")
        return
    for name, row in add:
        find_entry(doc, name).setdefault("transitions", []).append(row)
    apply(add, patch)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nWrote {DATA} (+{len(add)} rows, {len(patch)} patches). Run 'python _author_polymorphs.py --check' and the suite.")


if __name__ == "__main__":
    main()
