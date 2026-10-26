#!/usr/bin/env python3
"""Probe ZrO2 polymorphs + deep-gap candidates."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API_KEY = os.environ.get('MP_API_KEY') or sys.exit('no MP_API_KEY')
FIELDS = 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'


def search(formula, limit=14):
    params = {'formula': formula, '_fields': FIELDS, '_limit': limit}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API_KEY, 'Accept': 'application/json',
                                               'User-Agent': 'ceramictransitions-mp-probe/0.1'})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = json.loads(r.read())
    rows = body.get('data') or []
    out = []
    for r in sorted(rows, key=lambda x: x.get('energy_above_hull', 9e9))[:limit]:
        sg = (r.get('symmetry') or {}).get('symbol')
        out.append((r.get('energy_above_hull'), r.get('material_id'), r.get('formula_pretty'), sg, r.get('nsites')))
    return out


for label, f in {
    'ZrO2 (m/t/c)': 'ZrO2',
    'Ti2AlC (MAX)': 'Ti2AlC',
    'CeO2 (ceria)': 'CeO2',
    'CaAl12O19 (hibonite)': 'CaAl12O19',
    'LaB6': 'LaB6',
    'MgCr2O4 (magnesiochromite)': 'MgCr2O4',
    'VN': 'VN',
    'BaZrO3': 'BaZrO3',
    'Ta4HfC5': 'Ta4HfC5',
    'Ta4HfC5 alt': 'HfTa4C5',
}.items():
    print('== %s' % label)
    try:
        for r in search(f):
            print('   %.4f  %-14s %-10s %-16s %s' % (r[0], r[1], r[2], r[3], r[4]))
    except Exception as e:
        print('   ERR', e)
    print()