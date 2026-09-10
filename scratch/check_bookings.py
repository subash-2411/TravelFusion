import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "travel_fusion.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query bookings
cursor.execute("SELECT * FROM Bookings ORDER BY id DESC LIMIT 5")
bookings = cursor.fetchall()
print("--- Recent Bookings ---")
for b in bookings:
    print(dict(b))

# Query TripTracking
cursor.execute("SELECT * FROM TripTracking ORDER BY id DESC LIMIT 5")
tracking = cursor.fetchall()
print("\n--- Recent Trip Tracking ---")
for t in tracking:
    print(dict(t))

# Query RideBookings
cursor.execute("SELECT * FROM RideBookings ORDER BY id DESC LIMIT 5")
rides = cursor.fetchall()
print("\n--- Recent Ride Bookings ---")
for r in rides:
    print(dict(r))

conn.close()
