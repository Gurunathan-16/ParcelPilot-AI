import sqlite3
from app.data.database import DATABASE_FILE

conn = sqlite3.connect(DATABASE_FILE)

conn.execute(
    "UPDATE orders SET status = ? WHERE order_id = ? AND account_id = ?",
    ("BOOKED", "ORD-1001", "ACCT-001")
)

conn.commit()
conn.close()

print("✅ ORD-1001 reset to BOOKED")