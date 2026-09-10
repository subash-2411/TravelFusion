import os
import sys
import sqlite3
import config

DB_TYPE = 'sqlite' # Default fallback
connection_error_msg = None

# Attempt to connect to MySQL
if config.DB_TYPE == 'mysql':
    try:
        import mysql.connector
        # Test connection
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD
        )
        # Create database if not exists
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB}")
        conn.close()
        
        DB_TYPE = 'mysql'
        print(" * Connected to MySQL Database successfully.")
    except Exception as e:
        connection_error_msg = str(e)
        print(f" * MySQL Connection failed ({e}). Falling back to SQLite.")
        DB_TYPE = 'sqlite'
else:
    DB_TYPE = 'sqlite'
    print(" * Using SQLite Database as configured.")

def get_db_connection():
    if DB_TYPE == 'mysql':
        import mysql.connector
        return mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB
        )
    else:
        conn = sqlite3.connect(config.SQLITE_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row # Return dictionary-like rows
        # Enable Foreign Keys in SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

def translate_query(query):
    """Translates MySQL query parameters (%s) to SQLite (?) if needed."""
    if DB_TYPE == 'sqlite':
        # Replace MySQL placeholder %s with SQLite placeholder ?
        # Be careful not to replace actual strings containing %s, but simple replacement is fine for our controlled queries.
        return query.replace('%s', '?')
    return query

def execute_query(query, params=None):
    """Executes a INSERT/UPDATE/DELETE query and commits."""
    query = translate_query(query)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Database Error executing [{query}]: {e}")
        try:
            with open("C:\\Kutty\\db_errors.txt", "a") as f:
                f.write(f"Execute Error: {str(e)} | Query: {query}\n")
        except:
            pass
        return False
    finally:
        conn.close()

def insert_query(query, params=None):
    """Executes an INSERT query and returns the last inserted row ID."""
    query = translate_query(query)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        if DB_TYPE == 'mysql':
            return cursor.lastrowid
        else:
            return cursor.lastrowid
    except Exception as e:
        print(f"Database Error inserting [{query}]: {e}")
        try:
            with open("C:\\Kutty\\db_errors.txt", "a") as f:
                f.write(f"Insert Error: {str(e)} | Query: {query}\n")
        except:
            pass
        return None
    finally:
        conn.close()

class DictObj(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No such attribute: {name}")

def fetch_all(query, params=None):
    """Fetches all results from a SELECT query."""
    query = translate_query(query)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if DB_TYPE == 'mysql':
            columns = [col[0] for col in cursor.description]
            return [DictObj(zip(columns, row)) for row in cursor.fetchall()]
        else:
            return [DictObj(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Database Error fetching all [{query}]: {e}")
        return []
    finally:
        conn.close()

def fetch_one(query, params=None):
    """Fetches a single result from a SELECT query."""
    query = translate_query(query)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        row = cursor.fetchone()
        if not row:
            return None
            
        if DB_TYPE == 'mysql':
            columns = [col[0] for col in cursor.description]
            return DictObj(zip(columns, row))
        else:
            return DictObj(row)
    except Exception as e:
        print(f"Database Error fetching one [{query}]: {e}")
        return None
    finally:
        conn.close()

def init_db():
    """Initializes the database using db_schema.sql, performing SQLite translation if needed."""
    # Speed check: If table 'Users' already exists, skip reading schema and executing queries
    if DB_TYPE == 'sqlite' and os.path.exists(config.SQLITE_PATH):
        try:
            conn = sqlite3.connect(config.SQLITE_PATH, timeout=2.0)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users';")
            exists = cursor.fetchone()
            conn.close()
            if exists:
                print(f" * Database already initialized ({DB_TYPE.upper()}). Skipping schema setup.")
                return True
        except Exception:
            pass
    elif DB_TYPE == 'mysql':
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DB
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES LIKE 'Users'")
            exists = cursor.fetchone()
            conn.close()
            if exists:
                print(f" * Database already initialized ({DB_TYPE.upper()}). Skipping schema setup.")
                return True
        except Exception:
            pass

    schema_path = os.path.join(os.path.dirname(__file__), 'db_schema.sql')
    if not os.path.exists(schema_path):
        print(" * db_schema.sql not found! Cannot initialize database.")
        return False
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_content = f.read()
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DB_TYPE == 'mysql':
        # Executing MySQL commands. We split by semicolon to run individually.
        # But MySQL connector doesn't easily execute multiple statements unless specified,
        # so we run each non-empty line/statement.
        statements = schema_content.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(f"MySQL Init Warn on stmt [{stmt[:100]}...]: {e}")
        conn.commit()
    else:
        # SQLite Translation
        lines = []
        for line in schema_content.splitlines():
            # Skip MySQL-specific database creation commands
            if line.strip().startswith('CREATE DATABASE') or line.strip().startswith('USE '):
                continue
            # Translate auto increment
            line = line.replace('INT AUTO_INCREMENT PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
            line = line.replace('AUTO_INCREMENT', '') # SQLite autoincrement triggers on INTEGER PRIMARY KEY
            line = line.replace('DATETIME', 'TEXT') # SQLite stores datetime as Text
            line = line.replace('TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            # For table schema, SQLite requires table fields first, then table constraints.
            # Our SQL file is formatted standardly, so executing statements directly will work.
            lines.append(line)
            
        sqlite_schema = '\n'.join(lines)
        statements = sqlite_schema.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    # If table already exists, ignore or log
                    if "already exists" not in str(e):
                        print(f"SQLite Init Warn on stmt [{stmt[:100]}...]: {e}")
        conn.commit()
        
    conn.close()
    print(f" * Database initialized successfully. ({DB_TYPE.upper()})")
    return True

# Initialize database on import/startup
if __name__ == '__main__':
    init_db()
else:
    # Proactively initialize database if we are running in the application
    init_db()
