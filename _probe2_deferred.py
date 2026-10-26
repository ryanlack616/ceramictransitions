#!/usr/bin/env python3
"""Probe MP for the 8 deferred additions (Open Operational Threads #2):
Y2O3, YAG, HfSiO4, Tridymite, Celsian, VC, Mo2C, 6H-SiC."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)

API_KEY = os.environ.get('MP_API_KEY') or sys.exit('no MP_API_KEY')
FIELDS = 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'


def search(formula, limit=10):
    params = {'formula': formula, '_fields': FIELDS, '_limit': limit}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API_KEY, 'Accept': 'application/json',
                                               'User-Agent': 'ceramictransitions-mp-probe/0.1'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
    except Exception as e:
        return [('ERR', str(e))]
    rows = body.get('data') or []
    out = []
    for r in rows:
        sg = r.get('symmetry') or {}
        out.append((r.get('energy_above_hull'), r.get('material_id'), r.get('formula_pretty'),
                    sg.get('symbol'), r.get('nsites')))
    return sorted(out)[:limit]


for label, formulas in {
    'Yttria (Y2O3)': ['Y2O3'],
    'YAG (Y3Al5O12)': ['Y3Al5O12'],
    'Hafnon (HfSiO4)': ['HfSiO4'],
    'Tridymite (SiO2)': ['SiO2'],
    'Celsian (BaAl2Si2O8)': ['BaAl2Si2O8'],
    'VC (Vanadium Carbide)': ['VC'],
    'Mo2C (Molybdenum Carbide)': ['Mo2C'],
    '6H-SiC': ['SiC'],
}.items():
    print('== %s' % label)
    seen = set()
    for f in formulas:
        for r in search(f):
            if r[1] not in seen:
                seen.add(r[1])
                print('   %-14s %-14s %-16s %-5s %.4f' % (r[1], r[2], r[3], r[4], r[0]))
    print()