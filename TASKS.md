# 👥 Phân Công Công Việc

## Tổng quan

| Thành viên       | Vai trò chính                                                    |
| ---------------- | ---------------------------------------------------------------- |
| **Thành viên A** | Data Engineering, Data Pipeline, MongoDB, Dashboard              |
| **Thành viên B** | Graph Analytics, Fraud Detection, Thuật toán, Báo cáo thuật toán |

---

# 👤 Thành viên A - Data Engineering

## Module 1. Chuẩn bị môi trường

### Mục tiêu

Chuẩn bị toàn bộ môi trường để nhóm có thể bắt đầu phát triển.

### Công việc

* Cài đặt Python
* Cài đặt Apache Spark
* Cài đặt Java
* Cài đặt MongoDB
* Cài đặt GraphFrames
* Tạo Virtual Environment
* Tạo `requirements.txt`
* Kiểm tra toàn bộ môi trường hoạt động

### Deliverable

* Spark chạy thành công
* MongoDB hoạt động
* Có thể kết nối Spark ↔ MongoDB

### Checkpoint

Hai thành viên cùng xác nhận môi trường hoạt động.

---

## Module 2. Data Pipeline

### Mục tiêu

Đưa dữ liệu từ Dataset vào MongoDB và đọc lên Spark.

### Công việc

* Tìm hiểu Dataset
* Import Dataset vào MongoDB
* Đọc dữ liệu bằng MongoDB Spark Connector
* Tiền xử lý dữ liệu cơ bản
* Chuyển đổi kiểu dữ liệu
* Xử lý dữ liệu thiếu
* Kiểm tra Schema

### Deliverable

Spark DataFrame sạch.

### Bàn giao

Bàn giao DataFrame cho Thành viên B.

### Checkpoint

Hai thành viên xác nhận:

* Schema đúng
* Dữ liệu đầy đủ
* Không còn lỗi kiểu dữ liệu

---

## Module 3. Dashboard

### Mục tiêu

Hiển thị kết quả phân tích.

### Công việc

* Kết nối MongoDB
* Đọc dữ liệu kết quả
* Xây dựng Dashboard bằng Streamlit
* Hiển thị bảng dữ liệu
* Hiển thị biểu đồ
* Hiển thị danh sách tài khoản nghi ngờ

### Deliverable

Dashboard hoạt động.

### Checkpoint

Thành viên B xác nhận Dashboard hiển thị đúng dữ liệu.

---

## Module 4. Kiểm thử hệ thống

### Công việc

* Kiểm tra Pipeline
* Kiểm tra Dashboard
* Kiểm tra MongoDB
* Kiểm tra kết nối toàn hệ thống

---

# 👤 Thành viên B - Graph Analytics

## Module 1. Nghiên cứu dữ liệu

### Mục tiêu

Hiểu cấu trúc Dataset và xác định cách biểu diễn dữ liệu dưới dạng đồ thị.

### Công việc

* Đọc tài liệu Dataset
* Phân tích các cột dữ liệu
* Xác định Vertex
* Xác định Edge
* Thiết kế Graph Model

### Deliverable

Tài liệu mô tả Graph Model.

### Checkpoint

Thống nhất với Thành viên A về Data Contract.

---

## Module 2. Xây dựng Graph

### Mục tiêu

Biểu diễn dữ liệu thành GraphFrame.

### Công việc

* Tạo Vertices
* Tạo Edges
* Khởi tạo GraphFrame
* Kiểm tra Graph

### Deliverable

GraphFrame hoạt động.

### Checkpoint

Thành viên A xác nhận Graph được tạo thành công.

---

## Module 3. Phát hiện chu trình

### Mục tiêu

Tìm các vòng giao dịch đáng ngờ.

### Công việc

* Nghiên cứu Motif Finding
* Xây dựng truy vấn GraphFrame
* Lọc chu trình 3 cạnh
* Bổ sung điều kiện thời gian
* Bổ sung điều kiện số tiền

### Deliverable

Danh sách các chu trình nghi ngờ.

### Checkpoint

Đánh giá kết quả với dữ liệu mẫu trước khi chạy dữ liệu lớn.

---

## Module 4. PageRank

### Mục tiêu

Xác định tài khoản trung chuyển.

### Công việc

* Nghiên cứu PageRank
* Chạy thuật toán
* Phân tích kết quả
* Xếp hạng tài khoản

### Deliverable

Danh sách tài khoản có PageRank cao.

### Checkpoint

So sánh kết quả với cấu trúc đồ thị.

---

## Module 5. Community Detection

### Mục tiêu

Tìm nhóm tài khoản giao dịch bất thường.

### Công việc

* Nghiên cứu Label Propagation
* Chạy thuật toán
* Phân tích cộng đồng
* Đánh giá kết quả

### Deliverable

Danh sách Community.

### Checkpoint

Kiểm tra số lượng Community và tính hợp lý.

---

## Module 6. Tổng hợp kết quả

### Mục tiêu

Chuẩn bị dữ liệu cho Dashboard.

### Công việc

* Tổng hợp kết quả Motif
* Tổng hợp PageRank
* Tổng hợp Community
* Chuẩn hóa DataFrame kết quả

### Deliverable

DataFrame kết quả cuối cùng.

### Bàn giao

Bàn giao cho Thành viên A để lưu vào MongoDB và hiển thị Dashboard.

---

## Module 7. Báo cáo

### Công việc

* Viết phần Graph Analytics
* Viết phần Motif Finding
* Viết phần PageRank
* Viết phần Label Propagation
* Giải thích kết quả thực nghiệm

---

# 👥 Công việc chung

Hai thành viên cùng thực hiện:

* Thiết kế kiến trúc hệ thống.
* Thống nhất Data Contract.
* Quản lý GitHub Repository.
* Kiểm thử toàn bộ hệ thống.
* Hoàn thiện báo cáo.
* Chuẩn bị slide thuyết trình.
* Luyện tập báo cáo.
