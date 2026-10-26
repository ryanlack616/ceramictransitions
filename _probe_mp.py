#!/usr/bin/env python3
"""Probe Materials Project for the 7 deviant-model compositions + deferred
additions. Lists candidate phases (material_id, formula, spacegroup, nsites,
ehull) so we can pick a stable, on-topic polymorph."""
import json, os, sys, urllib.parse, urllib.request

# load .env WITHOUT echoing the key
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

API_KEY = os.environ.get('MP_API_KEY')
if not API_KEY:
    sys.exit('no MP_API_KEY')

PROBES = {
    'Zircon (ZrSiO4)': ['ZrSiO4'],
    'Leucite (KAlSi2O6)': ['KAlSi2O6'],
    'Willemite (Zn2SiO4)': ['Zn2SiO4'],
    'Enstatite (MgSiO3)': ['MgSiO3'],
    'Anorthite (CaAl2Si2O8)': ['CaAl2Si2O8'],
    'Kaolinite': ['Al2H4O9Si2', 'Al2Si2O5(OH)4'],
    'Talc': ['Mg3H4O12Si4', 'Mg3Si4O10(OH)2'],
}

FIELDS = 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'


def search(formula):
    params = {'formula': formula, '_fields': FIELDS, '_limit': 8}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API_KEY, 'Accept': 'application/json',
                                               'User-Agent': 'ceramictransitions-mp-probe/0.1'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
    except Exception as e:
        return f'ERR {e}'
    rows = body.get('data') or []
    out = []
    for r in rows:
        sg = r.get('symmetry') or {}
        out.append((r.get('energy_above_hull'), r.get('material_id'),
                    r.get('formula_pretty'), sg.get('symbol'), r.get('nsites')))
    return sorted(out)


for label, forms in PROBES.items():
    print(f'== {label}')
    seen = []
    for f in forms:
        rows = search(f)
        if isinstance(rows, str):
            print('   ', f, rows); continue
        for r in rows:
            if r[1] not in seen:
                seen.append(r[1])
                print('   %-6s %-12s %-12s %-14s %s' % (r[1], r[2], r[3], r[4], r[0]))
    print()