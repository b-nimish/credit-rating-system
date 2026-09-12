import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'credit_system.db')

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)

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
            employment_status TEXT NOT NULL
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
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
