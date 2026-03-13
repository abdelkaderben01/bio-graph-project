import pandas as pd

wanted_cols = [
    "Entry",
    "Entry Name",
    "Protein names",
    "Gene Names",
    "Organism",
    "Length",
    "Gene Ontology IDs",
    "InterPro",
    "EC number",
]

rename_map = {
    "Entry": "accession",
    "Entry Name": "entry_name",
    "Protein names": "protein_name",
    "Gene Names": "gene_name",
    "Organism": "organism",
    "Length": "length",
    "Gene Ontology IDs": "go_ids",
    "InterPro": "interpro_ids",
    "EC number": "ec_number",
}


def clean_uniprot(input_file: str, output_file: str) -> None:
    df = pd.read_csv(input_file, sep="\t")

    print("\n" + "=" * 80)
    print("Fichier source :", input_file)
    print("Colonnes disponibles :")
    print(df.columns.tolist())

    existing_cols = [col for col in wanted_cols if col in df.columns]
    df = df[existing_cols].copy()
    df = df.rename(columns=rename_map)

    if "accession" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["accession"])
        print("Doublons accession supprimés :", before - len(df))

    df.to_csv(output_file, index=False)

    print("Fichier nettoyé créé :", output_file)
    print("Nombre de lignes finales :", len(df))
    print(df.head())


if __name__ == "__main__":
    clean_uniprot(
        "data/extracted/uniprotkb_AND_model_organism_9606_2026_02_06 (1).tsv",
        "data/processed/proteins_human_clean.csv",
    )

    clean_uniprot(
        "data/extracted/uniprotkb_AND_model_organism_10116_2026_02_06 (1).tsv",
        "data/processed/proteins_rat_clean.csv",
    )
