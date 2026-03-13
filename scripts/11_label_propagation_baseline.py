from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd


def build_weighted_neighbors(sim_df: pd.DataFrame) -> dict[str, list[tuple[str, float]]]:
    neighbors: dict[str, list[tuple[str, float]]] = defaultdict(list)

    for row in sim_df.itertuples(index=False):
        a = str(row.protein_a)
        b = str(row.protein_b)
        w = float(row.weight)
        neighbors[a].append((b, w))
        neighbors[b].append((a, w))

    return neighbors


def build_labels_map(rel_df: pd.DataFrame, label_col: str) -> dict[str, set[str]]:
    labels: dict[str, set[str]] = defaultdict(set)
    for row in rel_df[["accession", label_col]].dropna().itertuples(index=False):
        labels[str(row.accession)].add(str(getattr(row, label_col)))
    return labels


def propagate_for_label_type(
    proteins: list[str],
    neighbors: dict[str, list[tuple[str, float]]],
    known_labels: dict[str, set[str]],
    top_k: int,
    only_unlabelled: bool,
    label_type: str,
) -> pd.DataFrame:
    rows = []

    for acc in proteins:
        if only_unlabelled and acc in known_labels and known_labels[acc]:
            continue

        score_by_label: dict[str, float] = defaultdict(float)
        support_by_label: dict[str, int] = defaultdict(int)

        for nb, w in neighbors.get(acc, []):
            for label in known_labels.get(nb, set()):
                score_by_label[label] += w
                support_by_label[label] += 1

        if not score_by_label:
            continue

        ranked = sorted(score_by_label.items(), key=lambda x: x[1], reverse=True)[:top_k]
        for rank, (label, score) in enumerate(ranked, start=1):
            rows.append(
                {
                    "accession": acc,
                    "label_type": label_type,
                    "predicted_label": label,
                    "score": round(score, 6),
                    "support_neighbors": support_by_label[label],
                    "rank": rank,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline label propagation on PPN graph")
    parser.add_argument("--proteins", default="data/processed/proteins_all_clean.csv")
    parser.add_argument("--similarity", default="data/processed/protein_similarity_jaccard.csv")
    parser.add_argument("--go-rel", default="data/processed/protein_go_rel.csv")
    parser.add_argument("--ec-rel", default="data/processed/protein_enzyme_rel.csv")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--only-unlabelled", action="store_true")
    parser.add_argument("--output", default="data/processed/protein_label_predictions.csv")
    args = parser.parse_args()

    proteins_df = pd.read_csv(args.proteins, usecols=["accession"]).dropna().drop_duplicates()
    sim_df = pd.read_csv(args.similarity)
    go_df = pd.read_csv(args.go_rel, usecols=["accession", "go_id"]).dropna()
    ec_df = pd.read_csv(args.ec_rel, usecols=["accession", "ec_number"]).dropna()

    proteins = proteins_df["accession"].astype(str).tolist()
    neighbors = build_weighted_neighbors(sim_df)
    go_known = build_labels_map(go_df, "go_id")
    ec_known = build_labels_map(ec_df, "ec_number")

    go_pred = propagate_for_label_type(
        proteins=proteins,
        neighbors=neighbors,
        known_labels=go_known,
        top_k=args.top_k,
        only_unlabelled=args.only_unlabelled,
        label_type="GO",
    )

    ec_pred = propagate_for_label_type(
        proteins=proteins,
        neighbors=neighbors,
        known_labels=ec_known,
        top_k=args.top_k,
        only_unlabelled=args.only_unlabelled,
        label_type="EC",
    )

    out_df = pd.concat([go_pred, ec_pred], ignore_index=True)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print(f"Predictions ecrites: {out_path}")
    print(f"Lignes GO: {len(go_pred)} | Lignes EC: {len(ec_pred)} | Total: {len(out_df)}")


if __name__ == "__main__":
    main()
