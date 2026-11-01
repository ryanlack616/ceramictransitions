#!/usr/bin/env python3
"""Check catalog asset and geometry budgets before release."""
from __future__ import annotations

import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crystal_vr.json"
RAW_LIMIT = 8 * 1024 * 1024
GZIP_LIMIT = 1 * 1024 * 1024
STRUCTURE_ATOM_LIMIT = 2500


def main() -> int:
    raw = DATA.read_bytes()
    document = json.loads(raw)
    structures = document["structures"]
    largest = max((len(s.get("atoms", [])), s["name"]) for s in structures)
    compressed = gzip.compress(raw, compresslevel=9)
    print(f"catalog: raw={len(raw)} bytes gzip={len(compressed)} bytes")
    print(f"largest baked structure: {largest[1]} ({largest[0]} atoms)")
    failures = []
    if len(raw) > RAW_LIMIT:
        failures.append(f"raw catalog exceeds {RAW_LIMIT} bytes")
    if len(compressed) > GZIP_LIMIT:
        failures.append(f"gzip catalog exceeds {GZIP_LIMIT} bytes")
    if largest[0] > STRUCTURE_ATOM_LIMIT:
        failures.append(f"largest structure exceeds {STRUCTURE_ATOM_LIMIT} atoms")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: catalog performance budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
