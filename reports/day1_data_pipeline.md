# Ngày 1 — Data Pipeline

## 1. Mục tiêu
Chuẩn hóa dataset giao dịch từ Kaggle thành dữ liệu đầu vào cho hệ thống phát hiện vòng giao dịch đáng ngờ bằng Graph Analytics.

## 2. Dataset
Dataset được tải từ Kaggle, gồm các giao dịch chuyển tiền giữa các tài khoản. Dữ liệu có dạng từ tài khoản gửi đến tài khoản nhận, kèm số tiền, thời gian và nhãn rửa tiền nếu có.

## 3. Schema chuẩn
| Cột | Ý nghĩa |
|---|---|
| transaction_id | Mã giao dịch |
| source_account | Tài khoản gửi |
| target_account | Tài khoản nhận |
| amount | Số tiền giao dịch |
| timestamp | Thời gian giao dịch |
| transaction_type | Hình thức giao dịch |
| is_laundering | Nhãn rửa tiền nếu dataset có |

## 4. Quy trình xử lý
Raw CSV → Inspect columns → Normalize schema → Clean invalid records → Export transactions_clean.csv.

## 5. Vai trò trong graph
- Account là node.
- Transaction là directed edge.
- Amount và timestamp là thuộc tính của edge.

## 6. Kết quả ngày 1
- Đã tạo dữ liệu sạch: data/processed/transactions_clean.csv
- Đã chuẩn bị dữ liệu cho graph pipeline.
- Đã chạy thử pipeline phát hiện cycle.