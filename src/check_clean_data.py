from pathlib import Path
import pandas as pd

CLEAN_PATH = Path("data/processed/transactions_clean.csv")

def main():
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {CLEAN_PATH}")

    df = pd.read_csv(CLEAN_PATH, nrows=10000)

    print("=== SAMPLE SHAPE ===")
    print(df.shape)

    print("\n=== COLUMNS ===")
    print(df.columns.tolist())

    print("\n=== FIRST 5 ROWS ===")
    print(df.head())

    print("\n=== UNIQUE ACCOUNTS ===")
    accounts = pd.concat([df["source_account"], df["target_account"]])
    print(accounts.nunique())

    print("\n=== LAUNDERING LABEL COUNT ===")
    if "is_laundering" in df.columns:
        print(df["is_laundering"].value_counts())

if __name__ == "__main__":
    main()