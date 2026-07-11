import sqlite3
import pandas as pd
import os

# Configuration Constants
DB_PATH = '../data/ecommerce.db'
CLEANED_DIR = '../data/cleaned'

def setup_database():
    """Loads cleaned CSV datasets into an SQLite relational database."""
    print("[INFO] Initializing SQLite database setup...")
    
    # Establish connection to SQLite (Creates the file if it doesn't exist)
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    datasets = ['customers', 'products', 'orders', 'order_items']
    
    for table in datasets:
        file_path = f"{CLEANED_DIR}/{table}.csv"
        print(f"[INFO] Processing and loading '{table}'...")
        try:
            df = pd.read_csv(file_path)
            # Export dataframe to SQLite table
            df.to_sql(table, conn, if_exists='replace', index=False)
            print(f"  -> [SUCCESS] Loaded {len(df)} records into '{table}' table.")
        except FileNotFoundError:
            print(f"  -> [ERROR] {file_path} not found. Ensure cleaning step is completed.")
        except Exception as e:
            print(f"  -> [ERROR] Failed to load {table}. Exception: {e}")
            
    conn.close()
    print(f"\n[SUCCESS] Database integration complete. Database path: {os.path.abspath(DB_PATH)}")

if __name__ == "__main__":
    setup_database()