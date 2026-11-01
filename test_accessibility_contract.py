#!/usr/bin/env python3
"""Cheap static accessibility contract checks for the two viewer surfaces."""
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    lattice = (ROOT / "lattice.html").read_text(encoding="utf-8")
    required_index = [
        'class="skip-link"',
        'id="structure-announcer"',
        'aria-label="Search structures"',
        ':focus-visible',
        'prefers-reduced-motion',
        "viewer-canvas",
    ]
    required_lattice = [
        'aria-label="Filter structures"',
        'aria-live="polite"',
        ':focus-visible',
        'prefers-reduced-motion',
    ]
    missing = [f"index:{item}" for item in required_index if item not in index]
    missing += [f"lattice:{item}" for item in required_lattice if item not in lattice]
    if missing:
        print("MISSING:", missing)
        return 1
    print("PASS: accessibility contract markers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
