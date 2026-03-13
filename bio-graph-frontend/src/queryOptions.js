// Entity types available as global filter
export const ENTITY_TYPES = [
  { key: "protein",  label: "Protein",   icon: "🧬", inputLabel: "Protein accession", placeholder: "Ex: Q04828" },
  { key: "go",       label: "GO Term",   icon: "🌿", inputLabel: "GO ID",             placeholder: "Ex: GO:0005886" },
  { key: "enzyme",   label: "Enzyme",    icon: "⚗️",  inputLabel: "EC number",         placeholder: "Ex: 1.1.1.1" },
  { key: "interpro", label: "InterPro",  icon: "🔬", inputLabel: "InterPro ID",       placeholder: "Ex: IPR000276" },
];

// Default query to activate when the user switches entity type
export const DEFAULT_QUERY_BY_TYPE = {
  protein:  "protein_neighbors",
  go:       "go_hierarchy",
  enzyme:   "enzyme_to_proteins",
  interpro: "interpro_to_proteins",
};

export const QUERY_OPTIONS = [
  {
    key: "protein_neighbors",
    label: "Protein + neighbours",
    description: "General view around an accession (all relations).",
    entityType: "protein",
  },
  {
    key: "protein_ppn_neighbors",
    label: "PPN: Similar proteins",
    description: "SIMILAR_TO neighbours (Jaccard InterPro weight) around a protein.",
    entityType: "protein",
  },
  {
    key: "protein_go",
    label: "Protein + GO",
    description: "Shows GO annotations for a target protein.",
    entityType: "protein",
  },
  {
    key: "protein_interpro",
    label: "Protein + InterPro",
    description: "Shows InterPro domains for a target protein.",
    entityType: "protein",
  },
  {
    key: "protein_enzyme",
    label: "Protein + Enzyme",
    description: "Shows the HAS_EC link between a protein and its enzyme.",
    entityType: "protein",
  },
  {
    key: "protein_predicted",
    label: "Predicted functions",
    description: "GO annotations predicted by label propagation (PREDICTED_ANNOTATION).",
    entityType: "protein",
  },
  {
    key: "go_hierarchy",
    label: "GO + hierarchy",
    description: "Explores the hierarchical neighbourhood around a GO term.",
    entityType: "go",
  },
  {
    key: "go_annotated_proteins",
    label: "GO + proteins",
    description: "Shows proteins annotated by a given GO term.",
    entityType: "go",
  },
  {
    key: "interpro_to_proteins",
    label: "InterPro + proteins",
    description: "Shows proteins linked to an InterPro entry.",
    entityType: "interpro",
  },
  {
    key: "enzyme_to_proteins",
    label: "Enzyme + proteins",
    description: "Shows proteins linked to an EC number.",
    entityType: "enzyme",
  },
];

export function getQueryOption(queryType) {
  return QUERY_OPTIONS.find((option) => option.key === queryType) || QUERY_OPTIONS[0];
}

export function getQueriesForType(entityType) {
  return QUERY_OPTIONS.filter((option) => option.entityType === entityType);
}
