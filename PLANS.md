# Ceramics Aerospace Materials Integration — Complete Project Plan
**Status:** Phase 2.5 COMPLETE | Updated: May 16, 2026  
**Scope:** howell-help (28 aerospace materials) + ceramictransitions (3D viewer integration)

---

## Executive Summary

**Completed:**
- ✅ **howell-help Phase E:** 28 aerospace/extreme-temp materials catalog with full metadata, schema validation, and governance rules
- ✅ **ceramictransitions Phase 2:** 60-material library (38 native + 17 procedural + 5 metadata-only stubs) deployed to ceramictransitions.com via pixie-sh FTP (not GitHub Pages — see deploy notes)
- ✅ **ceramictransitions Phase 2.5.1:** procedural prototype renderer (rocksalt / fluorite / zincblende / AlB₂ / wurtzite / hBN). 17 aerospace stubs now render with valid 3D atoms+bonds at runtime; renderable count 38 → 55. Promoted live May 15, 2026 (commits edf89b5 → 9b3b0dc).
- ✅ **Cross-project integration:** Bidirectional sync architecture planned; materials now live in both systems
- ✅ **Companion site:** ceramic-micros (diffusion kinetics, L1+L2 tools) cross-linked from index.html, lattice.html, transitions-graph.html

**Deliverables:**
1. **howell-help:** `data/high_temp_ceramics_starter.json` (source of truth for aerospace specs)
2. **howell-help:** `data/high_temp_ceramics_index.json` (auto-generated lookup table)
3. **ceramictransitions:** `data/crystal_vr.json` (60 structures with 3D viewer metadata, `renderableCount: 55`)
4. **ceramictransitions:** `BUILD.md` (6-phase development roadmap)
5. **ceramictransitions:** `_deploy.py` FTP deploy + `test_prototype_generators.js` (215-check smoke test)
6. **ceramictransitions:** `transitions-graph.html` (zero-dependency SVG + canvas; yFiles removed)

**Deploy mechanism:** Static FTP to pixie-sh (Porkbun). Run `python _deploy.py` after committing. The `.github/workflows/pages.yml` workflow is dormant/legacy — Pages is disabled on the repo.

**Roadmap constraint (effective now):** All remaining heavy implementation work for Phase 3+ is Taichi-only in `C:\rje\dev\ceramictransitions-taichi`. The current `ceramictransitions` repo is retained as the completed Phase 1–2.5.1 web delivery track; small UX polish (filter, mobile, error states, cross-links) is in scope here.

---

## Phase Overview & Completion Status

### Phase 1: Core Ceramic Structures (COMPLETE · May 8, 2026)
**Scope:** Establish baseline ceramictransitions project with 38 pedagogical crystal structures  
**Status:** Live at https://ceramictransitions.com  
**Materials:** Periclase, Corundum, Mullite, Spinel, silicates, oxides, refractories  
**Tech:** Three.js 3D viewer, pixie-sh static FTP, VR-ready dual-track narratives  

### Phase 2: Aerospace Materials Integration (COMPLETE · May 10, 2026)
**Scope:** Expand both projects with 28 aerospace/extreme-temp ceramics  

**howell-help side:**
- Expanded `high_temp_ceramics_starter.json`: 9 → 28 materials
- Added 19 aerospace-critical materials across 5 categories
- Validation: All 28 pass schema checks + fixture integrity
- Governance: Starter = source of truth; index auto-generated
- Full metadata: thermal expansion, service temp, phase transitions, uncertainty notes

**ceramictransitions side:**
- Integrated 22 new structures into `crystal_vr.json` (after dedupe vs. baseline)
- Total inventory: 60 materials (38 native + 17 procedurally-promoted + 5 metadata-only stubs)
- Metadata per material: formula, crystal system, thermal properties, aerospace context
- Phase 2.5.1 (May 15) generates 3D atoms+bonds at runtime for 17 of the 22 aerospace stubs
- Deployed via FTP (`_deploy.py`)

### Phase 2.5.1: Procedural Prototype Renderer (COMPLETE · May 15, 2026)
**Scope:** Eliminate "metadata-only" UI placeholders for prototype-mapped materials  
**Delivered:**
- 6 crystal prototypes implemented: rocksalt, fluorite, zincblende, AlB₂, wurtzite, hBN
- Prototype lookup table maps 17 aerospace formulas to (prototype, lattice params, cation/anion)
- `ensureElementsCoverage` + `ensureBondColorsCoverage` prevent crashes on missing color metadata
- Node smoke test (`test_prototype_generators.js`) — 215 checks all passing
- Renderable count: 38 → 55 (5 stubs remain, pending Phase 3 explicit modeling)

**Cross-project handoff:**
- howell-help materials confirmed used by ceramictransitions
- Both projects now reference aerospace data
- Memory nodes updated with integration points

---

## Material Inventory: 60 Total (Organized by Function)

### Traditional Refractories (38 native + 4 aerospace updates)
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

**Next milestone:** Phase 2.5 web-delivery hardening (in flight, see below) → Phase 3 kickoff in Taichi repo.

---

## Phase 2.5: Web Delivery Hardening (COMPLETE · May 16, 2026)

**All 10 items shipped.** See commits `da94e57` (2.5.1/3/5/6/7/8 + cross-links) and `bb6ff9d` (2.5.4/9/10). 2.5.2 permalinks already covered by Phase 5 `encodeShareState`/`applyShareState` (richer than spec — covers structure idx, all toggles, firing T, slice, compare, dual-track, melt, oxidation).

**Status:** Bug-fix pass shipped May 15 (commit `64f3fb4`). Remaining items below are the gap analysis for the Phase 1–2 web track. Phase 3+ scientific structure generation remains Taichi-only per repo split.

**Scope guardrail:** Everything in Phase 2.5 is *web-delivery scaffolding* — UI, UX, render fallbacks, build hygiene. Original atomic structures (full ab-initio coordinates, simulation-derived bonds) stay in `ceramictransitions-taichi`. When Taichi produces canonical structures, they replace any procedural fallback shipped here.

### Completed May 15, 2026 (commit `64f3fb4` · `8e46dd2`)
- Crash guard in `buildCellWireframe` / `buildCompareCellWireframe` for empty/malformed `cellVectors`
- Load-time dedupe in `index.html` + `lattice.html` (key on name+formula, keep richer entry)
- `isStub` flag + amber "Metadata only · 3D model pending (Phase 3)" info-panel branch
- `lattice.html` count derived: "{renderable} of {total} structures · {missing} pending 3D models"
- Source-side fix: `add_aerospace_materials.py` made idempotent on (name, formula)
- JSON deduped: 71 → 60 unique, every structure carries explicit `isStub: bool`, top-level `renderableCount: 38`
- New `dedupe_crystal_vr.py` + `validate_crystal_vr.py` (CI-ready, exits non-zero on failure)

### 2.5.1 Procedural prototype renderer ★ HIGHEST LEVERAGE — ✅ DELIVERED May 15, 2026 (commit `edf89b5`)
**Goal:** Eliminate the 22 visible "metadata pending" placeholders without waiting for Taichi.

**Rationale:** Every stub already has `prototype` + lattice parameters. ~150 lines of JS converts that into a renderable supercell. This is web-delivery scaffolding (a visual approximation), not original science — when Taichi ships per-material atomic coordinates they override the procedural output.

**Scope:**
- New function `generateAtomsFromPrototype(s)` in `index.html`, called from `loadData` when `s.isStub && s.prototype`
- Supported prototypes (covers all 22 stubs):
  - `rocksalt` (Fm-3m, 2 atoms/cell): ZrC, HfC, TaC, TiC, and any future MX carbides/nitrides
  - `fluorite` (Fm-3m, 3 atoms/cell): HfO₂-cubic, YSZ-3, YSZ-8, CSZ, La₂Zr₂O₇ (pyrochlore is a fluorite superstructure — first pass renders as disordered fluorite, flagged in info panel)
  - `wurtzite` (P6₃mc, 4 atoms/cell): AlN
  - `AlB2-type` / hP3 (P6/mmm, 3 atoms/cell): ZrB₂, HfB₂
  - `h-BN` / hP4 (P6₃/mmc, 4 atoms/cell): BN
  - `monoclinic-baddeleyite` (deferred — too complex for procedural; remains stub or hand-coded later)
- Reuse existing `supercell` tiling logic — generator emits unit-cell atoms, existing pipeline tiles
- Bond detection: reuse current `distance < cutoff` heuristic; per-prototype `bondCutoff` override allowed
- Atomic radii / colors: already in `data.elements` map — no new data needed
- Mark procedurally-generated structures with `s.proceduralFallback = true`; info panel adds a subtle "Procedural approximation · Phase 3 will replace with simulation-derived structure" line (preserves intellectual honesty)
- Unit-cell prototypes hard-coded in JS literal at top of `index.html` — no data file changes needed

**Acceptance:**
- All 60 structures renderable (38 real + 22 procedural)
- `lattice.html` count reads "60 structures repeating in space" (no more "pending" suffix)
- Procedural marker visible in info panel
- Validation script extended: `validate_crystal_vr.py` no longer reports stubs as "renderable: 38" — instead "renderable: 60 (38 native + 22 procedural)"

**Out of scope:** Pyrochlore cation ordering, monoclinic baddeleyite, real bond-order analysis. Those wait for Taichi.

**Files touched:** `index.html` (+~200 lines), `lattice.html` (mirror generator or share via small module), `validate_crystal_vr.py` (+~20 lines)

**Estimated effort:** One focused session.

**Delivery note (May 15, 2026):** Shipped as commit `edf89b5`. Final coverage: **38 native + 17 procedural = 55 of 60 renderable in viewer**. 5 stubs remain metadata-only (Si₃N₄ ×2, Yb₂SiO₅, Yb₂Si₂O₇, Sialon) — those need true prototypes (β-Si₃N₄ P6₃, X2 rare-earth silicate) or hand-coded structures and were left for a follow-up. Stub `prototype` fields turned out to be absent in the data, so promotion uses a formula → prototype lookup table keyed off `s.formula` with Unicode-subscript normalization. Procedural structures show a cyan info-panel badge distinct from the amber stub badge. Validator extended to report `native + procedural = renderable / metadata-only stubs`.

**Hardening pass (same day):** Added bond color fallback (`FALLBACK_BOND_COLORS` + `ensureBondColorsCoverage`) so procedural bonds get sensible colors instead of grey — covers `C-Hf, C-Ta, C-Zr, C-Si, Hf-O, O-Zr, B-Hf, B-Zr, Al-N, B-N, B-B`. Added `test_prototype_generators.js` Node smoke test that extracts the procedural module from `index.html` via regex + `vm`, then asserts per-prototype invariants (atom count > 0, bond count > 0, finite coords, valid bond indices, homoatomic policy, max-CN within expected range per prototype, bond color coverage). 215 checks across all 17 table entries — runnable without a browser: `node test_prototype_generators.js`.

**Deployment note:** `ceramictransitions.com` is hosted on **pixie-sh** (Porkbun FTP, `Server: openresty`, `X-Service: pixie-sh`), NOT GitHub Pages — confirmed via response headers May 15. Git pushes to `master` do not deploy the site. To get a new build live, FTP-upload `index.html`, `lattice.html`, and `data/` to the pixie-sh account for `ceramictransitions.com`. The howell.help repo (`C:\rje\dev\howell-help`) has a reference `_deploy.py` pattern (FTP password via env var). Until a `_deploy.py` is added here, manual FTP is required. Live site was on a May 10 build at time of this work.

### 2.5.2 URL state + permalinks (SHIPPED — already done as Phase 5)
**Goal:** Every viewer state shareable via URL.

**Schema:**
- `#s=<structureName>` — select structure (slug-cased name or formula)
- `?compare=<a>,<b>` — open comparison mode with these two
- `?t=<celsius>` — initial firing-phase / temperature slider position
- `?cam=<azimuth>,<elevation>,<zoom>` — restore camera pose (optional, low priority)

**Implementation:**
- `parseURLState()` runs after `loadData`, drives initial UI
- `history.replaceState` on every UI change (debounced 300ms) keeps URL in sync
- No router framework — plain `URLSearchParams` + hashchange listener
- Backward compat: bare URL still lands on default first structure

**Acceptance:**
- Copy URL while viewing ZrO₂ → paste in new tab → lands on ZrO₂
- Compare URL with two slugs → opens compare mode pre-populated
- Bad slug → falls back to first structure, no crash

**Files:** `index.html`, `lattice.html` (consistent slug scheme across both)

### 2.5.3 Filter + search
**Goal:** Make 60 structures findable in <5 seconds.

**Filters (multi-select, AND'd):**
- Phase family: oxide / carbide / nitride / boride / silicate / composite (derived from `phase_family` if present, else inferred from formula)
- Application: TBC / UHTC / CMC / EBC / kiln / structural (from `application_context` array)
- Crystal system: cubic / tetragonal / hexagonal / monoclinic / trigonal (from `crystalSystem`)
- Service temp: dual-slider 0–3500 °C (from `service_temp_max_c`)
- Render quality: native 3D / procedural / stub (from `isStub` + `proceduralFallback`)

**Search:** Plain substring match across `name`, `formula`, `notes`. No fuzzy lib — 60 entries don't need it.

**UI:** Collapsible filter rail on left of `lattice.html` (gallery is where search matters most). Main `index.html` gets a top search box only (faster context switch).

**Acceptance:** Type "carbide" → list narrows to ZrC/HfC/TaC/SiC/SiC-SiC. Select "service temp >2500" → narrows further. Clear filters with one button.

**Files:** `lattice.html` (+~150 lines), `index.html` (+search box ~30 lines)

### 2.5.4 Phase-transition visualizer (SHIPPED · May 16, 2026)

**Impl note:** Snap-switching via `switchStructure()` with existing dissolve fade, not atom-position lerp. Honest for reconstructive transitions (ZrO₂ tetra→cubic, SiO₂ β-quartz→cristobalite). Lives in `#transitions-panel` inside info panel; only visible when current structure has `transitions[]` array or is referenced by another structure's transitions chain.

**Wired chains:**
- ZrO₂: Baddeleyite (20–1170°C) → Tetragonal Zirconia (1170–2370°C) → Cubic Zirconia (2370–2715°C)
- SiO₂: α-Quartz (20–573°C) → Tridymite (573–1470°C) → β-Cristobalite (1470–1713°C)

Labeled "Schematic — not simulation-derived."
**Goal:** Make the site name literal — show *transitions*, not just snapshots.

**Mechanism:** When a material has known polymorphs (e.g. ZrO₂ monoclinic ↔ tetragonal ↔ cubic), and we have data entries for each, a T-slider above the canvas lerps:
- Lattice parameters (a, b, c, α, β, γ) linearly between phase boundaries
- Atom positions (need correspondence map between phases — start with simple 1-to-1 nearest-atom match)
- Cell wireframe redraws each frame

**Scope (first pass):**
- ZrO₂ family (monoclinic 0–1170 °C, tetragonal 1170–2370, cubic >2370)
- SiO₂ family (α-quartz / β-quartz / β-cristobalite — already have β-cristobalite)
- HfO₂ family if structures exist
- Drop-down on info panel: "View transitions" → reveals T-slider

**Data requirement:** A new `transitions` key on parent material listing child structures with T-ranges:
```json
"transitions": [
  { "structure": "ZrO2-monoclinic", "tempRange": [0, 1170] },
  { "structure": "ZrO2-tetragonal", "tempRange": [1170, 2370] },
  { "structure": "ZrO2-cubic", "tempRange": [2370, 2715] }
]
```

**Acceptance:** Sliding T crosses 1170 °C → atoms visibly rearrange to tetragonal positions; info panel updates "Current phase: tetragonal".

**Out of scope:** Reconstructive transformations (atoms break bonds and re-form) — those just snap at the boundary with a fade transition, not lerp. Flag as limitation.

**Files:** `index.html` (+~250 lines), `data/crystal_vr.json` (+`transitions` arrays on ~6 parent materials)

### 2.5.5 Enriched metadata display
**Goal:** Surface fields the data already has but the UI ignores.

**Currently hidden:** `service_temp_max_c`, `thermal_expansion_1e6_per_c`, `thermal_shock_risk`, `application_context`, `phase_transition_notes`, `uncertainty_notes`, `source_quality`.

**UI addition:** Below the formula in info panel, a 2-column key-value table (collapsible "Details" disclosure). Source quality badges (handbook / aerospace-spec / estimated) styled distinctly.

**Data gap:** Some baseline (non-aerospace) materials lack these fields — add a `dataCompleteness` boolean per material and gray-out missing rows rather than omit silently.

**Acceptance:** Selecting Periclase shows Service temp 2000 °C, CTE 13.5 ×10⁻⁶/°C, Source: handbook. Selecting a missing-data structure shows the same table with "—" placeholders.

**Files:** `index.html` (+~80 lines), `data/crystal_vr.json` (backfill missing fields on baseline materials — separate PR, can pull from howell-help starter where available)

### 2.5.6 Mobile + touch reflow
**Goal:** Site works on a phone.

**Audit needed:** OrbitControls already touch-capable. The chrome (info panel, controls, compare split) likely overflows. Specific checks:
- Single-column layout below 768px
- Compare mode: stacked vertical canvases instead of side-by-side on portrait
- Tap targets ≥44px (current select dropdowns may be smaller)
- Pinch-zoom on canvas without zooming page (touch-action: none on canvas)
- Filter rail collapses to bottom sheet on mobile

**Acceptance:** Open on iPhone Safari, rotate ZrO₂ with one finger, pinch to zoom, swap to compare mode, both halves visible.

**Files:** mostly CSS in `index.html` + `lattice.html`. Use browser tools to test live.

### 2.5.7 Accessibility floor
**Goal:** WCAG AA basics so the site isn't keyboard- and screen-reader-hostile.

**Checklist:**
- All interactive controls reachable via Tab; visible focus ring
- Structure picker: keyboard arrow-key navigation
- `aria-label` on canvas describing current structure ("3D viewer: Zirconium Diboride, hexagonal, 96 atoms")
- `aria-live="polite"` region announces structure changes
- Color contrast audit on amber/grey badges (info panel) — verify 4.5:1
- Reduced-motion respect: skip transition animations when `prefers-reduced-motion: reduce`
- Skip-link "Skip to viewer" at top of page

**Acceptance:** Navigate entire site with keyboard only. Run axe-core scan, zero serious issues.

**Files:** `index.html`, `lattice.html`. No new dependencies.

### 2.5.8 Loading + error states
**Goal:** No silent failure surfaces, no empty-canvas-while-loading ambiguity.

**Additions:**
- Skeleton card layout while `crystal_vr.json` fetches (current state: blank dark page)
- Explicit "Loading 60 structures…" with spinner
- Fetch failure → retry button + descriptive error ("Could not load structures. Check connection, or [retry].")
- WebGL unavailable → fallback message ("Your browser does not support WebGL. Try Chrome, Firefox, or Safari latest.")
- Per-structure render failure (e.g. atom count zero unexpectedly) → caught, info panel shows "Render error — please report" with link

**Acceptance:** Throttle network to "Slow 3G" in devtools — loading state visible >1s. Block fetch with devtools network panel — error message + retry works.

**Files:** `index.html`, `lattice.html` (+~60 lines each)

### 2.5.9 Phase-4 dead checkboxes — implement or remove (SHIPPED Option A · May 16, 2026)

Melt progression was already implemented (Phase 4 features #27). Added oxidation overlay (`chk-oxidation`): when firing T ≥ material's `oxidation_temp_c`, tints atoms toward burnt-orange (#cc7733), linear ramp over 300°C, max 60% blend. 13 non-oxides annotated: SiC family, Si₃N₄ family, ZrB₂, HfB₂, AlN, BN, ZrC, HfC, TaC. Info subtext shows onset T and active/inactive status. Persists in share link as `ox=1`.
**Goal:** Eliminate the credibility leak from non-functional UI.

**Current state:** "Oxidation overlay" and "Melt progression" checkboxes exist in `index.html` and toggle nothing visible.

**Decision required from owner:**
- **Option A (preferred):** Minimum-viable implementations now in web repo:
  - Oxidation overlay: tint surface atoms a desaturated brown/orange when T > material's oxidation threshold (`oxidation_temp_c` field, add to data)
  - Melt progression: above material's `service_temp_max_c`, randomize atom positions with growing amplitude as T approaches `T_melt`; fade out cell wireframe; render as "atoms losing crystalline order"
  - Honest framing: info panel says "Schematic — not simulation-derived"
- **Option B:** Remove the checkboxes; full implementation lives in Taichi repo

**Recommendation:** Option A. Both are <100 lines of JS and add narrative value. Schematic framing keeps them honest.

**Acceptance:** Checking "Melt progression" + setting T=2500°C on Periclase (T_melt=2852) → atoms visibly start jittering, cell wireframe fades to 40% opacity.

**Files:** `index.html` (+~150 lines if Option A, –20 lines if Option B), `data/crystal_vr.json` (+`oxidation_temp_c` if Option A)

### 2.5.10 Build hygiene + CI (SHIPPED · May 16, 2026)

- `data/crystal_vr.schema.json` — JSON Schema Draft 2020-12. Loose enough to accept real data (`version: number|string`, `supercell: array|null` for stubs).
- `validate_crystal_vr.py` — runs schema check when `jsonschema` installed; falls back to invariant-only check otherwise.
- `.github/workflows/validate.yml` — runs validator + schema check + `node test_prototype_generators.js` on PR + push to master.
- `_deploy.py` — injects `<!-- build: {short-sha} {iso8601-utc} -->` after `<head>` on every HTML upload.
- `_headers` — Cache-Control hints (data/*.json: 5min, *.html: 10min, *.js/*.css: 24h). Honored by Cloudflare/pixie-sh as origin headers.

**Goal:** Bad data can't ship to production.

**Additions:**
1. Extend `.github/workflows/pages.yml` (or new `validate.yml` running on PR):
   ```yaml
   - name: Validate crystal_vr.json
     run: python validate_crystal_vr.py
   - name: Lint HTML
     run: npx html-validate index.html lattice.html
   - name: JS syntax check
     run: node --check (extracted script blocks)
   ```
2. `data/crystal_vr.schema.json` — JSON Schema for the data contract. `validate_crystal_vr.py` switches to schema-based validation (jsonschema lib).
3. Pre-commit hook (`.git/hooks/pre-commit` — opt-in, document in BUILD.md): runs `validate_crystal_vr.py`, blocks commits with broken data.
4. GH Pages deploy includes a build-stamp comment in `index.html` (`<!-- build: {commit-sha} {timestamp} -->`) — makes stale-CDN diagnosis trivial.
5. Cache-Control headers via `_headers` file if Pages supports it — set `Cache-Control: public, max-age=300, must-revalidate` on `data/*.json` to bound the CDN staleness we hit on May 15.

**Acceptance:**
- Open a PR with a deliberately-broken JSON → CI fails before merge
- After deploy, `view-source` shows build stamp matching the commit
- `curl -I .../data/crystal_vr.json` returns explicit Cache-Control header

**Files:** `.github/workflows/pages.yml`, new `data/crystal_vr.schema.json`, new `_headers`, `BUILD.md` (document hook setup), `validate_crystal_vr.py` (schema mode)

---

### Phase 2.5 Sequencing

| Order | Item | Rationale |
|-------|------|-----------|
| 1 | 2.5.1 Procedural renderer | Highest user-visible impact; eliminates "22 pending" caveat |
| 2 | 2.5.10 Build hygiene | Lock the gate before the team ships more data |
| 3 | 2.5.8 Loading + error states | Cheap, high signal-to-effort |
| 4 | 2.5.7 Accessibility floor | Bundled with #3; same files |
| 5 | 2.5.5 Metadata display | Unlocks data we already have |
| 6 | 2.5.2 Permalinks | Unblocks sharing, citations, embedding |
| 7 | 2.5.3 Filter + search | Becomes essential once procedural lifts count to 60 visible |
| 8 | 2.5.6 Mobile reflow | Quality-of-life; not blocking desktop demo flow |
| 9 | 2.5.9 Phase-4 checkboxes | Decision needed first; can ship anytime after |
| 10 | 2.5.4 Phase-transition visualizer | Biggest payoff but largest scope; last because it benefits from all prior polish |

**Total estimated scope:** 3–5 focused sessions. None require Taichi-side work or block Phase 3.

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
