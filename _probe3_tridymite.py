#!/usr/bin/env python3
"""Probe MP specifically for genuine tridymite polytypes (Deer et al. 2004):
OC C2221, OP P212121, MC Cc, MX C1, HP P63/mmm, LHP P6322.
Earlier top-10-by-ehull SiO2 search missed them (tridymite sits at higher
ehull — metastable vs quartz). Search wide, filter by space group."""
import json, os, sys, urllib.parse, urllib.request

for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
    line = line.strip()
    if line and '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k, v)
API_KEY = os.environ.get('MP_API_KEY') or sys.exit('no MP_API_KEY')
FIELDS = 'material_id,formula_pretty,nsites,energy_above_hull,symmetry'

WANT = {'C2221', 'P212121', 'P2(1)2(1)2(1)', 'Cc', 'C1', 'P63/mcm', 'P63/mmc',
        'P63/mmm', 'P6322', 'P6(3)22', 'P63', 'P6_3/m', 'C1h'}

params = {'formula': 'SiO2', '_fields': FIELDS, '_limit': 80}
url = 'https://api.materialsproject.org/materials/summary/?' + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={'X-API-KEY': API_KEY, 'Accept': 'application/json',
                                           'User-Agent': 'ceramictransitions-mp-probe/0.1'})
with urllib.request.urlopen(req, timeout=90) as r:
    body = json.loads(r.read())
rows = body.get('data') or []
hits = []
print('tridymite-relevant space groups in MP (SiO2), %d phases searched:' % len(rows))
for r in sorted(rows, key=lambda x: x.get('energy_above_hull', 9e9)):
    sg = (r.get('symmetry') or {}).get('symbol')
    short = (sg or '').replace('_', '').replace(' ', '').replace('(', '').replace(')', '')
    if sg in WANT or short in {w.replace('_', '').replace('(', '').replace(')', '') for w in WANT}:
        hits.append((r.get('energy_above_hull'), r.get('material_id'), r.get('formula_pretty'), sg, r.get('nsites')))
for h in sorted(hits):
    print('   %.4f  %-14s %-8s %-16s %s' % (h[0], h[1], h[2], h[3], h[4]))
if not hits:
    print('   (none — MP has no phase in the Deer-2004 tridymite space groups)')
print()
print('all SiO2 space groups present (>0.02 eV above hull, excluding quartz/cristobalite):')
seen = {}
for r in rows:
    sg = (r.get('symmetry') or {}).get('symbol')
    e = r.get('energy_above_hull')
    if e and e > 0.02 and sg not in ('P3121', 'P3221', 'P41212', 'P6222', 'P4332', 'P4132', 'Fm-3m'):
        seen.setdefault(sg, (e, r.get('material_id'), r.get('nsites')))
for sg in sorted(seen):
    e, mid, n = seen[sg]
    print('   %.4f  %-14s %-16s %s' % (e, mid, sg, n))