#!/usr/bin/env python3
"""Probe the native-tier rejects: dump MP candidates so we can tune SG aliases."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API = os.environ.get('MP_API_KEY') or sys.exit('no key')


def q(f, limit=14):
    params = {'formula': f, '_limit': limit,
              '_fields': 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API, 'Accept': 'application/json',
                                               'User-Agent': 'probe'})
    with urllib.request.urlopen(req, timeout=90) as r:
        body = json.loads(r.read())
    out = []
    for row in (body.get('data') or []):
        sg = (row.get('symmetry') or {}).get('symbol')
        out.append((row.get('energy_above_hull'), row.get('material_id'),
                    row.get('formula_pretty'), sg, row.get('nsites')))
    return sorted(out)


for label, f in {
    'Rutile (TiO2)': 'TiO2',
    'Corundum (Al2O3)': 'Al2O3',
    'Diopside (CaMgSi2O6)': 'CaMgSi2O6',
    'Spodumene (LiAlSi2O6)': 'LiAlSi2O6',
    'Orthoclase (KAlSi3O8)': 'KAlSi3O8',
    'Mullite (Al6Si2O13)': 'Al6Si2O13',
    'Mullite alt (Al4.6Si1.4O9.7)': 'Al43Si13O93',
    'Brucite (MgH2O2)': 'MgH2O2',
    'Dolomite (CaMgC2O6)': 'CaMgC2O6',
    'alpha-Quartz SiO2 (P3121/P3221)': 'SiO2',
}.items():
    print('== %s' % label)
    try:
        for r in q(f):
            print('   %.4f %-14s %-12s %-18s %s' % (r[0], r[1], r[2], r[3], r[4]))
    except Exception as e:
        print('   ERR', e)
    print()