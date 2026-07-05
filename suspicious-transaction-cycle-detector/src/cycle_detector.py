"""
cycle_detector.py

Tìm các vòng giao dịch trong directed graph.
"""

from __future__ import annotations

import networkx as nx


def _canonical_cycle(cycle: list[str]) -> tuple[str, ...]:
    """
    Chuẩn hóa cycle để tránh trùng do xoay vòng.
    Ví dụ: A->B->C và B->C->A là cùng một cycle.
    """
    min_index = min(range(len(cycle)), key=lambda i: cycle[i])
    rotated = cycle[min_index:] + cycle[:min_index]
    return tuple(rotated)


def detect_cycles(
    graph: nx.DiGraph,
    min_length: int = 3,
    max_length: int = 6,
) -> list[list[str]]:
    raw_cycles = list(nx.simple_cycles(graph))
    unique: dict[tuple[str, ...], list[str]] = {}

    for cycle in raw_cycles:
        if min_length <= len(cycle) <= max_length:
            key = _canonical_cycle(cycle)
            unique[key] = list(key)

    # Thêm node đầu vào cuối path để hiển thị A -> B -> C -> A
    cycles = []
    for cycle in unique.values():
        cycles.append(cycle + [cycle[0]])

    return cycles
