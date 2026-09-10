import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "travel_fusion.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login TIMESTAMP NULL
)
''')

try:
    cur.execute('''
    INSERT INTO Admin (username, email, password_hash)
    VALUES ('Narmu', 'Narmu@travelfusion.ai', 'pbkdf2:sha256:260000$adminhashpwd')
    ''')
except sqlite3.IntegrityError:
    pass # Already exists

conn.commit()
conn.close()
print("Admin table created and seeded.")
