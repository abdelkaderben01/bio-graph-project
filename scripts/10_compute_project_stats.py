from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def read_optional_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute project statistics required by Task 2")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--output-json", default="data/processed/project_stats.json")
    parser.add_argument("--output-csv", default="data/processed/project_stats_table.csv")
    args = parser.parse_args()

    base = Path(args.processed_dir)

    proteins = pd.read_csv(base / "proteins_all_clean.csv")
    go_rel = read_optional_csv(base / "protein_go_rel.csv", ["accession", "go_id"])
    ec_rel = read_optional_csv(base / "protein_enzyme_rel.csv", ["accession", "ec_number"])
    ipr_rel = read_optional_csv(base / "protein_interpro_rel.csv", ["accession", "ipr_id"])
    sim_rel = read_optional_csv(base / "protein_similarity_jaccard.csv", ["protein_a", "protein_b", "weight"])

    all_proteins = set(proteins["accession"].dropna().astype(str).unique())
    go_proteins = set(go_rel.get("accession", pd.Series(dtype=str)).dropna().astype(str).unique())
    ec_proteins = set(ec_rel.get("accession", pd.Series(dtype=str)).dropna().astype(str).unique())
    ipr_proteins = set(ipr_rel.get("accession", pd.Series(dtype=str)).dropna().astype(str).unique())

    labelled = go_proteins | ec_proteins
    unlabelled = all_proteins - labelled

    if sim_rel.empty:
        isolated = None
    else:
        connected = set(sim_rel["protein_a"].astype(str)).union(set(sim_rel["protein_b"].astype(str)))
        isolated = all_proteins - connected

    stats = {
        "proteins_total": len(all_proteins),
        "proteins_with_go": len(go_proteins),
        "proteins_with_ec": len(ec_proteins),
        "proteins_with_interpro": len(ipr_proteins),
        "labelled_proteins_go_or_ec": len(labelled),
        "unlabelled_proteins_go_and_ec": len(unlabelled),
        "go_annotations_total": int(len(go_rel)),
        "ec_annotations_total": int(len(ec_rel)),
        "interpro_annotations_total": int(len(ipr_rel)),
        "similarity_edges_total": int(len(sim_rel)),
        "isolated_proteins_in_ppn": None if isolated is None else len(isolated),
    }

    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    table_df = pd.DataFrame([{"metric": k, "value": v} for k, v in stats.items()])
    table_df.to_csv(args.output_csv, index=False)

    print("Statistiques calculees:")
    for k, v in stats.items():
        print(f"- {k}: {v}")
    print(f"JSON: {args.output_json}")
    print(f"CSV : {args.output_csv}")


if __name__ == "__main__":
    main()
