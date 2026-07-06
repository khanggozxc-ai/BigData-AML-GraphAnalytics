# Suspicious Transaction Cycle Detector — Day 1 MVP

## Mục tiêu
Xây dựng pipeline phát hiện vòng giao dịch đáng ngờ bằng Graph Analytics.

## Luồng xử lý
Raw transactions → Data cleaning → Graph construction → Cycle detection → Risk scoring → CSV output.

## Cài đặt
```bash
pip install -r requirements.txt
```

## Chạy pipeline ngày 1
```bash
python src/main.py
```

## Kết quả đầu ra
- `data/raw/transactions_raw.csv`
- `data/processed/transactions_clean.csv`
- `data/output/suspicious_cycles.csv`

## Ý nghĩa dữ liệu
- `source_account`: tài khoản gửi tiền.
- `target_account`: tài khoản nhận tiền.
- Một giao dịch là một cạnh có hướng: `source_account -> target_account`.
- Một vòng giao dịch là đường đi quay lại tài khoản ban đầu, ví dụ `A001 -> A002 -> A003 -> A001`.

## Lưu ý
Hệ thống chỉ đánh dấu giao dịch đáng ngờ để hỗ trợ kiểm tra, không kết luận gian lận.
