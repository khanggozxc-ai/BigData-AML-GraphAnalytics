from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.graph_builder import build_transaction_graph, summarize_graph
from src.cycle_detector import detect_cycles
from src.risk_scoring import score_cycles

CLEAN_PATH = PROJECT_ROOT / "data/processed/transactions_laundering_subgraph.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/output/suspicious_cycles.csv"

OUTPUT_COLUMNS = [
    "cycle_id",
    "path",
    "total_amount",
    "duration_minutes",
    "amount_variance",
    "risk_score",
    "risk_level",
    "explanation",
]


def main():
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            "Chưa có data/processed/transactions_graph_edges.csv. "
            "Hãy chạy python src/prepare_kaggle_dataset.py trước."
        )

    print("STEP 1 — Load graph edge transactions")

    # Ngày 1: lấy một phần dữ liệu để tránh NetworkX chạy quá lâu.
    df = pd.read_csv(CLEAN_PATH, nrows=26_397)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print(f"Loaded rows: {len(df)}")
    print(f"Unique source accounts: {df['source_account'].nunique()}")
    print(f"Unique target accounts: {df['target_account'].nunique()}")
    print(f"Laundering rows in sample: {df['is_laundering'].sum()}")

    print("\nSTEP 2 — Build graph")
    graph = build_transaction_graph(df)
    print(summarize_graph(graph))

    print("\nSTEP 3 — Detect cycles")
    cycles = detect_cycles(graph, min_length=2, max_length=6)
    print(f"Detected cycles: {len(cycles)}")

    print("\nSTEP 4 — Risk scoring")

    if cycles:
        result = score_cycles(cycles, df)
    else:
        result = pd.DataFrame(columns=OUTPUT_COLUMNS)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\nSaved output to: {OUTPUT_PATH}")

    if result.empty:
        print("No cycles found in the current sample.")
        print("Output file was still created with headers.")
    else:
        print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()