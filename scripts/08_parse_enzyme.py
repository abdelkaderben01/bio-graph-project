import pandas as pd
import re

enzyme_file = "data/raw/enzyme.dat"
proteins_file = "data/processed/proteins_all_clean.csv"

enzyme_nodes_output = "data/processed/enzyme_nodes.csv"
protein_enzyme_rel_output = "data/processed/protein_enzyme_rel.csv"

# 1. Charger les protéines
proteins_df = pd.read_csv(proteins_file)

# Garder seulement les protéines ayant au moins une valeur EC
proteins_with_ec = proteins_df.dropna(subset=["ec_number"]).copy()

print(f"Nombre de protéines avec EC number : {len(proteins_with_ec)}")

# 2. Construire les relations Protein -> Enzyme
relations = []

for _, row in proteins_with_ec.iterrows():
    accession = str(row["accession"]).strip()
    ec_field = str(row["ec_number"]).strip()

    # Séparation sur ; ou ,
    raw_ecs = re.split(r"[;,]", ec_field)

    for ec in raw_ecs:
        ec = ec.strip()
        if ec:
            relations.append({
                "accession": accession,
                "ec_number": ec
            })

protein_enzyme_rel = pd.DataFrame(relations).drop_duplicates()

print(f"Relations Protein-Enzyme finales : {len(protein_enzyme_rel)}")

# 3. Parser enzyme.dat
enzyme_entries = []
current_id = None
current_name = None

with open(enzyme_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.rstrip()

        if line.startswith("ID   "):
            current_id = line.replace("ID   ", "").strip()
            current_name = None

        elif line.startswith("DE   "):
            current_name = line.replace("DE   ", "").strip()

        elif line.startswith("//"):
            if current_id:
                enzyme_entries.append({
                    "ec_number": current_id,
                    "enzyme_name": current_name
                })
            current_id = None
            current_name = None

enzyme_nodes = pd.DataFrame(enzyme_entries).drop_duplicates()

print(f"Nœuds Enzyme extraits depuis enzyme.dat : {len(enzyme_nodes)}")

# 4. Filtrer les enzymes vraiment utilisées
used_ec_numbers = set(protein_enzyme_rel["ec_number"].astype(str).unique())
enzyme_nodes_used = enzyme_nodes[enzyme_nodes["ec_number"].astype(str).isin(used_ec_numbers)].copy()

print(f"Nœuds Enzyme réellement utilisés : {len(enzyme_nodes_used)}")

# 5. Sauvegarder
protein_enzyme_rel.to_csv(protein_enzyme_rel_output, index=False)
enzyme_nodes_used.to_csv(enzyme_nodes_output, index=False)

print(f"Fichier créé : {protein_enzyme_rel_output}")
print(f"Fichier créé : {enzyme_nodes_output}")

if not protein_enzyme_rel.empty:
    print("\nAperçu relations :")
    print(protein_enzyme_rel.head())

if not enzyme_nodes_used.empty:
    print("\nAperçu enzymes :")
    print(enzyme_nodes_used.head())
