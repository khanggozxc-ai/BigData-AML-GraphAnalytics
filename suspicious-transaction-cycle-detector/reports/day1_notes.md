# Ghi chú Ngày 1

## Định nghĩa bài toán
Hệ thống phát hiện các vòng giao dịch đáng ngờ bằng Graph Analytics.

## Mô hình dữ liệu
- Account = Node
- Transaction = Directed Edge
- Amount, timestamp = Edge attributes
- Cycle = Đường đi có hướng quay lại node ban đầu

## Risk scoring
| Điều kiện | Điểm |
|---|---:|
| Vòng có 3–5 tài khoản | 20 |
| Hoàn tất dưới 24 giờ | 25 |
| Số tiền lệch dưới 10% | 20 |
| Tổng giá trị vòng trên 10 triệu | 20 |
| Có tài khoản trung gian chuyển tiếp nhanh | 15 |

## Kết luận an toàn
Hệ thống không kết luận gian lận. Hệ thống chỉ hỗ trợ phát hiện mẫu giao dịch bất thường.
