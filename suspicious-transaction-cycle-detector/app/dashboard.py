"""
dashboard.py

Dashboard đơn giản để chuẩn bị cho ngày 2.
Ngày 1 chưa bắt buộc hoàn thiện giao diện, nhưng file này để sẵn.
"""

from pathlib import Path
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / "data/processed/transactions_clean.csv"
OUTPUT_PATH = ROOT / "data/output/suspicious_cycles.csv"

st.set_page_config(page_title="Suspicious Transaction Cycle Detector", layout="wide")

st.title("Suspicious Transaction Cycle Detector")
st.caption("Graph Analytics MVP — phát hiện vòng giao dịch đáng ngờ")

if not CLEAN_PATH.exists() or not OUTPUT_PATH.exists():
    st.warning("Chưa có dữ liệu đầu ra. Hãy chạy: python src/main.py")
    st.stop()

transactions = pd.read_csv(CLEAN_PATH)
cycles = pd.read_csv(OUTPUT_PATH)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", len(transactions))
col2.metric("Accounts", pd.concat([transactions["source_account"], transactions["target_account"]]).nunique())
col3.metric("Detected Cycles", len(cycles))
col4.metric("High Risk", int((cycles["risk_level"] == "High").sum()) if not cycles.empty else 0)

st.subheader("Suspicious Cycles")
st.dataframe(cycles, use_container_width=True)

st.subheader("Clean Transactions")
st.dataframe(transactions.head(100), use_container_width=True)
