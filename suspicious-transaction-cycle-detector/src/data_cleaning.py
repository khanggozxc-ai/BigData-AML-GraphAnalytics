"""
data_cleaning.py

Làm sạch dữ liệu giao dịch.

Input:
- data/raw/transactions_raw.csv

Output:
- data/processed/transactions_clean.csv
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = [
    "transaction_id",
    "source_account",
    "target_account",
    "amount",
    "timestamp",
]


def clean_transactions(
    input_path: str | Path = "data/raw/transactions_raw.csv",
    output_path: str | Path = "data/processed/transactions_clean.csv",
) -> tuple[pd.DataFrame, dict]:
    input_path = Path(input_path)
    output_path = Path(output_path)

    df = pd.read_csv(input_path)
    initial_rows = len(df)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Chuẩn hóa text
    for col in ["transaction_id", "source_account", "target_account", "transaction_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Chuẩn hóa amount và timestamp
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Đếm lỗi để báo cáo
    quality_report = {
        "initial_rows": initial_rows,
        "duplicate_transaction_id": int(df["transaction_id"].duplicated().sum()),
        "missing_source_or_target": int(
            (df["source_account"].isin(["", "nan", "None"]))
            | (df["target_account"].isin(["", "nan", "None"]))
        ),
        "invalid_amount": int(df["amount"].isna().sum() + (df["amount"] <= 0).sum()),
        "invalid_timestamp": int(df["timestamp"].isna().sum()),
        "self_loop": int((df["source_account"] == df["target_account"]).sum()),
    }

    # Rule cleaning
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")
    df = df[~df["source_account"].isin(["", "nan", "None"])]
    df = df[~df["target_account"].isin(["", "nan", "None"])]
    df = df[df["amount"].notna() & (df["amount"] > 0)]
    df = df[df["timestamp"].notna()]
    df = df[df["source_account"] != df["target_account"]]

    df = df.sort_values("timestamp").reset_index(drop=True)

    quality_report["final_rows"] = len(df)
    quality_report["removed_rows"] = initial_rows - len(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    return df, quality_report


if __name__ == "__main__":
    clean_df, report = clean_transactions()
    print("Data quality report:")
    for key, value in report.items():
        print(f"- {key}: {value}")
