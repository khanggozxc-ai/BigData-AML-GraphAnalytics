from pathlib import Path
from typing import Tuple

import pandas as pd


RAW_FILE = Path("data/raw/HI-Small_Trans.csv")
CLEAN_OUTPUT = Path("data/processed/transactions_clean.csv")
GRAPH_OUTPUT = Path("data/processed/transactions_graph_edges.csv")
REPORT_OUTPUT = Path("data/processed/data_quality_report.csv")

CHUNK_SIZE = 100_000


def clean_text(series: pd.Series) -> pd.Series:
    """
    Chuẩn hóa dữ liệu dạng text:
    - Ép kiểu string
    - Xóa khoảng trắng thừa
    - Chuyển chuỗi rỗng thành NA
    """
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    )


def normalize_columns(df: pd.DataFrame, chunk_id: int) -> pd.DataFrame:
    """
    Chuẩn hóa schema gốc của IBM AML dataset thành schema thống nhất
    dùng cho graph analytics.

    Schema đầu ra:
    - transaction_id
    - source_account
    - target_account
    - amount
    - timestamp
    - transaction_type
    - is_laundering
    """

    # Quan trọng: reset_index để tránh lỗi lệch index giữa các chunk.
    df = df.rename(columns=lambda col: str(col).strip()).reset_index(drop=True)

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

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Dataset thiếu các cột bắt buộc: {missing_cols}")

    output = pd.DataFrame()

    output["transaction_id"] = [
        f"T{chunk_id:04d}_{i:07d}" for i in range(len(df))
    ]

    from_bank = clean_text(df["From Bank"])
    from_account = clean_text(df["Account"])
    to_bank = clean_text(df["To Bank"])
    to_account = clean_text(df["Account.1"])

    output["source_account"] = from_bank + "_" + from_account
    output["target_account"] = to_bank + "_" + to_account

    amount_text = (
        df["Amount Paid"]
        .astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
    )

    output["amount"] = pd.to_numeric(amount_text, errors="coerce")

    timestamp_text = df["Timestamp"].astype("string").str.strip()
    output["timestamp"] = pd.to_datetime(timestamp_text, errors="coerce")

    output["transaction_type"] = clean_text(df["Payment Format"])

    output["is_laundering"] = (
        pd.to_numeric(df["Is Laundering"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return output


def clean_transactions(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """
    Làm sạch dữ liệu transaction đã được normalize.

    Điều kiện giữ lại:
    - source_account không rỗng
    - target_account không rỗng
    - amount hợp lệ và > 0
    - timestamp hợp lệ

    Lưu ý:
    - Không xóa self-loop ở bước này.
    - Self-loop được giữ trong transactions_clean.csv.
    - Self-loop chỉ bị loại khi tạo transactions_graph_edges.csv.
    """

    before = len(df)

    invalid_amount = int((df["amount"].isna() | (df["amount"] <= 0)).sum())
    invalid_timestamp = int(df["timestamp"].isna().sum())

    missing_accounts = int(
        (
            df["source_account"].isna()
            | df["target_account"].isna()
            | (df["source_account"].astype("string").str.strip() == "")
            | (df["target_account"].astype("string").str.strip() == "")
        ).sum()
    )

    self_loop = int((df["source_account"] == df["target_account"]).sum())

    valid_mask = (
        df["source_account"].notna()
        & df["target_account"].notna()
        & df["amount"].notna()
        & (df["amount"] > 0)
        & df["timestamp"].notna()
    )

    cleaned = df[valid_mask].copy()
    cleaned = cleaned.sort_values("timestamp").reset_index(drop=True)

    after = len(cleaned)

    report = {
        "rows_before": before,
        "rows_after_cleaning": after,
        "rows_removed": before - after,
        "invalid_amount": invalid_amount,
        "invalid_timestamp": invalid_timestamp,
        "missing_accounts": missing_accounts,
        "self_loop_rows_kept_in_clean_data": self_loop,
    }

    return cleaned, report


def create_graph_edges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo tập dữ liệu cạnh cho graph.

    Graph edge chỉ giữ giao dịch có:
    source_account != target_account

    Vì trong graph analytics:
    - Account là node
    - Transaction là directed edge
    - Self-loop A -> A không phục vụ tốt cho phát hiện vòng nhiều tài khoản
    """

    graph_edges = df[df["source_account"] != df["target_account"]].copy()
    graph_edges = graph_edges.reset_index(drop=True)

    return graph_edges


def process_raw_dataset(
    raw_file: Path = RAW_FILE,
    clean_output: Path = CLEAN_OUTPUT,
    graph_output: Path = GRAPH_OUTPUT,
    report_output: Path = REPORT_OUTPUT,
    chunk_size: int = CHUNK_SIZE,
) -> None:
    """
    Xử lý toàn bộ IBM AML dataset theo từng chunk để tránh quá tải RAM.

    Output:
    - data/processed/transactions_clean.csv
    - data/processed/transactions_graph_edges.csv
    - data/processed/data_quality_report.csv
    """

    if not raw_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {raw_file}")

    clean_output.parent.mkdir(parents=True, exist_ok=True)

    first_write_clean = True
    first_write_graph = True

    total_clean_rows = 0
    total_graph_rows = 0
    reports = []

    for chunk_id, chunk in enumerate(
        pd.read_csv(raw_file, chunksize=chunk_size),
        start=1,
    ):
        print(f"\nProcessing chunk {chunk_id}...")

        normalized = normalize_columns(chunk, chunk_id)
        cleaned, report = clean_transactions(normalized)
        graph_edges = create_graph_edges(cleaned)

        cleaned.to_csv(
            clean_output,
            mode="w" if first_write_clean else "a",
            index=False,
            header=first_write_clean,
            encoding="utf-8-sig",
        )

        graph_edges.to_csv(
            graph_output,
            mode="w" if first_write_graph else "a",
            index=False,
            header=first_write_graph,
            encoding="utf-8-sig",
        )

        report["chunk_id"] = chunk_id
        report["graph_edge_rows"] = len(graph_edges)

        reports.append(report)

        total_clean_rows += len(cleaned)
        total_graph_rows += len(graph_edges)

        first_write_clean = False
        first_write_graph = False

        print(f"Rows after cleaning : {len(cleaned)}")
        print(f"Graph edge rows     : {len(graph_edges)}")
        print(f"Self-loop rows kept : {report['self_loop_rows_kept_in_clean_data']}")

    report_df = pd.DataFrame(reports)
    report_df.to_csv(report_output, index=False, encoding="utf-8-sig")

    print("\nDONE")
    print(f"Saved clean data to       : {clean_output}")
    print(f"Saved graph edge data to  : {graph_output}")
    print(f"Saved quality report to   : {report_output}")
    print(f"Total clean rows          : {total_clean_rows}")
    print(f"Total graph edge rows     : {total_graph_rows}")


def main() -> None:
    process_raw_dataset()


if __name__ == "__main__":
    main()