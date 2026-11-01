#!/usr/bin/env python3
"""Headless browser smoke test for the static viewer.

This intentionally uses the Chromium executable already available in CI or a
developer environment instead of introducing a browser framework dependency.
It verifies that the catalog loads over HTTP, the first structure renders into
the DOM, and a stable share key selects the requested material.
"""
from __future__ import annotations

import http.server
import os
import shutil
import socketserver
import subprocess
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def chromium_path() -> str:
    candidates = [
        os.environ.get("CHROMIUM_BIN", ""),
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
        shutil.which("google-chrome") or "",
        "/snap/bin/chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("Chromium not found; set CHROMIUM_BIN to run viewer smoke test")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        pass


def dump_dom(url: str, width: int = 1280, height: int = 900) -> str:
    browser = chromium_path()
    command = [
        browser,
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-background-networking",
        "--no-first-run",
        "--enable-unsafe-swiftshader",
        "--use-angle=swiftshader",
        "--dump-dom",
        "--virtual-time-budget=3000",
        f"--window-size={width},{height}",
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=45, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Chromium exited {result.returncode}: {result.stderr[-1000:]}")
    return result.stdout


def main() -> int:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]
        try:
            base = f"http://127.0.0.1:{port}"
            first = dump_dom(f"{base}/index.html")
            if 'id="fatal" class="show"' in first:
                raise AssertionError("index.html displayed its fatal error overlay")
            if 'id="info-name">Periclase</div>' not in first:
                raise AssertionError("index.html did not render the first structure")
            if 'data-idx="112"' not in first:
                raise AssertionError("index.html did not build the complete structure list")
            if 'id="lattice-gallery-link" href="lattice.html?id=periclase%7Cmgo"' not in first:
                raise AssertionError("index-to-lattice link did not preserve the selected material")

            shared = dump_dom(f"{base}/index.html#id=hafnium%20carbide%7Chfc")
            if 'id="info-name">Hafnium Carbide</div>' not in shared:
                raise AssertionError("stable share key did not select Hafnium Carbide")

            sort_test = dump_dom(f"{base}/index.html?ct_test=sort")
            if 'all sort modes preserve button-to-structure selection' not in sort_test:
                raise AssertionError("sort interaction scenario did not pass")

            catalog_test = dump_dom(f"{base}/index.html?ct_test=catalog")
            if 'catalog mode count, selection, and shared material state' not in catalog_test:
                raise AssertionError("catalog interaction scenario did not pass")

            system_test = dump_dom(f"{base}/index.html?ct_test=system")
            if 'system record layer stack and material context' not in system_test:
                raise AssertionError("system architecture scenario did not pass")

            transition_test = dump_dom(f"{base}/index.html?ct_test=transitions")
            if 'transition timeline and selected material context' not in transition_test:
                raise AssertionError("transition timeline scenario did not pass")

            malformed = dump_dom(f"{base}/index.html#id=missing-material&sc=not-a-number&sp=999&mp=-5")
            if 'id="info-name">Periclase</div>' not in malformed or 'id="fatal" class="show"' in malformed:
                raise AssertionError("malformed share-link fallback failed")

            lattice = dump_dom(f"{base}/lattice.html?id=periclase%7Cmgo")
            if 'id="info-name">Periclase</div>' not in lattice:
                raise AssertionError("lattice stable link did not select Periclase")

            local = dump_dom((ROOT / "index.html").as_uri())
            if 'id="info-name">Periclase</div>' not in local:
                raise AssertionError("file:// fallback did not render the first structure")

            mobile_index = dump_dom(f"{base}/index.html", 390, 844)
            if 'id="info-name">Periclase</div>' not in mobile_index or 'id="fatal" class="show"' in mobile_index:
                raise AssertionError("mobile flagship smoke test failed")
            mobile_lattice = dump_dom(f"{base}/lattice.html", 390, 844)
            if 'id="info-name">Periclase</div>' not in mobile_lattice or 'id="fatal" class="show"' in mobile_lattice:
                raise AssertionError("mobile lattice smoke test failed")
        finally:
            server.shutdown()
            thread.join(timeout=2)

    print("PASS: viewer HTTP load, structure list, stable share key, and lattice link")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
