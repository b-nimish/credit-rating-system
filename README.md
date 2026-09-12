# 📊 Credit Rating & Loan Eligibility System

A modular desktop application built with **Python, Tkinter, and SQLite** to manage customer profiles, process periodic financial updates via CSV files, and dynamically calculate credit scores and loan eligibility using a custom scoring engine.

---

## 📁 Project Architecture

The project follows a modular design pattern to keep the user interface, database models, business logic, and testing utilities decoupled.

```text
credit_rating_system/
│
├── data/                       # Database storage and transaction streams
│   ├── credit_system.db        # Auto-generated SQLite database
│   └── updates/                # Folder for staging new update CSV files
│
├── src/                        # Core source application logic
│   ├── __init__.py
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
Launch the primary initialization script. On your very first boot, the system will **automatically generate the local SQL database database**, fill it with mock user profiles, and save a sample transaction file (`february_updates.csv`) inside your updates folder:
```bash
python main.py
```

---

## 🕹️ How to Use the Application

1. **Dashboard Overview:** The primary window displays a grid list of all generated profiles.
2. **Ingesting New Records:** Click the **"Import CSV Updates"** button on the UI header and select your update file. The app reads the file, matches entries to users via email, and adds new records to the database.
3. **Credit Analytics Summary:** Double-click on any consumer row to open an analysis modal. The modal displays:
   * **Calculated Credit Score:** A dynamic calculation ranging from 300 to 850 based on payment trends, utilization ratios, and income stability.
   * **Loan Approval Assessment:** Instantly determines if the client is *Approved* or *Denied* for new financing based on debt-to-income limits.
   * **Historical Trend Log:** A clean table showcasing their past record cycles.
