"""
Export graph data for Neo4j import.

Mục tiêu:
- MVP hiện tại dựng graph tạm bằng NetworkX từ CSV.
- Phase 2 đề xuất Neo4j làm graph storage.
- File này xuất nodes và edges để có thể import vào Neo4j sau.

Cách chạy:
    python src/export_neo4j.py

Input mặc định:
    data/processed/transactions_graph_edges.csv

Output:
    data/neo4j/accounts_nodes.csv
    data/neo4j/transactions_edges.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_CANDIDATES = [
    PROJECT_ROOT / "data/processed/transactions_graph_edges.csv",
    PROJECT_ROOT / "data/processed/transactions_laundering_subgraph.csv",
]

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/neo4j"


def resolve_input_path(input_arg: str | None) -> Path:
    """Chọn file input hợp lệ."""
    if input_arg:
        path = PROJECT_ROOT / input_arg if not Path(input_arg).is_absolute() else Path(input_arg)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy input: {path}")
        return path

    for path in DEFAULT_INPUT_CANDIDATES:
        if path.exists():
            return path

    expected = "\n".join(str(path) for path in DEFAULT_INPUT_CANDIDATES)
    raise FileNotFoundError(
        "Không tìm thấy file graph edges. Hãy chạy pipeline trước.\n"
        f"Các vị trí đã thử:\n{expected}"
    )


def normalize_edges(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa schema edge cho Neo4j."""
    columns = set(df.columns)

    if {"source_account", "target_account"}.issubset(columns):
        source_col = "source_account"
        target_col = "target_account"
    elif {"src", "dst"}.issubset(columns):
        source_col = "src"
        target_col = "dst"
    else:
        raise ValueError(
            "Input cần có cột source_account,target_account hoặc src,dst. "
            f"Cột hiện có: {list(df.columns)}"
        )

    output = pd.DataFrame()
    output["source_account"] = df[source_col].astype(str)
    output["target_account"] = df[target_col].astype(str)

    output["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0) if "amount" in columns else 0
    output["timestamp"] = df["timestamp"].astype(str) if "timestamp" in columns else ""
    output["transaction_type"] = df["transaction_type"].astype(str) if "transaction_type" in columns else ""
    output["is_laundering"] = pd.to_numeric(df["is_laundering"], errors="coerce").fillna(0).astype(int) if "is_laundering" in columns else 0

    output = output.dropna(subset=["source_account", "target_account"])
    output = output[output["source_account"] != output["target_account"]]
    output = output.drop_duplicates()

    return output


def extract_bank_id(account_id: str) -> str:
    """Tách bank_id đơn giản từ account_id nếu có dạng BANK_ACCOUNT."""
    text = str(account_id)

    if "_" in text:
        return text.split("_", 1)[0]

    return "UNKNOWN"


def build_nodes(edges: pd.DataFrame) -> pd.DataFrame:
    """Tạo danh sách account nodes từ edges."""
    accounts = pd.concat(
        [
            edges["source_account"].rename("account_id"),
            edges["target_account"].rename("account_id"),
        ],
        ignore_index=True,
    ).drop_duplicates()

    nodes = pd.DataFrame({"account_id": accounts.astype(str)})
    nodes["bank_id"] = nodes["account_id"].apply(extract_bank_id)
    nodes["label"] = "Account"

    return nodes.sort_values("account_id").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AML graph data to Neo4j CSV format.")
    parser.add_argument("--input", default=None, help="Đường dẫn file CSV graph edges.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Thư mục output Neo4j CSV.")
    parser.add_argument("--limit", type=int, default=0, help="Giới hạn số dòng để export thử. 0 = không giới hạn.")
    args = parser.parse_args()

    input_path = resolve_input_path(args.input)
    output_dir = PROJECT_ROOT / args.output_dir if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Input:", input_path)

    df = pd.read_csv(input_path)

    if args.limit and args.limit > 0:
        df = df.head(args.limit)

    edges = normalize_edges(df)
    nodes = build_nodes(edges)

    nodes_path = output_dir / "accounts_nodes.csv"
    edges_path = output_dir / "transactions_edges.csv"

    nodes.to_csv(nodes_path, index=False, encoding="utf-8-sig")
    edges.to_csv(edges_path, index=False, encoding="utf-8-sig")

    print("[DONE] Nodes:", len(nodes), "->", nodes_path)
    print("[DONE] Edges:", len(edges), "->", edges_path)


if __name__ == "__main__":
    main()
