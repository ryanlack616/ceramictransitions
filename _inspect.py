import json
d = json.load(open(r'data/crystal_vr.json', 'r', encoding='utf-8'))
for s in d['structures']:
    name = s['name']
    na = len(s['atoms'])
    nb = len(s.get('bonds', []))
    sc = s.get('supercell', '?')
    cv = s.get('cellVectors', [])
    cvs = len(cv)
    print(f"{name:22s} atoms={na:3d} bonds={nb:3d} supercell={sc} cellVecs={cvs}")
    if cv:
        for i, v in enumerate(cv):
            print(f"  v{i}: [{v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f}]")
