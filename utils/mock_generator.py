import sqlite3
import os
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_connection, init_db

def generate_mock_data():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if data already exists to avoid duplication
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return "Database already initialized with data."
        
    first_names = ["Arjun", "Neha", "Rohan", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Rahul", "Pooja",
                   "Karan", "Isha", "Manav", "Divya", "Sahil", "Nisha", "Aditya", "Sakshi", "Nitin", "Meera",
                   "Harsh", "Tanvi", "Yash", "Mitali", "Rajat", "Kavya", "Om", "Ritika", "Vipul", "Aisha",
                   "Dev", "Shreya", "Parth", "Komal", "Tushar", "Esha", "Gaurav", "Heena", "Jay", "Riya",
                   "Abhishek", "Jiya", "Sameer", "Anjali", "Varun", "Pallavi", "Nikhil", "Swati", "Deepak", "Ankita"]
    last_names = ["Sharma", "Verma", "Kumar", "Patel", "Singh", "Joshi", "Das", "Mehta", "Reddy", "Nair",
                  "Mishra", "Gupta", "Iyer", "Bose", "Saxena", "Kapoor", "Kulkarni", "Naik", "Roy", "Sen",
                  "Chopra", "Agarwal", "Malhotra", "Jain", "Balakrishnan", "Yadav", "Rao", "Banerjee", "Dutta", "Sethi",
                  "Bhatia", "Desai", "Pillai", "Murthy", "Khanna", "Bharadwaj", "Nadkarni", "Khan", "Sengupta", "Vora",
                  "Chatterjee", "Prasad", "Tripathi", "Lal", "Pandey", "Mayekar", "Soni", "Bhardwaj", "Chauhan", "Shah"]
    statuses = ["Employed", "Self-Employed", "Unemployed"]
    
    users_data = []
    for i in range(50):
        fname = first_names[i]
        lname = last_names[i]
        email = f"{fname.lower()}.{lname.lower()}@example.com"
        dob = f"19{random.randint(75,99)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        estat = random.choice(statuses)
        users_data.append((fname, lname, email, dob, estat))
        
    cursor.executemany('''
        INSERT INTO users (first_name, last_name, email, date_of_birth, employment_status)
        VALUES (?, ?, ?, ?, ?)
    ''', users_data)
    
    # Generate historical base entries for Month 1 (Jan 2026)
    cursor.execute("SELECT user_id, email FROM users")
    users = cursor.fetchall()
    
    for uid, email in users:
        income = random.randint(40000, 150000)
        emi = random.choice([0, 0, 5000, 12000, 25000])
        utilization = round(random.uniform(0.05, 0.85), 2)
        missed = random.choice([0, 0, 0, 0, 1])
        
        cursor.execute('''
            INSERT INTO financial_records (user_id, record_date, monthly_income, existing_loan_emi, credit_card_utilization, missed_payments_count)
            VALUES (?, '2026-01-15', ?, ?, ?, ?)
        ''', (uid, income, emi, utilization, missed))
        
    conn.commit()
    
    # Create a batch update file template for Month 2 (Feb 2026)
    update_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'updates')
    os.makedirs(update_dir, exist_ok=True)
    csv_path = os.path.join(update_dir, 'february_updates.csv')
    
    with open(csv_path, 'w') as f:
        f.write("email,record_date,monthly_income,existing_loan_emi,credit_card_utilization,missed_payments_count\n")
        for uid, email in users:
            # Shift data slightly to simulate updates
            income = random.randint(40000, 150000)
            emi = random.choice([0, 0, 5000, 12000, 25000])
            utilization = round(random.uniform(0.05, 0.85), 2)
            missed = random.choice([0, 0, 0, 0, 2])
            f.write(f"{email},2026-02-15,{income},{emi},{utilization},{missed}\n")
            
    conn.close()
    return f"Sample database built. Mock CSV template created at: {csv_path}"


if __name__ == '__main__':
    print(generate_mock_data())
