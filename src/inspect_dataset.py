from pathlib import Path
import pandas as pd

RAW_FILE = Path("data/raw/HI-Small_Trans.csv")


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {RAW_FILE}")

    print("Reading dataset sample...")
    df = pd.read_csv(RAW_FILE, nrows=1000)

    print("\n=== FILE PATH ===")
    print(RAW_FILE)

    print("\n=== SHAPE SAMPLE ===")
    print(df.shape)

    print("\n=== COLUMNS ===")
    for col in df.columns:
        print("-", col)

    print("\n=== FIRST 5 ROWS ===")
    print(df.head())

    print("\n=== DATA TYPES ===")
    print(df.dtypes)

    print("\n=== MISSING VALUES IN SAMPLE ===")
    print(df.isna().sum())


if __name__ == "__main__":
    main()