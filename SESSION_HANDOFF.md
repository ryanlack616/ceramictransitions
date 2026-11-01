# Session Handoff

**Last updated:** 2026-11-01
**Repository:** `ceramictransitions`
**Production host:** GitHub Pages at `https://ceramictransitions.com`
**Legacy mirror:** Porkbun/pixie-sh FTP via `_deploy.py`

## Current State

- Catalog: 113 entries.
- Baked structures: 99.
- Runtime procedural candidates: 9.
- Illustrative system architectures: 5.
- Materials Project-linked records: 98.
- Transition-bearing materials: 13 with 29 rows.
- Provenance statuses are stored in `data/crystal_vr.json`.
- Shared catalog runtime: `viewer-core.js`.
- Shared procedural runtime: `prototype-runtime.js`.
- File fallback bundle: `data/crystal_vr.js`.

## Completed This Session

- Fixed post-sort selection drift.
- Added stable material IDs for share and cross-page links.
- Made Pages deployment validation-gated and artifact-staged.
- Excluded MP cache/source files from the legacy deploy collector.
- Added release manifest generation and post-deploy public verification.
- Added shared prototype/catalog runtimes and removed duplicated prototype code.
- Added catalog/table mode with shared filtering and sorting.
- Added material provenance, operating-envelope, caveat, notes, bookmark, citation, and export workflows.
- Added system layer-stack rendering and transition timelines.
- Added browser smoke, mobile viewport, system, transition, malformed-link, parity, accessibility, deploy-allowlist, audit, and performance checks.
- Added `CHANGELOG.md`, `DEPENDENCIES.md`, and the detailed `MASTER_TASKS.md` expansion program.

## Verification

The final local suite passed:

```text
python3 test_accessibility_contract.py
python3 test_viewer_smoke.py
python3 test_prototype_parity.py
node test_prototype_generators.js
python3 test_deploy_artifact.py
python3 check_performance_budget.py
python3 generate_catalog_audit.py --output /tmp/catalog-audit.json
python3 validate_crystal_vr.py
JSON Schema validation with Draft202012Validator
```

Expected key results:

```text
113 structures · 99 native + 9 procedural = 108 renderable · 5 metadata-only stubs
prototype catalogs match (26 formulas)
SCHEMA: 0 errors
catalog gzip size: approximately 382 KB
largest structure: 540 atoms
```

## Important Files

- `MASTER_TASKS.md` - canonical current backlog and expansion plan.
- `BUILD.md` - current operator, deployment, and verification instructions.
- `data/crystal_vr.json` - canonical catalog.
- `data/crystal_vr.schema.json` - catalog contract.
- `viewer-core.js` - shared catalog identity, normalization, provenance, and application-job runtime.
- `prototype-runtime.js` - shared procedural generator runtime.
- `validate_crystal_vr.py` - data and geometry validator.
- `test_viewer_smoke.py` - Chromium HTTP/file/mobile/browser scenarios.
- `.github/workflows/pages.yml` - validation-gated staged GitHub Pages deployment.

## Next Work

Remaining work is intentionally documented in `MASTER_TASKS.md` and is mostly outside the current foundational implementation:

- Real iOS/Android and axe-core accessibility verification.
- Dedicated architecture browser and deeper system failure/degradation views.
- Contextual facet counts and full compare/filter interaction coverage.
- MP retrieval dates, energy-above-hull, DOI, atmosphere, pressure, and time-scale metadata.
- Lazy-loaded geometry and real-device performance profiling.
- POSCAR/XYZ and glTF/USDZ export validation.
- Taichi-backed polymorph, degradation, stress, and thermal-cycle modeling.

## Worktree Note

No commit, push, or deployment was performed during this session. The worktree contains the implementation and documentation changes listed above, including generated runtime/data artifacts that should be reviewed before staging.
