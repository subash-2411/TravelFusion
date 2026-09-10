import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "travel_fusion.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE EmergencyAlerts ADD COLUMN emergency_type VARCHAR(50)")
    print("Added emergency_type column")
except Exception as e:
    print("Error adding emergency_type:", e)

try:
    cursor.execute("ALTER TABLE EmergencyAlerts ADD COLUMN message TEXT")
    print("Added message column")
except Exception as e:
    print("Error adding message:", e)

conn.commit()
conn.close()
