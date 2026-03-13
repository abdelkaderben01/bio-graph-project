from __future__ import annotations

import argparse
import itertools
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


def build_domain_sets(rel_df: pd.DataFrame) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    protein_to_domains: dict[str, set[str]] = defaultdict(set)
    domain_to_proteins: dict[str, set[str]] = defaultdict(set)

    for row in rel_df.itertuples(index=False):
        accession = str(row.accession).strip()
        ipr_id = str(row.ipr_id).strip()
        if not accession or not ipr_id:
            continue
        protein_to_domains[accession].add(ipr_id)
        domain_to_proteins[ipr_id].add(accession)

    return protein_to_domains, domain_to_proteins


def compute_weighted_ppn(
    protein_to_domains: dict[str, set[str]],
    domain_to_proteins: dict[str, set[str]],
    min_shared: int,
    min_jaccard: float,
    max_domain_frequency: int,
) -> pd.DataFrame:
    pair_intersections: Counter[tuple[str, str]] = Counter()

    ignored_domains = 0
    kept_domains = 0
    for proteins in domain_to_proteins.values():
        if len(proteins) < 2:
            continue
        if len(proteins) > max_domain_frequency:
            ignored_domains += 1
            continue

        kept_domains += 1
        sorted_proteins = sorted(proteins)
        for a, b in itertools.combinations(sorted_proteins, 2):
            pair_intersections[(a, b)] += 1

    rows = []
    for (a, b), inter_size in pair_intersections.items():
        if inter_size < min_shared:
            continue

        union_size = len(protein_to_domains[a] | protein_to_domains[b])
        if union_size == 0:
            continue

        jaccard = inter_size / union_size
        if jaccard < min_jaccard:
            continue

        rows.append(
            {
                "protein_a": a,
                "protein_b": b,
                "weight": round(jaccard, 6),
                "shared_domains": inter_size,
                "union_domains": union_size,
            }
        )

    out_df = pd.DataFrame(rows)
    if not out_df.empty:
        out_df = out_df.sort_values(["weight", "shared_domains"], ascending=[False, False]).reset_index(drop=True)

    print(f"Domaines utilises: {kept_domains} | domaines ignores (trop frequents): {ignored_domains}")
    print(f"Paires candidates apres filtres: {len(out_df)}")
    return out_df


def keep_top_k_neighbors(ppn_df: pd.DataFrame, top_k: int) -> pd.DataFrame:
    if ppn_df.empty or top_k <= 0:
        return ppn_df

    expanded = pd.concat(
        [
            ppn_df[["protein_a", "protein_b", "weight", "shared_domains", "union_domains"]].rename(
                columns={"protein_a": "source", "protein_b": "target"}
            ),
            ppn_df[["protein_a", "protein_b", "weight", "shared_domains", "union_domains"]].rename(
                columns={"protein_b": "source", "protein_a": "target"}
            ),
        ],
        ignore_index=True,
    )

    expanded = expanded.sort_values(["source", "weight", "shared_domains"], ascending=[True, False, False])
    expanded = expanded.groupby("source", as_index=False).head(top_k)

    canonical_rows = []
    seen = set()
    for row in expanded.itertuples(index=False):
        a, b = sorted((row.source, row.target))
        key = (a, b)
        if key in seen:
            continue
        seen.add(key)
        canonical_rows.append(
            {
                "protein_a": a,
                "protein_b": b,
                "weight": row.weight,
                "shared_domains": int(row.shared_domains),
                "union_domains": int(row.union_domains),
            }
        )

    result = pd.DataFrame(canonical_rows).sort_values(["weight", "shared_domains"], ascending=[False, False])
    result = result.reset_index(drop=True)
    print(f"Apres top-{top_k} voisins/proteine: {len(result)} relations")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Protein-Protein SIMILAR_TO graph using Jaccard on InterPro")
    parser.add_argument("--input", default="data/processed/protein_interpro_rel.csv")
    parser.add_argument("--output", default="data/processed/protein_similarity_jaccard.csv")
    parser.add_argument("--min-shared", type=int, default=2)
    parser.add_argument("--min-jaccard", type=float, default=0.2)
    parser.add_argument("--max-domain-frequency", type=int, default=1000)
    parser.add_argument("--top-k-neighbors", type=int, default=25)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    rel_df = pd.read_csv(in_path, usecols=["accession", "ipr_id"]).dropna().drop_duplicates()
    print(f"Relations Protein-InterPro lues: {len(rel_df)}")

    protein_to_domains, domain_to_proteins = build_domain_sets(rel_df)
    print(f"Proteines avec domaines: {len(protein_to_domains)}")
    print(f"Domaines InterPro distincts: {len(domain_to_proteins)}")

    ppn_df = compute_weighted_ppn(
        protein_to_domains=protein_to_domains,
        domain_to_proteins=domain_to_proteins,
        min_shared=args.min_shared,
        min_jaccard=args.min_jaccard,
        max_domain_frequency=args.max_domain_frequency,
    )

    ppn_df = keep_top_k_neighbors(ppn_df, args.top_k_neighbors)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ppn_df.to_csv(out_path, index=False)
    print(f"Fichier cree: {out_path}")


if __name__ == "__main__":
    main()
