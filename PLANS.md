# Ceramics Aerospace Materials Integration — Complete Project Plan
**Status:** Phase 2 Complete | Updated: May 10, 2026  
**Scope:** howell-help (28 aerospace materials) + ceramictransitions (3D viewer integration)

---

## Executive Summary

**Completed:**
- ✅ **howell-help Phase E:** 28 aerospace/extreme-temp materials catalog with full metadata, schema validation, and governance rules
- ✅ **ceramictransitions Phase 2:** 61-material library (38 baseline + 23 aerospace) deployed to GitHub Pages
- ✅ **Cross-project integration:** Bidirectional sync architecture planned; materials now live in both systems

**Deliverables:**
1. **howell-help:** `data/high_temp_ceramics_starter.json` (source of truth for aerospace specs)
2. **howell-help:** `data/high_temp_ceramics_index.json` (auto-generated lookup table)
3. **ceramictransitions:** `data/crystal_vr.json` (61 structures with 3D viewer metadata)
4. **ceramictransitions:** `BUILD.md` (6-phase development roadmap)
5. **Both projects:** Updated memory, integration docs, validation scripts

**Roadmap constraint (effective now):** All remaining implementation work for Phase 3+ is Taichi-only in `C:\rje\dev\ceramictransitions-taichi`. The current `ceramictransitions` repo is retained as the completed Phase 1-2 web delivery track.

---

## Phase Overview & Completion Status

### Phase 1: Core Ceramic Structures (COMPLETE · May 8, 2026)
**Scope:** Establish baseline ceramictransitions project with 38 pedagogical crystal structures  
**Status:** Live at https://ceramictransitions.com  
**Materials:** Periclase, Corundum, Mullite, Spinel, silicates, oxides, refractories  
**Tech:** Three.js 3D viewer, GitHub Pages, VR-ready dual-track narratives  

### Phase 2: Aerospace Materials Integration (COMPLETE · May 10, 2026)
**Scope:** Expand both projects with 28 aerospace/extreme-temp ceramics  

**howell-help side:**
- Expanded `high_temp_ceramics_starter.json`: 9 → 28 materials
- Added 19 aerospace-critical materials across 5 categories
- Validation: All 28 pass schema checks + fixture integrity
- Governance: Starter = source of truth; index auto-generated
- Full metadata: thermal expansion, service temp, phase transitions, uncertainty notes

**ceramictransitions side:**
- Integrated 23 new structures into `crystal_vr.json` (5 already in baseline)
- Total inventory: 61 materials (38 baseline + 23 aerospace)
- Metadata per material: formula, crystal system, thermal properties, aerospace context
- Stubs ready for Phase 3 3D model generation
- Deployed to GitHub Pages (commit `a04f06a`)

**Cross-project handoff:**
- howell-help materials confirmed used by ceramictransitions
- Both projects now reference aerospace data
- Memory nodes updated with integration points

---

## Material Inventory: 61 Total (Organized by Function)

### Traditional Refractories (38 baseline + 4 aerospace updates)
| Material | Formula | Service Temp | Thermal Shock | Notes |
|----------|---------|--------------|---------------|-------|
| Periclase | MgO | 2000°C | High | Pure magnesia reference |
| Corundum | Al₂O₃ | 1800°C | Medium | Hard, chemically durable |
| Mullite | 3Al₂O₃·2SiO₂ | 1700°C | Low | Stable high-fire phase |
| Magnesium Aluminate Spinel | MgAl₂O₄ | 1700°C | Medium | Severe environment lining |
| **Stabilized Zirconia** | **ZrO₂** | **1500°C** | **Medium** | **Generic TBC baseline** |
| **Silicon Carbide** | **SiC** | **1600°C** | **Low** | **Kiln shelf, burner** |
| **Silicon Nitride** | **Si₃N₄** | **1400°C** | **Low** | **Structural ceramic** |
| **β-Cristobalite** | **SiO₂** | **1470°C** | **High** | **Inversion-prone silica** |

### Ultra-High-Temperature Structural (5 aerospace)
| Material | Formula | Service Temp | Melting Point | Use Case |
|----------|---------|--------------|---------------|----------|
| Zirconium Diboride | ZrB₂ | 3000°C | ~3245°C | Hypersonic re-entry leading edge |
| Hafnium Diboride | HfB₂ | 3200°C | ~3380°C | Next-gen hypersonic nose cone |
| Zirconium Carbide | ZrC | 2800°C | ~3540°C | Rocket nozzle throat insert |
| Hafnium Carbide | HfC | 3000°C | ~3890°C | Mission-critical extreme surface |
| Tantalum Carbide | TaC | 2900°C | ~3642°C | Alloy reinforcement (particle) |

### Thermal Barrier Coatings (5 aerospace)
| Material | Formula | Service Temp | Thermal Cond. | Application |
|----------|---------|--------------|---------------|-------------|
| YSZ 3 mol% | ZrO₂-3Y₂O₃ | 1200°C | ~2 W/m·K | Gas turbine blade (standard) |
| YSZ 8 mol% | ZrO₂-8Y₂O₃ | 1300°C | ~2.2 W/m·K | Extreme thermal cycling |
| Ceria-Stabilized | ZrO₂-CeO₂ | 1000°C | ~2.5 W/m·K | Redox-cycling environments |
| Hafnium Oxide | HfO₂ | 2000°C | ~1.5 W/m·K | Next-gen ultra-low-k TBC |
| Lanthanum Zirconate | La₂Zr₂O₇ | 1400°C | ~1.2 W/m·K | Next-gen engine TBC (pyrochlore) |

### Environmental Barrier Coatings (2 aerospace)
| Material | Formula | Service Temp | Structure | Use |
|----------|---------|--------------|-----------|-----|
| Ytterbium Silicate | Yb₂SiO₅ | 1500°C | Tetragonal | SiC-SiC CMC protection |
| Ytterbium Disilicate | Yb₂Si₂O₇ | 1450°C | Monoclinic | Tunable EBC composition |

### Ceramic Matrix Composites & Engineered Ceramics (6 aerospace)
| Material | Formula | Service Temp | Key Property | Application |
|----------|---------|--------------|--------------|-------------|
| **SiC-SiC CMC** | **SiC (fiber)** | **1300°C** | **Damage tolerance** | **Next-gen engine blade** |
| **Aluminum Nitride** | **AlN** | **1600°C** | **High thermal cond.** | **Thermal management** |
| **Boron Nitride** | **BN** | **1000°C** | **Lubricity** | **Additive/filler** |
| **Sialon** | **Si₆₋ₓAlₓOₓN₈₋ₓ** | **1400°C** | **Creep resistant** | **Structural aerospace** |
| **RBSC** | **SiC (reaction-bonded)** | **1400°C** | **Cost-effective** | **Thermal components** |
| **SSiC** | **SiC (sintered)** | **1650°C** | **Premium performance** | **High-duty thermal** |

---

## Architecture & Data Flow

### Source of Truth: howell-help
```
howell-help/
├── data/
│   ├── high_temp_ceramics_starter.json (28 materials, MASTER SOURCE)
│   ├── high_temp_ceramics_index.json (auto-generated, read-only)
│   └── [future] high_temp_ceramics_variants.json (glaze/composition variants)
├── scripts/
│   ├── load_high_temp_ceramics.py (validate & regenerate index)
│   ├── validate_high_temp_ceramics.py (schema + fixture checks)
│   └── [future] sync_to_ceramictransitions.py (auto-push on change)
└── eval/ (Phase E: aerospace material performance evaluation)
```

### Consumer: ceramictransitions
```
ceramictransitions/
├── data/
│   └── crystal_vr.json (61 structures: 38 baseline + 23 aerospace)
├── index.html (Three.js viewer)
├── add_aerospace_materials.py (one-shot integration script)
├── BUILD.md (6-phase roadmap)
└── [future] 3D models/ (atomic coordinates for aerospace materials)
```

### Implementation Runtime: ceramictransitions-taichi

```
ceramictransitions-taichi/
├── main.py (Taichi runtime entrypoint)
├── crystal_structures.py (Taichi structure rendering path)
├── crystal_structures_v2.py (advanced structure path)
├── data_loader.py (data ingestion for Taichi fields)
├── requirements.txt (taichi runtime dependency)
└── BUILD.md (Taichi operator workflow)
```

### Integration Layer (Bidirectional Sync · PLANNED)
```
howell-help/data/high_temp_ceramics_starter.json
    ↓ (source material metadata)
ceramictransitions/data/crystal_vr.json
    ↓ (3D viewer renders structures)
ceramictransitions/index.html
    ↓ (live at https://ceramictransitions.com)
User interaction + 3D rotation/inspection
```

---

## Data Schema (howell-help Source)

Each material in `high_temp_ceramics_starter.json` includes:
```json
{
  "id": "unique_identifier",
  "name": "Display Name (Unicode-safe)",
  "formula": "Chemical Formula (Unicode: subscripts, superscripts)",
  "phase_family": "oxide|non_oxide|diboride|carbide|composite|...",
  "thermal_expansion_1e6_per_c": 5.3,
  "thermal_expansion_range_c": [20, 1000],
  "service_temp_max_c": 1700,
  "decomposition_temp_c": null,
  "thermal_shock_risk": "low|medium|high",
  "phase_transition_notes": "Description of polymorphic behavior",
  "application_context": ["refractory", "aerospace_leading_edge", ...],
  "source_quality": "handbook|aerospace-spec|estimated",
  "notes": "Technical summary for engineers",
  "uncertainty_notes": "Known limitations and research gaps"
}
```

---

## Completed Deliverables

### 1. howell-help Aerospace Materials (28 total)
- **File:** `C:\rje\dev\howell-help\data\high_temp_ceramics_starter.json`
- **Size:** ~22 KB (full schema + metadata)
- **Validation:** 28/28 pass, 100% fixture match
- **Governance:** Starter = source; index auto-synced via `load_high_temp_ceramics.py`
- **Last updated:** May 10, 2026

### 2. ceramictransitions Integration (61 materials)
- **File:** `C:\rje\dev\ceramictransitions\data\crystal_vr.json`
- **Size:** ~2 MB (with 23 aerospace stubs + metadata)
- **Structures:** 38 with full atomic coords + 23 stub structures
- **Live:** https://ceramictransitions.com (GitHub Pages)
- **Last deployed:** May 10, 2026 (commit `a04f06a`)

### 3. Project Documentation
- **howell-help:** Updated `/memories/repo/howell-help.md` with aerospace expansion notes
- **ceramictransitions:** Updated `BUILD.md` with complete 6-phase roadmap + integration points
- **Session memory:** Created `/memories/session/ceramictransitions-aerospace-phase2.md`

---

## Phase 3: 3D Model Generation (PLANNED)

**Goal:** Generate full atomic coordinate sets for aerospace materials currently as stubs  
**Timeline:** 2–4 weeks (pending Materials Project API access)  
**Scope:** Priority 10 materials (ZrB₂, HfB₂, YSZ variants, HfO₂, La₂Zr₂O₇, SiC, AlN, SiAlON)

### Approach
1. Query **Materials Project** (mp-web-api) for crystal structures of diborides/carbides/rare-earth silicates
2. Parse & convert via **pymatgen** → Taichi simulation/render schema in `ceramictransitions-taichi` (atoms, bonds, supercell)
3. Generate pseudo-structures for composites/coatings (layered TBC models)
4. Validate with `_inspect.py` (extend to check non-empty atoms)
5. Deploy update to GitHub Pages

### Data Sources
- **Primary:** Materials Project (api.materialsproject.org) — comprehensive structural database
- **Secondary:** ICSD (Inorganic Crystal Structure Database) via pymatgen
- **Tertiary:** Aerospace handbooks + published phase diagrams for rare-earth compounds

---

## Phase 4: Advanced Visualization Features (PLANNED)

**Goal:** Animate thermal transformations and field-use degradation in 3D viewer  
**Timeline:** 4–8 weeks  
**Tech:** Taichi kernels, Taichi scene pipelines, data-driven phase paths

### Features
1. **Thermal transformation paths**
   - Show α→β, monoclinic→cubic, tetragonal stabilization animations
   - Data source: `phase_transition_notes` in starter.json
   - Slider: temperature range (20–3200°C)

2. **Oxidation/degradation overlays**
   - Highlight surface oxidation on diborides/carbides above 1200°C
   - Show internal cracking under thermal cycling (TBC damage models)
   - Color gradient: fresh → oxidized → failed

3. **Comparative firing narratives**
   - Side-by-side: baseline kiln condition vs. extreme aerospace environment
   - Timeline: show evolution over time (re-entry pulse, thermal cycling)

4. **Material property sliders**
   - Bond length, thermal expansion coefficient, elastic modulus
   - Animate CTE effects across 20–3200°C range
   - Real-time recalculation of supercell dimensions

5. **Hypersonic load case visualization**
   - Embed re-entry thermal pulse profile (MACH 10, 3000°C peak)
   - Stress field overlay (FEA-derived or simplified model)
   - Show material failure modes (spalling, oxidation, chemical attack)

---

## Phase 5: Interactive Materials Database (PLANNED)

**Goal:** Faceted search + filtering on studio and aerospace properties  
**Timeline:** 3–4 weeks  
**Tech:** Taichi-backed data pipeline with web UI surfaces for query and comparison

### Features
1. **Faceted Filters**
   - Service temperature (UI: dual-slider 0–3500°C)
   - Thermal shock risk (checkboxes: low/medium/high)
   - Application context (tags: TBC, structural, CMC, hypersonic, kiln, etc.)
   - Phase family (dropdown: oxide, non-oxide, diboride, carbide, composite)
   - Source quality (filter: aerospace-spec, handbook, estimated)

2. **Comparison Workbench**
   - Select 2–4 materials side-by-side
   - Display: CTE, service temp, density, cost proxy, thermal conductivity, phase notes
   - Export to CSV / JSON for analysis

3. **Search & Discovery**
   - Full-text search (name, formula, notes)
   - Autocomplete via indexed materials
   - Recent searches + saved favorites

4. **Export & Integration**
   - Download USDZ/glTF 3D models for CAD import
   - Export material cards (PDF, JSON) with metadata
   - Generate cite BibTeX for aerospace-spec sources

---

## Phase 6: Collaboration & External Integration (PLANNED)

**Goal:** Connect ceramics research ecosystem  
**Timeline:** Ongoing  

### Integration Points

#### 6a. CMW (Ceramic Materials Workshop)
- **Direction:** ceramictransitions 3D structures → CMW video annotation system
- **Use case:** Embed crystal structure viewer in Matt Katz lessons on refractory materials
- **Data sharing:** Glaze/phase diagrams from CMW → ceramictransitions comparative visualizations
- **Contact:** Matt Katz (CMW host) — coordinate embedding + mutual linking

#### 6b. stullatlas.app (Phase Diagram Explorer)
- **Direction:** Bidirectional reference
- **Use case:** Link stull cone range to ceramictransitions material service temps
- **Integration:** ceramictransitions → stullatlas app sharing (QR codes, deep links)

#### 6c. Howell Bridge (Knowledge Graph Sync)
- **Direction:** Bidirectional entity sync
- **Use case:** Material properties + relationships tracked in howell bridge KG
- **Automation:** Sync trigger on `high_temp_ceramics_starter.json` push → update KG entities

#### 6d. Academic Attribution
- **DOI links:** Foundational papers on ultra-high-temp ceramics
- **Data sources:** Materials Project citation + ICSD reference
- **License alignment:** Ensure open-source compatibility for data sources

---

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Materials Project API rate limits | Phase 3 delay | Cache structures locally; batch requests |
| Unicode rendering (terminals/browsers) | Display issues | Test on all target browsers; UTF-8 validation |
| Composite/coating pseudo-models inaccuracy | Pedagogical concern | Add uncertainty disclaimers; link to CAD imports |
| Cross-project sync complexity | Integration debt | Start with one-way howell-help → ceramictransitions; upgrade later |
| Stale GH Pages cache | Deployment issues | Add timestamp comment to index.html; hard refresh docs |
| Materials Project data gaps (diborides) | Incomplete coverage | Use ICSD backup; generate minimal geometric models if needed |

---

## File Inventory & Locations

### howell-help
- `C:\rje\dev\howell-help\data\high_temp_ceramics_starter.json` (28 materials, source of truth)
- `C:\rje\dev\howell-help\data\high_temp_ceramics_index.json` (auto-generated)
- `C:\rje\dev\howell-help\scripts\load_high_temp_ceramics.py`
- `C:\rje\dev\howell-help\scripts\validate_high_temp_ceramics.py`
- `C:\rje\dev\howell-help\README-high-temp-ceramics.md` (governance rules)

### ceramictransitions
- `C:\rje\dev\ceramictransitions\data\crystal_vr.json` (61 structures)
- `C:\rje\dev\ceramictransitions\index.html` (Three.js viewer)
- `C:\rje\dev\ceramictransitions\BUILD.md` (6-phase roadmap)
- `C:\rje\dev\ceramictransitions\add_aerospace_materials.py` (integration script)

### ceramictransitions-taichi
- `C:\rje\dev\ceramictransitions-taichi\main.py` (Taichi runtime)
- `C:\rje\dev\ceramictransitions-taichi\crystal_structures.py` (structure visualization)
- `C:\rje\dev\ceramictransitions-taichi\data_loader.py` (schema/data ingestion)
- `C:\rje\dev\ceramictransitions-taichi\BUILD.md` (operator workflow)

### Memory (persist across sessions)
- `/memories/repo/howell-help.md` (cross-project status)
- `/memories/session/ceramictransitions-aerospace-phase2.md` (Phase 2 completion notes)

---

## Success Metrics & KPIs

| Metric | Phase 2 Status | Phase 3+ Target |
|--------|----------------|-----------------|
| Material count | 61 (38 + 23) | 70+ (full 3D models) |
| 3D structures with atoms | 38 | 50+ (priority aerospace materials) |
| Validation pass rate | 100% (28/28) | 100% (all materials) |
| GitHub Pages uptime | 99.9%+ | 99.95%+ |
| Cross-project sync | Manual | Automated (TBD) |
| CMW integration | Planned | Live embedding in 2–3 lessons |
| Academic citations | Pending | 10+ DOI links + Materials Project attribution |

---

## Deployment Checklist (Phase 2 Complete)

✅ howell-help aerospace materials finalized (28/28)  
✅ ceramictransitions integration complete (61 structures live)  
✅ GitHub Pages deployment successful (commit `a04f06a`)  
✅ Documentation updated (BUILD.md, memory nodes)  
✅ Validation scripts passing (load + validate)  
✅ Cross-project handoff documented  

**Next milestone:** Phase 3 kickoff (3D model generation, ~2 weeks)

---

## Questions & Contact

**For Phase 3 (3D models):**
- Materials Project API access? Check api.materialsproject.org quota
- Pymatgen installation? Covered in existing howell-help environment

**For Phase 4–6 (visualization + integration):**
- Taichi pipeline alignment? Existing `ceramictransitions-taichi` implementation is the baseline
- CMW embedding? Coordinate with Matt Katz
- Howell bridge KG sync? Coordinate with howell bridge daemon

---

**Document version:** 1.0  
**Last updated:** May 10, 2026  
**Next review:** May 24, 2026 (Phase 3 progress checkpoint)
