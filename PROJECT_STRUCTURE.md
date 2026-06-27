# 📁 PROJECT_STRUCTURE

## Mục đích

Tài liệu này mô tả cấu trúc thư mục của dự án và quy ước tổ chức mã nguồn nhằm giúp các thành viên phát triển thống nhất, dễ bảo trì và dễ tích hợp.

---

# 📂 Cấu trúc thư mục

```text
AML-Graph-Analytics/
│
├── README.md
├── PROJECT_STRUCTURE.md
├── ROADMAP.md
├── TASKS.md
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│   ├── meeting_notes.md
│   ├── decisions.md
│   └── references.md
│
├── src/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── graph/
│   ├── algorithms/
│   ├── config/
│   └── utils/
│
├── dashboard/
│
├── notebooks/
│
└── report/
```

---

# 📄 Các file ở thư mục gốc

## README.md

Giới thiệu dự án.

Bao gồm:

* Mục tiêu
* Công nghệ sử dụng
* Cách chạy project
* Liên kết đến các tài liệu khác

---

## PROJECT_STRUCTURE.md

Mô tả cấu trúc thư mục và quy ước phát triển.

---

## TASKS.md

Theo dõi phân công công việc của từng thành viên.

---

## ROADMAP.md

Theo dõi tiến độ tổng của dự án.

---

## requirements.txt

Danh sách toàn bộ thư viện Python cần cài đặt.

Ví dụ:

* pyspark
* graphframes
* pymongo
* pandas
* streamlit

---

# 📂 data/

Chứa toàn bộ dữ liệu sử dụng trong dự án.

## raw/

Lưu dataset gốc.

Quy định:

* Không chỉnh sửa trực tiếp.
* Không ghi đè.
* Luôn giữ nguyên dữ liệu ban đầu.

---

## processed/

Lưu dữ liệu sau khi tiền xử lý.

Ví dụ:

* dữ liệu đã làm sạch
* dữ liệu đã chuyển đổi kiểu
* dữ liệu đã loại bỏ giá trị thiếu

---

## sample/

Dữ liệu nhỏ dùng để:

* test thuật toán
* debug
* thử nghiệm GraphFrame

Không dùng để đánh giá kết quả cuối cùng.

---

# 📂 docs/

Lưu các tài liệu trong quá trình phát triển.

## meeting_notes.md

Ghi lại nội dung các buổi họp.

Ví dụ:

* công việc đã hoàn thành
* vấn đề gặp phải
* kế hoạch tiếp theo

---

## decisions.md

Ghi lại các quyết định quan trọng của nhóm.

Ví dụ:

* sử dụng MongoDB
* sử dụng Streamlit
* chỉ phát hiện chu trình 3 cạnh

Mục đích:

Tránh quên hoặc hiểu khác nhau giữa các thành viên.

---

## references.md

Lưu các tài liệu tham khảo.

Ví dụ:

* Apache Spark
* GraphFrames
* MongoDB
* Dataset
* Bài báo khoa học

---

# 📂 src/

Chứa toàn bộ mã nguồn chính của dự án.

Không đặt Notebook trong thư mục này.

---

## ingestion/

Đọc dữ liệu.

Ví dụ:

* import dữ liệu
* kết nối MongoDB
* đọc Spark DataFrame

---

## preprocessing/

Tiền xử lý dữ liệu.

Ví dụ:

* xử lý dữ liệu thiếu
* đổi kiểu dữ liệu
* loại bỏ dữ liệu lỗi

---

## graph/

Xây dựng đồ thị.

Ví dụ:

* tạo Vertices
* tạo Edges
* khởi tạo GraphFrame

---

## algorithms/

Các thuật toán phân tích.

Ví dụ:

* motif.py
* pagerank.py
* label_propagation.py

---

## config/

Lưu các thông tin cấu hình.

Ví dụ:

* URI MongoDB
* tên Database
* tên Collection
* cấu hình Spark

Không ghi mật khẩu thật vào Repository.

---

## utils/

Các hàm dùng chung.

Ví dụ:

* logger
* helper functions
* validate schema

---

# 📂 dashboard/

Chứa toàn bộ mã nguồn Dashboard.

Ví dụ:

* app.py
* components
* biểu đồ
* bảng dữ liệu

---

# 📂 notebooks/

Chứa Notebook phục vụ nghiên cứu.

Ví dụ:

* EDA
* thử nghiệm thuật toán
* phân tích dữ liệu

Không sử dụng Notebook làm chương trình chính của dự án.

---

# 📂 report/

Lưu các tài liệu phục vụ nộp đồ án.

Ví dụ:

* báo cáo
* slide
* hình ảnh
* sơ đồ

---

# 📌 Quy ước đặt tên

* Tên thư mục: chữ thường.
* Không dùng khoảng trắng.
* Dùng dấu gạch dưới (`_`) nếu tên có nhiều từ.
* File Python đặt theo chức năng.

Ví dụ:

```
motif.py
pagerank.py
graph_builder.py
```

---

# 📌 Quy tắc làm việc

* Không chỉnh sửa module do thành viên khác phụ trách nếu chưa trao đổi.
* Mỗi module cần được kiểm tra trước khi tích hợp.
* Mã nguồn phải được đặt đúng thư mục theo chức năng.
* Không lưu dữ liệu tạm hoặc file thử nghiệm vào Repository.
* Cập nhật tài liệu khi có thay đổi lớn về cấu trúc dự án.

---

# 📌 Quy trình phát triển

```
Dataset
    │
    ▼
Ingestion
    │
    ▼
Preprocessing
    │
    ▼
Graph Construction
    │
    ▼
Graph Analytics
    │
    ▼
MongoDB
    │
    ▼
Dashboard
```
