from pathlib import Path
import pandas as pd

INPUT_PATH = Path("data/processed/transactions_graph_edges.csv")
OUTPUT_PATH = Path("data/processed/transactions_laundering_subgraph.csv")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Không tìm thấy data/processed/transactions_graph_edges.csv. "
            "Hãy chạy python src/prepare_kaggle_dataset.py trước."
        )

    print("Loading graph edge data...")
    df = pd.read_csv(INPUT_PATH)

    print(f"Input rows: {len(df)}")

    laundering_df = df[df["is_laundering"] == 1].copy()
    print(f"Laundering rows: {len(laundering_df)}")

    laundering_accounts = set(laundering_df["source_account"]) | set(
        laundering_df["target_account"]
    )

    print(f"Laundering-related accounts: {len(laundering_accounts)}")

    subgraph_df = df[
        df["source_account"].isin(laundering_accounts)
        | df["target_account"].isin(laundering_accounts)
    ].copy()

    subgraph_df = subgraph_df.sort_values("timestamp")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    subgraph_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Subgraph rows: {len(subgraph_df)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()