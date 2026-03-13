import pandas as pd

files = [
    "data/extracted/uniprotkb_AND_model_organism_9606_2025_02_07 (1).tsv",
    "data/extracted/uniprotkb_AND_model_organism_9606_2026_02_06 (1).tsv",
    "data/extracted/uniprotkb_AND_model_organism_10116_2026_02_06 (1).tsv",
]

for file_path in files:
    print("\n" + "=" * 80)
    print("FICHIER :", file_path)

    df = pd.read_csv(file_path, sep="\t")

    print("Nombre de lignes :", len(df))
    print("Colonnes :")
    for col in df.columns:
        print("-", col)

    print("Aperçu :")
    print(df.head(3))
