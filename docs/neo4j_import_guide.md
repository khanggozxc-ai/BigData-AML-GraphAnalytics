# Neo4j Import Guide - Phase 2 Graph Storage

## 1. Mục tiêu

Ở MVP, graph được dựng tạm thời bằng NetworkX từ file CSV.  
Ở Phase 2, hệ thống có thể dùng Neo4j để lưu trữ graph lâu dài.

Neo4j giúp biểu diễn dữ liệu tự nhiên hơn:

```text
(Account)-[:TRANSFER]->(Account)
```

## 2. Tạo file import

Chạy:

```powershell
python src/export_neo4j.py
```

Output:

```text
data/neo4j/accounts_nodes.csv
data/neo4j/transactions_edges.csv
```

## 3. Schema nodes

`accounts_nodes.csv`

| Cột | Ý nghĩa |
|---|---|
| account_id | Mã tài khoản |
| bank_id | Mã ngân hàng tách từ account_id nếu có |
| label | Loại node, mặc định Account |

## 4. Schema edges

`transactions_edges.csv`

| Cột | Ý nghĩa |
|---|---|
| source_account | Tài khoản gửi |
| target_account | Tài khoản nhận |
| amount | Số tiền |
| timestamp | Thời gian giao dịch |
| transaction_type | Loại giao dịch |
| is_laundering | Nhãn laundering nếu có |

## 5. Import vào Neo4j

Copy 2 file CSV vào thư mục import của Neo4j, sau đó chạy Cypher:

```cypher
LOAD CSV WITH HEADERS FROM 'file:///accounts_nodes.csv' AS row
MERGE (:Account {
    id: row.account_id,
    bank_id: row.bank_id
});
```

```cypher
LOAD CSV WITH HEADERS FROM 'file:///transactions_edges.csv' AS row
MATCH (a:Account {id: row.source_account})
MATCH (b:Account {id: row.target_account})
MERGE (a)-[:TRANSFER {
    amount: toFloat(row.amount),
    timestamp: row.timestamp,
    transaction_type: row.transaction_type,
    is_laundering: toInteger(row.is_laundering)
}]->(b);
```

## 6. Query vòng giao dịch

Vòng 2 tài khoản:

```cypher
MATCH path = (a:Account)-[:TRANSFER]->(b:Account)-[:TRANSFER]->(a)
RETURN path
LIMIT 50;
```

Vòng 3 tài khoản:

```cypher
MATCH path = (a:Account)-[:TRANSFER]->(b:Account)-[:TRANSFER]->(c:Account)-[:TRANSFER]->(a)
RETURN path
LIMIT 50;
```

Vòng từ 2 đến 6 bước:

```cypher
MATCH path = (a:Account)-[:TRANSFER*2..6]->(a)
RETURN path
LIMIT 100;
```

## 7. Cách ghi trong báo cáo

> Ở MVP, nhóm sử dụng NetworkX để dựng graph tạm thời từ CSV nhằm kiểm chứng logic phát hiện chu trình. Trong Phase 2, nhóm đề xuất Neo4j làm tầng lưu trữ graph để lưu tài khoản và giao dịch dưới dạng native graph, hỗ trợ truy vấn quan hệ và trực quan hóa tốt hơn.
