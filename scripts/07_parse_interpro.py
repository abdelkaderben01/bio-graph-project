import gzip
import pandas as pd

input_file = "data/raw/protein2ipr.dat.gz"
proteins_file = "data/processed/proteins_all_clean.csv"
rel_output = "data/processed/protein_interpro_rel.csv"
nodes_output = "data/processed/interpro_nodes.csv"

# Charger les protéines du projet
proteins_df = pd.read_csv(proteins_file)
valid_accessions = set(proteins_df["accession"].dropna().astype(str).unique())

print(f"Nombre d'accessions protéines retenues : {len(valid_accessions)}")

relations = []
total_lines = 0
kept_lines = 0

with gzip.open(input_file, "rt", encoding="utf-8") as f:
    for line in f:
        total_lines += 1
        parts = line.strip().split("\t")

        # Format attendu minimal
        if len(parts) < 3:
            continue

        accession = parts[0].strip()
        ipr_id = parts[1].strip()
        ipr_name = parts[2].strip()

        if accession not in valid_accessions:
            continue

        if not ipr_id.startswith("IPR"):
            continue

        relations.append({
            "accession": accession,
            "ipr_id": ipr_id,
            "ipr_name": ipr_name
        })
        kept_lines += 1

rel_df = pd.DataFrame(relations).drop_duplicates()

# Relations Protein -> InterPro
protein_interpro_rel = rel_df[["accession", "ipr_id"]].drop_duplicates()

# Nœuds InterPro
interpro_nodes = rel_df[["ipr_id", "ipr_name"]].drop_duplicates()

protein_interpro_rel.to_csv(rel_output, index=False)
interpro_nodes.to_csv(nodes_output, index=False)

print("\nParsing InterPro terminé.")
print(f"Lignes totales lues : {total_lines}")
print(f"Lignes conservées avant déduplication : {kept_lines}")
print(f"Relations finales Protein-InterPro : {len(protein_interpro_rel)}")
print(f"Nœuds InterPro finaux : {len(interpro_nodes)}")
print(f"Fichier créé : {rel_output}")
print(f"Fichier créé : {nodes_output}")

if not protein_interpro_rel.empty:
    print("\nAperçu relations :")
    print(protein_interpro_rel.head())

if not interpro_nodes.empty:
    print("\nAperçu nœuds InterPro :")
    print(interpro_nodes.head())
