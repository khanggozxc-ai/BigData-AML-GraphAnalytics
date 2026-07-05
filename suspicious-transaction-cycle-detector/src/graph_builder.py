"""
graph_builder.py

Dựng directed graph từ dữ liệu giao dịch sạch.

Account = node
Transaction = directed edge
"""

from __future__ import annotations

import pandas as pd
import networkx as nx


def build_transaction_graph(transactions: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()

    for _, row in transactions.iterrows():
        src = row["source_account"]
        dst = row["target_account"]

        graph.add_node(src)
        graph.add_node(dst)

        edge_data = {
            "transaction_id": row["transaction_id"],
            "amount": float(row["amount"]),
            "timestamp": row["timestamp"],
            "transaction_type": row.get("transaction_type", "transfer"),
        }

        # MVP dùng DiGraph. Nếu đã có edge trùng, lưu danh sách giao dịch để không mất thông tin.
        if graph.has_edge(src, dst):
            graph[src][dst].setdefault("transactions", [])
            graph[src][dst]["transactions"].append(edge_data)
        else:
            graph.add_edge(src, dst, **edge_data, transactions=[edge_data])

    return graph


def summarize_graph(graph: nx.DiGraph) -> dict:
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": nx.density(graph),
    }
