import sqlite3
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
print(dict(conn.execute('SELECT * FROM RideBookings ORDER BY id DESC LIMIT 1').fetchone()))
