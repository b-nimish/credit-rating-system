import sqlite3
from src.database import get_connection

def calculate_credit_score(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT monthly_income, existing_loan_emi, credit_card_utilization, missed_payments_count
        FROM financial_records WHERE user_id = ?
        ORDER BY record_date DESC
    ''', (user_id,))
    
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        return 500, "No History", 0.0  # Default base score, status, max loan
        
    # Weight calculations based on cumulative records
    total_records = len(records)
    latest_record = records[0]
    
    latest_income = latest_record[0]
    latest_emi = latest_record[1]
    latest_utilization = latest_record[2]
    
    total_missed_payments = sum(r[3] for r in records)
    avg_utilization = sum(r[2] for r in records) / total_records
    
    # Base starting score
    score = 700
    
    # 1. Payment History Impact (Heavy Weight)
    score -= (total_missed_payments * 40)
    
    # 2. Credit Utilization Impact
    if avg_utilization > 0.70:
        score -= 50
    elif avg_utilization <= 0.30:
        score += 50
        
    # 3. Debt to Income Ratio Impact
    dti = (latest_emi / latest_income) if latest_income > 0 else 1.0
    if dti > 0.45:
        score -= 60
    elif dti < 0.20:
        score += 40
        
    # Bound score between 300 and 850
    score = max(300, min(850, score))
    
    # Loan Eligibility Decision
    if score >= 750:
        status = "Excellent (Highly Eligible)"
        max_loan = latest_income * 12
    elif score >= 650:
        status = "Good (Eligible with Standard Rates)"
        max_loan = latest_income * 6
    elif score >= 550:
        status = "Fair (High Risk/Conditional)"
        max_loan = latest_income * 2
    else:
        status = "Poor (Ineligible)"
        max_loan = 0.0
        
    # Adjust loan cap if current DTI is already too high
    if dti > 0.50:
        max_loan = 0.0
        status = "Ineligible (Debt Load Too High)"
        
    return score, status, round(max_loan, 2)
