#!/usr/bin/env python3
"""Verify the legacy mirror collector cannot publish source/cache files."""
from __future__ import annotations

from pathlib import Path

from _deploy import ROOT, collect_files


REQUIRED = {
    "index.html",
    "lattice.html",
    "data/crystal_vr.json",
    "data/crystal_vr.schema.json",
    "data/crystal_vr.js",
    "viewer-core.js",
    "prototype-runtime.js",
    "panel-manager.js",
}


def main() -> int:
    files = {path.relative_to(ROOT).as_posix() for path in collect_files()}
    forbidden = [path for path in files if ".mp_cache/" in path or path.endswith((".py", ".md"))]
    missing = sorted(REQUIRED - files)
    if forbidden or missing:
        if forbidden:
            print("FORBIDDEN:", sorted(forbidden))
        if missing:
            print("MISSING:", missing)
        return 1
    print(f"PASS: deploy artifact allowlist ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
