# Day 2 - Hoàn thiện góp ý và Phase 2

## 1. Hiện trạng MVP

Hệ thống hiện tại đã hoàn thành pipeline:

```text
Raw transactions
→ Data cleaning
→ Graph edge building
→ NetworkX cycle detection
→ Rule-based risk scoring
→ suspicious_cycles.csv
→ Streamlit dashboard
```

Kết quả demo:

```text
Tổng số case: 21
Vòng 2 tài khoản: 19
Vòng 3 tài khoản: 2
```

## 2. Góp ý đã xử lý

| Góp ý | Cách xử lý |
|---|---|
| Giao diện đẹp nhưng chưa rõ vai trò | Dashboard tập trung vào vai trò Chuyên viên rà soát |
| NetworkX chỉ phù hợp graph nhỏ-vừa | Giữ NetworkX cho MVP, bổ sung PySpark prototype cho Phase 2 |
| Cần liên quan Big Data hơn | Thêm file `src/spark_cycle_detection.py` |
| Không có chỗ lưu graph | Thêm hướng Neo4j bằng `src/export_neo4j.py` |
| Dữ liệu lớn không nên đưa lên GitHub | Cập nhật `.gitignore` để bỏ qua CSV lớn |

## 3. Dashboard mới

Dashboard hiện tập trung vào một vai trò duy nhất:

```text
Chuyên viên rà soát
```

Workflow:

```text
Hàng đợi rà soát
→ Điều tra dòng tiền
→ Tổng quan hỗ trợ
→ Ghi chú hệ thống
```

Câu giải thích khi báo cáo:

> Nhóm chọn tập trung dashboard vào vai trò Chuyên viên rà soát vì đây là người trực tiếp xử lý cảnh báo AML. Dashboard được thiết kế theo workflow: xem hàng đợi case, chọn case, điều tra dòng tiền, kiểm tra giao dịch trong chu trình và dùng checklist rà soát.

## 4. PySpark prototype

File:

```text
src/spark_cycle_detection.py
```

Cách chạy:

```powershell
python src/spark_cycle_detection.py --limit 100000
```

Output:

```text
data/output/spark_detected_cycles.csv
```

Câu giải thích khi báo cáo:

> NetworkX được dùng trong MVP để kiểm chứng logic phát hiện chu trình giao dịch. Vì NetworkX chạy trên một máy nên không phù hợp khi graph quá lớn. Do đó nhóm bổ sung PySpark prototype ở local mode để minh họa hướng nâng cấp xử lý dữ liệu lớn trong Phase 2.

## 5. Neo4j export

File:

```text
src/export_neo4j.py
```

Cách chạy:

```powershell
python src/export_neo4j.py
```

Output:

```text
data/neo4j/accounts_nodes.csv
data/neo4j/transactions_edges.csv
```

Câu giải thích khi báo cáo:

> Ở MVP, graph được dựng tạm thời từ CSV. Trong Phase 2, nhóm đề xuất Neo4j làm tầng lưu trữ graph để lưu tài khoản và giao dịch theo mô hình graph tự nhiên, hỗ trợ truy vấn quan hệ và trực quan hóa tốt hơn.

## 6. Lệnh chạy demo cuối

```powershell
python src/main.py --step clean
python src/main.py --step subgraph
python src/main.py --step detect --min-cycle-length 2
streamlit run app/dashboard.py
```

Kiểm tra output:

```powershell
python -c "import pandas as pd; df=pd.read_csv('data/output/suspicious_cycles.csv'); print('Tổng số case:', len(df)); print(df.head())"
```

## 7. Lệnh Git đề xuất

```powershell
git add .gitignore app/dashboard.py src/spark_cycle_detection.py src/export_neo4j.py docs/neo4j_import_guide.md docs/day2_phase2_notes.md
git commit -m "Add analyst dashboard and phase 2 PySpark Neo4j prototype"
git push
```
