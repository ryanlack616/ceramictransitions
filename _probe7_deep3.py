#!/usr/bin/env python3
"""Wide re-probe: (1) the 4 keep-natives deserve one generous re-check
(corundum/rutile absence from MP is suspicious); (2) probe the on-thesis
additions: 4H-SiC, Ti2AlN, SrHfO3, CaHfO3, La2Hf2O7, Gd2Hf2O7, NbN."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API = os.environ.get('MP_API_KEY') or sys.exit('no key')


def q(f, limit=60):
    params = {'formula': f, '_limit': limit,
              '_fields': 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'}
    url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-API-KEY': API, 'Accept': 'application/json',
                                               'User-Agent': 'probe'})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = json.loads(r.read())
    rows = body.get('data') or []
    out = []
    for row in sorted(rows, key=lambda x: x.get('energy_above_hull', 9e9)):
        sg = (row.get('symmetry') or {}).get('symbol')
        out.append((row.get('energy_above_hull'), row.get('material_id'),
                    row.get('formula_pretty'), sg, row.get('nsites')))
    return out


def show(label, rows, filt=None, mx=18):
    print('== %s' % label)
    n = 0
    for r in rows:
        if filt and not filt(r):
            continue
        print('   %.4f %-14s %-12s %-16s %s' % (r[0], r[1], r[2], r[3], r[4]))
        n += 1
        if n >= mx:
            break
    print()


# 1. keep-natives re-check (all rows, filtered)
show('Al2O3 (want R-3c / R-3m corundum)', q('Al2O3', 80),
     lambda r: 'R-3' in str(r[3]) or 'C2/m' in str(r[3]) or 'P22' in str(r[3]) or 'R3C' in str(r[3]))
show('TiO2 (want P42/mnm rutile)', q('TiO2', 80), lambda r: 'P4' in str(r[3]))
show('SiO2 (want P3121/P3221 low-quartz)', q('SiO2', 80), lambda r: 'P3' in str(r[3]) or 'P6' in str(r[3]))
show('Mullite Al6Si2O13 (wider)', q('Al6Si2O13', 80))
show('Mullite alt formulas', q('Al5O13Si', 40))

# 2. on-thesis additions
for label, f in {
    '4H-SiC': 'SiC',
    'Ti2AlN': 'Ti2AlN',
    'SrHfO3': 'SrHfO3',
    'CaHfO3': 'CaHfO3',
    'La2Hf2O7': 'La2Hf2O7',
    'Gd2Hf2O7': 'Gd2Hf2O7',
    'NbN': 'NbN',
    'TaN': 'TaN',
}.items():
    rows = q(f)
    # filter to the right composition quickly
    comp = {}
    for el, n in __import__('re').findall(r"([A-Z][a-z]?)([0-9.]*)", f):
        comp[el] = comp.get(el, 0) + (float(n) if n else 1)
    def ck(r, _c=comp):
        import re
        cc = {}
        for el, n in re.findall(r"([A-Z][a-z]?)([0-9.]*)", r[2] or ''):
            cc[el] = cc.get(el, 0) + (float(n) if n else 1)
        return cc == _c and r[0] < 0.25
    filtered = [r for r in rows if ck(r)][:8]
    if not filtered:
        filtered = [r for r in rows if ck(r)][:8]
    print('== %s' % label)
    for r in (filtered or rows[:6]):
        print('   %.4f %-14s %-12s %-16s %s' % (r[0], r[1], r[2], r[3], r[4]))
    print()