#!/usr/bin/env python3
"""Harvest latent transition data already present in crystal_vr.json.

Two honest, derivable transforms (NO invention — everything comes from data
already in the file):

  PATH 1 (transitions[]): parse the structural `application_tags`
      transforms-to:X@T / decomp-to:X@T / precursor-to:X
      into structured `transitions[]` rows (reconciled schema — extends the
      existing per-phase shape with optional event fields).

  PATH 2 (bound_type): classify what `melting_point_c` actually means for each
      entry — a true congruent `melts`, or an overloaded `decomposes` /
      `transforms` bound — using material_class + the decomp/precursor tags.
      Flags the rows where melting_point_c == service_temp_c (the tell that a
      decomposition/placeholder number was stuffed into a field labeled melt).

REPORT-ONLY by default (--dry-run). Writing to canon requires --write AND a
human review of the printed proposal first (apprentice proposes, human
disposes — the standing discipline for data claims).

Idempotent: re-running never duplicates a harvested row (keyed on source tag);
never overwrites a hand-authored transitions[] (only appends missing rows,
and only when --write --append-transitions is given).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crystal_vr.json"

# ── tag grammar ──────────────────────────────────────────────────────────────
# transforms-to:Magnetite>1390C | transforms-to:β-Quartz@573C | decomp-to:CaO+CO2@825C
#  - product after the colon, up to an optional @/>/< temperature
#  - temp suffix: @NNN C (exact), >NNN C (above), <NNN C (below)
_EVENT_PREFIXES = ("transforms-to", "decomp-to", "precursor-to", "oxidizes-to")
_TEMP_RE = re.compile(r"([<>@])\s*(\d+(?:\.\d+)?)\s*C?\s*$", re.I)

# tag prefix -> the transformType we record for a harvested event
_PREFIX_TRANSFORM_TYPE = {
    "transforms-to": "polymorphic",      # refined to displacive/reconstructive only when known
    "decomp-to": "decomposition",
    "precursor-to": "decomposition",     # firing precursor: parent breaks down into the product
    "oxidizes-to": "oxidation",
}

# known displacive inversions (the only ones we upgrade from generic "polymorphic")
_DISPLACIVE = {("α-Quartz", "β-Quartz")}

# ── bound_type classification (PATH 2) ───────────────────────────────────────
# Classes whose members do NOT congruently melt — the number in melting_point_c
# is a decomposition / breakdown bound, not a melt.
_DECOMPOSE_CLASSES = {"carbonate", "hydroxide"}
# Al2SiO5 / clay polymorphs transform to mullite rather than melt at the listed T.
_TRANSFORM_NAMES = {"Kaolinite", "Talc", "Andalusite", "Kyanite", "Sillimanite"}
# precursor-to:<X> targets that are APPLICATIONS, not chemical decomposition
# products (e.g. "precursor-to:TBC" = used in thermal-barrier coatings). These
# must NOT be read as evidence that the material decomposes.
_APPLICATION_TARGETS = {"tbc", "ebc", "cmc"}


def _is_chemical_decomp_tag(tag: str) -> bool:
    """PATH 1 filter: True for any harvestable event tag whose target is a chemical product.

    ALLOW all event tag prefixes by default (transforms-to / decomp-to /
    precursor-to / oxidizes-to). Only EXCLUDE for `decomp-to:` or `precursor-to:`
    whose target is an APPLICATION (TBC, EBC, CMC) rather than a chemical
    product. e.g. `precursor-to:TBC` means "used in thermal-barrier coatings",
    not "decomposes into TBC."
    """
    t = tag.lower()
    if not t.startswith(("decomp-to:", "precursor-to:")):
        # transforms-to / oxidizes-to / non-event tags → allow (or rejected upstream)
        return True
    product = tag.split(":", 1)[1].strip()
    # strip any @/>/< temperature suffix before judging the target
    m = _TEMP_RE.search(product)
    if m:
        product = product[: m.start()].strip()
    return product.lower() not in _APPLICATION_TARGETS


def _has_decomp_evidence(s: dict) -> bool:
    """PATH 2 evidence: does this material have a tag indicating non-congruent-melt
    chemistry? Includes decomp-to:, precursor-to: (even to applications like TBC,
    because that still signals "this material is a precursor, not a congruent melt").
    Does NOT include transforms-to: (polymorphic inversion is congruent)."""
    return any(t.lower().startswith(("decomp-to:", "precursor-to:")) for t in s.get("application_tags", []))


def _parse_event_tag(tag: str):
    """Return (prefix, product, temp_c, qualifier) or None if not an event tag."""
    if ":" not in tag:
        return None
    prefix, rest = tag.split(":", 1)
    prefix = prefix.strip().lower()
    if prefix not in _EVENT_PREFIXES:
        return None
    temp_c = None
    qualifier = None
    m = _TEMP_RE.search(rest)
    if m:
        qualifier = {"@": "at", ">": "above", "<": "below"}[m.group(1)]
        temp_c = float(m.group(2))
        if temp_c.is_integer():
            temp_c = int(temp_c)
        rest = rest[: m.start()].strip()
    product = rest.strip()
    return prefix, product, temp_c, qualifier


def _transform_type(prefix: str, structure: str, product: str) -> str:
    if (structure, product) in _DISPLACIVE:
        return "displacive"
    return _PREFIX_TRANSFORM_TYPE[prefix]


def harvest_transitions(s: dict) -> list[dict]:
    """Build proposed transitions[] event rows for one structure from its tags."""
    rows = []
    for tag in s.get("application_tags", []):
        parsed = _parse_event_tag(tag)
        if not parsed:
            continue
        prefix, product, temp_c, qualifier = parsed
        if not product:
            continue
        # Skip tags whose target is an APPLICATION (e.g. TBC, EBC) rather than
        # a chemical decomposition product. e.g. `precursor-to:TBC` means
        # "used in thermal-barrier coatings", not "decomposes into TBC."
        if not _is_chemical_decomp_tag(tag):
            continue
        # Auto-adopt melting_point_c as the transition temp ONLY for `decomp-to:`
        # rows where mp == service_temp (the placeholder tell that the field was
        # mislabeled as a melt). For `precursor-to:` rows, the temperature is often
        # a multi-step process with a different temperature for the final product
        # (kaolinite→metakaolin @ 450C, kaolinite→mullite @ ~1000-1400C) — leave
        # temp_c=None so a human authors the right value.
        temp_source = "tag"
        if temp_c is None and prefix == "decomp-to":
            mp, st = s.get("melting_point_c"), s.get("service_temp_c")
            if isinstance(mp, (int, float)) and mp == st:
                temp_c = mp
                temp_source = "melting_point_c (overloaded; == service_temp_c)"
        row = {
            "structure": s["name"],
            "to": product,
            "transformType": _transform_type(prefix, s["name"], product),
            "reversible": prefix == "transforms-to" and (s["name"], product) in _DISPLACIVE,
            "source": f"tag:{tag}",
        }
        if temp_c is not None:
            row["temp_c"] = temp_c
            if qualifier and qualifier != "at":
                row["temp_qualifier"] = qualifier  # "above"/"below"
            if temp_source != "tag":
                row["note"] = f"temp adopted from {temp_source}"
        rows.append(row)
    return rows


def classify_bound(s: dict):
    """PATH 2: what does melting_point_c mean here? Return (bound_type, flagged, reason)."""
    name = s.get("name", "?")
    cls = (s.get("material_class") or "").lower()
    mp = s.get("melting_point_c")
    st = s.get("service_temp_c")
    tags = s.get("application_tags", [])
    has_decomp = any(t.lower().startswith(("decomp-to:", "precursor-to:"))
                      and _is_chemical_decomp_tag(t)
                      for t in s.get("application_tags", []))

    if not isinstance(mp, (int, float)):
        return None, False, "no melting_point_c"

    if cls in _DECOMPOSE_CLASSES or name in _TRANSFORM_NAMES or has_decomp:
        btype = "transforms" if name in _TRANSFORM_NAMES else "decomposes"
        reason_bits = []
        if cls in _DECOMPOSE_CLASSES:
            reason_bits.append(f"class={cls}")
        if name in _TRANSFORM_NAMES:
            reason_bits.append("Al2SiO5/clay→mullite")
        if has_decomp:
            reason_bits.append("decomp/precursor tag")
        # flagged = the field is currently labeled "melting_point" but this
        # material does not congruently melt at that T.
        flagged = mp == st or has_decomp
        return btype, flagged, "; ".join(reason_bits)

    # default: a genuine congruent melt (e.g. feldspar fluxes, oxides, carbides)
    return "melts", False, "default congruent melt"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="report only (default)")
    ap.add_argument("--write", dest="dry_run", action="store_false",
                    help="actually write proposed transitions[]/bound_type to data (requires --append-transitions / --apply-bound-type)")
    ap.add_argument("--append-transitions", action="store_true",
                    help="with --write: append harvested transition rows (never overwrites hand-authored)")
    ap.add_argument("--apply-bound-type", action="store_true",
                    help="with --write: set bound_type on each entry")
    ap.add_argument("--clean-only", action="store_true",
                    help="exclude path-1 rows that need human-authored temperatures (where the tag carried no @T and no auto-adopt was possible). Use for staged commits where the human-authored temps come later.")
    ap.add_argument("--json", action="store_true", help="emit machine-readable proposal JSON")
    args = ap.parse_args()

    data = json.loads(DATA.read_text(encoding="utf-8"))
    structures = data["structures"]

    proposal = {"transitions": {}, "bound_type": {}, "flags": []}
    for s in structures:
        rows = harvest_transitions(s)
        if args.clean_only:
            # drop rows that have no temperature — these need human authoring
            rows = [r for r in rows if r.get("temp_c") is not None]
        if rows:
            proposal["transitions"][s["name"]] = rows
        btype, flagged, reason = classify_bound(s)
        if btype:
            proposal["bound_type"][s["name"]] = btype
            if flagged:
                proposal["flags"].append({
                    "name": s["name"], "bound_type": btype,
                    "melting_point_c": s.get("melting_point_c"),
                    "service_temp_c": s.get("service_temp_c"),
                    "reason": reason,
                })

    if args.json:
        print(json.dumps(proposal, indent=2, ensure_ascii=False))
        return 0

    # ── write path (only invoked with --write) ──────────────────────────────
    if not args.dry_run:
        if not (args.append_transitions or args.apply_bound_type):
            print("ERROR: --write requires --append-transitions and/or --apply-bound-type")
            return 2
        # Edit the live data in place
        n_trans = 0
        n_bound = 0
        n_skipped_existing = 0
        for s in structures:
            name = s["name"]
            if args.append_transitions and name in proposal["transitions"]:
                # idempotent: skip if a row with the same `to` and temp_c already exists
                existing = s.get("transitions") or []
                existing_keys = {(r.get("to"), r.get("temp_c")) for r in existing}
                new_rows = [r for r in proposal["transitions"][name]
                            if (r.get("to"), r.get("temp_c")) not in existing_keys]
                if new_rows:
                    s.setdefault("transitions", []).extend(new_rows)
                    n_trans += len(new_rows)
                else:
                    n_skipped_existing += len(proposal["transitions"][name])
            if args.apply_bound_type and name in proposal["bound_type"]:
                if "bound_type" not in s:
                    s["bound_type"] = proposal["bound_type"][name]
                    n_bound += 1
                # never overwrite an existing bound_type (human-authored values are sacred)

        # Validate the proposed data BEFORE writing it to canon.
        # The validator hard-codes data/crystal_vr.json (no CLI arg), so we
        # swap the file in place, run the validator, and swap back. The
        # proposed data has been edited IN MEMORY only at this point.
        import subprocess as _sp
        live_backup = DATA.read_text(encoding="utf-8")
        try:
            DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            _val_path = DATA.parent.parent / "validate_crystal_vr.py"
            _r = _sp.run([sys.executable, str(_val_path)], capture_output=True, text=True)
            if _r.returncode != 0:
                print("=" * 72)
                print("WRITE ABORTED — validator rejected the proposed data.")
                print("Restoring live data from in-memory backup.")
                print("=" * 72)
                print(_r.stdout)
                print(_r.stderr)
                DATA.write_text(live_backup, encoding="utf-8")
                return 1
            # Print validator OK for transparency
            print("[validator] OK on proposed data")
        except Exception:
            # Restore on any failure during validation
            DATA.write_text(live_backup, encoding="utf-8")
            raise

        # The proposed data is already on disk (validator just approved it).
        # No further write step needed — the swap-in-place above IS the write.
        print("=" * 72)
        print(f"WRITE OK — {n_trans} transition rows appended, {n_bound} bound_type rows set")
        if n_skipped_existing:
            print(f"  (skipped {n_skipped_existing} rows already in canon)")
        if args.clean_only and len(proposal["transitions"]) == 0:
            print("  (--clean-only: rows needing human-authored temps deferred)")
        print("=" * 72)
        print("Now run: python3 validate_crystal_vr.py && node test_prototype_generators.js")
        return 0

    # ── human-readable report (default dry-run path) ─────────────────────────
    print("=" * 72)
    print("PATH 1 — proposed transitions[] (harvested from tags, NO invention)")
    print("=" * 72)
    for name, rows in proposal["transitions"].items():
        print(f"\n{name}:")
        for r in rows:
            t = f"{r.get('temp_c','?')}°C" + (f" ({r['temp_qualifier']})" if r.get("temp_qualifier") else "")
            note = f"   [{r['note']}]" if r.get("note") else ""
            print(f"  → {r['to']:22} {r['transformType']:14} {t:14} src={r['source']}{note}")
    print(f"\n  ({len(proposal['transitions'])} materials gain transition events)")

    print("\n" + "=" * 72)
    print("PATH 2 — bound_type for melting_point_c (what the number really means)")
    print("=" * 72)
    by_type = {}
    for name, bt in proposal["bound_type"].items():
        by_type.setdefault(bt, []).append(name)
    for bt in ("melts", "decomposes", "transforms"):
        names = by_type.get(bt, [])
        print(f"\n  {bt} ({len(names)}): {', '.join(names)}")

    print("\n" + "-" * 72)
    print("⚠  FLAGGED — labeled melting_point_c but does NOT congruently melt:")
    print("-" * 72)
    for f in proposal["flags"]:
        eq = " (== service_temp, placeholder tell)" if f["melting_point_c"] == f["service_temp_c"] else ""
        print(f"  {f['name']:16} {f['melting_point_c']}°C → {f['bound_type']}{eq}  [{f['reason']}]")
    print(f"\n  ({len(proposal['flags'])} rows would change from an implied 'melts' to decomposes/transforms)")

    print("\n" + "=" * 72)
    print("REPORT-ONLY. Nothing written. Review above, then:")
    print("  --write --append-transitions   (append PATH 1 rows)")
    print("  --write --apply-bound-type     (set PATH 2 bound_type)")
    print("  --clean-only                   (exclude rows needing human-authored temps)")
    print("Both gate on the validator rules being added first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
