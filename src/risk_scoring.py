"""
risk_scoring.py

Chấm điểm rủi ro cho từng vòng giao dịch.
"""

from __future__ import annotations

from datetime import timedelta
import pandas as pd


def _get_cycle_edges(cycle_path: list[str], transactions: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for src, dst in zip(cycle_path[:-1], cycle_path[1:]):
        matched = transactions[
            (transactions["source_account"] == src)
            & (transactions["target_account"] == dst)
        ].copy()

        # MVP: nếu có nhiều giao dịch cùng một cặp, lấy giao dịch sớm nhất.
        if not matched.empty:
            parts.append(matched.sort_values("timestamp").head(1))

    if not parts:
        return pd.DataFrame(columns=transactions.columns)

    return pd.concat(parts, ignore_index=True)


def _amount_variance_ratio(amounts: pd.Series) -> float:
    if len(amounts) == 0:
        return 1.0
    mean_amount = amounts.mean()
    if mean_amount == 0:
        return 1.0
    return float((amounts.max() - amounts.min()) / mean_amount)


def _risk_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def score_cycle(
    cycle_id: str,
    cycle_path: list[str],
    transactions: pd.DataFrame,
    amount_threshold: float = 10_000_000,
    fast_minutes_threshold: int = 60,
) -> dict:
    edges = _get_cycle_edges(cycle_path, transactions)

    if edges.empty:
        return {
            "cycle_id": cycle_id,
            "path": " -> ".join(cycle_path),
            "total_amount": 0,
            "duration_minutes": None,
            "amount_variance": None,
            "risk_score": 0,
            "risk_level": "Low",
            "explanation": "Không tìm thấy đủ giao dịch tương ứng với vòng.",
        }

    timestamps = pd.to_datetime(edges["timestamp"])
    amounts = edges["amount"].astype(float)

    duration_minutes = int((timestamps.max() - timestamps.min()).total_seconds() // 60)
    total_amount = float(amounts.sum())
    variance_ratio = _amount_variance_ratio(amounts)

    score = 0
    reasons: list[str] = []

    cycle_accounts_count = len(cycle_path) - 1

    if 3 <= cycle_accounts_count <= 5:
        score += 20
        reasons.append(f"vòng có {cycle_accounts_count} tài khoản")

    if duration_minutes <= 24 * 60:
        score += 25
        reasons.append(f"hoàn tất trong {duration_minutes} phút, dưới 24 giờ")

    if variance_ratio <= 0.10:
        score += 20
        reasons.append("số tiền giữa các giao dịch chênh lệch dưới 10%")

    if total_amount >= amount_threshold:
        score += 20
        reasons.append(f"tổng giá trị vòng đạt {total_amount:,.0f}, vượt ngưỡng {amount_threshold:,.0f}")

    if duration_minutes <= fast_minutes_threshold and cycle_accounts_count >= 3:
        score += 15
        reasons.append(f"các tài khoản trung gian chuyển tiếp nhanh trong dưới {fast_minutes_threshold} phút")

    score = min(score, 100)
    level = _risk_level(score)

    explanation = (
        f"Vòng {cycle_id} được đánh dấu {level} vì "
        + "; ".join(reasons)
        + "."
        if reasons
        else f"Vòng {cycle_id} có điểm thấp vì chưa thỏa nhiều tiêu chí bất thường."
    )

    return {
        "cycle_id": cycle_id,
        "path": " -> ".join(cycle_path),
        "total_amount": round(total_amount, 2),
        "duration_minutes": duration_minutes,
        "amount_variance": round(variance_ratio, 4),
        "risk_score": score,
        "risk_level": level,
        "explanation": explanation,
    }


def score_cycles(cycles: list[list[str]], transactions: pd.DataFrame) -> pd.DataFrame:
    results = []
    for idx, cycle_path in enumerate(cycles, start=1):
        results.append(score_cycle(f"C{idx:03d}", cycle_path, transactions))

    output = pd.DataFrame(results)

    if not output.empty:
        output = output.sort_values(
            by=["risk_score", "total_amount"],
            ascending=[False, False],
        ).reset_index(drop=True)

    return output
