from pathlib import Path
import argparse
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data_cleaning import process_raw_dataset
from src.graph_builder import build_transaction_graph, summarize_graph
from src.cycle_detector import detect_cycles
from src.risk_scoring import score_cycles


GRAPH_EDGES_PATH = PROJECT_ROOT / "data/processed/transactions_graph_edges.csv"
LAUNDERING_SUBGRAPH_PATH = PROJECT_ROOT / "data/processed/transactions_laundering_subgraph.csv"
DEMO_CYCLE_PATH = PROJECT_ROOT / "data/processed/demo_cycle_transactions.csv"
OUTPUT_PATH = PROJECT_ROOT / "data/output/suspicious_cycles.csv"

CHUNK_SIZE = 200_000

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


def build_laundering_subgraph(
    input_path: Path = GRAPH_EDGES_PATH,
    output_path: Path = LAUNDERING_SUBGRAPH_PATH,
    chunk_size: int = CHUNK_SIZE,
) -> None:
    """
    Tạo subgraph tập trung quanh các tài khoản có liên quan đến giao dịch laundering.

    Lý do:
    - File graph edge toàn bộ có thể rất lớn.
    - NetworkX không phù hợp để quét cycle trên hàng triệu edges trong MVP.
    - Subgraph giúp giảm kích thước graph và tập trung vào vùng đáng ngờ.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {input_path}. "
            "Hãy chạy bước clean data trước."
        )

    print("STEP 1 — Finding laundering-related accounts")

    laundering_accounts = set()
    total_rows = 0
    total_laundering_rows = 0

    usecols = ["source_account", "target_account", "is_laundering"]

    for chunk in pd.read_csv(input_path, usecols=usecols, chunksize=chunk_size):
        total_rows += len(chunk)

        laundering_chunk = chunk[chunk["is_laundering"] == 1]

        total_laundering_rows += len(laundering_chunk)

        laundering_accounts.update(laundering_chunk["source_account"].dropna())
        laundering_accounts.update(laundering_chunk["target_account"].dropna())

    print(f"Total graph edge rows: {total_rows}")
    print(f"Laundering rows: {total_laundering_rows}")
    print(f"Laundering-related accounts: {len(laundering_accounts)}")

    if not laundering_accounts:
        raise ValueError("Không tìm thấy tài khoản liên quan đến laundering.")

    print("\nSTEP 2 — Building laundering subgraph")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    first_write = True
    total_subgraph_rows = 0

    for chunk in pd.read_csv(input_path, chunksize=chunk_size):
        subgraph_chunk = chunk[
            chunk["source_account"].isin(laundering_accounts)
            | chunk["target_account"].isin(laundering_accounts)
        ].copy()

        if subgraph_chunk.empty:
            continue

        subgraph_chunk = subgraph_chunk.sort_values("timestamp")

        subgraph_chunk.to_csv(
            output_path,
            mode="w" if first_write else "a",
            index=False,
            header=first_write,
            encoding="utf-8-sig",
        )

        total_subgraph_rows += len(subgraph_chunk)
        first_write = False

    print(f"Subgraph rows: {total_subgraph_rows}")
    print(f"Saved laundering subgraph to: {output_path}")


def create_demo_cycle_dataset(
    input_path: Path = LAUNDERING_SUBGRAPH_PATH,
    output_path: Path = DEMO_CYCLE_PATH,
) -> None:
    """
    Tạo dataset demo có một vòng giao dịch mô phỏng để kiểm thử thuật toán.

    Lưu ý:
    - Dữ liệu demo chỉ dùng để validate thuật toán.
    - Không được trình bày các dòng DEMO là fraud thật.
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {input_path}. "
            "Hãy chạy bước build-subgraph trước."
        )

    df = pd.read_csv(input_path, nrows=100)

    if df.empty:
        raise ValueError("Subgraph rỗng, không thể tạo demo cycle dataset.")

    base_time = pd.to_datetime(df["timestamp"].iloc[0], errors="coerce")

    if pd.isna(base_time):
        base_time = pd.Timestamp.now()

    demo_cycle = pd.DataFrame(
        [
            {
                "transaction_id": "DEMO_CYCLE_001",
                "source_account": "DEMO_ACC_A",
                "target_account": "DEMO_ACC_B",
                "amount": 100000,
                "timestamp": base_time,
                "transaction_type": "ACH",
                "is_laundering": 1,
            },
            {
                "transaction_id": "DEMO_CYCLE_002",
                "source_account": "DEMO_ACC_B",
                "target_account": "DEMO_ACC_C",
                "amount": 98000,
                "timestamp": base_time + pd.Timedelta(minutes=20),
                "transaction_type": "ACH",
                "is_laundering": 1,
            },
            {
                "transaction_id": "DEMO_CYCLE_003",
                "source_account": "DEMO_ACC_C",
                "target_account": "DEMO_ACC_A",
                "amount": 97000,
                "timestamp": base_time + pd.Timedelta(minutes=40),
                "transaction_type": "ACH",
                "is_laundering": 1,
            },
        ]
    )

    output_df = pd.concat([df, demo_cycle], ignore_index=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saved demo cycle dataset to: {output_path}")
    print(f"Rows: {len(output_df)}")


def run_graph_detection(
    input_path: Path = LAUNDERING_SUBGRAPH_PATH,
    output_path: Path = OUTPUT_PATH,
    max_rows: int | None = 100_000,
    min_cycle_length: int = 2,
    max_cycle_length: int = 6,
) -> None:
    """
    Chạy pipeline graph analytics:
    - Load dữ liệu transaction graph
    - Build directed graph
    - Detect transaction cycles
    - Risk scoring
    - Xuất suspicious_cycles.csv
    """

    if not input_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file: {input_path}. "
            "Hãy chạy bước build-subgraph trước."
        )

    print("STEP 1 — Load graph transactions")

    if max_rows is None:
        df = pd.read_csv(input_path)
    else:
        df = pd.read_csv(input_path, nrows=max_rows)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(
        subset=[
            "source_account",
            "target_account",
            "amount",
            "timestamp",
        ]
    )

    df = df[df["source_account"] != df["target_account"]].copy()

    print(f"Loaded rows: {len(df)}")
    print(f"Unique source accounts: {df['source_account'].nunique()}")
    print(f"Unique target accounts: {df['target_account'].nunique()}")

    if "is_laundering" in df.columns:
        print(f"Laundering rows in input: {int(df['is_laundering'].sum())}")

    print("\nSTEP 2 — Build graph")
    graph = build_transaction_graph(df)
    graph_summary = summarize_graph(graph)
    print(graph_summary)

    print("\nSTEP 3 — Detect cycles")
    cycles = detect_cycles(
        graph,
        min_length=min_cycle_length,
        max_length=max_cycle_length,
    )

    print(f"Detected cycles: {len(cycles)}")

    print("\nSTEP 4 — Risk scoring")

    if cycles:
        result = score_cycles(cycles, df)

        if result.empty:
            result = pd.DataFrame(columns=OUTPUT_COLUMNS)
    else:
        result = pd.DataFrame(columns=OUTPUT_COLUMNS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"\nSaved output to: {output_path}")

    if result.empty:
        print("No cycles found in the current input.")
        print("Output file was still created with headers.")
    else:
        print(result.head(10).to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Main pipeline for AML Graph Analytics project."
    )

    parser.add_argument(
        "--step",
        choices=[
            "clean",
            "subgraph",
            "detect",
            "demo",
            "detect-demo",
            "all",
        ],
        default="detect",
        help=(
            "Pipeline step to run: "
            "clean, subgraph, detect, demo, detect-demo, or all."
        ),
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=100_000,
        help=(
            "Maximum rows used for graph detection. "
            "Use 0 to read all rows from the selected input file."
        ),
    )

    parser.add_argument(
        "--min-cycle-length",
        type=int,
        default=2,
        help="Minimum number of accounts in a detected cycle.",
    )

    parser.add_argument(
        "--max-cycle-length",
        type=int,
        default=6,
        help="Maximum number of accounts in a detected cycle.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    max_rows = None if args.max_rows == 0 else args.max_rows

    if args.step == "clean":
        process_raw_dataset()

    elif args.step == "subgraph":
        build_laundering_subgraph()

    elif args.step == "detect":
        run_graph_detection(
            input_path=LAUNDERING_SUBGRAPH_PATH,
            max_rows=max_rows,
            min_cycle_length=args.min_cycle_length,
            max_cycle_length=args.max_cycle_length,
        )

    elif args.step == "demo":
        create_demo_cycle_dataset()

    elif args.step == "detect-demo":
        run_graph_detection(
            input_path=DEMO_CYCLE_PATH,
            max_rows=max_rows,
            min_cycle_length=args.min_cycle_length,
            max_cycle_length=args.max_cycle_length,
        )

    elif args.step == "all":
        process_raw_dataset()
        build_laundering_subgraph()
        run_graph_detection(
            input_path=LAUNDERING_SUBGRAPH_PATH,
            max_rows=max_rows,
            min_cycle_length=args.min_cycle_length,
            max_cycle_length=args.max_cycle_length,
        )

    else:
        raise ValueError(f"Step không hợp lệ: {args.step}")


if __name__ == "__main__":
    main()