import pandas as pd
import sqlite3
import os
from src.database import get_connection

def import_csv_update(csv_file_path):
    if not os.path.exists(csv_file_path):
        return False, "File not found."
        
    try:
        df = pd.read_csv(csv_file_path)
        required_cols = ['email', 'record_date', 'monthly_income', 'existing_loan_emi', 'credit_card_utilization', 'missed_payments_count']
        
        if not all(col in df.columns for col in required_cols):
            return False, f"CSV must contain headers: {', '.join(required_cols)}"
            
        conn = get_connection()
        cursor = conn.cursor()
        
        success_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            # Find user ID by email
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (row['email'],))
            user = cursor.fetchone()
            
            if user:
                user_id = user[0]
                # Insert dynamic performance history snapshot
                cursor.execute('''
                    INSERT INTO financial_records (user_id, record_date, monthly_income, existing_loan_emi, credit_card_utilization, missed_payments_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, row['record_date'], row['monthly_income'], row['existing_loan_emi'], row['credit_card_utilization'], row['missed_payments_count']))
                success_count += 1
            else:
                skipped_count += 1
                
        conn.commit()
        conn.close()
        return True, f"Successfully parsed. Added {success_count} updates. Skipped {skipped_count} unrecognized emails."
        
    except Exception as e:
        return False, str(e)
