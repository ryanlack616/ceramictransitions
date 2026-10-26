#!/usr/bin/env python3
"""Probe SrZrO3 / CaZrO3 for the extras pass."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API = os.environ.get('MP_API_KEY') or sys.exit('no key')


def q(f):
    params = {'formula': f, '_limit': 6,
              '_fields': 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API, 'Accept': 'application/json',
                                               'User-Agent': 'probe'})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = json.loads(r.read())
    rows = body.get('data') or []
    out = []
    for row in sorted(rows, key=lambda x: x.get('energy_above_hull', 9e9))[:6]:
        sg = (row.get('symmetry') or {}).get('symbol')
        out.append((row.get('energy_above_hull'), row.get('material_id'),
                    row.get('formula_pretty'), sg, row.get('nsites')))
    return out


for label, f in {'SrZrO3': 'SrZrO3', 'CaZrO3': 'CaZrO3'}.items():
    print('== %s' % label)
    for r in q(f):
        print('   %.4f %-14s %-12s %-16s %s' % r)
    print()