import csv
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_connection, init_db


MOCK_DATA_SEED = 2026
DATA_DIR = PROJECT_ROOT / "data"
UPDATES_DIR = DATA_DIR / "updates"


def generate_mock_data():
    """Create deterministic January data and sequential February/March updates."""
    random.seed(MOCK_DATA_SEED)
    init_db()
    with get_connection() as connection:
        if connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
            return "Database already initialized with data."

        first_names = [
            "Arjun", "Neha", "Rohan", "Priya", "Amit", "Sneha", "Vikram", "Ananya", "Rahul", "Pooja",
            "Karan", "Isha", "Manav", "Divya", "Sahil", "Nisha", "Aditya", "Sakshi", "Nitin", "Meera",
            "Harsh", "Tanvi", "Yash", "Mitali", "Rajat", "Kavya", "Om", "Ritika", "Vipul", "Aisha",
            "Dev", "Shreya", "Parth", "Komal", "Tushar", "Esha", "Gaurav", "Heena", "Jay", "Riya",
            "Abhishek", "Jiya", "Sameer", "Anjali", "Varun", "Pallavi", "Nikhil", "Swati", "Deepak", "Ankita",
        ]
        last_names = [
            "Sharma", "Verma", "Kumar", "Patel", "Singh", "Joshi", "Das", "Mehta", "Reddy", "Nair",
            "Mishra", "Gupta", "Iyer", "Bose", "Saxena", "Kapoor", "Kulkarni", "Naik", "Roy", "Sen",
            "Chopra", "Agarwal", "Malhotra", "Jain", "Balakrishnan", "Yadav", "Rao", "Banerjee", "Dutta", "Sethi",
            "Bhatia", "Desai", "Pillai", "Murthy", "Khanna", "Bharadwaj", "Nadkarni", "Khan", "Sengupta", "Vora",
            "Chatterjee", "Prasad", "Tripathi", "Lal", "Pandey", "Mayekar", "Soni", "Bhardwaj", "Chauhan", "Shah",
        ]
        statuses = ["Employed", "Self-Employed", "Unemployed"]
        users_data = []
        for index in range(50):
            first_name = first_names[index]
            last_name = last_names[index]
            employment_status = (
                random.choice(["Employed", "Self-Employed"])
                if index in (1, 2)
                else random.choice(statuses)
            )
            users_data.append(
                (
                    first_name,
                    last_name,
                    f"{first_name.lower()}.{last_name.lower()}@example.com",
                    f"19{random.randint(75, 99)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    employment_status,
                )
            )
        connection.executemany(
            "INSERT INTO users (first_name, last_name, email, date_of_birth, employment_status) VALUES (?, ?, ?, ?, ?)",
            users_data,
        )

        users = connection.execute(
            "SELECT user_id, email, employment_status FROM users ORDER BY user_id"
        ).fetchall()
        january_profiles = {}
        for user_index, (user_id, email, employment_status) in enumerate(users):
            monthly_income = 0 if employment_status == "Unemployed" else random.randint(40000, 150000)
            existing_loan_emi = (
                5000
                if user_index == 2
                else 0 if monthly_income == 0 else random.choice([0, 0, 5000, 12000, 25000])
            )
            values = (
                monthly_income,
                existing_loan_emi,
                round(random.uniform(0.05, 0.85), 2),
                random.choice([0, 0, 0, 0, 1]),
                random.randint(3, 120) if employment_status == "Employed" else 0,
                random.randint(10000, 750000),
            )
            january_profiles[email] = {
                "income": values[0],
                "emi": values[1],
                "utilization": values[2],
                "missed": values[3],
                "tenure": values[4],
                "savings": values[5],
            }
            connection.execute(
                """INSERT INTO financial_records (
                    user_id, record_date, monthly_income, existing_loan_emi,
                    credit_card_utilization, missed_payments_count,
                    employment_tenure_months, savings_balance
                ) VALUES (?, '2026-01-15', ?, ?, ?, ?, ?, ?)""",
                (user_id, *values),
            )

    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    monthly_profiles = dict(january_profiles)
    headers = [
        "email", "record_date", "monthly_income", "existing_loan_emi",
        "credit_card_utilization", "missed_payments_count",
        "employment_tenure_months", "savings_balance",
    ]
    for month_index, (filename, date) in enumerate(
        (("february_updates.csv", "2026-02-15"), ("March_updates.csv", "2026-03-15")),
        start=1,
    ):
        with (UPDATES_DIR / filename).open("w", newline="", encoding="utf-8") as update_file:
            writer = csv.writer(update_file)
            writer.writerow(headers)
            for user_index, (_, email, employment_status) in enumerate(users):
                previous = monthly_profiles[email]
                income = previous["income"]
                if user_index == 1 and month_index == 1:
                    income = round(previous["income"] * 1.25)
                elif user_index == 1:
                    income = previous["income"]
                elif employment_status == "Self-Employed" and income > 0:
                    income = round(income * random.uniform(0.70, 1.30))
                elif income > 0:
                    income = round(income * (1 + random.choice([0, 0, 0, 0.005])))

                missed_payments = max(0, previous["missed"] + random.choice([-1, 1]))
                utilization = (
                    0.88
                    if user_index == 0 and month_index == 1
                    else 0.95
                    if user_index == 0
                    else round(min(0.95, previous["utilization"] + random.uniform(-0.03, 0.03)), 2)
                )
                tenure = previous["tenure"] + 1 if employment_status == "Employed" else 0
                savings = previous["savings"]
                if income > 0 and income - previous["emi"] > 0:
                    savings = round(savings * (1 + random.choice([0.01, 0.02, 0.03])))
                elif employment_status == "Unemployed" and utilization > 0:
                    savings = max(0, round(savings * (1 - random.choice([0.01, 0.02, 0.03]))))

                monthly_profiles[email] = {
                    **previous,
                    "income": income,
                    "missed": missed_payments,
                    "utilization": utilization,
                    "tenure": tenure,
                    "savings": savings,
                }
                writer.writerow([
                    email, date, income, previous["emi"], utilization,
                    missed_payments, tenure, savings,
                ])
    return f"Sample database built. Mock CSV templates created at: {UPDATES_DIR}"


if __name__ == "__main__":
    print(generate_mock_data())
