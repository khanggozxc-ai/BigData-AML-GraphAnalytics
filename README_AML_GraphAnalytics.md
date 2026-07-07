# BigData-AML-GraphAnalytics

## 1. Giới thiệu dự án

**BigData-AML-GraphAnalytics** là đồ án môn **Phân tích Dữ liệu lớn**, tập trung vào bài toán:

> **Phát hiện vòng giao dịch đáng ngờ bằng Graph Analytics**

Hệ thống mô phỏng quy trình giám sát giao dịch trong bối cảnh AML (*Anti-Money Laundering*). Dữ liệu giao dịch được biểu diễn dưới dạng đồ thị:

- **Tài khoản ngân hàng** là **node**.
- **Giao dịch chuyển tiền** là **directed edge**.
- Một **chu trình giao dịch đáng ngờ** xuất hiện khi dòng tiền đi qua nhiều tài khoản rồi quay lại tài khoản ban đầu.

Mục tiêu của hệ thống không phải là kết luận một giao dịch chắc chắn là rửa tiền, mà là **phát hiện và ưu tiên các vòng giao dịch cần được rà soát**.

---

## 2. Mục tiêu chính

Dự án xây dựng một pipeline hoàn chỉnh gồm:

1. Đọc dữ liệu giao dịch gốc.
2. Làm sạch và chuẩn hóa dữ liệu.
3. Chuyển dữ liệu giao dịch thành đồ thị tài khoản - tài khoản.
4. Tạo subgraph tập trung vào các tài khoản liên quan đến laundering.
5. Phát hiện chu trình giao dịch bằng Graph Analytics.
6. Chấm điểm rủi ro cho từng chu trình.
7. Xuất kết quả ra file CSV.
8. Hiển thị kết quả trên dashboard Streamlit dạng **AML Control Tower**.

---

## 3. Dataset

Dự án sử dụng dataset:

```text
IBM Transactions for Anti Money Laundering (AML)
```

File chính cần có:

```text
data/raw/HI-Small_Trans.csv
```

Schema gốc kỳ vọng:

```text
Timestamp
From Bank
Account
To Bank
Account.1
Amount Received
Receiving Currency
Amount Paid
Payment Currency
Payment Format
Is Laundering
```

Trong repository GitHub, các file CSV lớn **không được push lên GitHub** vì dung lượng lớn. Các file này được đưa vào `.gitignore`.

Người mới clone project cần tự đặt dataset vào đúng thư mục:

```text
data/raw/HI-Small_Trans.csv
```

Sau đó chạy lại pipeline để sinh dữ liệu processed và output.

---

## 4. Kiến trúc tổng quan

```text
Raw Dataset
    ↓
Data Cleaning
    ↓
Graph Edge Dataset
    ↓
Laundering Subgraph
    ↓
Graph Construction
    ↓
Cycle Detection
    ↓
Risk Scoring
    ↓
Suspicious Cycles Output
    ↓
Streamlit Dashboard
```

Diễn giải:

| Tầng xử lý | Vai trò |
|---|---|
| Raw Dataset | Dữ liệu giao dịch gốc |
| Data Cleaning | Chuẩn hóa schema, xử lý kiểu dữ liệu, loại lỗi cơ bản |
| Graph Edge Dataset | Tập cạnh dùng để dựng đồ thị |
| Laundering Subgraph | Lọc vùng dữ liệu có liên quan đến giao dịch laundering |
| Graph Construction | Dựng directed graph bằng NetworkX |
| Cycle Detection | Tìm các vòng giao dịch khép kín |
| Risk Scoring | Chấm điểm rủi ro theo rule |
| Dashboard | Trực quan hóa kết quả cho người xem |

---

## 5. Cấu trúc thư mục

```text
BigData-AML-GraphAnalytics/
├── app/
│   └── dashboard.py
│
├── data/
│   ├── raw/
│   │   ├── HI-Small_Trans.csv              # Không push GitHub
│   │   └── README_DATA.md
│   │
│   ├── processed/
│   │   ├── transactions_clean.csv          # Không push GitHub
│   │   ├── transactions_graph_edges.csv    # Không push GitHub
│   │   ├── transactions_laundering_subgraph.csv
│   │   └── data_quality_report.csv
│   │
│   └── output/
│       └── suspicious_cycles.csv
│
├── reports/
│   ├── day1_data_pipeline.md
│   └── day1_notes.md
│
├── src/
│   ├── data_cleaning.py
│   ├── data_generator.py
│   ├── filter_active_accounts.py
│   ├── graph_builder.py
│   ├── cycle_detector.py
│   ├── risk_scoring.py
│   ├── inspect_dataset.py
│   ├── run_pipeline_real_data.py
│   └── main.py
│
├── explain_code/
│   └── pipeline.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 6. Vai trò các file chính

| File | Vai trò |
|---|---|
| `src/main.py` | File điều phối pipeline chính |
| `src/data_cleaning.py` | Đọc raw dataset, chuẩn hóa và tạo dữ liệu processed |
| `src/graph_builder.py` | Dựng directed graph từ transaction data |
| `src/cycle_detector.py` | Phát hiện chu trình giao dịch |
| `src/risk_scoring.py` | Chấm điểm rủi ro và sinh giải thích |
| `src/data_generator.py` | Tạo dữ liệu demo/synthetic để test |
| `app/dashboard.py` | Dashboard Streamlit hiển thị kết quả |
| `data/output/suspicious_cycles.csv` | Kết quả cuối cùng của hệ thống |

---

## 7. Cài đặt môi trường

### Bước 1: Clone repository

```powershell
git clone https://github.com/khanggozxc-ai/BigData-AML-GraphAnalytics.git
cd BigData-AML-GraphAnalytics
```

### Bước 2: Tạo virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Bước 3: Cài thư viện

```powershell
pip install -r requirements.txt
```

Nếu thiếu thư viện dashboard:

```powershell
pip install streamlit plotly streamlit-agraph
```

---

## 8. Chuẩn bị dữ liệu

Đặt file dataset gốc vào:

```text
data/raw/HI-Small_Trans.csv
```

Kiểm tra file:

```powershell
Get-Content data\raw\HI-Small_Trans.csv -TotalCount 1
```

Header đúng phải gần dạng:

```text
Timestamp,From Bank,Account,To Bank,Account.1,Amount Received,Receiving Currency,Amount Paid,Payment Currency,Payment Format,Is Laundering
```

---

## 9. Cách chạy pipeline

Chạy lần lượt:

```powershell
python src/main.py --step clean
python src/main.py --step subgraph
python src/main.py --step detect
```

Ý nghĩa:

| Lệnh | Chức năng |
|---|---|
| `--step clean` | Tạo `transactions_clean.csv`, `transactions_graph_edges.csv`, `data_quality_report.csv` |
| `--step subgraph` | Tạo `transactions_laundering_subgraph.csv` |
| `--step detect` | Phát hiện cycles và tạo `suspicious_cycles.csv` |

Có thể chạy toàn bộ pipeline:

```powershell
python src/main.py --step all
```

---

## 10. Kiểm tra kết quả

Kiểm tra dữ liệu processed:

```powershell
dir data\processed
```

Kiểm tra output:

```powershell
dir data\output
```

Kiểm tra số cycle phát hiện:

```powershell
python -c "import pandas as pd; df=pd.read_csv('data/output/suspicious_cycles.csv'); print('detected cycles:', len(df)); print(df.head())"
```

Kết quả chạy thực tế của nhóm đã phát hiện được:

```text
detected cycles: 21
```

---

## 11. Chạy dashboard

```powershell
streamlit run app/dashboard.py
```

Dashboard hiển thị các phần chính:

1. **Overview** — Tổng quan giám sát.
2. **Case Queue** — Danh sách cảnh báo cần rà soát.
3. **Graph Investigation** — Xem đường đi dòng tiền.
4. **Model Notes** — Giải thích hệ thống và giới hạn.

Dashboard được thiết kế theo hướng **AML Control Tower**, giúp người xem hiểu:

- Hệ thống phát hiện bao nhiêu vòng giao dịch.
- Tổng dòng tiền trong các vòng đáng ngờ là bao nhiêu.
- Mức rủi ro của từng case.
- Dòng tiền đi qua tài khoản nào.
- Vì sao case đó cần được rà soát.

---

## 12. Quy tắc Risk Scoring

Mỗi cycle được chấm điểm rủi ro dựa trên các tiêu chí như:

| Tiêu chí | Ý nghĩa |
|---|---|
| Độ dài chu trình | Số tài khoản tham gia vòng |
| Thời gian hoàn tất | Vòng diễn ra càng nhanh càng đáng chú ý |
| Tổng số tiền | Số tiền càng lớn thì mức độ ưu tiên càng cao |
| Độ lệch số tiền | Các giao dịch có số tiền gần nhau có thể đáng chú ý |
| Laundering label | Nếu có nhãn laundering trong dữ liệu, tăng độ ưu tiên rà soát |

Mức rủi ro:

```text
Low       : 0 - 39
Medium    : 40 - 69
High      : 70 - 100
```

---

## 13. Giới hạn của hệ thống

Hệ thống hiện tại là bản MVP phục vụ đồ án, có các giới hạn:

1. Chưa phải hệ thống AML thật của ngân hàng.
2. Không kết luận chắc chắn một giao dịch là rửa tiền.
3. Risk scoring đang dựa trên rule, chưa phải mô hình học máy hoàn chỉnh.
4. Dữ liệu là dữ liệu mô phỏng.
5. NetworkX phù hợp MVP, nhưng chưa tối ưu cho graph cực lớn.
6. Khi mở rộng, nên dùng PySpark GraphFrames hoặc Neo4j cho xử lý graph quy mô lớn.

---

## 14. Hướng mở rộng

Các hướng nâng cấp:

1. Dùng **PySpark / GraphFrames** cho xử lý đồ thị lớn.
2. Lưu dữ liệu vào **MongoDB** hoặc Data Lake.
3. Dùng **Neo4j** để truy vấn và trực quan hóa graph.
4. Tích hợp mô hình ML để học risk score.
5. Thêm case management thật: assign analyst, status, history.
6. Thêm API backend phục vụ dashboard.
7. Tối ưu dashboard theo role: manager, analyst, technical reviewer.

---

## 15. Phân công nhóm

| Thành viên | Nhiệm vụ chính |
|---|---|
| Thành viên A | Data pipeline, data cleaning, raw-to-processed processing |
| Thành viên B | Graph analytics, cycle detection, risk scoring, dashboard |

---

## 16. Lưu ý GitHub

Không push các file CSV lớn:

```text
data/raw/*.csv
data/processed/*.csv
data/output/*.csv
```

Các file này được tạo lại bằng pipeline. Repository chỉ nên lưu:

```text
source code
README
reports
documentation
configuration
```

---

## 17. Cách giải thích ngắn khi báo cáo

> Nhóm biểu diễn dữ liệu giao dịch dưới dạng đồ thị, trong đó tài khoản là node và giao dịch là cạnh có hướng. Sau khi làm sạch dữ liệu, hệ thống dựng graph tài khoản - tài khoản, tìm các chu trình khép kín và chấm điểm rủi ro cho từng chu trình. Kết quả được hiển thị trên dashboard AML Control Tower để hỗ trợ người xem nhận diện các vòng giao dịch đáng ngờ cần rà soát.
