# Ceramic Transitions Master Task List

**Status:** Proposed execution backlog
**Created:** 2026-10-31
**Current catalog:** 113 entries, 99 baked structures, 9 runtime procedural promotions, 5 metadata-only system entries
**Canonical planning document:** This file

`PLANS.md` is a historical project journal containing completed phases, old snapshots, and design decisions. Use this file for the current actionable backlog. Do not treat old counts or deployment statements in `PLANS.md` as current without checking the repository and release manifest.

## Product Direction

Ceramic Transitions should be treated as two connected surfaces over one trustworthy materials catalog:

- **Analyze:** the flagship viewer for structure, properties, provenance, firing, transitions, comparison, and spatial tools.
- **Behold:** the lattice gallery for large repeated unit cells and visual pattern recognition.

The product should be explicit about the difference between measured or literature-backed structure data, MP-sourced analogues, procedural prototypes, and illustrative composite architectures.

## Priority And Status

- `P0` means release-blocking correctness, deployment safety, or data-integrity work.
- `P1` means important product quality, maintainability, scientific trust, or user workflow work.
- `P2` means valuable capability or polish after the foundation is stable.
- `P3` means exploratory or longer-term product work.
- `[ ]` means not started or not verified.
- `[~]` means partially complete and requiring a closeout pass.
- `[x]` means complete and verified in the current repository.

## Current Baseline

These are capabilities already present and verified during the 2026-10-31 review. They are recorded here so the backlog does not accidentally re-plan completed work.

- [x] `data/crystal_vr.json` is versioned and currently contains 113 entries.
- [x] The Python validator passes the current catalog and catches header-count drift, required fields, classifications, bounds, and transition shape errors.
- [x] The procedural generator smoke test passes 428 checks.
- [x] Materials Project ingestion scripts use an ignored local cache and atomic catalog rewrites.
- [x] The flagship has search, class/temperature filtering, application-job chips, sorting controls, provenance badges, comparison, firing, transitions, share state, screenshot, QR, VR, and AR paths.
- [x] The lattice gallery has search, class/temperature filtering, repeated unit-cell display, and cross-links back to the flagship.
- [x] Fatal data-load overlays exist in both viewers.
- [x] Transition data has been normalized to support both stability windows and point events, with source strings currently present on the published rows.
- [~] The current working tree contains a `file://` fallback bundle, but its tracking, freshness, and deployment policy are unresolved.
- [~] Discovery controls exist, but post-sort selection and some cross-viewer navigation are still incorrect.
- [~] Deployment and planning documentation contains contradictory historical/current statements.

## Milestone M0: Establish The Current Truth

**Goal:** remove ambiguity before changing behavior.

- [x] `P0` Decide whether GitHub Pages or Porkbun/pixie-sh FTP is the authoritative production host. GitHub Pages was verified from the live `Server: GitHub.com` response; FTP is now documented as a legacy mirror.
- [x] `P0` Record the decision in `BUILD.md`, `MASTER_TASKS.md`, and a release manifest.
- [x] `P0` Record the current catalog counts from `data/crystal_vr.json`: total, baked renderable, procedural candidates, runtime renderable, and system entries.
- [x] `P0` Audit the current working tree before the first cleanup commit and preserve the existing viewer changes; the `file://` fallback is now supported through a classic shared runtime script.
- [x] `P0` Define one release artifact list. Pages now stages only the public viewer, data, shared runtime, CNAME, and release manifest.
- [x] `P1` Add a small machine-readable release manifest containing catalog version, source commit, generated-artifact status, validation status, and deployment target.
- [x] `P1` Add a `CHANGELOG.md` or release-history section that records catalog versions and user-visible changes without mixing them into the historical planning journal.
- [ ] `P1` Mark stale sections in `BUILD.md` and `PLANS.md` as historical, then update current instructions to point here.

## Milestone M1: Release Safety And Deployment

**Goal:** invalid or unintended repository content cannot reach production.

### Authoritative Deployment

- [x] `P0` Make the production deployment depend on successful validation. Pages now has a required validation job.
- [x] `P0` If FTP is authoritative, keep the FTP path but remove or clearly disable the competing Pages deployment workflow. The verified Pages host is authoritative and FTP is explicitly secondary.
- [~] `P0` Make deployment fail closed when the expected artifact set is missing, unexpectedly large, or contains development-only paths. Required-file/source checks now fail CI; explicit size thresholds remain.
- [x] `P0` Make `_deploy.py --dry-run` print a clear allowlist summary and fail if `data/.mp_cache`, Python files, Markdown files, test files, or hidden source directories are included. Cache/source exclusions and CI allowlist checks are active.
- [x] `P0` Exclude `data/.mp_cache/` from FTP collection explicitly, not only through `.gitignore`.
- [x] `P0` If Pages is used, upload a staged artifact directory rather than `path: '.'`; never publish the whole source checkout.
- [x] `P1` Add a post-deploy smoke check for both HTML entry points and the canonical data/manifest URLs.
- [x] `P1` Add a post-deploy version/content check that compares the published release manifest/catalog with the expected release.
- [ ] `P1` Document rollback steps for both possible hosts.

### Generated Artifacts

- [x] `P0` Decide whether `data/crystal_vr.js` is committed, generated during deployment, or intentionally local-only. It is generated during the Pages build and retained for local file loading.
- [x] `P0` If it is shipped, track it or generate it in CI and include a freshness check against `data/crystal_vr.json`. Pages regenerates it from the canonical JSON before staging.
- [x] `P0` Local-only fallback alternative rejected: the generated bundle is intentionally retained for direct file loading while Pages regenerates and ships it.
- [ ] `P1` Add a deterministic generator check so JSON serialization, encoding, and generated output are reproducible.
- [x] `P1` Add a build step that produces a clean staging directory containing only deployable files.

### Dependency And Supply-Chain Hardening

- [ ] `P1` Pin GitHub Actions to commit SHAs or establish an intentional version-update policy.
- [ ] `P1` Pin the `jsonschema` CI dependency instead of installing an unconstrained latest version.
- [ ] `P1` Decide how to handle Three.js and QR-code CDN dependencies: pinned versions, integrity verification where supported, local vendoring, or a documented availability fallback.
- [x] `P1` Add a dependency inventory with versions and update ownership.
- [ ] `P2` Add a static security policy appropriate for the inline-module architecture. If a CSP is introduced, refactor inline scripts or use nonces/hashes as part of that work.

## Milestone M2: Fix Current Runtime Correctness

**Goal:** the existing interface must not silently select, link, or display the wrong material.

- [x] `P0` Fix the flagship sort selection closure in `index.html`: click handlers now use `btn.dataset.idx`, never the pre-sort loop index.
- [x] `P0` Add a browser regression test that sorts by every supported key and clicks a post-sort material; the `ct_test=sort` scenario covers all four sort modes.
- [x] `P0` Fix the flagship “View tiled” condition in `index.html`. Renderable entries link to the lattice viewer; system entries explain why no tiled crystal is available.
- [x] `P0` Add a cross-viewer link test for a normal crystal; the headless smoke test covers stable flagship/lattice navigation, with system-specific interaction coverage still open.
- [x] `P0` Replace index-based cross-page links with stable catalog IDs or stable slugs. Share state now uses normalized name/formula keys and accepts legacy indices.
- [x] `P0` Preserve backward compatibility for existing index-based links only if a concrete set of deployed links requires it; legacy `s`/`ci` parameters remain accepted while new links use stable IDs.
- [ ] `P1` Make the lattice viewer and flagship use the same normalized catalog index rather than separate implicit index conventions.
- [ ] `P1` Verify keyboard next/previous behavior after filtering and after a current-structure change.
- [x] `P1` Add explicit no-results states for search and filters instead of leaving an apparently empty list.
- [ ] `P1` Add an explicit retry action to fatal loading errors.
- [ ] `P1` Catch WebGL initialization failures and show a useful fallback instead of allowing an uncaught renderer exception.
- [ ] `P1` Catch per-structure build failures and keep the catalog usable when one record is malformed.

## Milestone M3: Shared Viewer Architecture

**Goal:** the two pages must not drift as separate implementations.

- [x] `P0` Extract the procedural definitions and generator into a shared JavaScript module. Both viewers now consume `prototype-runtime.js`.
- [x] `P0` Extract catalog normalization, deduplication, stub classification, procedural promotion, element fallback, and bond-color fallback into shared code.
- [ ] `P1` Remove the duplicated prototype tables from `index.html` and `lattice.html`.
- [ ] `P1` Give each structure a normalized runtime identity and normalized renderability/provenance fields.
- [x] `P1` Add a single source of truth for catalog identity, renderable subsets, and system-entry classification through `viewer-core.js`.
- [x] `P1` Replace regex extraction in `test_prototype_generators.js` with direct evaluation of the shared runtime namespace.
- [ ] `P1` Separate page-specific UI from shared data/model logic without requiring a framework migration.
- [ ] `P2` Decide whether the project should remain two static HTML entry points or adopt a minimal build step for modules, linting, and bundling.
- [ ] `P2` Avoid a large framework rewrite unless profiling shows that the current architecture cannot support the planned features.

## Milestone M4: Data Contract And Validation

**Goal:** the published catalog is structurally valid, semantically coherent, and honest about its source.

### Schema Model

- [x] `P0` Split the schema into explicit `crystal` and `system` entry branches using `entry_type`; system layers now have their own required shape and crystal/system conditional validation.
- [x] `P0` Define types and constraints for `material_class`, `service_temp_c`, `melting_point_c`, `bound_type`, `application_tags`, `mp_id`, `entry_type`, and `source_quality`.
- [x] `P0` Make transition row requirements explicit: structure identity, valid temperature representation, allowed qualifier, transform type, and source policy.
- [ ] `P1` Restrict `additionalProperties` where practical, while allowing deliberately versioned extension fields.
- [ ] `P1` Add schema versioning and a migration policy.
- [ ] `P1` Validate that transition targets and sibling phase references resolve to known catalog records or are explicitly marked as external phases.

### Geometry Validation

- [x] `P0` Validate every baked bond endpoint against the atom array.
- [x] `P0` Reject self-bonds, malformed bonds, duplicate bonds, and invalid bond-type array lengths.
- [x] `P0` Validate finite atom coordinates, positive radii, nonnegative coordination values, and nonzero cell volume.
- [x] `P1` Validate formula-to-atom stoichiometry for ordinary Unicode-subscript formulas; parenthesized/disordered solid solutions remain explicitly excluded for domain-specific review.
- [ ] `P1` Validate expected element metadata and bond-color coverage for every baked structure.
- [ ] `P1` Validate sensible bond-length distributions and flag outliers for human review rather than blindly rejecting unusual chemistry.
- [ ] `P1` Validate supercell products against atom counts where the record declares a conventional repeat.
- [ ] `P1` Add a per-entry audit report that names the source, geometry status, renderability status, and known caveats.

### Provenance And Epistemic Status

- [x] `P0` Replace the broad `Verified - DFT` label with a more precise taxonomy. The UI now says `MP-sourced`, `MP analogue`, `Procedural`, `Reference`, `System architecture`, or `Metadata only`.
- [x] `P0` Distinguish exact-composition MP structures, MP analogues/substitutions, literature/reference coordinates, procedural prototypes, illustrative systems, and metadata-only entries.
- [x] `P1` Add structured source records instead of relying mainly on prose in `info[]`.
- [ ] `P1` Store MP ID, retrieval date, source formula, source phase, energy-above-hull when available, and any substitution rationale.
- [ ] `P1` Add DOI, URL, or bibliographic identifiers for authored transition claims and key literature structures.
- [x] `P1` Require an uncertainty or caveat field for every non-exact or schematic entry; the migration backfilled missing caveats conservatively.
- [ ] `P1` Preserve processing/application distinctions such as sintered SiC versus crystalline SiC without implying they are different crystal structures.
- [ ] `P1` Make “service temperature in air,” “melting point,” “decomposition point,” and “phase transition temperature” separate typed concepts.
- [ ] `P2` Add measurement conditions: atmosphere, pressure, time scale, and whether a temperature is approximate, onset, range, or sustained limit.

### System And Composite Entries

- [x] `P1` Keep multilayer systems as a separate entry type rather than crystal-shaped stubs; schema and runtime provenance now distinguish them.
- [ ] `P1` Validate layer roles, thickness units, material references, and representative/illustrative status.
- [ ] `P1` Decide whether each system should appear in the crystal browser, a separate architecture browser, or both.
- [ ] `P2` Add a layered stack visualization for TBC, EBC, CMC, C/C, and oxide-oxide systems.
- [ ] `P2` Support clicking a layer to open the corresponding crystal/material record.

## Milestone M5: Browser, CI, And Quality Gates

**Goal:** regressions in the actual product surface are caught before release.

- [x] `P0` Add a browser smoke test that opens `index.html` over HTTP and confirms data loading, first render, structure count, stable share selection, and absence of fatal errors.
- [~] `P0` Add sorting, filtering, selection, share-link, and cross-page navigation tests. Sorting, stable links, and cross-page navigation are covered; broader filter/compare interaction coverage remains.
- [x] `P1` Test procedural promotion in both viewers through shared catalog normalization, matching prototype catalogs, and browser load coverage.
- [ ] `P1` Test metadata-only and system records without uncaught errors.
- [ ] `P1` Test transition panel rendering for window rows, event rows, mixed rows, missing sibling phases, and source links.
- [ ] `P1` Test compare mode, firing mode, melt mode, oxidation mode, screenshot, and QR failure handling.
- [x] `P1` Run browser tests at desktop, tablet, and narrow-mobile viewport sizes; HTTP smoke covers narrow mobile for both viewers.
- [~] `P1` Add a reduced-motion test path. CSS support is present; automated preference emulation remains.
- [ ] `P1` Add HTML and JavaScript lint/syntax checks that operate on stable extracted modules, not fragile comment boundaries.
- [~] `P1` Add accessibility checks with keyboard navigation and automated axe-core scanning. Static accessibility contracts and semantic browser smoke are present; axe/keyboard automation remains.
- [x] `P1` Add a deploy-artifact test that fails if private/cache/source files are present.
- [ ] `P2` Add a small performance budget: initial HTML, data payload, time to first usable structure, and structure-switch latency.
- [ ] `P2` Add visual regression screenshots for the two main surfaces after major UI changes.

## Milestone M6: Interface Information Architecture

**Goal:** users should understand what the site is, find a material quickly, and know how much to trust what they see.

### Entry And Orientation

- [ ] `P1` Add a concise first-run orientation: “Analyze” versus “Lattice gallery,” what a crystal model represents, and what the provenance colors mean.
- [ ] `P1` Add a compact legend for `MP-sourced`, `Reference`, `Procedural`, `System architecture`, and `Metadata only`.
- [ ] `P1` Make the first screen answer three questions immediately: what material is selected, what can I do with it, and how trustworthy is this model?
- [x] `P1` Add a visible catalog count generated from the current data rather than stale hard-coded marketing copy.
- [ ] `P2` Add a small “How to read this view” panel for atoms, bonds, unit cells, and coordination numbers.

### Browse And Discovery

- [~] `P0` Add and unify search, material class, service temperature, application, provenance, and renderability filters in one consistent filtering model across both viewers. The flagship now has provenance/system filtering; the lattice needs the same facet model.
- [x] `P1` Add an explicit “clear all filters” action and a visible active-filter summary.
- [x] `P1` Add result counts to every facet and distinguish “no match” from “not yet renderable.”
- [ ] `P1` Add sort choices that are understandable to non-specialists: name, service temperature, melting/decomposition bound, source confidence, and data completeness.
- [ ] `P1` Add an optional “show architecture records” toggle rather than mixing system entries into crystal results without explanation.
- [ ] `P1` Add aliases and common names so searches such as “lime,” “beryllia,” “YSZ,” “hafnia,” and “SiC” work naturally.
- [ ] `P2` Add facet counts that update against the current filtered result set, with a deliberate choice between stable counts and contextual counts.
- [ ] `P2` Add a compact catalog/table view for users who want to compare materials without opening every 3D model.

### Material Detail Panel

- [x] `P0` Fix the current structure/link behavior before adding more detail fields.
- [ ] `P1` Reorganize the info panel into stable sections: identity, use, operating envelope, structure, provenance, transitions, caveats, and actions.
- [x] `P1` Surface service temperature, melting/decomposition bound, crystal system, atom count, bond count, CTE, thermal shock, oxidation onset, and source quality when available.
- [ ] `P1` Use explicit “unknown” or “not applicable” values instead of silently omitting fields.
- [ ] `P1` Put caveats next to the claim they qualify, especially for schematic and substituted structures.
- [x] `P1` Add direct actions: analyze, view tiled, compare, copy stable link, download metadata, and open source record.
- [ ] `P2` Add a compact provenance drawer rather than making the main panel prose-heavy.

### Transitions And Firing

- [ ] `P1` Make the distinction between firing narrative, phase transition data, and true simulation explicit in the UI.
- [ ] `P1` Show transition temperature ranges as a timeline with source/citation affordances.
- [ ] `P1` Distinguish point events from stability windows visually.
- [ ] `P1` Explain when a transition snaps to another structure instead of morphing atom-by-atom.
- [ ] `P1` Show atmosphere/pressure limitations wherever transition values depend on them.
- [ ] `P2` Add a phase-family timeline that can navigate among sibling records without hiding the current material context.
- [ ] `P2` Add a “schematic visual mode” label directly above melt and oxidation controls.

### Comparison

- [ ] `P1` Make compare mode a first-class workflow from search results, not only a hidden Pro control.
- [ ] `P1` Add a readable property table with units, missing values, provenance status, and source caveats.
- [ ] `P1` Allow comparison of a crystal against a system architecture or clearly prevent invalid comparisons.
- [ ] `P2` Add radar/plot views only if the underlying metadata is complete and normalized; do not visualize incomparable estimated values as precise measurements.

## Milestone M7: Interface Quality, Accessibility, And Mobile

**Goal:** retain the distinctive technical visual language while making the interface legible and usable outside a desktop demo.

- [x] `P0` Add an obvious focus ring to every keyboard-focusable control in the flagship.
- [x] `P1` Give the canvas an accessible label and expose selected-material changes through an `aria-live` region.
- [ ] `P1` Give the structure list proper listbox/tab semantics or use straightforward buttons with predictable keyboard behavior.
- [ ] `P1` Add a skip link to the viewer and a keyboard-accessible route to every major control.
- [x] `P1` Respect `prefers-reduced-motion` by disabling dissolve, camera, and panel animations where appropriate.
- [ ] `P1` Test contrast of provenance badges, dim text, sliders, and active states against WCAG AA targets.
- [ ] `P1` Add touch targets of at least approximately 44px for primary mobile actions.
- [ ] `P1` Reflow the firing controls, compare view, info panel, and filter rail below 720px; remove fixed desktop widths such as the 520px temperature panel on narrow screens.
- [ ] `P1` Ensure the lattice gallery's bottom strip, filters, and info panel do not cover one another on portrait screens.
- [ ] `P1` Add a mobile-friendly material action bar: search, filter, compare, share, and reset camera.
- [~] `P1` Add a visible camera reset button and a clear gesture hint for orbit/pan/zoom. Reset is now present; gesture guidance remains.
- [ ] `P2` Add a bottom-sheet presentation for material details on mobile.
- [ ] `P2` Add a “focus mode” that hides secondary chrome while preserving the 3D object and one key action.
- [ ] `P2` Test Safari iOS, Chrome Android, desktop Chrome, Firefox, and Safari with WebGL enabled and disabled.

## Milestone M8: Performance And Asset Strategy

**Goal:** the atlas should feel immediate without sacrificing geometry quality.

- [~] `P0` Measure current compressed transfer size and first usable render time on slow mobile and desktop connections. Raw/gzip catalog and largest-structure budgets are now enforced; real-device timing remains.
- [ ] `P1` Confirm the host serves JSON/JS/HTML with compression and correct cache headers.
- [ ] `P1` Split a lightweight catalog manifest from heavy coordinates so browse/search does not require all geometry up front.
- [ ] `P1` Lazy-load heavy structure geometry when a material is selected, with a clear loading state.
- [ ] `P1` Add an atom/bond budget and adaptive detail policy for mobile GPUs.
- [ ] `P1` Profile structure switching, comparison, repeat tiling, polyhedra, and screenshots for disposal leaks.
- [ ] `P2` Consider compact binary or compressed coordinate storage only after measuring whether JSON is the actual bottleneck.
- [ ] `P2` Cache normalized catalog and recently viewed geometry where browser storage is available.
- [ ] `P2` Add performance telemetry only if it can be done privacy-consciously and without turning the static site into a backend product.

## Milestone M9: Security And Resilience

**Goal:** reduce avoidable supply-chain, content, and failure-surface risk.

- [x] `P1` Escape catalog-derived names, formulas, element labels, metadata, and source text before inserting them into HTML.
- [ ] `P1` Replace string-built DOM fragments with DOM APIs for user-visible catalog content where practical.
- [ ] `P1` Pin and integrity-check third-party runtime assets or vendor them.
- [ ] `P1` Make QR-code loading failure non-blocking and provide a copy-link fallback.
- [ ] `P1` Add a visible offline/network failure path that explains whether the problem is the viewer, catalog, or CDN dependency.
- [x] `P1` Add safe bounds to share-link numeric parameters so malformed URLs cannot create invalid scale, temperature, slice, and melt state.
- [ ] `P1` Validate query/hash material identifiers against stable IDs rather than using unchecked array positions.
- [ ] `P2` Add dependency and secret scanning to CI.
- [ ] `P2` Add a privacy statement if analytics, telemetry, or external QR/CDN requests remain.

## Milestone M10: Product Capabilities After The Foundation

- [ ] `P2` Export material metadata and coordinates to CSV and a documented machine-readable format.
- [ ] `P2` Evaluate glTF/USDZ export for 3D-printing, presentation, or CAD-adjacent workflows, with clear limits around scientific fidelity.
- [ ] `P2` Add downloadable citation/provenance bundles for individual materials.
- [ ] `P2` Add browser-local bookmarks or comparison sets without requiring accounts or a backend.
- [ ] `P2` Add shareable saved views using stable IDs and versioned state parameters.
- [ ] `P3` Add a data/API boundary only if external consumers need programmatic access; do not add a backend solely to solve static catalog organization.
- [ ] `P3` Integrate the Taichi pipeline through versioned exports and schema checks rather than hand-maintained duplicated structure lists.
- [ ] `P3` Add animated polymorph transformations only when correspondence maps, physical assumptions, and source data are explicit.
- [ ] `P3` Add degradation, oxidation, thermal cycling, and stress visualizations only when backed by an identified model rather than visual randomization.

## Expansion Program EP1: From Atlas To Materials Workspace

**Purpose:** execute the next product phase after the release/data foundation. The
goal is not to add more isolated controls. The goal is to make the existing
catalog coherent, reviewable, citeable, and useful for material decisions.

**Execution rule:** complete each batch in order, run the production verification
suite, and update these checkboxes with file/test references. Do not mark a task
complete because a UI control exists; verify the behavior and its failure state.

### EP1-A: One Shared Runtime

- [x] `P0` Move the full procedural prototype definitions, lattice parameters, bond rules, fallback element metadata, fallback bond colors, and generator into one canonical runtime module.
- [x] `P0` Make both `index.html` and `lattice.html` consume the same prototype module without copied prototype tables or copied generator logic.
- [x] `P0` Keep `file://` loading compatible with the shared runtime and test it in Chromium.
- [~] `P1` Expose one shared catalog API for stable IDs, normalization, provenance, renderable subsets, and application jobs; transition-context normalization remains page-specific.
- [x] `P1` Replace regex-based prototype extraction tests with direct evaluation of the shared runtime namespace.
- [x] `P1` Remove the prototype parity workaround once both pages use the same source module; parity now verifies shared-runtime loading rather than comparing duplicate tables.
- [x] `P1` Add a module-level test for every prototype: generated atoms, bonds, cell, composition, finite coordinates, coordination, and fallback colors.
- [x] `P1` Acceptance: editing a prototype definition in one file changes both viewers, `test_prototype_generators.js` passes, and no duplicate prototype table remains in either HTML page.

### EP1-B: Catalog/Table Discovery Mode

- [x] `P0` Add an explicit toggle between 3D browse mode and compact catalog/table mode.
- [x] `P0` Keep one filter state shared between the table and 3D structure list.
- [~] `P1` Add table columns for material, formula, class, service temperature, melting/decomposition bound, provenance, renderability, transition count, and application jobs. Core identity/class/service/source columns are present; additional columns remain.
- [x] `P1` Make table rows keyboard accessible and selectable into the 3D viewer.
- [x] `P1` Add sortable table ordering through the shared sort control with missing-value-last behavior.
- [~] `P1` Add a table row action menu for Analyze, View tiled, Compare, Copy link, Source, and Download metadata. Selection, stable links, tiled/source actions, and metadata download exist; a dedicated row action menu and compare action remain.
- [x] `P1` Show system architectures in a clearly labeled category rather than making them look like crystal records.
- [x] `P1` Add aliases and common names for searches such as lime, beryllia, YSZ, hafnia, and SiC.
- [~] `P2` Add contextual facet counts and a visible active-filter summary. Active-filter summary is present; contextual facet counts remain.
- [x] `P2` Add a table export of the current filtered result set.
- [x] `P2` Acceptance: a user can find, sort, select, export, and link a material without opening every 3D model; direct compare/menu coverage remains partial.

### EP1-C: Material Workspace And Interface Hierarchy

- [~] `P0` Reorganize the flagship information panel into Identity, Use, Operating envelope, Structure, Provenance, Transitions, Caveats, and Actions. Provenance, operating envelope, use, caveat, transition, and action sections are now explicit; identity/structure headings and full action coverage remain.
- [ ] `P0` Keep the first screen focused on material identity, key limits, provenance, and the crystal.
- [ ] `P1` Move advanced spatial and chemistry tools into a deliberate analysis drawer instead of exposing every control at once.
- [x] `P1` Add a compact provenance legend for MP-sourced, MP analogue, Reference, Procedural, System architecture, and Metadata only.
- [ ] `P1` Place caveats next to the claims they qualify.
- [x] `P1` Add direct actions for Compare, View tiled, Copy stable link, Download metadata, Open source, and Reset camera.
- [x] `P1` Add explicit Unknown and Not applicable values rather than silently omitting metadata.
- [ ] `P1` Add a first-run orientation describing Analyze versus Lattice gallery, atoms/bonds/cells, and provenance colors.
- [ ] `P2` Add a compact provenance drawer so the main panel does not become prose-heavy.
- [ ] `P2` Add a focus mode that hides secondary chrome while preserving the object and one primary action.
- [ ] `P2` Acceptance: a first-time user can identify the selected material, its use, its confidence level, and the next useful action without opening Pro mode.

### EP1-D: Layered System And Composite Workspace

- [~] `P0` Add a separate system-architecture browser for TBC, EBC, CMC, C/C, and oxide-oxide records. System entries are now clearly categorized in the catalog and render a dedicated layer stack; a separate browser surface remains.
- [x] `P0` Render TBC stack layers with substrate, bond coat, TGO, and topcoat roles.
- [x] `P1` Render EBC and CMC layer stacks with thickness, role, purpose, and cross-reference.
- [x] `P1` Make each layer clickable to its corresponding material/crystal record.
- [x] `P1` Label representative thicknesses and illustrative geometry clearly.
- [x] `P1` Show architecture-level operating envelope and failure modes separately from crystal melting points.
- [ ] `P1` Prevent invalid crystal/system comparisons or explicitly label them as architecture comparisons.
- [ ] `P2` Add system degradation annotations for TGO growth, CMAS infiltration, steam recession, oxidation, and thermal-cycle stress when backed by cited data.
- [ ] `P2` Acceptance: selecting a system opens a meaningful layer view, not a blank crystal overlay, and every referenced layer can navigate to a material record.

### EP1-E: Transition Timeline And Firing UX

- [x] `P0` Replace the current transition list presentation with a horizontal temperature timeline.
- [ ] `P1` Render stability windows as bands and point events as markers.
- [~] `P1` Show source/citation controls on every transition claim. Source text is shown; dedicated citation controls remain.
- [~] `P1` Distinguish reversible, irreversible, decomposition, oxidation, and polymorphic events visually. Timeline/list text includes event types and reversibility; distinct visual styles remain.
- [x] `P1` Show volume-change values with explicit sign and units.
- [ ] `P1` Show atmosphere, pressure, and time-scale caveats where available.
- [x] `P1` Explain why reconstructive transitions snap between structures instead of morphing atom-by-atom.
- [ ] `P1` Add phase-family navigation between sibling records while retaining the current material context.
- [x] `P2` Add an explicit Schematic visual mode label above melt, oxidation, and non-simulation animation controls.
- [ ] `P2` Acceptance: a user can distinguish known data, inferred chain context, and schematic visualization at every point in the firing workflow.

### EP1-F: Browser And Device Quality

- [~] `P0` Add browser tests for metadata-only records, system records, procedural records, catalog/sort workflows, and transitions. Compare, full filter/no-result, and metadata-only interaction cases remain.
- [~] `P1` Add browser tests for firing, melt, oxidation, screenshot, QR fallback, camera reset, and malformed share links. Malformed links and camera/reset-adjacent workflows are covered; feature-specific mode/fallback assertions remain.
- [x] `P1` Run browser tests at desktop, tablet, and narrow-mobile viewports; HTTP smoke covers narrow mobile for both viewers.
- [ ] `P1` Add reduced-motion browser coverage.
- [ ] `P1` Add automated accessibility scanning and keyboard-only navigation coverage.
- [ ] `P1` Add real-device checks for Safari iOS and Chrome Android.
- [ ] `P1` Add a mobile bottom-sheet for filters and material details.
- [ ] `P1` Ensure compare mode stacks correctly in portrait orientation.
- [ ] `P1` Ensure lattice strip, filters, information panel, and controls do not overlap on portrait screens.
- [ ] `P1` Add gesture guidance for orbit, pan, zoom, and camera reset.
- [ ] `P2` Add visual regression screenshots for the two primary surfaces.
- [ ] `P2` Acceptance: the primary browse, select, compare, and share workflows work by keyboard, touch, and desktop pointer input.

### EP1-G: Citation, Export, And Local Research Workflows

- [x] `P0` Add a Copy citation action for each material with MP/reference/transition sources.
- [x] `P1` Add downloadable citation/provenance JSON for a material.
- [x] `P1` Add metadata JSON export for a material.
- [x] `P1` Add atom-coordinate CSV and bond-list CSV exports.
- [x] `P2` Add a table export of the current filtered result set.
- [ ] `P2` Add XYZ/POSCAR-like export with explicit limitations and provenance headers.
- [ ] `P2` Evaluate glTF/USDZ export for presentation and CAD-adjacent use, never implying simulation fidelity.
- [x] `P1` Add browser-local bookmarks, recent materials, saved comparisons, personal notes, and saved filter state without requiring accounts.
- [x] `P1` Make saved views use stable IDs and versioned state parameters.
- [ ] `P2` Add downloadable review bundles containing catalog record, sources, caveats, and selected view state.
- [ ] `P2` Acceptance: a researcher can find a material, compare it, cite it, export its metadata, and reopen the same view later without a backend account.

### EP1-H: Scientific Data Review And Governance

- [x] `P0` Generate a per-entry audit report covering formula, geometry, source, renderability, transitions, missing metadata, and caveats.
- [ ] `P1` Store MP retrieval date, source formula, source phase, energy-above-hull, and substitution rationale where available.
- [ ] `P1` Add DOI/URL/bibliographic identifiers for authored transition and reference-structure claims.
- [ ] `P1` Separate service-in-air, melting, decomposition, phase-transition, oxidation, and thermal-shock concepts in the data model.
- [ ] `P1` Add atmosphere, pressure, time scale, uncertainty, and temperature-basis fields.
- [ ] `P1` Add a human-review report for transition target resolution and external-phase references.
- [x] `P2` Add catalog migration scripts with dry-run reports and reversible output.
- [ ] `P2` Add a versioned source-of-truth contract for howell-help and Taichi ingestion.
- [ ] `P2` Acceptance: every non-schematic claim has an identifiable source or an explicit statement that the data is unavailable/illustrative.

### EP1-I: Performance And Release Completion

- [ ] `P0` Measure first usable render and structure-switch latency on slow mobile and desktop connections.
- [ ] `P1` Split a lightweight catalog manifest from heavy coordinates.
- [ ] `P1` Lazy-load heavy geometry after material selection.
- [ ] `P1` Add adaptive atom/bond detail policies for mobile GPUs.
- [ ] `P1` Profile comparison, repeat tiling, polyhedra, and screenshots for disposal leaks.
- [ ] `P1` Pin GitHub Actions and external runtime dependencies or document the accepted risk.
- [x] `P1` Add dependency inventory, update ownership, rollback instructions, and public release notes.
- [ ] `P2` Add privacy-conscious performance telemetry only if the static-site model still makes sense.
- [ ] `P2` Integrate Taichi exports through versioned schema-checked feeds, not duplicated structure lists.
- [ ] `P3` Add atom-level polymorph/degradation/stress animation only when correspondence maps and physical models exist.
- [ ] `P3` Do not add a backend unless external consumers need programmatic access or collaboration state.
- [ ] `P3` Acceptance: release validation, artifact staging, public verification, performance budget, and current catalog manifest all pass from a clean checkout.

## Recommended Execution Order

1. `M0`: establish host, artifact, count, and source-of-truth decisions.
2. `M1`: close deployment and generated-artifact safety gaps.
3. `M2`: fix sort, cross-page navigation, stable links, and fatal/error behavior.
4. `M5`: add browser tests before further interface expansion.
5. `M3`: extract shared viewer/catalog modules.
6. `M4`: strengthen schemas, geometry validation, and provenance semantics.
7. `M6`: reorganize discovery and material detail around user decisions.
8. `M7`: complete mobile and accessibility work.
9. `M8`: measure and optimize loading/rendering based on evidence.
10. `M9`: harden the static supply chain and content boundaries.
11. `M10`: add exports, architecture visualization, and deeper scientific workflows.

## Definition Of Done For A Production Release

- The authoritative deployment target is documented and unambiguous.
- Validation is a required deployment dependency.
- The deploy artifact contains only intended public files.
- The generated local-file bundle is either reproducibly shipped or intentionally removed.
- Stable material IDs are used for share and cross-page links.
- Browser tests cover load, browse, sort, select, filter, share, compare, transitions, and both viewers.
- Baked and procedural geometry pass the same essential integrity checks.
- Every material exposes a meaningful provenance and caveat status.
- System architectures are either intentionally separated from crystals or rendered as their own entity type.
- Mobile and keyboard workflows are tested, not inferred from CSS.
- Current counts and release version are generated from the catalog.
- Schematic visualizations are labeled as schematic and are not presented as simulations.

## Interface Verdict

The existing interface has a distinctive technical character and a good conceptual split between analysis and visual gallery. It should not be flattened into a generic dashboard. The main improvement is hierarchy, not decoration.

The current flagship presents too many capabilities at once. A new user sees filters, Pinch/Pro, firing, spatial tools, comparison, melt, oxidation, transitions, tour, screenshot, QR, VR, and AR before understanding the material itself. The next interface pass should make the first screen calm and decision-oriented:

- Start with material identity, provenance, key operating limits, and the 3D structure.
- Keep advanced spatial and chemistry tools behind an explicit analysis drawer.
- Make search/filter and compare easier to discover than VR/AR and QR.
- Put the trust status beside every important claim, not only in an isolated badge.
- Use stable, readable labels alongside the existing compact monospace aesthetic.
- Treat the lattice gallery as a deliberate second mode, not as a hidden cross-link.
- Make “what can I learn here?” and “what should I believe here?” equally visible.

The strongest future interface is not a larger control panel. It is a clearer material workspace with a stable identity, an evidence trail, a phase/application story, and an obvious path from discovery to comparison to citation.
