import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database
admins = database.fetch_all("SELECT id, username, email, password_hash FROM Admin")
for a in admins:
    print(dict(a))
