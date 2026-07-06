from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/HI-Small_Trans.csv")
CLEAN_OUTPUT = Path("data/processed/transactions_clean.csv")
GRAPH_OUTPUT = Path("data/processed/transactions_graph_edges.csv")
REPORT_OUTPUT = Path("data/processed/data_quality_report.csv")

CHUNK_SIZE = 100_000


def normalize_columns(df: pd.DataFrame, chunk_id: int) -> pd.DataFrame:
    required_cols = [
        "Timestamp",
        "From Bank",
        "Account",
        "To Bank",
        "Account.1",
        "Amount Paid",
        "Payment Format",
        "Is Laundering",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset thiếu các cột bắt buộc: {missing}")

    output = pd.DataFrame()

    output["transaction_id"] = [
        f"T{chunk_id:04d}_{i:07d}" for i in range(len(df))
    ]

    output["source_account"] = (
        df["From Bank"].astype(str).str.strip()
        + "_"
        + df["Account"].astype(str).str.strip()
    )

    output["target_account"] = (
        df["To Bank"].astype(str).str.strip()
        + "_"
        + df["Account.1"].astype(str).str.strip()
    )

    output["amount"] = pd.to_numeric(df["Amount Paid"], errors="coerce")
    output["timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    output["transaction_type"] = df["Payment Format"].astype(str).str.strip()

    output["is_laundering"] = (
        pd.to_numeric(df["Is Laundering"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return output


def clean_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    before = len(df)

    invalid_amount = int((df["amount"].isna() | (df["amount"] <= 0)).sum())
    invalid_timestamp = int(df["timestamp"].isna().sum())
    missing_accounts = int(
        (
            df["source_account"].isna()
            | df["target_account"].isna()
            | (df["source_account"].astype(str).str.len() == 0)
            | (df["target_account"].astype(str).str.len() == 0)
        ).sum()
    )
    self_loop = int((df["source_account"] == df["target_account"]).sum())

    df = df.drop_duplicates(subset=["transaction_id"])

    df = df.dropna(
        subset=[
            "source_account",
            "target_account",
            "amount",
            "timestamp",
        ]
    )

    df = df[df["source_account"].astype(str).str.len() > 0]
    df = df[df["target_account"].astype(str).str.len() > 0]
    df = df[df["amount"] > 0]

    df = df.sort_values("timestamp").reset_index(drop=True)

    after = len(df)

    report = {
        "rows_before": before,
        "rows_after_cleaning": after,
        "rows_removed": before - after,
        "invalid_amount": invalid_amount,
        "invalid_timestamp": invalid_timestamp,
        "missing_accounts": missing_accounts,
        "self_loop_rows_kept_in_clean_data": self_loop,
    }

    return df, report


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {RAW_FILE}")

    CLEAN_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    first_write_clean = True
    first_write_graph = True

    total_clean_rows = 0
    total_graph_rows = 0
    reports = []

    for chunk_id, chunk in enumerate(
        pd.read_csv(RAW_FILE, chunksize=CHUNK_SIZE),
        start=1,
    ):
        print(f"\nProcessing chunk {chunk_id}...")

        normalized = normalize_columns(chunk, chunk_id)
        cleaned, report = clean_transactions(normalized)

        graph_edges = cleaned[
            cleaned["source_account"] != cleaned["target_account"]
        ].copy()

        cleaned.to_csv(
            CLEAN_OUTPUT,
            mode="w" if first_write_clean else "a",
            index=False,
            header=first_write_clean,
            encoding="utf-8-sig",
        )

        graph_edges.to_csv(
            GRAPH_OUTPUT,
            mode="w" if first_write_graph else "a",
            index=False,
            header=first_write_graph,
            encoding="utf-8-sig",
        )

        report["chunk_id"] = chunk_id
        report["graph_edge_rows"] = len(graph_edges)
        reports.append(report)

        total_clean_rows += len(cleaned)
        total_graph_rows += len(graph_edges)

        first_write_clean = False
        first_write_graph = False

        print(f"Rows after cleaning : {len(cleaned)}")
        print(f"Graph edge rows     : {len(graph_edges)}")
        print(f"Self-loop rows kept : {report['self_loop_rows_kept_in_clean_data']}")

    report_df = pd.DataFrame(reports)
    report_df.to_csv(REPORT_OUTPUT, index=False, encoding="utf-8-sig")

    print("\nDONE")
    print(f"Saved clean data to       : {CLEAN_OUTPUT}")
    print(f"Saved graph edge data to  : {GRAPH_OUTPUT}")
    print(f"Saved quality report to   : {REPORT_OUTPUT}")
    print(f"Total clean rows          : {total_clean_rows}")
    print(f"Total graph edge rows     : {total_graph_rows}")


if __name__ == "__main__":
    main()