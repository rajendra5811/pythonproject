import sqlite3
 
conn = sqlite3.connect("crypto.db")
rows = conn.execute(
    "SELECT name, price_usd FROM coins ORDER BY market_cap_usd DESC LIMIT 5"
)
for name, price in rows:
    print(f"{name:<15} ${price:,.2f}")