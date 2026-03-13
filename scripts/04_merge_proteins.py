import pandas as pd

human_file = "data/processed/proteins_human_clean.csv"
rat_file = "data/processed/proteins_rat_clean.csv"
output_file = "data/processed/proteins_all_clean.csv"

df_human = pd.read_csv(human_file)
df_rat = pd.read_csv(rat_file)

df_all = pd.concat([df_human, df_rat], ignore_index=True)

if "accession" in df_all.columns:
    df_all = df_all.drop_duplicates(subset=["accession"])

df_all.to_csv(output_file, index=False)

print("Fichier fusionné créé :", output_file)
print("Nombre de lignes :", len(df_all))
