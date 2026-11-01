# BUILD.md

Operator playbook for building, verifying, and releasing ceramictransitions.

**Current master backlog:** see [`MASTER_TASKS.md`](MASTER_TASKS.md). `PLANS.md` is
the historical project journal; its older counts and deployment statements are not
the current release contract.

## 1) Prerequisites

- Git
- GitHub repository access
- Python 3.10+ (for `validate_crystal_vr.py` and `_deploy.py`)
- Node 18+ (for `test_prototype_generators.js`)
- Porkbun / pixie-sh FTP credentials (only for the legacy mirror)

## 2) Repo Layout (Build-Relevant)

- `index.html` - primary static viewer (Three.js + VR crystal structure visualization)
- `lattice.html` - compact lattice viewer (shares procedural module with index.html)
- `MASTER_TASKS.md` - current prioritized execution backlog and interface direction
- `data/crystal_vr.json` - crystal structure library (113 entries: 99 baked + 9 procedural candidates + 5 system entries)
- `data/crystal_vr.js` - generated file:// fallback bundle, regenerated from the JSON catalog
- `build_release_manifest.py` - generated public catalog/deployment manifest
- `DEPENDENCIES.md` - runtime and CI dependency inventory
- `CHANGELOG.md` - current release/change history
- `validate_crystal_vr.py` - structure inventory + renderable-count audit
- `test_prototype_generators.js` - Node smoke test for procedural module (428 invariants)
- `test_viewer_smoke.py` - headless browser load/share-state smoke test
- `check_performance_budget.py` - catalog transfer and geometry budget check
- `test_deploy_artifact.py` - legacy mirror public-file allowlist test
- `generate_catalog_audit.py` - per-entry source, geometry, transition, and caveat report
- `_deploy.py` - legacy FTP mirror deploy script (GitHub Pages is authoritative)
- `_inspect.py` - quick structure dump helper
- `add_aerospace_materials.py` - integration script (howell-help → crystal_vr.json)
- `.github/workflows/pages.yml` - validated GitHub Pages deployment workflow
- root-level static HTML/runtime assets + `data/` are staged into the public artifact

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

- GitHub Actions validates the catalog, stages a public artifact, generates the file:// bundle, and deploys only the staged artifact.
- Local HTTP development uses the repository root; direct file:// loading uses the generated `data/crystal_vr.js` fallback.
- Material library (`data/crystal_vr.json`) is versioned directly.
- The Pages artifact includes `release-manifest.json`, generated from the catalog at deploy time.

## 5) Deploy

**The live site at https://ceramictransitions.com is served by GitHub Pages.** This was verified on 2026-10-31 from the `Server: GitHub.com` response header. A push to `master` triggers validation and then the Pages deployment workflow. `_deploy.py` is retained as a legacy/secondary FTP mirror only.

Deploy command sequence:

```powershell
cd C:\rje\dev\ceramictransitions
# 1. commit + push source
git add .
git commit -m "<message>"
git push origin master

# 2. optionally update the legacy FTP mirror; this is not the authoritative release
$env:CERAMICTRANSITIONS_FTP_PASS = '<porkbun ftp password>'
python _deploy.py --dry-run   # preview which files would upload
python _deploy.py             # actual upload (size-compare optimization)
python _deploy.py --force     # upload every file unconditionally
python _deploy.py --tls       # use FTP_TLS if plain FTP is blocked (per howell.help gotcha)
```

FTP target:
- Host: `pixie-ss1-ftp.porkbun.com` (override with `CERAMICTRANSITIONS_FTP_HOST`)
- User: `ceramictransitions.com` (override with `CERAMICTRANSITIONS_FTP_USER`)
- Password: env `CERAMICTRANSITIONS_FTP_PASS` (required; never commit)

What `_deploy.py` uploads to the legacy mirror:
- `index.html`, `lattice.html`
- `data/crystal_vr.json`, `data/crystal_vr.schema.json`, and generated viewer assets
- Any root-level `.ico`/`.png`/`.svg`/`.css`/`.js` viewer assets

What `_deploy.py` skips (never uploaded):
- `yfiles/`, `yfiles-demo/` (legacy eval SDKs, gitignored)
- `.git/`, `.github/`, `__pycache__/`, `node_modules/`, `.vscode/`, `.idea/`
- `*.py`, `*.md`, `.gitignore`, `.env*`, `.pass.local`, `_deploy.py` itself
- `test_prototype_generators.js` (dev-only smoke test)
- Anything containing `taichi` in the path (sibling-repo guard)
- `data/.mp_cache/` (private ingestion cache; never a public artifact)

## 6) Secrets and Env Vars (Names Only)

- `CERAMICTRANSITIONS_FTP_PASS` - Porkbun pixie-sh FTP password (required for deploy)
- `CERAMICTRANSITIONS_FTP_HOST` - optional override of FTP host
- `CERAMICTRANSITIONS_FTP_USER` - optional override of FTP user

No secrets are required to develop locally — only to deploy.

### Rollback

- GitHub Pages: revert the bad source commit on `master`, push the revert, and wait for the validated Pages workflow to publish it.
- Confirm rollback by checking `release-manifest.json` and `data/crystal_vr.json` on the public host with a cache-busting query.
- Legacy FTP mirror: restore the previous known-good artifact set with `_deploy.py --force --tls` only when the mirror is intentionally being maintained.

## 7) Verification Checklist

Before deploy:

1. `python validate_crystal_vr.py` reports `113 structures · 99 native + 9 procedural = 108 renderable · 5 metadata-only stubs`.
2. `node test_prototype_generators.js` reports `PASS: 428 checks passed, 0 failed`.
3. `python _deploy.py --dry-run` lists only the legacy mirror allowlist and no `.mp_cache`, `.py`, `.md`, or `yfiles/` files.
4. `git status` is clean and pushed to `origin/master`; GitHub Actions validation is green before the Pages deployment runs.

After deploy:

1. `https://ceramictransitions.com/` loads index.html and renders 3D structures.
2. Hard-refresh (Ctrl+F5) clears any stale CDN/browser cache.
3. Procedural structures show the cyan info-panel badge; metadata-only stubs show the amber badge.
4. No `cv[0] is not iterable` or `count=66 + duplicates` symptoms in the browser console (those bugs are fixed in current master).

## 8) Project Status & Plans

Roadmap constraint: simulation-heavy Phase 3+ work remains in the existing Taichi codebase at `C:\rje\dev\ceramictransitions-taichi`. This repository is the active static web workspace: catalog, provenance, browser UX, system stacks, transitions, exports, and release tooling are maintained here.

The historical Phase 1/2/2.5 sections below document how the project evolved. For current work, use `MASTER_TASKS.md` and the current catalog/release checks above.

### Phase 1: Core Ceramic Structures (COMPLETE)
- **38 native materials** in `data/crystal_vr.json` (silicates, oxides, refractories) with full atomic coordinates + bonds
- Three.js / InstancedMesh visualization with supercell info
- VR-ready dual-track phase narratives and firing trajectories
- Live site at https://ceramictransitions.com (served from GitHub Pages, see §5)

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

### Phase 2.5.1: Procedural Prototype Renderer (COMPLETE · May 15, 2026)
- 17 of 22 aerospace stubs promoted to renderable via in-browser procedural generators (rocksalt, fluorite, zincblende, AlB2, wurtzite, hBN prototypes)
- 5 stubs remain metadata-only: Si₃N₄ ×2, Yb₂SiO₅, Yb₂Si₂O₇, SiAlON (need β-Si₃N₄ P6₃ + X2 rare-earth silicate prototypes)
- Procedural structures show cyan info-panel badge; full atomic coordinates from Phase 3 will replace them
- See `PLANS.md` §2.5.1 for delivery notes; commits `edf89b5` (renderer) + `5434491` (bond-color fallback + smoke test)

### Phase 3: Full 3D Model Generation (PLANNED, in `ceramictransitions-taichi`)
**Goal:** Replace procedural fallbacks with full ab-initio atomic coordinates for the remaining 5 stubs and any procedural structure where simulation data is available.
**Approach:**
1. Use Materials Project / ICSD databases for ultra-high-temp ceramics where crystal data exists
2. Run Taichi / phonopy / ASE pipelines in `C:\rje\dev\ceramictransitions-taichi`
3. Export canonical atomic coordinates back into `data/crystal_vr.json` via `add_aerospace_materials.py`-style integration
4. Extend `validate_crystal_vr.py` to flag any structure still using `proceduralFallback`

**Priority:** Si₃N₄ (β-phase), Yb-silicates (EBC), then SiAlON.

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

- **Changes not live yet:** confirm the GitHub Actions validation and Pages deployment jobs are green. `_deploy.py` updates only the legacy FTP mirror.
- **`_deploy.py` ConnectionError / timeout on plain FTP:** add `--tls` to use explicit FTPS; if both fail, try `curl.exe --ftp-ssl` on port 990 (per howell.help gotcha, May 12 2026).
- **`_deploy.py` errors out on missing env var:** export `CERAMICTRANSITIONS_FTP_PASS` before running.
- **Stale client cache:** hard refresh browser (Ctrl+F5); CloudFront / CDN edges may also cache for ~5 minutes.
- **Structure not loading in 3D:** verify the catalog entry's provenance and renderability status. The five current metadata-only records are layered system architectures; they intentionally show a stack view rather than a single-crystal lattice.
- **Unicode errors in `_inspect.py` / validators:** script expects UTF-8; on Windows run with `python -X utf8` or set `PYTHONUTF8=1`.

## 10) Integration Points (Cross-Project)

### howell-help → ceramictransitions (Source → Consumer)
- **Sync direction:** howell-help `high_temp_ceramics_starter.json` (28 materials) → ceramictransitions `data/crystal_vr.json` (23 new entries)
- **Trigger:** Manual via `add_aerospace_materials.py`; future: automated on push to howell-help, with Taichi pipeline sync in `C:\rje\dev\ceramictransitions-taichi`
- **Versioning:** ceramictransitions ships complete material list; howell-help is source of truth for aerospace spec data
- **Last source integration note:** May 10, 2026 is the historical howell-help aerospace import. Current catalog changes are governed by the validation, provenance migration, audit, and release-manifest checks.

### ceramictransitions → CMW (Potential Future)
- **Direction:** ceramictransitions 3D structures → CMW video annotation system
- **Use case:** Embed crystal structure viewer in CMW lessons on refractory materials
- **Data sharing:** Glaze/phase diagrams from CMW → ceramictransitions comparative visualizations

## 11) Last Verified

- Date: 2026-11-01
- Status: 113 entries (99 baked + 9 procedural candidates + 5 system entries); validator, JSON Schema, stoichiometry/geometry checks, 428 generator checks, shared-runtime parity, deploy allowlist, performance budget, accessibility contract, mobile/headless browser scenarios, system stack scenario, and transition timeline scenario are green.
- Deploy mechanism: GitHub Pages via `.github/workflows/pages.yml`; `_deploy.py` is a legacy/secondary FTP mirror.
- Current planning: `MASTER_TASKS.md`; historical commit receipts remain in `PLANS.md`.

