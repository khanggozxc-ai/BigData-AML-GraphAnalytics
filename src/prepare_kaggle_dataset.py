from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/HI-Small_Trans.csv")
OUTPUT_FILE = Path("data/processed/transactions_clean.csv")

CHUNK_SIZE = 100_000


def normalize_columns(df: pd.DataFrame, chunk_id: int) -> pd.DataFrame:
    """
    Chuẩn hóa file HI-Small_Trans.csv về schema chung của hệ thống.

    Schema đầu ra:
    - transaction_id
    - source_account
    - target_account
    - amount
    - timestamp
    - transaction_type
    - is_laundering
    """

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


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Làm sạch dữ liệu sau khi đã chuẩn hóa.
    """

    before = len(df)

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

    # Loại self-loop: A -> A
    # Với MVP ngày 1, ta chỉ xét vòng có ít nhất 2 tài khoản khác nhau.
    df = df[df["source_account"] != df["target_account"]]

    df = df.sort_values("timestamp").reset_index(drop=True)

    after = len(df)

    print(f"Rows before cleaning: {before}")
    print(f"Rows after cleaning : {after}")
    print(f"Rows removed        : {before - after}")

    return df


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {RAW_FILE}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    first_write = True
    total_rows = 0

    for chunk_id, chunk in enumerate(
        pd.read_csv(RAW_FILE, chunksize=CHUNK_SIZE),
        start=1,
    ):
        print(f"\nProcessing chunk {chunk_id}...")

        normalized = normalize_columns(chunk, chunk_id)
        cleaned = clean_transactions(normalized)

        cleaned.to_csv(
            OUTPUT_FILE,
            mode="w" if first_write else "a",
            index=False,
            header=first_write,
            encoding="utf-8-sig",
        )

        total_rows += len(cleaned)
        first_write = False

    print("\nDONE")
    print(f"Saved clean data to: {OUTPUT_FILE}")
    print(f"Total clean rows: {total_rows}")


if __name__ == "__main__":
    main()