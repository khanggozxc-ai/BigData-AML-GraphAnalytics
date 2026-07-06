from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.graph_builder import build_transaction_graph, summarize_graph
from src.cycle_detector import detect_cycles
from src.risk_scoring import score_cycles

CLEAN_PATH = PROJECT_ROOT / "data/processed/transactions_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/output/suspicious_cycles.csv"

def main():
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            "Chưa có data/processed/transactions_clean.csv. "
            "Hãy chạy python src/prepare_kaggle_dataset.py trước."
        )

    print("STEP 1 — Load clean transactions")

    # Để chạy nhanh ngày 1, chỉ lấy một phần dữ liệu trước.
    # Khi pipeline ổn mới tăng lên.
    df = pd.read_csv(CLEAN_PATH, nrows=200_000)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print(f"Loaded rows: {len(df)}")
    print(f"Unique source accounts: {df['source_account'].nunique()}")
    print(f"Unique target accounts: {df['target_account'].nunique()}")

    print("\nSTEP 2 — Build graph")
    graph = build_transaction_graph(df)
    print(summarize_graph(graph))

    print("\nSTEP 3 — Detect cycles")
    cycles = detect_cycles(graph, min_length=3, max_length=6)
    print(f"Detected cycles: {len(cycles)}")

    print("\nSTEP 4 — Risk scoring")
    result = score_cycles(cycles, df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nSaved output to: {OUTPUT_PATH}")

    if result.empty:
        print("Không tìm thấy cycle trong 50,000 dòng đầu.")
        print("Ngày 1 xử lý: tăng nrows hoặc lọc theo các tài khoản có giao dịch nhiều.")
    else:
        print(result.head(10).to_string(index=False))

if __name__ == "__main__":
    main()