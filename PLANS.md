# Ceramics Aerospace Materials Integration — Complete Project Plan
**Status:** Phase 3.3 COMPLETE | Updated: June 17, 2026  
**Scope:** howell-help (28 aerospace materials) + ceramictransitions (3D viewer integration)

---

## Executive Summary

**Completed:**
- ✅ **howell-help Phase E:** 28 aerospace/extreme-temp materials catalog with full metadata, schema validation, and governance rules
- ✅ **ceramictransitions Phase 2:** 60-material library deployed to ceramictransitions.com via pixie-sh FTP
- ✅ **ceramictransitions Phase 2.5.1:** procedural prototype renderer (rocksalt / fluorite / zincblende / AlB₂ / wurtzite / hBN). 17 aerospace stubs promoted to runtime-renderable; renderable count 38 → 55. Live May 15, 2026 (edf89b5 → 9b3b0dc).
- ✅ **ceramictransitions Phase 3.1:** β-Si₃N₄ prototype (P6₃, 14-atom Wyckoff basis) covering Silicon Nitride + Sintered Silicon Nitride + Sialon. Yb-silicate stubs enriched with lattice + EBC service metadata. Renderable 55 → 58; smoke 215 → 240. Master `4debeca` pushed May 16, 2026.
- ✅ **ceramictransitions Phase 3.2:** Materials Project ingest for Yb-silicate EBC structures. β-Yb₂Si₂O₇ from `mp-4300` (real Yb, C2/m, 2×2×2 → 88 atoms, 118 bonds, Yb-O 2.22 Å, Si-O 1.63 Å); X2-Yb₂SiO₅ from `mp-16969` (Lu₂SiO₅ C2/c with Lu→Yb substitution; ionic radii <1% apart, isostructural across late lanthanides). Renderable 58 → 60; **0 metadata-only stubs remaining**. Smoke 240/240. `_ingest_mp_silicates.py` shipped; MP responses cached in `data/.mp_cache/`. May 27, 2026.
- ✅ **Cross-project integration:** Bidirectional sync architecture planned; materials live in both systems
- ✅ **Companion site:** ~~ceramic-micros~~ — cross-links removed 2026-06-17 (per Ryan).

**Deliverables:**
1. **howell-help:** `data/high_temp_ceramics_starter.json` (source of truth for aerospace specs)
2. **howell-help:** `data/high_temp_ceramics_index.json` (auto-generated lookup table)
3. **ceramictransitions:** `data/crystal_vr.json` (60 structures with 3D viewer metadata, **60/60 renderable** — 40 native + 20 procedural)
4. **ceramictransitions:** `BUILD.md` (6-phase development roadmap)
5. **ceramictransitions:** `_deploy.py` FTP deploy + `test_prototype_generators.js` (240-check smoke test)
6. **ceramictransitions:** ~~`transitions-graph.html`~~ — **RETIRED 2026-06-17** (generic SVG/canvas firing toy, disconnected from the 83-material atlas; see Tier D)

**Deploy mechanism:** **GitHub Pages** is the live host — `ceramictransitions.com` (CNAME) is served from `master` and auto-deployed by `.github/workflows/pages.yml` on every push, after `.github/workflows/validate.yml` gates any `data/**`/HTML change (validator + JSON Schema + 240-check smoke). So **`git push origin master` deploys live** (verified 2026-06-17: `server: GitHub.com`). The FTP path (`python _deploy.py --tls --force`, requires `$CERAMICTRANSITIONS_FTP_PASS`) is a legacy/secondary Porkbun mirror, not the live host.

## Open Operational Threads

- ✅ **Live deploy = GitHub Pages (Phases 3.1–3.3 current)** — verified 2026-06-17: `ceramictransitions.com` is served by GitHub Pages (`server: GitHub.com`, `CNAME`), auto-deployed by `.github/workflows/pages.yml` on every push to `master` (gated by `validate.yml`). Live `data/crystal_vr.json` is byte-identical to the repo (83 structures). To ship: commit + `git push origin master`. The FTP `_deploy.py` path (Porkbun) is a legacy/secondary mirror — `CERAMICTRANSITIONS_FTP_PASS=… python _deploy.py --tls --force` (`--tls` required; plain PASV times out).
- 📋 **Phase 3.3 (carry-forward)** — Migrate procedural-fallback path into Taichi repo so the web JSON ships simulation-derived structures and the client-side prototype renderer becomes a graceful-degradation fallback only.
- 📋 **Phase 4** — layered TBC composite pseudo-structures + thermal-transformation animation pipeline (Taichi-only).

**Roadmap constraint (effective now):** All remaining heavy implementation work for Phase 3+ is Taichi-only in `C:\rje\dev\ceramictransitions-taichi`. The current `ceramictransitions` repo is retained as the completed Phase 1–2.5.1 web delivery track; small UX polish (filter, mobile, error states, cross-links) is in scope here.

---

## INTERFACE & DISCOVERY ROADMAP (2026-06-17, CH-260617-1)

**Why this exists.** The 3D *rendering* is mature (polyhedra, slice, measure, symmetry, firing, compare, AR/VR, share). What is thin is everything around *finding* and *trusting* the material. Data audit (`data/crystal_vr.json`, 83 structures) proves it: `application_tags` is 100% populated (133 distinct) and surfaced **nowhere**; `service_temp_c`/`melting_point_c` are 100% but only a min-T slider uses them; `mp_id` provenance (28/83 DFT-verified) is buried in `info[]` prose; and the project named *Transitions* has machine-readable transition data on only **2/83** entries. This roadmap closes the discovery + trust gap, then makes the namesake real.

**Execution order (Ryan, 2026-06-17): A → B → C → think-deep checkpoint → D.** A/B/C are web-repo UI work (in scope here). D is partly data-authoring (in scope) + partly 3D animation (Taichi repo). All UI work is `index.html`-only unless noted; **data files stay untouched in A/B/C** so `validate.yml` (validator + JSON Schema + 240 smoke) stays green. Ship each tier as its own commit; `git push origin master` auto-deploys via Pages; verify live with a cache-busted curl before moving on.

**Shared gotchas (apply to every tier):**

- **Index coupling.** `applyFilter()` and the struct-button click handler both assume button position *i* maps to `data.structures[i]` (`btns.forEach((btn,i)=>data.structures[i])`, `switchStructure(i)`). Any feature that **reorders** the list (sort) MUST first migrate to `btn.dataset.idx` and read `data.structures[+btn.dataset.idx]` everywhere, or it will silently show the wrong crystal. This is the single highest-risk refactor in B — do it first and verify before adding sort.
- **Pinch/Pro tiers (shipped).** New discovery controls (search, sort, tag browse) belong in **Pinch** (they are core, not advanced). Provenance badges (C) also Pinch. Keep the `data-tier="pro"` wrappers intact.
- **Filtering is multiplicative.** `applyFilter()` already ANDs class + minT + hide-precursors. Search (B), tag (A) just add more AND clauses + update the `#filter-count` readout. One function stays the single source of truth for "what's visible."
- **Verify in a real browser with a true reload**, not a hash change — `init()` only re-runs on full load (lesson from the Pinch/Pro false-receipt: hash-only nav showed stale state).

---

### TIER A — Application-tag browse ("find the material for my job")  ⏳ NEXT

**Goal.** Turn 133 dead `application_tags` into the discovery spine: pick a job (rocket-nozzle, cutting-tool, kiln-furniture, turbine-blade, armor…) → the structure list narrows to materials used for it. This reframes the tool from "crystal viewer" to "computational materials selector" using data already at 100% coverage.

**A.0 — Tag curation (do FIRST; the raw tags are messy).** The 119 non-generic tags include near-duplicates that must be normalized/grouped or the browse is noise. Build a `TAG_GROUPS` map in `index.html` (small, hand-curated, ~12–16 canonical jobs):

- Merge variants → one canonical label, e.g. `{tbc, TBC-topcoat, TBC-topcoat-standard, TBC-topcoat-research, TBC-next-gen, next-gen-tbc} → "Thermal barrier coating"`; `{cte-match-sic, low-CTE-match-to-SiC} → "CTE-matched to SiC"`; `{cutting-tool, tool-coating, cemented-carbide} → "Cutting / tooling"`.
- Drop the generic `high-temperature-ceramic` (66 — useless as a filter) and the structural `polymorph-of:` / `decomp-to:` / `transforms-to:` / `precursor-to:` tags (those are **reserved for Tier D**, not job-browse).
- Curated canonical jobs to surface (each maps ≥2 materials): Thermal barrier coating, Environmental barrier coating, Cutting / tooling, Armor, Refractory / kiln furniture, Hypersonic leading edge, Rocket nozzle, Abrasive / wear-resistant, Crucible / molten-metal, Oxidation-resistant, CMAS-resistant, MAX phase, Damage-tolerant, Conductive ceramic.

**A.1 — Data helper.** Add `function matchesTag(structure, canonicalJob)` that resolves a structure's raw `application_tags` through `TAG_GROUPS` (case-insensitive) and returns whether it belongs to the canonical job. Add `activeTag` to module state (default `null`).

**A.2 — Browse UI.** In the `Filter` section of `#panel` (after the class `<select>`, before the temp slider), add a collapsible "Used for…" chip row: render one chip per canonical job that has ≥1 match, each showing its match count (e.g. `Rocket nozzle (3)`). Clicking a chip sets `activeTag`, toggles its `.active` class, and calls `applyFilter()`. Re-use the existing `.btn-mode`/chip styling; wrap in `data-tier` is **not** needed (Pinch-visible).

**A.3 — Wire into `applyFilter()`.** Add one clause: `if (activeTag && !matchesTag(s, activeTag)) ok = false;`. The `#filter-count` readout already reflects it. Clearing the chip (click again / a "× clear job" control) sets `activeTag=null`.

**A.4 — Clickable tags in the info panel.** In `updateInfoPanel()`, after the property rows, render the structure's resolved canonical jobs as small clickable chips. Clicking one sets `activeTag` + `applyFilter()` + scrolls the list — so a user reading about HfC can click "Hypersonic leading edge" and instantly see its peers.

**A.5 (optional, nice).** Persist `activeTag` into the share link (`encodeShareState`/`applyShareState`, param `tag=`), mirroring how Pinch/Pro added `mode=pro`.

**Acceptance:** clicking "Rocket nozzle" narrows the list to exactly the rocket-nozzle materials; count updates; clicking a tag in HfC's info panel cross-navigates; clear restores all 83; `node --check` clean; verified in a true-reload browser session.

**Files:** `index.html` only. **Effort:** ~M. **Risk:** low (additive; no index reorder).

---

### TIER B — Discovery basics: search + sort + comparison table

**B.1 — Name/formula search (the flagship is missing what the gallery already has).** `lattice.html` has `#filter-input` (a `type=search`); `index.html` does not — backwards. Add `<input type="search" id="filter-name">` to the `Filter` section. In `applyFilter()` add: `if (q && !(s.name+' '+s.formula).toLowerCase().includes(q)) ok=false;` (also match resolved tags so "nozzle" finds rocket-nozzle materials). Debounce on `input`.

**B.2 — Sort (DO THE INDEX REFACTOR FIRST — see Shared gotchas).** Step 1: migrate every `data.structures[i]`-by-button-position read to `data.structures[+btn.dataset.idx]` and stamp `btn.dataset.idx = i` in `buildStructureList()`; verify the viewer still selects the right crystal after a no-op. Step 2: add `<select id="sort-by">` with: **Data order** (default), **Service temp ↓**, **Melting point ↓**, **Name A–Z**. On change, reorder the `#struct-list` DOM children by the chosen key (stable sort; missing values sort last), then re-run `applyFilter()`. Acceptance: sort by service-temp puts Graphite (3000°C) / HfC near the top; clicking any post-sort button still loads the correct structure.

**B.3 — Comparison property table.** Compare mode currently renders two crystals side-by-side with **no numbers**. In `#compare-panel` (or the info panel when compare is active), add a 2-column table: Service temp, Melting point, Class, Crystal system, Atoms, Bonds, (density/CTE if present in `stats`/`info`). Pull current vs `compareIdx`. Highlight the higher service-temp/melting-point cell. Acceptance: comparing SiC vs HfC shows both columns with the HfC service-temp cell emphasized.

**Files:** `index.html` only. **Effort:** B.1 S, B.2 M (refactor), B.3 M. **Risk:** B.2 medium (index coupling) — gate behind its own verify.

---

### TIER C — Provenance badges (the Ground= "verify everything" thesis, made visible)

**Goal.** Make trust legible. Today a structure's epistemic status (DFT-verified vs prototype-approximation vs metadata-only) is buried in `info[]` prose. Surface it as a badge.

**C.1 — Taxonomy (from verified runtime flags).** Order matters; evaluate AFTER the procedural-synthesis pass (`proceduralFallback` is set at runtime ~L976):

- **Verified** (green) — `s.mp_id` present (28/83). DFT-relaxed, real Materials Project entry.
- **Reference** (blue) — native coords (`!isStub`, no `mp_id`). From literature crystallography.
- **Procedural** (amber) — `s.proceduralFallback === true`. Lattice + bond topology from a canonical prototype; not simulation-derived.
- **Metadata-only** (grey) — `s.isStub === true` (8 remain). No lattice yet.

**C.2 — Badge in the info panel.** Replace the current ad-hoc stub/procedural `<div>` banners in `updateInfoPanel()` with one consistent badge component (`renderProvenanceBadge(s)`). For **Verified**, link `mp_id` → `https://materialsproject.org/materials/{mp_id}` (new tab, rel=noopener). Keep the existing honest wording ("not simulation-derived") for Procedural.

**C.3 — Badge dot in the struct list (subtle).** Add a 6px colored dot to each `.struct-btn` so provenance is scannable while browsing. Optional matching filter ("Verified only").

**C.4 — Legend.** One-line key in the badge area or the Pro "What's New"/about area.

**Acceptance:** SiC (mp-8062) shows a green **Verified** badge linking to Materials Project; a stub shows grey **Metadata-only**; Sialon shows amber **Procedural**; dots render in the list; `node --check` clean.

**Files:** `index.html` only. **Effort:** ~M. **Risk:** low.

---

### ◆ THINK-DEEP CHECKPOINT (before D) — honest scope + epistemics

Stop and decide three things with the data in front of us, **before** authoring transition data:

1. **What does the data honestly support?** Only 2/83 carry a `transitions` field, but the structural `application_tags` (`transforms-to:β-Quartz@573C`, `transforms-to:Magnetite>1390C`, `decomp-to:CaO+CO2@825C`, `polymorph-of:SiO2`, plus the firing-phase quartz inversion already modeled) are a **latent transition dataset already in the file**. First task of D is to *harvest* these into the structured schema rather than inventing — provenance stays honest.
2. **Where is the repo boundary?** Per the standing roadmap constraint, heavy 3D animation is **Taichi-only** (`ceramictransitions-taichi`). So D's web scope = (a) author/normalize per-material transition **data** + (b) surface that data in the **flagship's Firing mode** (the standalone `transitions-graph.html` was retired 2026-06-17). The animated polymorph morph in the 3D viewer is a Taichi deliverable — name it, don't build it here.
3. **Schema before content.** Lock a `transitions[]` schema (below) and a validator rule for it BEFORE bulk-authoring, so D can't drift the way the header counts did. Pair every claim with a citation field. This is the "pair prose with a verifiable artifact" principle applied to transition data.

Output of the checkpoint: a short go/no-go + the locked schema, recorded in this file, before any D content lands.

#### ◆ CHECKPOINT DECISION (2026-06-17, CH-260617-1) — after A+B+C shipped live

**Verdict: GO — but D.3 (authoring cited claims) is report-only for human review, not auto-commit to canon.**

Three findings from inspecting the live data (`data/crystal_vr.json`), each of which would have bitten if D had started blind:

1. **A `transitions[]` schema ALREADY EXISTS** on 2 entries (α-Quartz, Baddeleyite), shape `{structure, phaseName, tempRange:[lo,hi], transformType}`. My roadmap proposed a *different* shape (`{from,to,temp_c,type,…}`). Locking the proposed shape would have created two incompatible schemas in one file — exactly the drift this checkpoint exists to stop. **Decision: extend the existing shape, do not replace it.**
2. **17 latent structural-transition tags** already encode transitions with temperatures: `transforms-to:β-Quartz@573C`, `decomp-to:CaO+CO2@825C`, `transforms-to:Magnetite>1390C`, `decomp-to:Metakaolin@450C`, `precursor-to:Mullite`, etc. These are honest, free seed data — D.2 harvests them; it does not invent them.
3. **The "namesake gap" is real and narrow**: only 2/83 have structured transitions, but ~17 more are one parse away. The highest-value authored set (ZrO₂ t↔m, SiC α↔β, HfO₂ m↔t↔c, Si₃N₄) is ~6–8 materials of genuine domain authoring with citations.

**LOCKED SCHEMA (reconciled — extends the existing 2-entry shape, all new fields optional so old entries stay valid):**

```json
"transitions": [
  {
    "structure": "α-Quartz",          // existing — the phase this row describes
    "phaseName": "α-quartz (trigonal)",// existing
    "tempRange": [20, 573],            // existing — [lo,hi] °C stability window
    "transformType": "displacive",     // existing — displacive|reconstructive|martensitic|decomposition|polymorphic
    "to": "β-Quartz",                  // NEW (optional) — product phase
    "temp_c": 573,                     // NEW (optional) — transition temperature
    "reversible": true,                // NEW (optional)
    "volume_change_pct": 0.86,         // NEW (optional) — + = expansion on heating
    "note": "…",                       // NEW (optional)
    "source": "literature ref or mp_id"// NEW (optional) — pair every authored claim with a citation
  }
]
```

**Validator rule to add BEFORE content (D.2 step 1):** in `validate_crystal_vr.py`, if an entry has `transitions`, assert it's a non-empty list and every row has at least `structure` + (`tempRange` OR `temp_c`); `transformType` ∈ the enum if present; `volume_change_pct` numeric if present. This makes the schema enforceable so D content can't drift.

**Build order for D (revised by this checkpoint):** (D.2) add the validator rule + `_harvest_transitions.py` (idempotent, `--dry-run`, parses the 17 tags into the locked shape) → run, eyeball, commit data. (D.3) author the ~8 cited polymorphs **report-only** → human reviews the proposed JSON before it enters canon (per the standing "apprentice proposes, human disposes" discipline for data claims). (D.4) ~~make `transitions-graph.html` load `crystal_vr.json`~~ → instead add a Material view *inside the flagship Firing mode* (standalone page retired 2026-06-17). (D.5) record the Taichi handoff for the animated morph.

---

### TIER D — Make *Transitions* real (the namesake)

> **DECISION 2026-06-17 (CH-260617-1, Ryan "a" = retire):** `transitions-graph.html` is **RETIRED** (file + both nav links deleted). It was a hardcoded studio-stoneware firing curve (tops out at 1280°C "mature") plus an off-topic draggable NaCl toy — neither loaded `crystal_vr.json`, and the 1280°C curve actively contradicts an atlas whose materials mature at 2000–3900°C (HfC, TaC, graphite). A generic decoration that fights its own data has no slot in the analyze/behold two-surface story (flagship = analyze, lattice = behold).
>
> **What survives:** the *data* work (D.1–D.3, D.5). If transitions return, they fold into the **flagship's existing Firing mode** (it already has Firing mode + Thermal vibration), keyed off the `transitions[]` field — NOT a separate page. **D.4 (the standalone data-driven page) is CANCELLED.** The locked schema below stays valid for that in-flagship Material view.

**Goal.** The weakest part of the project is its own title. Give the polymorphic high-temp ceramics real, cited phase-transition data — surfaced *inside the flagship's Firing mode*, not a standalone page.

**D.1 — Schema (lock at the checkpoint).** Extend each applicable entry with:

```json
"transitions": [
  { "from": "α-SiC (6H)", "to": "β-SiC (3C)", "temp_c": 2000, "type": "reconstructive|displacive|martensitic|decomposition",
    "reversible": false, "volume_change_pct": 0.0, "note": "…", "source": "literature ref or mp_id" }
]
```

**D.2 — Harvest existing hints (do first; honest + free).** Parse the structural `application_tags` (`transforms-to:…@T`, `decomp-to:…@T`, `polymorph-of:…`) + the firing-phase quartz inversion into the new schema. Script: `_harvest_transitions.py` (stdlib; idempotent; `--dry-run`), writing into `data/crystal_vr.json`. **This touches data → run the full `validate.yml` suite locally + extend `validate_crystal_vr.py` with a `transitions[]` shape rule.**

**D.3 — Author the key polymorph set (cited).** The materials PLANS already names: **α↔β SiC**, **t↔m ZrO₂ (Bain/martensitic path, the toughening transformation)**, **m↔t↔c HfO₂**, **α↔β Si₃N₄**, **sialon solid-solution**, **α↔β quartz (573°C displacive)**, **cristobalite inversion (~220°C)**. ~6–8 materials, each with cited `temp_c`, `type`, `volume_change_pct` (the ZrO₂ ~4–5% dilation is the whole point of PSZ — get it right). Report-only review before committing canon.

**D.4 — ~~Data-driven transitions graph~~ → CANCELLED (page retired 2026-06-17).** The standalone `transitions-graph.html` is gone. Its replacement, if pursued, is a **Material view *inside the flagship*** (`index.html`): when a selected material carries `transitions[]`, render its transition chain on a temperature axis (hover notes + volume-change + reversibility) within the existing Firing-mode panel — no second page, no generic stoneware curve.

**D.5 — Taichi handoff note (NOT built here).** The animated 3D polymorph morph (atoms migrating α→β at T) belongs in `ceramictransitions-taichi`. Record the schema + the target materials as the handoff spec so the Taichi work consumes the same `transitions[]` data.

**Acceptance:** ≥8 materials carry cited `transitions[]`; validator enforces the shape; the flagship's Firing-mode **Material view** renders ZrO₂'s t↔m transformation with its volume change from data.

**Files:** `data/crystal_vr.json` (+ validator, + harvest script) and the Firing-mode panel in `index.html`. **Effort:** L (real domain authoring). **Risk:** medium — data-touching; gate on schema + validator + citations.

---

### Deferred / parallel (not in the A–D line)

- **Tier E — fill the 8 metadata-only stubs** (Cr₂AlC, c-BN, ZrN, Lu₂SiO₅, (Hf,Zr,Ti,Ta,Nb)C, …) via `_ingest_mp.py` (needs `MP_API_KEY`). Mechanical; every entry then renders a real lattice. Composes naturally with C (stubs become Verified).
- **Tier F — service-temperature visual scale/ladder** as the organizing spine of a *high-temp* tool (every entry has the data; today it's just a slider).
- **CI/process** — wire `validate.yml` to also run on PRs touching the harvest script; add a viewer data-load smoke test.

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

## Phase 3: 3D Model Generation (Phase 3.1 COMPLETE · May 16, 2026)

**Goal:** Generate full atomic coordinate sets for aerospace materials currently as stubs  
**Timeline:** 2–4 weeks (pending Materials Project API access)  
**Scope:** Priority 10 materials (ZrB₂, HfB₂, YSZ variants, HfO₂, La₂Zr₂O₇, SiC, AlN, SiAlON)

### Phase 3.1 — β-Si₃N₄ family + Yb-silicate metadata (SHIPPED May 16, 2026)

Stub-to-renderable progress: **17 → 20 procedural · 2 metadata-only stubs remain.**

- Added `si3n4` prototype to `PROTOTYPE_DEFS` in both `index.html` and `lattice.html`:
  - β-Si₃N₄ space group P6₃ (a=7.602 Å, c=2.907 Å), 14-atom basis (6 Si at 6h, 2 N at 2c, 6 N at 6h)
  - Wyckoff orbits expanded explicitly; supercell [2,2,3] → 168 atoms / 240 bonds
  - Bond cutoff 0.30·a captures all Si–N tetrahedral first neighbours
- Extended `PROTOTYPE_TABLE` with two entries mapped to `si3n4`:
  - `Si3N4` — covers "Silicon Nitride" + "Sintered Silicon Nitride" stubs
  - `Si6-xAlxOxN8-x` — covers "Sialon" stub (β-Si₃N₄ isostructural, a=7.659, c=2.929; substitutional disorder unmodeled)
- Extended `_normalizeFormula` to handle subscript x (ₓ → x) and subscript minus (₋ → -) so Sialon's Unicode formula maps to the table key.
- Added `N-Si` to `FALLBACK_BOND_COLORS` and matching `si3n4` entry to `EXPECTED_CN` in the smoke harness.
- Enriched `Ytterbium Silicate` (X2-Yb₂SiO₅, monoclinic B2/b) and `Ytterbium Disilicate` (β-Yb₂Si₂O₇, monoclinic C2/m) stubs with literature lattice parameters and EBC service notes; full atom coordinates deferred to Phase 3.2.
- Validator now recognises `Si3N4` and `Si6-xAlxOxN8-x` as procedural formulas.
- Smoke test: **240/240 passes** (up from 215/215).
- Validator: `60 structures · 38 native + 20 procedural = 58 renderable · 2 metadata-only stubs`.

### Phase 3.2 — COMPLETE (May 27, 2026)

**Shipped:** `_ingest_mp_silicates.py` — stdlib-only Materials Project REST ingest (`api.materialsproject.org/materials/summary/`, `X-API-KEY` auth, Cloudflare-friendly UA, JSON cache at `data/.mp_cache/`).

**Structures baked into `data/crystal_vr.json`:**

1. **Ytterbium Disilicate (β-Yb₂Si₂O₇, C2/m)** ← MP `mp-4300` — real Yb compound, DFT-relaxed, ehull=0 stable. Primitive cell (11 sites) tiled 2×2×2 → **88 atoms, 118 bonds**. Mean Yb-O = 2.22 Å, Si-O = 1.63 Å.
2. **Ytterbium Silicate (X2-Yb₂SiO₅, C2/c ≡ B2/b)** ← MP `mp-16969` (Lu₂SiO₅ X2, stable) with Lu→Yb element substitution. Lu³⁺ (0.861 Å) and Yb³⁺ (0.868 Å) differ <1% in 6-coord ionic radius; X2 RE-monosilicates are isostructural across the late lanthanides (Felsche 1973). Primitive cell (32 sites) used as-is → **32 atoms, 46 bonds**. Mean Yb-O = 2.27 Å, Si-O = 1.62 Å.

**Result:** renderable count 58 → 60, **zero metadata-only stubs remain**. Smoke test: 240/240 PASS. Validator: `60 structures · 40 native + 20 procedural = 60 renderable in viewer`.

**Note on MP coverage gap:** Materials Project does not contain a Yb₂SiO₅ entry (only Yb₂Si₂O₇ in the Yb-Si-O chemsys). The Lu→Yb substitution path is the canonical workaround for visualisation; literature lattice parameters (a=12.40, b=6.71, c=10.30 Å, β=102.4°) are preserved in `info[]` / `uncertainty_notes`. The MP primitive cell differs from the conventional setting; both are documented in the JSON entry.

### Phase 3.3 — High-Temp Focus Hardening (✅ COMPLETE · May 27, 2026)

**Goal:** Refocus the library, schema, and UI on **high-temperature ceramics** (the explicit project mission), eliminating mixed-purpose drift introduced by pedagogical mineral entries.

**Gap analysis (audit performed May 27, 2026):**

- **Library composition mixed:** 22 of 60 entries are NOT high-temp ceramics (clay minerals, hydroxides, carbonates that decompose <900°C, feldspars, feldspathoids). Useful as **precursors** but dilute the HT focus when unfiltered.
- **No classification:** `category`/`tags`/`class` fields on **0/60** entries. No way to filter UHTC vs TBC vs EBC vs precursor.
- **Temperature metadata sparse:** only 13/60 entries carry any temperature field (`oxidation_temp_c`), and HfB₂ states *"Service temperature up to 3200°C"* only in `info[]` prose — not machine-readable.
- **Stubs are exactly the HT materials:** 15 of the most aerospace-relevant entries (ZrB₂, HfB₂, ZrC, HfC, TaC, SiC, Si₃N₄, AlN, BN, SiAlON, RBSC, SSiC, SSN, HfO₂, La₂Zr₂O₇, YSZ, CSZ, SiC/SiC CMC) are still `isStub:true` and rendered via procedural prototype fallback — not DFT-relaxed lattice.
- **Missing HT materials:** MAX phases (Ti₃SiC₂, Ti₃AlC₂, Cr₂AlC), full RE silicate family (Y, Lu, Sc), Gd₂Zr₂O₇ (pyrochlore TBC), HfO₂-based TBCs, MoSi₂/WSi₂, B₄C, TiB₂, TiC/NbC/Cr₃C₂/WC, TiN/ZrN/HfN/TaN/c-BN, C/C, C/SiC, high-entropy carbides/borides.
- **No system-level views:** EBC stack, TBC stack, CMC architecture not modeled.
- **Frontend lacks HT framing:** `<title>` is generic; no filter UI; no service-temperature axis.
- **Validator under-constrains:** checks renderability but not HT-relevant metadata.

**P0 — schema + filter (high UX impact, low effort):**

1. Add per-entry fields: `material_class` (oxide / non_oxide / UHTC / TBC / EBC / CMC / silicate / carbide / nitride / boride / disilicide / precursor / mineral), `service_temp_c` (max sustained operating temperature in air), `melting_point_c`, `application_tags[]` (e.g. `turbine-blade`, `hypersonic-leading-edge`, `brake-disc`, `engine-liner`, `cutting-tool`, `nuclear-fuel`, `precursor-to:Mullite`).
2. Add temperature-range slider + class filter + application-tag filter to `index.html` and `lattice.html`.
3. Retitle to **"High-Temperature Ceramics — Structure + Transitions Explorer"**.
4. Demote (don't delete) clay minerals + carbonates + feldspars: tag `material_class="precursor"` and hide by default; surface via `precursor_for[]` back-links from mullite/cordierite/spinel.

**P1 — close the HT stub gap (biggest credibility win):**

5. Generalize `_ingest_mp_silicates.py` → `_ingest_mp.py` accepting a manifest of (target_name, mp_id, substitutions, supercell).
6. Ingest MP structures for the 15 remaining HT stubs: ZrB₂ (mp-1788), HfB₂ (mp-2310), ZrC (mp-2795), HfC (mp-2496), TaC (mp-7088), SiC polymorphs (mp-7140 / mp-8062), Si₃N₄ (mp-988 α / mp-2503 β), AlN (mp-661), BN-hex (mp-984), HfO₂ (mp-352 monoclinic), La₂Zr₂O₇ (mp-5304 pyrochlore), Y-doped ZrO₂ via Y₂O₃-ZrO₂ solid-solution model.

**P2 — content expansion (HT-only):**

7. Add new HT entries: MAX phases (Ti₃SiC₂, Ti₃AlC₂, Cr₂AlC), full RE silicate family (Y₂Si₂O₇, Lu₂Si₂O₇, Y₂SiO₅, Lu₂SiO₅), Gd₂Zr₂O₇, MoSi₂, B₄C, TiB₂, TiC, NbC, Cr₃C₂, WC, TiN, ZrN, c-BN, graphite, and the (Hf,Zr,Ti,Ta,Nb)C high-entropy carbide.

**P3 — system-level visualizations:**

8. Introduce `system` entry type modeling layered TBC (NiCoCrAlY bond coat / TGO Al₂O₃ / YSZ topcoat), EBC (Si bond coat / mullite / Yb-disilicate / Yb-monosilicate), and SiC/SiC CMC architecture.
9. ~~Audit `transitions-graph.html`~~ — **MOOT (page retired 2026-06-17).** The α↔β SiC / t↔m ZrO₂ (Bain path) / α↔β Si₃N₄ / m↔t↔c HfO₂ / sialon transition set is now Tier D data feeding the flagship Firing-mode Material view.

**P4 — pipeline hardening:**

10. `validate_crystal_vr.py` rule: every non-`precursor` entry must carry `material_class` AND `service_temp_c`.
11. Future carry-forward: migrate procedural-fallback path into the Taichi repo so the web JSON ships simulation-derived structures and the client-side prototype renderer becomes a graceful-degradation fallback only.

**Delivery log (May 27, 2026):**

- **P0 ✅** — `_classify_ht.py` classified all 60 original entries (`material_class`, `service_temp_c`, `melting_point_c`, `application_tags`). Distribution: silicate=9, precursor=9, refractory_oxide=8, TBC=6, mineral=5, nitride=5, UHTC=5, polymorph_silica=3, carbide=3, carbonate=2, EBC=2, oxide=1, hydroxide=1, CMC=1. Title + meta updated on `index.html` + `lattice.html`. Class dropdown + temperature range slider + filter-count UI live in both pages.
- **P1 ✅** — `_ingest_mp.py` (generalized MP ingest, PRESERVE_FIELDS keeps classification). Ingested 11 HT polymorphs with verified ground-state mp_ids: SiC=mp-8062, Si₃N₄=mp-988, ZrB₂=mp-1472 (AlB₂-type), HfB₂=mp-1994, ZrC=mp-2795, HfC=mp-21075, TaC=mp-1086, AlN=mp-661 (wurtzite), h-BN=mp-984, HfO₂=mp-352 (baddeleyite), La₂Zr₂O₇=mp-4974 (pyrochlore).
- **P2 ✅** — `_add_new_ht.py` appended 20 new HT entries (60→80). Real ingests (15): Ti₃SiC₂, Ti₃AlC₂, B₄C, TiB₂, TiC, NbC, Cr₃C₂, WC, TiN, Y₂Si₂O₇, Y₂SiO₅, Lu₂Si₂O₇, Gd₂Zr₂O₇, MoSi₂, Graphite. Stubs (5): Cr₂AlC, c-BN, ZrN, Lu₂SiO₅, (Hf,Zr,Ti,Ta,Nb)C HEC. Added Nb-C/Cr-C/W-C/C-C bond cutoffs to `_ingest_mp.py`.
- **P3 ✅** — `_add_systems.py` appended 3 layered system entries (80→83): TBC System (7YSZ/TGO/bond coat/superalloy, T=1200), EBC System (Yb₂Si₂O₇/Yb₂SiO₅/mullite/Si on SiC-CMC, T=1480), CMC Architecture (SiC fiber/BN interphase/SiC matrix, T=1315). New `entry_type="system"` shape with `layers[]` (role, material, thickness_um, purpose, xref).
- **P4 ✅** — `validate_crystal_vr.py` extended with `REQUIRED_SYSTEM` for system entries + HT-classification rule (every non-`{precursor,carbonate,hydroxide,mineral}` entry must carry `material_class` + `service_temp_c`). Stub builder + system builder both emit empty atoms/bonds/cellVectors/supercell arrays so JSON schema passes. Final state: **83 structures · 66 native + 9 procedural = 75 renderable · 8 metadata-only stubs**, smoke `test_prototype_generators.js` **240/240 PASS**.

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

## Opus 4.8 Expansion (2026-06-01)

_Auto-appended by DEV_SWEEP_2026-06 ENVISION phase. Additive._

> **RESOLUTION — 2026-06-17 (CH-260617-1).** Investigated and largely closed. The audit's headline "gap" was itself a stale receipt: the live `crystal_vr.json` array always held **83** structures (Phase 3.3 content present *and deployed* — live verified byte-identical to the repo). Only the top-level `structureCount` **header field** was stale at 60 — the append scripts grew the array but never updated the header, and nothing validated it. **Fixed:** header → 83, `renderableCount` → 66, plus a new `validate_crystal_vr.py` drift-guard that fails if the header ever diverges from the array again (make-drift-loud). The "MP ingest fails silently / `MP_API_KEY` unvalidated" claims did not reproduce — both `_ingest_mp.py` and `_ingest_mp_silicates.py` already `raise` on an empty `body.get("data")` and `return 2` on a missing key. The leaked personal-email User-Agent **was** real and is now scrubbed from all three ingest scripts (`_ingest_mp.py`, `_ingest_mp_silicates.py`, `_add_new_ht.py`).

**Audit snapshot (2026-06-01, as originally written):** 0 P0, 3 P1 (the headline: Phase 3.3 marked COMPLETE in plan but live data still Phase 3.2 — 60 vs claimed 83 structures; MP ingest fails silently; `MP_API_KEY` unvalidated). Security-clean, live. *Preserved verbatim; see resolution above — the 60/83 figure was a stale header field, not missing data, and the ingest claims did not reproduce.*

### Near-term (audit remediation) — ✅ DONE 2026-06-17

- ✅ Plan-vs-reality gap resolved: the 83 structures were already produced, committed, and deployed; corrected the stale `structureCount`/`renderableCount` header and added the validator drift-guard so it cannot recur.
- ✅ MP ingest hardening: data + key validation were already present; scrubbed the leaked personal-email User-Agent from all three ingest scripts.

### Mid-term (capability) — still open

- Make `validate_crystal_vr.py` schema-version aware so it doesn't fail against live data when Phase 3.3 fields are absent.
- Wire `test_prototype_generators.js` (240 assertions) into a CI hook + add an end-to-end `crystal_vr.json` load test for the viewer.

### Long-term (vision) — still open

- Continuous Materials Project ingest pipeline with schema-drift detection; a CHANGELOG tying each data `version` to a deployed phase so plan drift becomes structurally impossible.
