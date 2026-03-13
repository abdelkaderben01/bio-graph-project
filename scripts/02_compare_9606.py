import pandas as pd

file1 = "data/extracted/uniprotkb_AND_model_organism_9606_2025_02_07 (1).tsv"
file2 = "data/extracted/uniprotkb_AND_model_organism_9606_2026_02_06 (1).tsv"

df1 = pd.read_csv(file1, sep="\t")
df2 = pd.read_csv(file2, sep="\t")

print("File 1 rows :", len(df1))
print("File 2 rows :", len(df2))

print("\nColonnes file 1 :")
print(df1.columns.tolist())

print("\nColonnes file 2 :")
print(df2.columns.tolist())

print("\nMême colonnes ?", list(df1.columns) == list(df2.columns))
