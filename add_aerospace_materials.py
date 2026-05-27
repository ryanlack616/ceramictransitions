#!/usr/bin/env python3
"""
Add 28 aerospace/high-temp ceramics to crystal_vr.json from howell-help starter data.
Stub structures without atoms/bonds (viewer will handle gracefully).
"""
import json
from pathlib import Path

# Read the howell-help aerospace materials
howell_starter = json.load(open(r'C:\rje\dev\howell-help\data\high_temp_ceramics_starter.json', encoding='utf-8'))

# Read current crystal_vr.json
crystal_file = Path('data/crystal_vr.json')
vr_data = json.load(open(crystal_file, encoding='utf-8'))

# Build a map of existing structures by (name, formula) — keyed both ways so
# that aliases (e.g. howell "Beta-Cristobalite" vs baseline "β-Cristobalite")
# round-trip safely and we never re-append a material that's already present.
existing_names = {s['name'] for s in vr_data['structures']}
existing_keys = {(s['name'], s.get('formula', '')) for s in vr_data['structures']}

# Map howell materials to crystal structure info
# Some materials already exist (Corundum, Periclase, Mullite, Spinel, Zircon variants)
material_specs = {
    'alpha_quartz': {
        'name': 'α-Quartz',
        'formula': 'SiO₂',
        'system': 'Trigonal P3₂21',
        'info': [
            'Silicon dioxide, low-temperature polymorph',
            'a=4.913 c=5.405 Angstrom',
            'Thermal expansion anisotropic; α→β inversion at 573°C',
            'Highly thermal-shock-prone in kilns'
        ]
    },
    'beta_cristobalite': {
        'name': 'β-Cristobalite',
        'formula': 'SiO₂',
        'system': 'Cubic Fd-3m',
        'info': [
            'High-temperature SiO₂ polymorph',
            'a≈7.1 Angstrom (above 1470°C)',
            'β→α inversion on cooling causes severe thermal shock',
            'Used in low-expansion refractories when stabilized'
        ]
    },
    'zrb2': {
        'name': 'Zirconium Diboride',
        'formula': 'ZrB₂',
        'system': 'Hexagonal P6/mmm',
        'info': [
            'Ultra-high-temperature refractory ceramic',
            'Service temperature up to 3000°C',
            'Melting point ~3245°C; thermal conductivity ~80 W/m·K',
            'Leading-edge material for hypersonic re-entry vehicles; requires oxidation protection'
        ]
    },
    'hfb2': {
        'name': 'Hafnium Diboride',
        'formula': 'HfB₂',
        'system': 'Hexagonal P6/mmm',
        'info': [
            'Next-generation ultra-high-temp refractory',
            'Service temperature up to 3200°C',
            'Melting point ~3380°C; higher thermal stability than ZrB₂',
            'Density ~12.5 g/cm³; extreme material for hypersonic nose cones'
        ]
    },
    'zrc': {
        'name': 'Zirconium Carbide',
        'formula': 'ZrC',
        'system': 'Cubic Fm-3m (NaCl-type)',
        'info': [
            'Ultra-high-temperature refractory carbide',
            'Service temperature up to 2800°C; melting point ~3540°C',
            'High thermal conductivity (~25 W/m·K) useful for heat transfer',
            'Lower oxidation resistance than diborides; used in internal engine components'
        ]
    },
    'hfc': {
        'name': 'Hafnium Carbide',
        'formula': 'HfC',
        'system': 'Cubic Fm-3m (NaCl-type)',
        'info': [
            'Most refractory ceramic material known',
            'Melting point ~3890°C; service up to 3000°C',
            'Extremely expensive and brittle; reserve for mission-critical surfaces',
            'Used in rocket engine throat inserts and extreme hypersonic applications'
        ]
    },
    'tac': {
        'name': 'Tantalum Carbide',
        'formula': 'TaC',
        'system': 'Cubic Fm-3m (NaCl-type)',
        'info': [
            'Refractory carbide ceramic',
            'Service temperature up to 2900°C',
            'Often used as particle reinforcement in ultra-high-temp metal alloys',
            'High hardness and thermal stability in extreme aerospace environments'
        ]
    },
    'ysz_3mol': {
        'name': 'Yttria-Stabilized Zirconia (3 mol% Y₂O₃)',
        'formula': 'ZrO₂-3Y₂O₃',
        'system': 'Tetragonal P4₂/nmc',
        'info': [
            'Industry-standard thermal barrier coating (TBC)',
            'Service temperature ~1200°C in jet engines',
            'Tetragonal → monoclinic transformation risk on cooling',
            'Excellent insulation (low thermal conductivity ~2 W/m·K) for gas turbine blades'
        ]
    },
    'ysz_8mol': {
        'name': 'Yttria-Stabilized Zirconia (8 mol% Y₂O₃)',
        'formula': 'ZrO₂-8Y₂O₃',
        'system': 'Cubic Fm-3m',
        'info': [
            'Cubic-stabilized thermal barrier coating',
            'Service temperature up to 1300°C with minimal phase transition',
            'Superior cyclic thermal performance vs 3YSZ',
            'Higher yttria content eliminates damaging tetragonal transformation'
        ]
    },
    'csz': {
        'name': 'Ceria-Stabilized Zirconia',
        'formula': 'ZrO₂-CeO₂',
        'system': 'Cubic Fm-3m',
        'info': [
            'Alternative thermal barrier coating stabilizer',
            'Service temperature ~1000°C; cubic phase stable',
            'Less common than YSZ; useful for redox-cycling environments',
            'CeO₂ can undergo oxygen loss/gain affecting mechanical properties'
        ]
    },
    'hfo2': {
        'name': 'Hafnium Oxide',
        'formula': 'HfO₂',
        'system': 'Monoclinic P2₁/c',
        'info': [
            'Next-generation thermal barrier coating material',
            'Service temperature up to 2000°C; superior to YSZ',
            'Lower thermal conductivity (~1.5 W/m·K) provides better insulation',
            'Monoclinic → tetragonal transition near 1770°C; higher refractive index'
        ]
    },
    'la2zr2o7': {
        'name': 'Lanthanum Zirconate',
        'formula': 'La₂Zr₂O₇',
        'system': 'Cubic Fd-3m (pyrochlore)',
        'info': [
            'Next-generation TBC for advanced engines',
            'Service temperature up to 1400°C',
            'Excellent phase stability; minimal thermal shock risk',
            'Lower thermal conductivity and superior high-temp performance vs YSZ'
        ]
    },
    'yb2sio5': {
        'name': 'Ytterbium Silicate',
        'formula': 'Yb₂SiO₅',
        'system': 'Tetragonal I4₁/amd',
        'info': [
            'Environmental barrier coating for SiC-SiC composites',
            'Service temperature up to 1500°C',
            'Excellent oxidation and hydration resistance',
            'Critical for protecting CMC matrices in hypersonic flight environments'
        ]
    },
    'yb2si2o7': {
        'name': 'Ytterbium Disilicate',
        'formula': 'Yb₂Si₂O₇',
        'system': 'Monoclinic C2/c',
        'info': [
            'Environmental barrier coating variant',
            'Service temperature up to 1450°C',
            'Tunable composition for optimizing EBC performance',
            'Silicate structure provides excellent thermal shock resistance'
        ]
    },
    'sic_sic_cmc': {
        'name': 'SiC-SiC Ceramic Matrix Composite',
        'formula': 'SiC (fiber-reinforced)',
        'system': 'Composite (hexagonal fiber + matrix)',
        'info': [
            'Game-changing composite for aerospace propulsion',
            'Service temperature up to 1300°C in next-gen engines',
            'Low density combined with high strength and fracture toughness',
            'Combines SiC fibers with SiC matrix; fiber coatings enable crack bridging'
        ]
    },
    'aln': {
        'name': 'Aluminum Nitride',
        'formula': 'AlN',
        'system': 'Hexagonal P6₃mc',
        'info': [
            'High thermal conductivity ceramic',
            'Service temperature up to 1600°C',
            'Excellent thermal conductivity (~180 W/m·K) + electrical insulation',
            'Used in thermal management and structural aerospace applications'
        ]
    },
    'bn_hexagonal': {
        'name': 'Boron Nitride (Hexagonal)',
        'formula': 'BN',
        'system': 'Hexagonal P6₃/mmc',
        'info': [
            'Graphite-like layered structure',
            'Service temperature limited to ~1000°C (oxidation)',
            'Often used as filler or lubricant additive in composites',
            'Excellent lubricity and thermal insulation'
        ]
    },
    'sialon': {
        'name': 'Sialon',
        'formula': 'Si₆₋ₓAlₓOₓN₈₋ₓ',
        'system': 'Hexagonal or orthorhombic (composition-dependent)',
        'info': [
            'Silicon-aluminum oxynitride ceramic alloy',
            'Service temperature up to 1400°C',
            'High strength and creep resistance at temperature',
            'Used in structural aerospace and high-speed machining applications'
        ]
    },
    'rbsc': {
        'name': 'Reaction-Bonded Silicon Carbide',
        'formula': 'SiC (reaction-bonded)',
        'system': 'Hexagonal 6H or 4H SiC + residual Si',
        'info': [
            'Cost-effective high-performance ceramic',
            'Service temperature up to 1400°C',
            'Two-phase structure (SiC + residual Si); residual Si oxidizes above 1400°C',
            'Sintering-less consolidation via reactive infiltration'
        ]
    },
    'sic_sintered': {
        'name': 'Sintered Silicon Carbide',
        'formula': 'SiC',
        'system': 'Hexagonal 6H or 4H SiC',
        'info': [
            'Premium high-performance ceramic',
            'Service temperature up to 1650°C',
            'Fully dense SiC; no residual metal phase',
            'Highest thermal properties; used in kiln shelves and thermal-structural components'
        ]
    },
    'si3n4_sintered': {
        'name': 'Sintered Silicon Nitride',
        'formula': 'Si₃N₄',
        'system': 'Hexagonal α-Si₃N₄ (majority) + β-Si₃N₄',
        'info': [
            'Excellent high-temperature structural ceramic',
            'Service temperature up to 1500°C',
            'Outstanding creep resistance and thermal fatigue strength',
            'Used in advanced engine components and hypersonic vehicle structures'
        ]
    },
}

# Structures already in crystal_vr.json that we can skip (already present)
skip_materials = {'alpha_quartz', 'corundum', 'mullite', 'periclase', 'spinel_mgal2o4'}

# Create new structure entries (stub format without atoms/bonds for now)
new_structures = []

for mat_data in howell_starter['materials']:
    howell_id = mat_data['id']
    
    # Skip if already in crystal_vr or already handled.
    # Check both the howell name AND the spec-resolved name, since specs
    # canonicalize formulas (e.g. "Beta-Cristobalite" → "β-Cristobalite").
    spec_name = material_specs.get(howell_id, {}).get('name', mat_data['name'])
    spec_formula = material_specs.get(howell_id, {}).get('formula', mat_data.get('formula', ''))
    if (mat_data['name'] in existing_names
            or spec_name in existing_names
            or (spec_name, spec_formula) in existing_keys
            or howell_id in skip_materials):
        print(f"  Skip: {mat_data['name']} (already in crystal_vr)")
        continue
    
    # Use spec if available, otherwise build minimal entry
    if howell_id in material_specs:
        spec = material_specs[howell_id]
        new_structure = {
            'name': spec['name'],
            'formula': spec['formula'],
            'system': spec['system'],
            'info': spec['info'],
            'atoms': [],
            'bonds': [],
            'bondTypes': [],
            'cellVectors': [],
            'supercell': None,
            'stats': {
                'bondLengths': {},
                'coordDist': {}
            }
        }
    else:
        # Fallback: minimal entry from howell data
        new_structure = {
            'name': mat_data['name'],
            'formula': mat_data['formula'],
            'system': f"{mat_data['phase_family']} structure",
            'info': [
                mat_data['notes'],
                f"Service temperature: {mat_data['service_temp_max_c']}°C",
                f"Thermal expansion: {mat_data['thermal_expansion_1e6_per_c']} × 10⁻⁶/°C",
                f"Thermal shock risk: {mat_data['thermal_shock_risk']}"
            ],
            'atoms': [],
            'bonds': [],
            'bondTypes': [],
            'cellVectors': [],
            'supercell': None,
            'stats': {
                'bondLengths': {},
                'coordDist': {}
            }
        }
    
    new_structures.append(new_structure)
    print(f"  Add: {new_structure['name']} ({mat_data['formula']})")

# Append all new structures
vr_data['structures'].extend(new_structures)

# Write back
with open(crystal_file, 'w', encoding='utf-8') as f:
    json.dump(vr_data, f, indent=2, ensure_ascii=False)

print(f"\nTotal structures before: {len(vr_data['structures']) - len(new_structures)}")
print(f"New structures added: {len(new_structures)}")
print(f"Total structures after: {len(vr_data['structures'])}")
print(f"Written to: {crystal_file}")
