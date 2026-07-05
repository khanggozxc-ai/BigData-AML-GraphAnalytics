"""
main.py

Pipeline ngày 1:
1. Tạo dữ liệu raw
2. Làm sạch dữ liệu
3. Dựng graph
4. Tìm vòng giao dịch
5. Chấm điểm rủi ro
6. Xuất suspicious_cycles.csv
"""

from __future__ import annotations

from pathlib import Path
import sys

# Cho phép chạy file trực tiếp bằng: python src/main.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data_generator import generate_transactions
from src.data_cleaning import clean_transactions
from src.graph_builder import build_transaction_graph, summarize_graph
from src.cycle_detector import detect_cycles
from src.risk_scoring import score_cycles


RAW_PATH = PROJECT_ROOT / "data/raw/transactions_raw.csv"
CLEAN_PATH = PROJECT_ROOT / "data/processed/transactions_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/output/suspicious_cycles.csv"


def run_pipeline() -> None:
    print("STEP 1 — Generate raw data")
    raw_df = generate_transactions(RAW_PATH)
    print(f"Raw transactions: {len(raw_df)}")

    print("\nSTEP 2 — Clean transactions")
    clean_df, quality_report = clean_transactions(RAW_PATH, CLEAN_PATH)
    for key, value in quality_report.items():
        print(f"- {key}: {value}")

    print("\nSTEP 3 — Build directed graph")
    graph = build_transaction_graph(clean_df)
    print(summarize_graph(graph))

    print("\nSTEP 4 — Detect cycles")
    cycles = detect_cycles(graph, min_length=3, max_length=6)
    print(f"Detected cycles: {len(cycles)}")

    print("\nSTEP 5 — Risk scoring")
    suspicious_df = score_cycles(cycles, clean_df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    suspicious_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nSaved output to: {OUTPUT_PATH}")
    if suspicious_df.empty:
        print("No suspicious cycles found.")
    else:
        print(suspicious_df.head(10).to_string(index=False))


if __name__ == "__main__":
    run_pipeline()
