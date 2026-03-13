import gzip
import csv
import pandas as pd

gaf_file = "data/raw/goa_uniprot_all.gaf.gz"
proteins_file = "data/processed/proteins_all_clean.csv"
output_file = "data/processed/protein_go_rel.csv"

# Charger les accessions de protéines déjà retenues dans le projet
proteins_df = pd.read_csv(proteins_file)
valid_accessions = set(proteins_df["accession"].dropna().astype(str).unique())

print(f"Nombre d'accessions protéines retenues : {len(valid_accessions)}")

rows = []
total_lines = 0
kept_lines = 0
comment_lines = 0

with gzip.open(gaf_file, "rt", encoding="utf-8") as f:
    for line in f:
        total_lines += 1

        if line.startswith("!"):
            comment_lines += 1
            continue

        parts = line.strip().split("\t")

        # Vérification minimale format GAF
        if len(parts) < 15:
            continue

        db = parts[0]
        db_object_id = parts[1]
        qualifier = parts[3]
        go_id = parts[4]
        reference = parts[5]
        evidence_code = parts[6]
        aspect = parts[8]
        assigned_by = parts[14]

        # On garde seulement les entrées UniProtKB
        if db != "UniProtKB":
            continue

        accession = db_object_id.strip()

        # On garde seulement les protéines présentes dans proteins_all_clean.csv
        if accession not in valid_accessions:
            continue

        rows.append({
            "accession": accession,
            "go_id": go_id,
            "evidence_code": evidence_code,
            "reference": reference,
            "aspect": aspect,
            "assigned_by": assigned_by,
            "qualifier": qualifier
        })
        kept_lines += 1

df = pd.DataFrame(rows)

# Ajouter le nom complet de l'aspect
aspect_map = {
    "P": "biological_process",
    "F": "molecular_function",
    "C": "cellular_component"
}

df["aspect_name"] = df["aspect"].map(aspect_map)

# Supprimer les doublons exacts
df = df.drop_duplicates()

df.to_csv(output_file, index=False)

print("\nParsing GOA terminé.")
print(f"Lignes totales lues : {total_lines}")
print(f"Lignes commentaires ignorées : {comment_lines}")
print(f"Lignes conservées avant déduplication : {kept_lines}")
print(f"Lignes finales après déduplication : {len(df)}")
print(f"Fichier créé : {output_file}")

if not df.empty:
    print("\nAperçu :")
    print(df.head())

    print("\nRépartition des aspects :")
    print(df['aspect'].value_counts(dropna=False))

    print("\nTop evidence codes :")
    print(df['evidence_code'].value_counts(dropna=False).head(10))
