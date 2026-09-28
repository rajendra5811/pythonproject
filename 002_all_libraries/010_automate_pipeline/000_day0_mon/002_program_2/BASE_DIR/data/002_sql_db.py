import sqlite3
import pandas as pd

connection = sqlite3.connect("orders.db")

query = """
SELECT
    order_date,
    COUNT(*) AS completed_orders,
    SUM(total_amount) AS revenue
FROM orders
WHERE status = 'Completed'
GROUP BY order_date
ORDER BY order_date;
"""

result = pd.read_sql_query(query, connection)

print(result)

connection.close()