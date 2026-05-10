# BUILD.md

Operator playbook for building, verifying, and releasing ceramictransitions.

## 1) Prerequisites

- Git
- GitHub repository access
- GitHub Pages enabled for this repository

## 2) Repo Layout (Build-Relevant)

- `index.html` - primary static viewer (Three.js + VR crystal structure visualization)
- `.github/workflows/pages.yml` - deploy workflow (automatic on push to master)
- `data/crystal_vr.json` - crystal structure library (61 materials: 38 baseline + 23 aerospace)
- `_inspect.py` - utility to audit structure inventory
- `add_aerospace_materials.py` - integration script (howell-help → crystal_vr.json)
- root-level static assets and HTML files - published as-is

## 3) Local Setup / Run

This is a static site with no build step.

Quick open:

- Open `index.html` directly in a browser.

Optional local server:

```powershell
cd C:\rje\dev\ceramictransitions
python -m http.server 8080
```

Then open <http://localhost:8080>.

## 4) Build / Export

- No bundling/build pipeline.
- Repository root content is the deploy artifact.
- Material library (`data/crystal_vr.json`) is versioned directly.

## 5) Deploy

Deployment is automated by GitHub Actions on push to `master`.

Workflow details:

- Workflow file: `.github/workflows/pages.yml`
- Trigger: push to `master`
- Artifact path: repository root (`.`)
- Target: GitHub Pages

Deploy command sequence:

```powershell
cd C:\rje\dev\ceramictransitions
git add .
git commit -m "Update site + materials"
git push origin master
```

## 6) Secrets and Env Vars (Names Only)

- None required for this static Pages deploy flow.

## 7) Verification Checklist

1. Confirm GitHub Actions run succeeds (`Deploy to GitHub Pages`).
2. Confirm live site shows latest changes.
3. Validate no major console/runtime errors in browser.
4. Test 3D viewer loads and rotates structures smoothly.
5. Verify new aerospace materials appear in sidebar/search.

## 8) Project Status & Plans

### Phase 1: Core Ceramic Structures (COMPLETE)
- **38 baseline materials** in `data/crystal_vr.json` (silicates, oxides, refractories)
- Three.js visualization with full atomic coordinates, bonds, supercell info
- VR-ready dual-track phase narratives and firing trajectories
- GitHub Pages deployment live at https://ceramictransitions.com

### Phase 2: Aerospace Materials Integration (COMPLETE · May 10, 2026)
**Source:** `C:\rje\dev\howell-help\data\high_temp_ceramics_starter.json` (28 canonical materials)  
**Added to crystal_vr.json:** 23 new structures (5 already present: quartz, mullite, corundum, periclase, spinel)  
**Categories:**
- **5 Ultra-high-temp structural** (ZrB₂, HfB₂, ZrC, HfC, TaC) — service up to 3200°C
- **5 Thermal barrier coatings** (YSZ variants 3/8 mol%, CSZ, HfO₂, La₂Zr₂O₇) — TBC standards + next-gen
- **2 Rare-earth silicates** (Yb₂SiO₅, Yb₂Si₂O₇) — environmental barrier coatings for CMCs
- **1 CMC composite** (SiC-SiC) — fiber-reinforced matrix for next-gen engines
- **6 Engineered ceramics** (AlN, BN, SiAlON, RBSC, SSiC, Si₃N₄-sintered) — 1400–1650°C range
- **4 Broad-use refractories** (β-Cristobalite, Stabilized Zirconia, SiC, Si₃N₄) — from baseline expansion

**Integration approach:**
- All 23 new materials have full metadata (formula, crystal system, thermal properties, aerospace context)
- Stub atomic structures (empty atoms/bonds arrays) — 3D model generation deferred to Phase 3
- Full crystal data available via cross-reference to howell-help `high_temp_ceramics_starter.json`

### Phase 3: 3D Model Generation (PLANNED)
**Goal:** Generate full atomic coordinate sets for aerospace materials (currently stub structures)  
**Approach:**
1. Use Materials Project / ICSD databases for ultra-high-temp ceramics where crystal data exists
2. Generate pseudo-structures for composites/coatings (layered models showing TBC stacking)
3. Import/convert structures via phonopy/ASE into Three.js JSON format
4. Extend `_inspect.py` to validate complete structures

**Priority:** ZrB₂, HfB₂, YSZ variants (industry-standard; data widely available)

### Phase 4: Advanced Visualization Features (PLANNED)
**Goal:** Phase trajectories showing thermal transformations and field-use degradation  
**Features:**
1. **Thermal transformation paths** — show phase transitions (α→β, monoclinic→cubic, tetragonal stabilization)
2. **Oxidation/degradation overlays** — highlight surface oxidation, internal cracking under thermal cycling
3. **Comparative firing narratives** — baseline kiln conditions vs extreme aerospace environments (3000°C re-entry)
4. **Bond length / thermal expansion sliders** — animate CTE effects across temp range
5. **Hypersonic load case visualization** — show stresses during re-entry thermal pulse

**Data source:** Phase transition notes from `high_temp_ceramics_starter.json` + aerospace mission profiles

### Phase 5: Interactive Materials Database (PLANNED)
**Goal:** Faceted search + filtering on aerospace + studio properties  
**Features:**
1. **Filter by:**
   - Service temperature range (up to 3200°C)
   - Thermal shock risk (low/medium/high)
   - Application context (TBC, hypersonic, composite matrix, etc.)
   - Phase family (oxide, non-oxide, diboride, carbide, composite)
2. **Side-by-side comparison** of thermal properties, CTE, service limits
3. **Export** structure data + metadata to USDZ/glTF for 3D printing / CAD integration
4. **Cite & attribution** — link back to aerospace-spec source data in howell-help

### Phase 6: Collaboration & Integration (PLANNED)
**Goal:** Connect to external ceramic research pipelines  
**Connections:**
1. **CMW (Ceramic Materials Workshop)** — cross-reference Matt Katz's glaze/material library
2. **stullatlas.app** — ceramic phase diagram atlas integration
3. **Howell bridge** — bidirectional sync of material updates between ceramictransitions + howell-help
4. **Academic citations** — DOI links to foundational papers on ultra-high-temp ceramics

## 9) Common Failure Modes

- **Changes not live yet:** wait for Pages deploy completion (typically <2 min).
- **Wrong branch pushed:** deploy triggers from `master` only.
- **Stale client cache:** hard refresh browser; check `index.html` timestamp comment.
- **Structure not loading in 3D:** verify `atoms` array is non-empty (baseline materials only; aerospace materials are stubs pending Phase 3).
- **Unicode errors in `_inspect.py`:** script expects UTF-8; ensure terminal is in UTF-8 mode.

## 10) Integration Points (Cross-Project)

### howell-help → ceramictransitions (Source → Consumer)
- **Sync direction:** howell-help `high_temp_ceramics_starter.json` (28 materials) → ceramictransitions `data/crystal_vr.json` (23 new entries)
- **Trigger:** Manual via `add_aerospace_materials.py`; future: automated on push to howell-help
- **Versioning:** ceramictransitions ships complete material list; howell-help is source of truth for aerospace spec data
- **Last sync:** May 10, 2026 (all 23 aerospace + baseline materials integrated; validation passed)

### ceramictransitions → CMW (Potential Future)
- **Direction:** ceramictransitions 3D structures → CMW video annotation system
- **Use case:** Embed crystal structure viewer in CMW lessons on refractory materials
- **Data sharing:** Glaze/phase diagrams from CMW → ceramictransitions comparative visualizations

## 11) Last Verified

- Date: 2026-05-10
- Status: Pages workflow present; crystal_vr.json updated to 61 materials (38 baseline + 23 aerospace); integration validation complete
- Latest commit: aerospace materials added + documentation updated

