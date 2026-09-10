import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "travel_fusion.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(UserProfiles)")
columns = [col[1] for col in cursor.fetchall()]

print("Existing columns:", columns)

if "preferred_mode" not in columns:
    try:
        cursor.execute("ALTER TABLE UserProfiles ADD COLUMN preferred_mode VARCHAR(50) DEFAULT 'Train'")
        print("Added preferred_mode column")
    except Exception as e:
        print("Error adding preferred_mode:", e)

if "status_emoji" not in columns:
    try:
        cursor.execute("ALTER TABLE UserProfiles ADD COLUMN status_emoji VARCHAR(10) DEFAULT '✈️'")
        print("Added status_emoji column")
    except Exception as e:
        print("Error adding status_emoji:", e)

if "avatar_url" not in columns:
    try:
        cursor.execute("ALTER TABLE UserProfiles ADD COLUMN avatar_url VARCHAR(255) DEFAULT '/static/images/default-avatar.png'")
        print("Added avatar_url column")
    except Exception as e:
        print("Error adding avatar_url:", e)

conn.commit()
conn.close()
print("Database schema update finished successfully.")
