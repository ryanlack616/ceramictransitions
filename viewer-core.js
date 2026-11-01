// Shared catalog runtime used by both static viewers.
// A classic script namespace is intentional: direct file:// opening blocks
// local ES-module imports in several browsers.
(function (global) {
  function normalized(value) {
    return String(value || '').normalize('NFKC').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function structureKey(structure) {
    return normalized(`${structure.name}|${structure.formula}`);
  }

  function findStructureIndexByKey(data, key) {
    if (!data || !key || !Array.isArray(data.structures)) return -1;
    return data.structures.findIndex(structure => structureKey(structure) === key);
  }

  function normalizeCatalog(data) {
    if (!data || !Array.isArray(data.structures)) {
      throw new Error('Catalog is missing structures[]');
    }

    // Keep the most complete record when an ingestion pass appends a duplicate.
    const seen = new Map();
    for (const structure of data.structures) {
      const key = structureKey(structure);
      const previous = seen.get(key);
      const atomCount = Array.isArray(structure.atoms) ? structure.atoms.length : 0;
      const previousCount = previous && Array.isArray(previous.atoms) ? previous.atoms.length : -1;
      if (!previous || atomCount > previousCount) seen.set(key, structure);
    }

    data.structures = [...seen.values()];
    data.structures.forEach(structure => {
      const cell = structure.cellVectors;
      const hasCell = Array.isArray(cell)
        && cell.length >= 3
        && cell.every(row => Array.isArray(row) && row.length >= 3);
      const hasAtoms = Array.isArray(structure.atoms) && structure.atoms.length > 0;
      structure.isStub = !(hasCell && hasAtoms);
      if (!Array.isArray(structure.atoms)) structure.atoms = [];
      if (!Array.isArray(structure.bonds)) structure.bonds = [];
      if (!Array.isArray(structure.supercell) || structure.supercell.length !== 3) structure.supercell = [1, 1, 1];
    });

    data.structureCount = data.structures.length;
    data.renderableStructures = data.structures.filter(structure => !structure.isStub);
    data.renderableCount = data.renderableStructures.length;
    return data;
  }

  function provenanceKind(structure) {
    if (structure.entry_type === 'system') return 'system';
    if (structure.isStub) return 'stub';
    if (structure.proceduralFallback) return 'procedural';
    if (structure.mp_id) return 'mp-sourced';
    return 'reference';
  }

  const TAG_GROUPS = {
    "Thermal barrier coating": ["tbc","tbc-topcoat","tbc-topcoat-standard","tbc-topcoat-legacy","tbc-topcoat-pyrochlore","tbc-topcoat-research","tbc-next-gen","next-gen-tbc","tbc-research","next-gen-thermal-protection","low-thermal-conductivity","lower-thermal-conductivity"],
    "Environmental barrier coating": ["ebc","ebc-topcoat","ebc-intermediate","cmc-protection","sic-cmc-protection","steam-water-vapor-protection","steam-resistant"],
    "Cutting & tooling": ["cutting-tool","tool-coating","cemented-carbide","machinable-ceramic"],
    "Armor": ["armor","transparent-armor"],
    "Abrasive & wear-resistant": ["abrasive","wear-resistant","wear-coating","superhard","hvof-thermal-spray"],
    "Refractory & kiln furniture": ["refractory","refractory-brick","refractory-component","kiln-furniture","kiln-shelf","crucible","molten-metal-handling","foundry-mold"],
    "Hypersonic leading edge": ["hypersonic-leading-edge","atmospheric-reentry"],
    "Rocket nozzle": ["rocket-nozzle"],
    "Gas-turbine hot section": ["turbine-blade","turbine-rotor","turbine-shroud","turbine-hot-section","engine-hot-section","combustor-liner"],
    "MAX phase & damage-tolerant": ["max-phase","damage-tolerant"],
    "Oxidation & CMAS resistant": ["oxidation-resistant","cmas-resistant"],
    "Bearings & seals": ["bearing","bearing-ball","pump-seal","turbocharger-rotor"],
    "Glaze precursor (feldspar/flux)": ["feldspar","flux","feldspathoid","refractory-precursor"],
    "Pigment & ore": ["pigment","white-pigment","iron-ore","tin-ore"],
    "Electronic & thermal management": ["thermal-management","conductive-ceramic","electronic-substrate","breakdown-insulator","high-k-dielectric","low-loss-microwave"],
  };
  const rawTagToJob = {};
  for (const [job, raws] of Object.entries(TAG_GROUPS)) for (const raw of raws) rawTagToJob[raw] = job;
  function jobsForStructure(structure) {
    const jobs = new Set();
    for (const tag of (structure.application_tags || [])) {
      const job = rawTagToJob[String(tag).toLowerCase()];
      if (job) jobs.add(job);
    }
    return jobs;
  }
  function matchesTag(structure, job) { return !job || jobsForStructure(structure).has(job); }

  const SEARCH_ALIASES = {
    "periclase": ["magnesia", "mgo"],
    "calcium oxide": ["lime", "cao"],
    "beryllium oxide": ["beryllia", "beo"],
    "hafnium oxide": ["hafnia", "hfo2"],
    "stabilized zirconia": ["ysz", "zirconia", "tbc"],
    "yttria-stabilized zirconia (3 mol% y2o3)": ["3ysz", "ysz"],
    "yttria-stabilized zirconia (8 mol% y2o3)": ["8ysz", "ysz"],
    "silicon carbide": ["sic", "carborundum"],
    "silicon nitride": ["si3n4"],
    "boron nitride (hexagonal)": ["hbn", "hexagonal boron nitride"],
    "tantalum carbide": ["tac"],
    "hafnium carbide": ["hfc"],
    "zirconium carbide": ["zrc"],
  };
  function searchTextForStructure(structure) {
    const aliases = SEARCH_ALIASES[normalized(structure.name)] || [];
    return [structure.name, structure.formula, ...aliases, ...jobsForStructure(structure)].join(' ').toLowerCase();
  }

  global.ViewerCore = { TAG_GROUPS, findStructureIndexByKey, jobsForStructure, matchesTag, normalizeCatalog, provenanceKind, searchTextForStructure, structureKey };
})(window);
