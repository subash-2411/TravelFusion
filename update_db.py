import database
import config
import sqlite3

def run_migration():
    print("Running database migration...")
    
    # 1. Add new columns to Bookings
    columns = [
        "passenger_name VARCHAR(100) NULL",
        "passenger_age INT NULL",
        "passenger_gender VARCHAR(20) NULL",
        "passenger_phone VARCHAR(20) NULL",
        "passenger_email VARCHAR(255) NULL"
    ]
    for col in columns:
        try:
            database.execute_query(f"ALTER TABLE Bookings ADD COLUMN {col}")
            print(f"Added column {col.split()[0]}")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col.split()[0]} already exists.")
            else:
                print(f"Error adding {col}: {e}")

    # 2. Re-seed Drivers and Vehicles exactly as specified
    try:
        database.execute_query("DELETE FROM Vehicles")
        database.execute_query("DELETE FROM Drivers")
        print("Cleared old drivers and vehicles.")
        
        # Read the db_schema.sql, extract the driver INSERT lines and execute them
        with open('db_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            
        driver_section = schema.split("-- AUTO DRIVERS")[1].split("-- Seed Emergency Contact")[0]
        statements = driver_section.split(';')
        
        count = 0
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                database.execute_query(stmt)
                count += 1
                
        print(f"Successfully seeded new demo drivers. Executed {count} statements.")
    except Exception as e:
        print(f"Error seeding drivers: {e}")

if __name__ == '__main__':
    run_migration()
