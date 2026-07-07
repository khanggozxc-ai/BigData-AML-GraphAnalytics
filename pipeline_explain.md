# Explain Code — Pipeline xử lý AML Graph Analytics

Tài liệu này giải thích cách pipeline của dự án hoạt động, theo hướng dễ hiểu để chuẩn bị báo cáo và bảo vệ đồ án.

---

## 1. Ý tưởng cốt lõi

Dữ liệu giao dịch ngân hàng có thể được xem như một đồ thị có hướng:

```text
Account A  --transfer-->  Account B
```

Trong đó:

- **Account** là tài khoản ngân hàng.
- **Transaction** là giao dịch chuyển tiền.
- **Directed edge** là cạnh có hướng từ tài khoản gửi sang tài khoản nhận.

Một vòng giao dịch đáng ngờ có dạng:

```text
A → B → C → A
```

Nghĩa là tiền đi từ A sang B, sang C, rồi quay lại A. Đây là dạng **circular fund flow**. Trong AML, các vòng giao dịch như vậy thường được đưa vào danh sách cần rà soát vì có thể liên quan đến hành vi làm phức tạp đường đi của dòng tiền.

---

## 2. Pipeline tổng thể

Pipeline được điều phối bởi file:

```text
src/main.py
```

Luồng chính:

```text
HI-Small_Trans.csv
    ↓
data_cleaning.py
    ↓
transactions_clean.csv
transactions_graph_edges.csv
    ↓
build_laundering_subgraph()
    ↓
transactions_laundering_subgraph.csv
    ↓
graph_builder.py
    ↓
cycle_detector.py
    ↓
risk_scoring.py
    ↓
suspicious_cycles.csv
    ↓
app/dashboard.py
```

---

## 3. File `src/main.py`

### Vai trò

`main.py` là file điều phối. Nó cho phép chạy từng bước pipeline bằng tham số dòng lệnh.

Các lệnh chính:

```powershell
python src/main.py --step clean
python src/main.py --step subgraph
python src/main.py --step detect
python src/main.py --step demo
python src/main.py --step detect-demo
python src/main.py --step all
```

### Các mode chính

| Step | Ý nghĩa |
|---|---|
| `clean` | Làm sạch dữ liệu raw |
| `subgraph` | Tạo subgraph quanh tài khoản liên quan đến laundering |
| `detect` | Dựng graph, phát hiện cycle, chấm điểm rủi ro |
| `demo` | Tạo dataset demo có cycle để kiểm thử |
| `detect-demo` | Chạy phát hiện cycle trên dataset demo |
| `all` | Chạy toàn bộ pipeline |

---

## 4. File `src/data_cleaning.py`

### Vai trò

File này xử lý dữ liệu gốc từ:

```text
data/raw/HI-Small_Trans.csv
```

và tạo ra:

```text
data/processed/transactions_clean.csv
data/processed/transactions_graph_edges.csv
data/processed/data_quality_report.csv
```

### Vì sao cần cleaning?

Dataset gốc có tên cột theo định dạng IBM AML:

```text
Timestamp
From Bank
Account
To Bank
Account.1
Amount Paid
Payment Format
Is Laundering
```

Nhưng các module graph phía sau cần schema đơn giản hơn:

```text
transaction_id
source_account
target_account
amount
timestamp
transaction_type
is_laundering
```

Do đó `data_cleaning.py` thực hiện:

1. Đọc CSV theo từng chunk để tránh quá tải RAM.
2. Chuẩn hóa tên tài khoản nguồn.
3. Chuẩn hóa tên tài khoản đích.
4. Ép kiểu số tiền.
5. Ép kiểu timestamp.
6. Giữ lại nhãn `is_laundering`.
7. Tách dữ liệu thành:
   - clean data đầy đủ
   - graph edges dùng để dựng graph

### Vì sao xử lý theo chunk?

File raw có hàng triệu dòng. Nếu đọc toàn bộ vào RAM một lần, máy yếu có thể bị treo. Vì vậy code dùng:

```python
pd.read_csv(raw_file, chunksize=chunk_size)
```

Mỗi lần chỉ xử lý một phần dữ liệu, sau đó ghi nối tiếp ra file output.

---

## 5. File `transactions_clean.csv`

Đây là file dữ liệu đã chuẩn hóa.

Nó giữ lại các giao dịch hợp lệ với schema:

```text
transaction_id
source_account
target_account
amount
timestamp
transaction_type
is_laundering
```

File này có thể chứa cả self-loop, tức giao dịch có:

```text
source_account == target_account
```

Self-loop được giữ trong clean data để không mất dữ liệu gốc đã chuẩn hóa.

---

## 6. File `transactions_graph_edges.csv`

Đây là file dùng trực tiếp để dựng graph.

Khác với `transactions_clean.csv`, file này loại bỏ self-loop:

```text
source_account != target_account
```

Lý do:

- Graph analytics cần phân tích dòng tiền giữa các tài khoản.
- Self-loop A → A không giúp phát hiện vòng nhiều tài khoản.
- Cycle cần quan tâm thường là A → B → C → A hoặc A → B → A.

---

## 7. Hàm `build_laundering_subgraph()`

Hàm này nằm trong `src/main.py`.

### Mục đích

Tạo file:

```text
data/processed/transactions_laundering_subgraph.csv
```

### Vì sao cần subgraph?

File graph edge đầy đủ có thể có hàng triệu giao dịch. Nếu đưa toàn bộ vào NetworkX để tìm cycle, chương trình có thể chậm hoặc quá tải.

Vì vậy pipeline tạo subgraph bằng cách:

1. Tìm các tài khoản xuất hiện trong giao dịch có `is_laundering = 1`.
2. Lọc tất cả giao dịch có liên quan đến các tài khoản đó.
3. Ghi ra một file nhỏ hơn để phân tích graph.

Cách này giúp:

- Giảm kích thước graph.
- Tập trung vào vùng có khả năng đáng ngờ.
- Phù hợp với MVP đồ án.

---

## 8. File `src/graph_builder.py`

### Vai trò

File này dựng directed graph từ dataframe giao dịch.

Ý tưởng:

```python
source_account -> target_account
```

Mỗi tài khoản là một node. Mỗi giao dịch là một directed edge.

Graph được dùng để tìm cycle.

### Khái niệm cần nắm

- **Node**: tài khoản.
- **Edge**: giao dịch.
- **Directed graph**: đồ thị có hướng.
- **Cycle**: đường đi khép kín.

Ví dụ:

```text
A001 → A002
A002 → A003
A003 → A001
```

thì graph có một cycle:

```text
A001 → A002 → A003 → A001
```

---

## 9. File `src/cycle_detector.py`

### Vai trò

File này tìm các chu trình trong graph.

Nó nhận đầu vào:

```text
graph
min_length
max_length
```

và trả về danh sách các cycle.

### Vì sao giới hạn độ dài cycle?

Nếu không giới hạn, số lượng cycle trong graph lớn có thể rất nhiều và gây chậm. Trong đồ án, nhóm thường giới hạn:

```text
min_length = 2
max_length = 6
```

Lý do dùng `min_length = 2`:

- Một số pattern AML có dạng A → B → A.
- Đây là vòng 2 tài khoản, vẫn là circular flow.
- Self-loop A → A đã được loại bỏ trước đó.

---

## 10. File `src/risk_scoring.py`

### Vai trò

File này chấm điểm rủi ro cho từng cycle.

Input:

```text
cycles
transaction dataframe
```

Output:

```text
cycle_id
path
total_amount
duration_minutes
amount_variance
risk_score
risk_level
explanation
```

### Các cột output

| Cột | Ý nghĩa |
|---|---|
| `cycle_id` | Mã định danh case |
| `path` | Đường đi tài khoản trong cycle |
| `total_amount` | Tổng tiền trong cycle |
| `duration_minutes` | Thời gian hoàn tất cycle |
| `amount_variance` | Độ lệch số tiền giữa các bước |
| `risk_score` | Điểm rủi ro |
| `risk_level` | Low / Medium / High |
| `explanation` | Diễn giải vì sao có mức rủi ro đó |

### Ý tưởng risk score

Risk score được tính theo rule:

- Cycle ngắn và khép kín.
- Thời gian hoàn tất nhanh.
- Tổng số tiền lớn.
- Số tiền giữa các giao dịch gần nhau.
- Có liên quan đến nhãn laundering.

Mức phân loại:

```text
Low       : 0 - 39
Medium    : 40 - 69
High      : 70 - 100
```

---

## 11. File `data/output/suspicious_cycles.csv`

Đây là output cuối cùng của pipeline.

File này được dashboard đọc để hiển thị kết quả.

Ví dụ kiểm tra:

```powershell
python -c "import pandas as pd; df=pd.read_csv('data/output/suspicious_cycles.csv'); print('detected cycles:', len(df)); print(df.head())"
```

Trong lần chạy thực tế, nhóm phát hiện:

```text
detected cycles: 21
```

---

## 12. File `app/dashboard.py`

### Vai trò

Dashboard giúp người xem hiểu kết quả phát hiện cycle.

Các phần chính:

| Tab | Ý nghĩa |
|---|---|
| Overview | Tổng quan số lượng cycle, dòng tiền nghi vấn, mức rủi ro |
| Case Queue | Danh sách case cần rà soát |
| Graph Investigation | Xem đường đi dòng tiền của từng cycle |
| Model Notes | Giải thích logic và giới hạn hệ thống |

### Vì sao dashboard quan trọng?

Nếu chỉ có CSV, người xem khó hiểu. Dashboard giúp:

- Xem tổng số cycle.
- Biết case nào rủi ro cao hơn.
- Xem đường đi dòng tiền A → B → C → A.
- Hiểu vì sao case được đánh dấu.
- Trình bày kết quả trực quan khi báo cáo.

---

## 13. Vai trò của `.gitignore`

Các file CSV lớn không được push lên GitHub.

`.gitignore` loại bỏ:

```text
data/raw/*.csv
data/processed/*.csv
data/output/*.csv
```

Lý do:

1. File raw quá lớn.
2. GitHub có giới hạn dung lượng.
3. Repository sẽ nặng và khó clone.
4. Dữ liệu processed có thể tạo lại bằng pipeline.

Cách làm đúng:

- GitHub lưu code.
- Dataset được gửi riêng hoặc tải riêng.
- Người dùng clone code, đặt dataset vào `data/raw`, rồi chạy pipeline.

---

## 14. Cách giải thích pipeline khi báo cáo

Có thể nói:

> Đầu tiên, nhóm đọc dataset giao dịch gốc và chuẩn hóa các cột quan trọng như tài khoản gửi, tài khoản nhận, số tiền, thời gian và nhãn laundering. Sau đó, nhóm chuyển dữ liệu giao dịch thành đồ thị có hướng, trong đó mỗi tài khoản là một node và mỗi giao dịch là một edge. Trên đồ thị này, nhóm tìm các chu trình khép kín, tức các trường hợp dòng tiền đi qua nhiều tài khoản rồi quay lại điểm ban đầu. Những chu trình này được chấm điểm rủi ro và hiển thị trên dashboard để hỗ trợ rà soát.

---

## 15. Những câu hỏi dễ bị hỏi khi bảo vệ

### Câu 1: Vì sao dùng graph?

Vì dữ liệu giao dịch có quan hệ tự nhiên dạng mạng lưới. Tài khoản liên kết với nhau qua giao dịch, nên graph giúp phát hiện các pattern mà bảng dữ liệu thông thường khó nhìn thấy, đặc biệt là vòng giao dịch.

### Câu 2: Cycle là gì?

Cycle là đường đi khép kín trong graph. Ví dụ:

```text
A → B → C → A
```

Tiền đi qua nhiều tài khoản rồi quay lại tài khoản ban đầu.

### Câu 3: Phát hiện cycle có đồng nghĩa rửa tiền không?

Không. Hệ thống chỉ đánh dấu là đáng ngờ để rà soát. Muốn kết luận cần thêm dữ liệu KYC, thông tin chủ tài khoản, bối cảnh giao dịch và quy trình nghiệp vụ.

### Câu 4: Vì sao không push dữ liệu lên GitHub?

Vì file CSV quá lớn. Dữ liệu được đưa vào `.gitignore`. Repository chỉ lưu source code và tài liệu. Người chạy cần đặt dataset vào `data/raw` rồi chạy pipeline để tạo lại output.

### Câu 5: Vì sao cần subgraph?

Vì graph đầy đủ rất lớn. Subgraph giúp giảm kích thước dữ liệu và tập trung vào vùng có liên quan đến laundering, giúp NetworkX xử lý nhanh hơn trong MVP.

### Câu 6: NetworkX có phải Big Data không?

NetworkX phù hợp để làm MVP và chứng minh logic graph analytics. Với dữ liệu rất lớn, hướng mở rộng là dùng PySpark GraphFrames, Neo4j hoặc hệ thống graph database.

### Câu 7: Dashboard có vai trò gì?

Dashboard giúp biến kết quả kỹ thuật thành thông tin dễ hiểu cho người xem: số cycle, mức rủi ro, dòng tiền, đường đi giao dịch và hành động đề xuất.

---

## 16. Điểm cần nắm thật chắc

Trước khi báo cáo, cần nắm:

1. Dataset có các cột nào.
2. Tài khoản được tạo từ `Bank + Account`.
3. Vì sao cần loại self-loop khỏi graph edge.
4. Vì sao dùng subgraph.
5. Cycle detection tìm gì.
6. Risk score tính dựa trên ý tưởng nào.
7. Output `suspicious_cycles.csv` có những cột gì.
8. Dashboard đọc file nào.
9. Hệ thống không kết luận rửa tiền thật.
10. Hướng mở rộng bằng Spark/GraphFrames/MongoDB/Neo4j.
