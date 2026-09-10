import sqlite3
import json

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
trip = cursor.execute("SELECT * FROM RideBookings WHERE status IN ('accepted', 'active') ORDER BY id DESC LIMIT 1").fetchone()
if trip:
    print(json.dumps(dict(trip), indent=2))
else:
    print("No active trip")
