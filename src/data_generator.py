"""
data_generator.py

Tạo dữ liệu giao dịch giả lập cho MVP ngày 1.

Vai trò:
- Tạo giao dịch bình thường để hệ thống không báo nhầm toàn bộ.
- Cài sẵn một số vòng giao dịch đáng ngờ để kiểm thử thuật toán:
  A001 -> A002 -> A003 -> A001
"""

from __future__ import annotations

from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd


RAW_PATH = Path("data/raw/transactions_raw.csv")


def _tx(
    transaction_id: str,
    source: str,
    target: str,
    amount: float,
    timestamp: datetime | str,
    transaction_type: str = "transfer",
) -> dict:
    return {
        "transaction_id": transaction_id,
        "source_account": source,
        "target_account": target,
        "amount": amount,
        "timestamp": timestamp if isinstance(timestamp, str) else timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "transaction_type": transaction_type,
    }


def generate_transactions(output_path: Path = RAW_PATH, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)

    base_time = datetime(2026, 7, 1, 8, 0, 0)
    accounts = [f"A{i:03d}" for i in range(1, 61)]
    rows: list[dict] = []
    tx_no = 1

    # 1) Giao dịch bình thường, không cố ý tạo vòng
    for _ in range(180):
        source, target = random.sample(accounts, 2)
        amount = random.randint(100_000, 8_000_000)
        ts = base_time + timedelta(minutes=random.randint(0, 60 * 72))
        rows.append(_tx(f"T{tx_no:05d}", source, target, amount, ts))
        tx_no += 1

    # 2) Vòng rủi ro cao: ngắn, nhanh, số tiền gần nhau
    high_cycle = [
        ("A001", "A002", 5_000_000, 15),
        ("A002", "A003", 4_950_000, 42),
        ("A003", "A001", 4_900_000, 68),
    ]
    for src, dst, amount, minute in high_cycle:
        rows.append(_tx(f"T{tx_no:05d}", src, dst, amount, base_time + timedelta(minutes=minute)))
        tx_no += 1

    # 3) Vòng rủi ro cao 4 tài khoản
    high_cycle_4 = [
        ("A010", "A011", 9_000_000, 90),
        ("A011", "A012", 8_900_000, 130),
        ("A012", "A013", 8_850_000, 170),
        ("A013", "A010", 8_800_000, 210),
    ]
    for src, dst, amount, minute in high_cycle_4:
        rows.append(_tx(f"T{tx_no:05d}", src, dst, amount, base_time + timedelta(minutes=minute)))
        tx_no += 1

    # 4) Vòng có thời gian dài hơn -> risk thấp hơn
    slow_cycle = [
        ("A020", "A021", 3_000_000, 60),
        ("A021", "A022", 1_500_000, 60 * 30),
        ("A022", "A020", 2_800_000, 60 * 60),
    ]
    for src, dst, amount, minute in slow_cycle:
        rows.append(_tx(f"T{tx_no:05d}", src, dst, amount, base_time + timedelta(minutes=minute)))
        tx_no += 1

    # 5) Dữ liệu lỗi để kiểm tra cleaning
    rows.append(_tx(f"T{tx_no:05d}", "A030", "A030", 1_000_000, base_time))  # self-loop
    tx_no += 1
    rows.append(_tx(f"T{tx_no:05d}", "A031", "A032", -500_000, base_time))  # amount âm
    tx_no += 1
    rows.append(_tx(f"T{tx_no:05d}", "", "A033", 2_000_000, base_time))  # source thiếu
    tx_no += 1
    rows.append(_tx(f"T{tx_no:05d}", "A034", "A035", 2_000_000, "invalid-date"))  # timestamp lỗi
    tx_no += 1

    # Duplicate transaction_id
    rows.append(_tx("T00001", "A040", "A041", 999_000, base_time))

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    df = generate_transactions()
    print(f"Generated {len(df)} raw transactions at {RAW_PATH}")
