# README Update - Phase 2 additions

Bạn có thể copy phần này vào README.md chính.

## Chạy pipeline MVP

```powershell
python src/main.py --step clean
python src/main.py --step subgraph
python src/main.py --step detect --min-cycle-length 2
```

## Chạy dashboard

```powershell
streamlit run app/dashboard.py
```

Dashboard hiện tập trung vào vai trò **Chuyên viên rà soát**, gồm các tab:

```text
Hàng đợi rà soát
Điều tra dòng tiền
Tổng quan hỗ trợ
Ghi chú hệ thống
```

## PySpark prototype cho Phase 2

Cài thêm PySpark nếu chưa có:

```powershell
pip install pyspark
```

Chạy demo:

```powershell
python src/spark_cycle_detection.py --limit 100000
```

Output:

```text
data/output/spark_detected_cycles.csv
```

## Neo4j export cho Phase 2

Chạy:

```powershell
python src/export_neo4j.py
```

Output:

```text
data/neo4j/accounts_nodes.csv
data/neo4j/transactions_edges.csv
```

Xem hướng dẫn import Neo4j tại:

```text
docs/neo4j_import_guide.md
```

## Giới hạn hiện tại

- NetworkX phù hợp cho MVP và graph nhỏ-vừa.
- Risk scoring hiện tại là rule-based.
- Dashboard tập trung vào demo quy trình rà soát, chưa phải case management đầy đủ.
- Dữ liệu là dataset thử nghiệm, chưa phải hệ thống giao dịch real-time.

## Hướng phát triển

- PySpark / GraphFrames để xử lý graph lớn.
- Neo4j để lưu trữ graph.
- FastAPI để làm API backend.
- Case management để lưu analyst, trạng thái, lịch sử xử lý.
- Machine Learning risk scoring khi có dữ liệu gán nhãn đủ tốt.
