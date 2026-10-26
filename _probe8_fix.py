#!/usr/bin/env python3
"""Probe the still-schematic binaries (CaO, BeO, TaB2, HfN) + audit the
service==melting decomposition cases."""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
for line in open(os.path.join(HERE, '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API = os.environ.get('MP_API_KEY') or sys.exit('no key')


def q(f, limit=30):
    params = {'formula': f, '_limit': limit,
              '_fields': 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API, 'Accept': 'application/json',
                                               'User-Agent': 'probe'})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read())
    rows = body.get('data') or []
    out = []
    for row in sorted(rows, key=lambda x: x.get('energy_above_hull', 9e9))[:limit]:
        sg = (row.get('symmetry') or {}).get('symbol')
        out.append((row.get('energy_above_hull'), row.get('material_id'),
                    row.get('formula_pretty'), sg, row.get('nsites')))
    return out


for label, f in {'CaO': 'CaO', 'BeO': 'BeO', 'TaB2': 'TaB2', 'HfN': 'HfN'}.items():
    print('== %s' % label)
    for r in q(f)[:6]:
        print('   %.4f %-14s %-10s %-16s %s' % (r[0], r[1], r[2], r[3], r[4]))
    print()

print('== service==melting decomposition cases audit ==')
d = json.load(open(os.path.join(HERE, 'data', 'crystal_vr.json')))
for s in d['structures']:
    if s.get('service_temp_c') and s.get('service_temp_c') == s.get('melting_point_c') and s['name'] in (
            'Kaolinite', 'Talc', 'Brucite', 'Calcite', 'Dolomite',
            'Andalusite', 'Kyanite', 'Sillimanite', 'Spodumene', 'β-Cristobalite',
            'Wollastonite', 'Albite', 'Orthoclase', 'Anorthite', 'Nepheline', 'Leucite'):
        print('  %-14s service=mp=%-5s bound_type=%s' % (s['name'], s['service_temp_c'], s.get('bound_type')))