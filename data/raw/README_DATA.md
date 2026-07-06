\# Raw Dataset



Dataset dùng cho đồ án: IBM Transactions for Anti Money Laundering hoặc dataset giao dịch đáng ngờ tải từ Kaggle.



Do kích thước lớn, file CSV gốc không được commit lên GitHub.



Vị trí local:

data/raw/ibm\_aml\_transactions.csv



Mục tiêu xử lý:

\- Chuẩn hóa dữ liệu giao dịch về schema chung.

\- Biến tài khoản gửi và tài khoản nhận thành node.

\- Biến giao dịch thành directed edge.

\- Phục vụ phát hiện cycle giao dịch đáng ngờ.

