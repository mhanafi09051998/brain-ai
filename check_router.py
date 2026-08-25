import sqlite3
import json

conn = sqlite3.connect('/home/ubuntu/.9router/db/data.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

for t in tables:
    try:
        cursor.execute(f"SELECT * FROM {t}")
        rows = cursor.fetchall()
        print(f"\n--- TABLE: {t} ({len(rows)} rows) ---")
        for r in rows[:10]:
            print(r)
    except Exception as e:
        print(f"Error {t}: {e}")
