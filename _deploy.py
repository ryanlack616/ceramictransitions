#!/usr/bin/env python3
"""
FTP deploy for ceramictransitions.com (pixie-sh / Porkbun static hosting).

Mirrors the deploy pattern used for howell.help. The live site is served from
pixie-sh (Server: openresty, X-Service: pixie-sh) — git push does NOT deploy
this site. Run this script after committing to push changes live.

USAGE (PowerShell):
    $env:CERAMICTRANSITIONS_FTP_PASS = '<porkbun ftp password>'
    python _deploy.py                # uploads changed files
    python _deploy.py --dry-run      # show what would upload, no transfer
    python _deploy.py --force        # upload everything (ignore size compare)

ENV:
    CERAMICTRANSITIONS_FTP_PASS  (required) — pixie-sh password
    CERAMICTRANSITIONS_FTP_HOST  (optional) — default 'pixie-ss1-ftp.porkbun.com'
    CERAMICTRANSITIONS_FTP_USER  (optional) — default 'ceramictransitions.com'

What gets uploaded:
    *.html in repo root
    data/**/*.json
    favicon / .ico / .png / .svg if present in root

What gets skipped (never):
    yfiles/, yfiles-demo/, .git/, .github/, __pycache__/, node_modules/
    *.py, *.md, .gitignore, .pass.local, *.local, .env*, _deploy.py itself
    Any path containing 'taichi' (sibling repo guard)
"""
from __future__ import annotations
import argparse
import ftplib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Directories we never touch.
SKIP_DIRS = {
    'yfiles', 'yfiles-demo', '.git', '.github', '__pycache__',
    'node_modules', '.vscode', '.idea',
}

# Files we never upload.
SKIP_FILES = {
    '_deploy.py', '.gitignore', '.pass.local', '.env',
    '.env.local', '.env.prod', 'BUILD.md', 'PLANS.md',
    'test_prototype_generators.js', 'transitions-graph-local.html',
}

# Extensions we never upload (source / dev artifacts).
SKIP_EXTS = {'.py', '.md', '.log', '.bak', '.tmp', '.local', '.swp'}

# Extensions we DO upload.
ALLOWED_EXTS = {'.html', '.json', '.ico', '.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp', '.css', '.js'}


def should_upload(path: Path) -> bool:
    """Decide if a path should be uploaded based on the skip/allow rules."""
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if any(p in SKIP_DIRS for p in parts):
        return False
    if 'taichi' in str(rel).lower():
        return False
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() in SKIP_EXTS:
        return False
    if path.suffix.lower() not in ALLOWED_EXTS:
        return False
    # test_prototype_generators.js is a dev test, not a viewer asset.
    if path.name.startswith('test_') and path.suffix == '.js':
        return False
    return True


def collect_files() -> list[Path]:
    """Walk the repo root and return all deployable files."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune dirs in place so we don't recurse into them.
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if should_upload(p):
                out.append(p)
    return sorted(out)


def ftp_mkdirs(ftp: ftplib.FTP, remote_dir: str) -> None:
    """Recursively create remote directories. Tolerates already-exists."""
    if not remote_dir or remote_dir in ('.', '/'):
        return
    parts = remote_dir.replace('\\', '/').strip('/').split('/')
    cur = ''
    for part in parts:
        cur = f'{cur}/{part}' if cur else part
        try:
            ftp.mkd(cur)
        except ftplib.error_perm:
            # 550: already exists, or permission — ignore and continue.
            pass


def remote_size(ftp: ftplib.FTP, remote_path: str) -> int | None:
    """Return remote file size in bytes, or None if missing."""
    try:
        return ftp.size(remote_path)
    except ftplib.error_perm:
        return None
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='list files that would upload; do not transfer')
    ap.add_argument('--force', action='store_true', help='upload all files (skip size-equal optimization)')
    ap.add_argument('--tls', action='store_true', help='use FTP_TLS (explicit, port 21)')
    args = ap.parse_args()

    host = os.environ.get('CERAMICTRANSITIONS_FTP_HOST', 'pixie-ss1-ftp.porkbun.com')
    user = os.environ.get('CERAMICTRANSITIONS_FTP_USER', 'ceramictransitions.com')
    pw = os.environ.get('CERAMICTRANSITIONS_FTP_PASS', '').strip()

    files = collect_files()
    print(f'[deploy] root: {ROOT}')
    print(f'[deploy] host: {host}   user: {user}   tls: {args.tls}')
    print(f'[deploy] {len(files)} file(s) would deploy:')
    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        print(f'    {rel}  ({f.stat().st_size} bytes)')

    if args.dry_run:
        print('[deploy] dry-run complete; no transfer.')
        return 0

    if not pw:
        print('[deploy] ERROR: CERAMICTRANSITIONS_FTP_PASS not set in environment.', file=sys.stderr)
        print('         export it via:  $env:CERAMICTRANSITIONS_FTP_PASS = "..."', file=sys.stderr)
        return 2

    if args.tls:
        ftp = ftplib.FTP_TLS(host, timeout=30)
        ftp.login(user=user, passwd=pw)
        ftp.prot_p()
    else:
        ftp = ftplib.FTP(host, timeout=30)
        ftp.login(user=user, passwd=pw)

    uploaded = 0
    skipped_same_size = 0
    try:
        # Ensure data/ exists.
        ftp_mkdirs(ftp, 'data')

        for local in files:
            rel = local.relative_to(ROOT).as_posix()
            local_size = local.stat().st_size

            # Create parent dirs.
            parent = '/'.join(rel.split('/')[:-1])
            if parent:
                ftp_mkdirs(ftp, parent)

            if not args.force:
                rsize = remote_size(ftp, rel)
                if rsize == local_size:
                    print(f'    = {rel}  (same size, skip)')
                    skipped_same_size += 1
                    continue

            with open(local, 'rb') as fh:
                ftp.storbinary(f'STOR {rel}', fh)
            print(f'    + {rel}  ({local_size} bytes)')
            uploaded += 1
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    print(f'[deploy] done. uploaded={uploaded}  skipped_same_size={skipped_same_size}  total={len(files)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
