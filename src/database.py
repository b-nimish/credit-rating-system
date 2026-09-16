import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'credit_system.db')

# Ensures the data directory exists and returns a connection to the local SQLite database.
def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

# Creates the users and financial-record tables when they do not already exist.
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            date_of_birth TEXT NOT NULL,
            employment_status TEXT NOT NULL,
            password_hash TEXT
        )
    ''')
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)")}
    if "password_hash" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create financial_records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            record_date TEXT NOT NULL,
            monthly_income REAL NOT NULL,
            existing_loan_emi REAL NOT NULL,
            credit_card_utilization REAL NOT NULL,
            missed_payments_count INTEGER NOT NULL,
            employment_tenure_months INTEGER NOT NULL DEFAULT 0,
            savings_balance REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(financial_records)")}
    if "employment_tenure_months" not in columns:
        cursor.execute(
            "ALTER TABLE financial_records ADD COLUMN employment_tenure_months INTEGER NOT NULL DEFAULT 0"
        )
    if "savings_balance" not in columns:
        cursor.execute(
            "ALTER TABLE financial_records ADD COLUMN savings_balance REAL NOT NULL DEFAULT 0"
        )
    
    conn.commit()
    conn.close()
