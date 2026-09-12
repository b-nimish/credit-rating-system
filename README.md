# 📊 Credit Rating & Loan Eligibility System

A modular desktop application built with **Python, Tkinter, and SQLite** to manage customer profiles, process periodic financial updates via CSV files, and dynamically calculate credit scores and loan eligibility using a custom scoring engine.

---

## 📁 Project Architecture

The project follows a modular, function-based design to keep the user interface, database logic, business logic, and testing utilities decoupled.
```text
credit_rating_system/
│
├── data/                       # Database storage and transaction streams
│   ├── credit_system.db        # Auto-generated SQLite database
│   └── updates/                # Folder for staging new update CSV files
│
├── src/                        # Core source application logic
│   ├── __init__.py
│   ├── auth.py                 # Login credential verification
│   ├── database.py             # SQLite connection pools and table schemas
│   ├── credit_engine.py        # Credit scoring algorithms & loan validation
│   ├── csv_parser.py           # Pandas engine for safe bulk CSV ingestion
│   └── gui.py                  # Tkinter desktop interface implementation
│
├── utils/                      # Developer utilities
│   └── mock_generator.py       # Mock profile and update CSV generator
│
├── main.py                     # Application entry point
├── requirements.txt            # System dependencies
└── README.md                   # System documentation
```

---

## 🛠️ Data Model & Schema

The relational database architecture is split into static core entities and dynamic transaction log ledgers:

### 1. `users` Table
Stores permanent identity information for registered consumers.
* `user_id` (INTEGER, Primary Key): Unique internal system identifier.
* `first_name` / `last_name` (TEXT): Customer name.
* `email` (TEXT, Unique): Unique anchor point used to map CSV data imports.
* `date_of_birth` (TEXT): Age tracking parameter.
* `employment_status` (TEXT): Working status (e.g., *Employed, Self-Employed, Unemployed*).

### 2. `financial_records` Table
Tracks sequential, historical financial snapshots over time fed by periodic CSV updates.
* `record_id` (INTEGER, Primary Key): Unique row identifier.
* `user_id` (INTEGER, Foreign Key): Links record to a profile in the `users` table.
* `record_date` (TEXT): The effective calendar timestamp of the incoming data batch.
* `monthly_income` (REAL): Base recurring income.
* `existing_loan_emi` (REAL): Outgoing monthly debt payments.
* `credit_card_utilization` (REAL): Credit card balance ratio (from `0.00` to `1.00`).
* `missed_payments_count` (INTEGER): Payment delinquency tally within that cycle.

---

## ⚙️ Setting Up and Running the System

### Prerequisites
Make sure you have **Python 3.8+** installed on your machine.

### 1. Installation
Clone or navigate to your local repository directory, then run the package installer:
```bash
pip3 install virtualenv
python3 -m virtualenv env --python=python3.11
.\env\Scripts\activate.bat
pip install -r requirements.txt
```

### 2. Initialization and Execution
Launch the primary initialization script. On your very first boot, the system will **automatically generate the local SQLite database**, fill it with mock user profiles, and save a sample transaction file (`february_updates.csv`) inside your updates folder:
```bash
python main.py
```

The application displays a login screen before opening the dashboard. Use the default credentials:

* **Username:** `admin`
* **Password:** `password`

---

## 🕹️ How to Use the Application

1. **Log in:** Enter the default credentials before accessing the dashboard:
   * **Username:** `admin`
   * **Password:** `password`
   Database initialization and dashboard loading occur only after successful authentication.
2. **Dashboard Overview:** The primary window displays a grid list of all generated profiles.
3. **Search and filter:** Use the **Search** field to filter rows as you type. The search checks the ID, first name, last name, email, and employment status. Click **Clear** to remove the filter.
4. **Sort entries:** Click a column header to sort by that column. Click the same header again to reverse the order. IDs are sorted numerically, while text columns are sorted alphabetically without case sensitivity.
5. **Refresh the list:** Click **Refresh List** to reload the latest users from the database. This redraws the table but does not modify database records or recalculate scores.
6. **Add a user:** Click **Add User** and provide the first name, last name, email, date of birth, and employment status. The database assigns the new user's ID automatically. Email addresses must be unique.
7. **Delete an entry:** Select an applicant and click **Delete Selected**. The application asks for confirmation before deleting the applicant and all linked financial records. Canceling the confirmation leaves the data unchanged.
8. **Ingesting New Records:** Click the **"Import Update CSV"** button on the UI header and select your update file. The app reads the file, matches entries to users via email, adds financial records for recognized users, reports unrecognized emails as skipped, and refreshes the list after a successful import.
9. **Credit Analytics Summary:** Double-click on any consumer row to open an analysis modal. The modal displays:
   * **Calculated Credit Score:** A dynamic calculation ranging from 300 to 850 based on payment trends, utilization ratios, and income stability.
   * **Loan Approval Assessment:** Instantly determines if the client is *Approved* or *Denied* for new financing based on debt-to-income limits.
   * **Historical Trend Log:** A clean table showcasing their past record cycles.

The login protects database access through the application UI. The SQLite database file is still stored locally and is not encrypted, so operating-system file permissions are required to protect against direct access to the database file.
