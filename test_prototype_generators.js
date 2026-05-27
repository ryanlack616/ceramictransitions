#!/usr/bin/env node
/**
 * Smoke test for Phase 2.5.1 procedural prototype renderer.
 *
 * Extracts the procedural module from index.html and asserts per-prototype
 * invariants (atom count, bond count, coordination numbers, homoatomic policy,
 * finite coordinates). Catches regressions in the generator without needing a
 * browser or the full WebGL viewer.
 *
 * Run: node test_prototype_generators.js
 * Exits non-zero on failure.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HTML_PATH = path.join(__dirname, 'index.html');
const html = fs.readFileSync(HTML_PATH, 'utf8');

// Extract the procedural module between its header comment and the data-loading
// section. Slightly forgiving so future cosmetic edits to the comment don't
// break extraction.
const startMarker = /\/\/ ── Procedural Prototype Renderer/;
const endMarker = /\/\/ ── Data Loading/;
const startIdx = html.search(startMarker);
const endIdx = html.search(endMarker);
if (startIdx < 0 || endIdx < 0 || endIdx <= startIdx) {
  console.error('FAIL: could not locate procedural module markers in index.html');
  process.exit(2);
}
const src = html.slice(startIdx, endIdx);

// Provide a no-op THREE shim — the prototype module doesn't use THREE itself,
// but keep this here in case future helpers reach for it.
const ctx = { console, THREE: { Color: function () {}, Vector3: function () {} } };
vm.createContext(ctx);

// Wrap the extracted (const/let) source in a function so we can return the
// names we care about — top-level `const` doesn't attach to the vm context.
const wrapped = `(function () {
${src}
  return {
    PROTOTYPE_TABLE,
    PROTOTYPE_DEFS,
    FALLBACK_ELEMENT_META,
    FALLBACK_BOND_COLORS,
    generateAtomsFromPrototype,
    ensureElementsCoverage,
    ensureBondColorsCoverage,
    promoteStubsWithPrototypes,
  };
})()`;

let mod;
try {
  mod = vm.runInContext(wrapped, ctx, { filename: 'index.html:procedural' });
} catch (e) {
  console.error('FAIL: error evaluating procedural module:', e.message);
  process.exit(2);
}

const PROTOTYPE_TABLE = mod.PROTOTYPE_TABLE;
const generateAtomsFromPrototype = mod.generateAtomsFromPrototype;
const ensureElementsCoverage = mod.ensureElementsCoverage;
const FALLBACK_ELEMENT_META = mod.FALLBACK_ELEMENT_META;
const FALLBACK_BOND_COLORS = mod.FALLBACK_BOND_COLORS;

if (!PROTOTYPE_TABLE || !generateAtomsFromPrototype) {
  console.error('FAIL: procedural module missing expected exports');
  process.exit(2);
}

// Build elementsMap covering both the fallback elements and the few baseline
// elements (Si, Al, C, O) that the JSON normally provides.
const elementsMap = {
  Si: { color: [0.5, 0.5, 0.6], radius: 1.10 },
  Al: { color: [0.7, 0.7, 0.8], radius: 1.25 },
  C:  { color: [0.3, 0.3, 0.3], radius: 0.70 },
  O:  { color: [0.9, 0.3, 0.3], radius: 0.60 },
  Zr: { color: [0.6, 0.7, 0.8], radius: 1.55 },
};
ensureElementsCoverage(elementsMap);

// Expected coordination number per prototype, by role (cation/anion).
// Approximate ranges — accounts for under-coordinated atoms at supercell edges.
const EXPECTED_CN = {
  rocksalt:   { C: { min: 3, max: 6 }, A: { min: 3, max: 6 } },
  fluorite:   { C: { min: 4, max: 8 }, A: { min: 2, max: 4 } },
  zincblende: { C: { min: 2, max: 4 }, A: { min: 2, max: 4 } },
  wurtzite:   { C: { min: 2, max: 4 }, A: { min: 2, max: 4 } },
  AlB2:       { C: { min: 6, max: 12 }, A: { min: 3, max: 9 } },
  hBN:        { C: { min: 2, max: 3 }, A: { min: 2, max: 3 } },
  si3n4:      { C: { min: 2, max: 4 }, A: { min: 2, max: 4 } },
};

let failures = 0;
let passed = 0;

function check(cond, msg) {
  if (!cond) {
    failures++;
    console.error('  ✗ ' + msg);
  } else {
    passed++;
  }
}

for (const [formula, entry] of Object.entries(PROTOTYPE_TABLE)) {
  console.log(`\n▶ ${formula}  (proto=${entry.proto}, cation=${entry.cation}, anion=${entry.anion})`);
  const s = { formula };
  const gen = generateAtomsFromPrototype(s, elementsMap);

  check(gen !== null, `${formula}: generator returned non-null`);
  if (!gen) continue;

  check(Array.isArray(gen.atoms) && gen.atoms.length > 0, `${formula}: atoms.length > 0 (got ${gen.atoms && gen.atoms.length})`);
  check(Array.isArray(gen.bonds) && gen.bonds.length > 0, `${formula}: bonds.length > 0 (got ${gen.bonds && gen.bonds.length})`);
  check(Array.isArray(gen.cellVectors) && gen.cellVectors.length === 3, `${formula}: cellVectors is 3-row array`);
  check(gen.cellVectors.every(row => Array.isArray(row) && row.length === 3), `${formula}: cellVectors rows are 3-element arrays`);
  check(Array.isArray(gen.supercell) && gen.supercell.length === 3, `${formula}: supercell is 3-element array`);

  // All atom coords finite.
  const allFinite = gen.atoms.every(a => Number.isFinite(a.x) && Number.isFinite(a.y) && Number.isFinite(a.z) && Number.isFinite(a.r));
  check(allFinite, `${formula}: all atom coords finite`);

  // Bonds reference valid atom indices.
  const bondsValid = gen.bonds.every(b =>
    Array.isArray(b) && b.length === 2 &&
    Number.isInteger(b[0]) && Number.isInteger(b[1]) &&
    b[0] >= 0 && b[0] < gen.atoms.length &&
    b[1] >= 0 && b[1] < gen.atoms.length &&
    b[0] !== b[1]
  );
  check(bondsValid, `${formula}: all bond indices valid`);

  // bondTypes parallel array length matches bonds.
  check(Array.isArray(gen.bondTypes) && gen.bondTypes.length === gen.bonds.length, `${formula}: bondTypes length matches bonds`);

  // Homoatomic policy: only AlB2 allows like-like bonds (B-B honeycomb).
  const allowHomo = entry.proto === 'AlB2';
  const homoCount = gen.bonds.filter(([i, j]) => gen.atoms[i].e === gen.atoms[j].e).length;
  if (!allowHomo) {
    check(homoCount === 0, `${formula}: no homoatomic bonds (got ${homoCount})`);
  } else {
    check(homoCount > 0, `${formula}: AlB2 should have B-B honeycomb bonds (got ${homoCount})`);
  }

  // CN range per role.
  const expCN = EXPECTED_CN[entry.proto];
  if (expCN) {
    const cnsC = gen.atoms.filter(a => a.e === entry.cation).map(a => a.cn);
    const cnsA = gen.atoms.filter(a => a.e === entry.anion).map(a => a.cn);
    const maxC = cnsC.length ? Math.max(...cnsC) : 0;
    const maxA = cnsA.length ? Math.max(...cnsA) : 0;
    check(maxC >= expCN.C.min && maxC <= expCN.C.max, `${formula}: max cation CN ${maxC} in [${expCN.C.min},${expCN.C.max}]`);
    check(maxA >= expCN.A.min && maxA <= expCN.A.max, `${formula}: max anion CN ${maxA} in [${expCN.A.min},${expCN.A.max}]`);
  }

  console.log(`  atoms=${gen.atoms.length}  bonds=${gen.bonds.length}  homoBonds=${homoCount}  cellVol=${cellVolume(gen.cellVectors).toFixed(2)} Å³`);
}

// Procedural pairs all have a fallback color (so they don't render grey).
console.log('\n▶ Bond color coverage');
const expectedPairs = new Set();
for (const [formula, entry] of Object.entries(PROTOTYPE_TABLE)) {
  const a = entry.cation, b = entry.anion;
  const pair = [a, b].sort().join('-');
  expectedPairs.add(pair);
  if (entry.proto === 'AlB2') expectedPairs.add('B-B');
}
for (const pair of expectedPairs) {
  check(FALLBACK_BOND_COLORS && FALLBACK_BOND_COLORS[pair], `bond color fallback for ${pair}`);
}

function cellVolume(cv) {
  const [a, b, c] = cv;
  // |a · (b × c)|
  const bx = b[1]*c[2] - b[2]*c[1];
  const by = b[2]*c[0] - b[0]*c[2];
  const bz = b[0]*c[1] - b[1]*c[0];
  return Math.abs(a[0]*bx + a[1]*by + a[2]*bz);
}

console.log(`\n${failures === 0 ? 'PASS' : 'FAIL'}: ${passed} checks passed, ${failures} failed`);
process.exit(failures === 0 ? 0 : 1);
