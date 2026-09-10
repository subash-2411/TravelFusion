import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database
import app

hashed = app.generate_password_hash("admin123")
database.execute_query("UPDATE Admin SET password_hash = %s", (hashed,))
print("Updated all admins to password_hash:", hashed)
# Print current DB status
admins = database.fetch_all("SELECT id, username, email, password_hash FROM Admin")
for a in admins:
    print(dict(a))
