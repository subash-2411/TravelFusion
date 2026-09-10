import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database
database.execute_query("INSERT OR IGNORE INTO Admin (username, email, password_hash) VALUES ('admin', 'admin@travelfusion.ai', 'pbkdf2:sha256:260000$adminhashpwd')")
print("Admin inserted successfully.")
