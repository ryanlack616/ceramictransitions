#!/usr/bin/env python3
"""Ensure both static viewers consume the one procedural runtime."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def table_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const PROTOTYPE_TABLE\s*=\s*\{(?P<body>.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError(f"missing PROTOTYPE_TABLE in {path.name}")
    return set(re.findall(r"['\"]([^'\"]+)['\"]\s*:", match.group("body")))


def main() -> int:
    runtime = table_keys(ROOT / "prototype-runtime.js")
    for page in (ROOT / "index.html", ROOT / "lattice.html"):
        text = page.read_text(encoding="utf-8")
        if '<script src="prototype-runtime.js"></script>' not in text:
            raise AssertionError(f"{page.name} does not load prototype-runtime.js")
        if "const PROTOTYPE_TABLE" in text:
            raise AssertionError(f"{page.name} still contains a duplicate prototype table")
    print(f"PASS: both viewers use shared prototype runtime ({len(runtime)} formulas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
