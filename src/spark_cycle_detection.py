"""
PySpark prototype for Phase 2: phát hiện vòng giao dịch đáng ngờ bằng Spark DataFrame.

Mục tiêu:
- Không thay thế NetworkX MVP hiện tại.
- Minh họa hướng nâng cấp Big Data bằng PySpark local mode.
- Tìm vòng 2 tài khoản: A -> B -> A.
- Tìm vòng 3 tài khoản: A -> B -> C -> A.
- Xuất kết quả ra data/output/spark_detected_cycles.csv.

Cách chạy:
    python src/spark_cycle_detection.py

Chạy với input cụ thể:
    python src/spark_cycle_detection.py --input data/processed/transactions_graph_edges.csv

Giới hạn số dòng để máy yếu không bị nặng:
    python src/spark_cycle_detection.py --limit 100000
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_CANDIDATES = [
    PROJECT_ROOT / "data/processed/transactions_graph_edges.csv",
    PROJECT_ROOT / "data/processed/transactions_laundering_subgraph.csv",
]

DEFAULT_OUTPUT = PROJECT_ROOT / "data/output/spark_detected_cycles.csv"


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


def create_spark_session() -> SparkSession:
    """Tạo SparkSession local mode cho máy cá nhân."""
    return (
        SparkSession.builder
        .appName("AML Spark Cycle Detection Prototype")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )


def normalize_edges(df):
    """
    Chuẩn hóa tên cột source/target.

    Hỗ trợ các schema thường gặp:
    - source_account, target_account
    - src, dst
    """
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
            f"Cột hiện có: {df.columns}"
        )

    amount_col = "amount" if "amount" in columns else None
    timestamp_col = "timestamp" if "timestamp" in columns else None
    tx_type_col = "transaction_type" if "transaction_type" in columns else None
    laundering_col = "is_laundering" if "is_laundering" in columns else None

    selected = [
        F.col(source_col).cast("string").alias("src"),
        F.col(target_col).cast("string").alias("dst"),
    ]

    if amount_col:
        selected.append(F.col(amount_col).cast("double").alias("amount"))
    else:
        selected.append(F.lit(0.0).alias("amount"))

    if timestamp_col:
        selected.append(F.col(timestamp_col).cast("string").alias("timestamp"))
    else:
        selected.append(F.lit("").alias("timestamp"))

    if tx_type_col:
        selected.append(F.col(tx_type_col).cast("string").alias("transaction_type"))
    else:
        selected.append(F.lit("").alias("transaction_type"))

    if laundering_col:
        selected.append(F.col(laundering_col).cast("int").alias("is_laundering"))
    else:
        selected.append(F.lit(0).alias("is_laundering"))

    edges = (
        df.select(*selected)
        .where(F.col("src").isNotNull() & F.col("dst").isNotNull())
        .where(F.col("src") != F.col("dst"))
        .dropDuplicates(["src", "dst", "amount", "timestamp"])
    )

    return edges


def detect_two_account_cycles(edges):
    """Tìm vòng 2 tài khoản: A -> B và B -> A."""
    e1 = edges.alias("e1")
    e2 = edges.alias("e2")

    cycles = (
        e1.join(
            e2,
            (F.col("e1.src") == F.col("e2.dst")) &
            (F.col("e1.dst") == F.col("e2.src")) &
            (F.col("e1.src") < F.col("e1.dst")),
            "inner",
        )
        .select(
            F.concat(F.lit("S2_"), F.monotonically_increasing_id()).alias("cycle_id"),
            F.array(F.col("e1.src"), F.col("e1.dst"), F.col("e1.src")).alias("path_array"),
            (F.col("e1.amount") + F.col("e2.amount")).alias("total_amount"),
            F.lit(2).alias("cycle_length"),
            F.lit("spark_2_cycle").alias("detection_method"),
        )
    )

    return cycles


def detect_three_account_cycles(edges):
    """Tìm vòng 3 tài khoản: A -> B, B -> C, C -> A."""
    e1 = edges.alias("e1")
    e2 = edges.alias("e2")
    e3 = edges.alias("e3")

    cycles = (
        e1.join(e2, F.col("e1.dst") == F.col("e2.src"), "inner")
        .join(
            e3,
            (F.col("e2.dst") == F.col("e3.src")) &
            (F.col("e3.dst") == F.col("e1.src")),
            "inner",
        )
        .where(F.col("e1.src") != F.col("e1.dst"))
        .where(F.col("e1.src") != F.col("e2.dst"))
        .where(F.col("e1.dst") != F.col("e2.dst"))
        # Chuẩn hóa để giảm bớt duplicate vòng xoay A-B-C-A, B-C-A-B, C-A-B-C.
        .where(F.col("e1.src") < F.col("e1.dst"))
        .where(F.col("e1.src") < F.col("e2.dst"))
        .select(
            F.concat(F.lit("S3_"), F.monotonically_increasing_id()).alias("cycle_id"),
            F.array(F.col("e1.src"), F.col("e1.dst"), F.col("e2.dst"), F.col("e1.src")).alias("path_array"),
            (F.col("e1.amount") + F.col("e2.amount") + F.col("e3.amount")).alias("total_amount"),
            F.lit(3).alias("cycle_length"),
            F.lit("spark_3_cycle").alias("detection_method"),
        )
    )

    return cycles


def export_cycles(two_cycles, three_cycles, output_path: Path, max_export_rows: int) -> None:
    """Gộp kết quả Spark và xuất thành một CSV đơn."""
    combined = two_cycles.unionByName(three_cycles)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result_pdf = (
        combined
        .limit(max_export_rows)
        .withColumn("path", F.concat_ws(" -> ", F.col("path_array")))
        .select("cycle_id", "path", "cycle_length", "total_amount", "detection_method")
        .toPandas()
    )

    if result_pdf.empty:
        result_pdf = pd.DataFrame(
            columns=["cycle_id", "path", "cycle_length", "total_amount", "detection_method"]
        )

    result_pdf.to_csv(output_path, index=False, encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser(description="PySpark prototype for AML cycle detection.")
    parser.add_argument("--input", default=None, help="Đường dẫn file CSV graph edges.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="File CSV output.")
    parser.add_argument("--limit", type=int, default=100000, help="Giới hạn số dòng input để máy yếu không bị nặng.")
    parser.add_argument("--max-export-rows", type=int, default=10000, help="Giới hạn số dòng output xuất ra CSV.")
    args = parser.parse_args()

    input_path = resolve_input_path(args.input)
    output_path = PROJECT_ROOT / args.output if not Path(args.output).is_absolute() else Path(args.output)

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("[INFO] Input:", input_path)
    print("[INFO] Output:", output_path)
    print("[INFO] Limit rows:", args.limit)

    try:
        raw_df = spark.read.option("header", True).option("inferSchema", True).csv(str(input_path))

        if args.limit and args.limit > 0:
            raw_df = raw_df.limit(args.limit)

        edges = normalize_edges(raw_df).cache()

        print("[INFO] Edge rows:", edges.count())

        two_cycles = detect_two_account_cycles(edges).cache()
        three_cycles = detect_three_account_cycles(edges).cache()

        two_count = two_cycles.count()
        three_count = three_cycles.count()

        export_cycles(two_cycles, three_cycles, output_path, args.max_export_rows)

        print("[DONE] Spark 2-account cycles:", two_count)
        print("[DONE] Spark 3-account cycles:", three_count)
        print("[DONE] Exported:", output_path)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
