from pathlib import Path
import pandas as pd

INPUT = Path("data/processed/transactions_clean.csv")
OUTPUT = Path("data/processed/transactions_active_accounts.csv")

def main():
    df = pd.read_csv(INPUT)
    print(f"Original rows: {len(df)}")

    accounts = pd.concat([
        df["source_account"],
        df["target_account"]
    ])

    counts = accounts.value_counts()

    # Lấy tài khoản có ít nhất 5 lần xuất hiện
    active_accounts = set(counts[counts >= 5].index)

    filtered = df[
        df["source_account"].isin(active_accounts)
        & df["target_account"].isin(active_accounts)
    ].copy()

    filtered.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print(f"Filtered rows: {len(filtered)}")
    print(f"Saved to: {OUTPUT}")

if __name__ == "__main__":
    main()
    