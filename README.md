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
│   ├── user_credentials.csv    # Generated email/password reference
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
* `password_hash` (TEXT): PBKDF2 hash used for user login; plaintext passwords are not stored.

### 2. `admins` Table
Stores the administrator username and PBKDF2 password hash. The default account is created on first startup with username `admin` and password `password`.

### 3. `financial_records` Table
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

On Windows, run the command from PowerShell in the project directory. If the Python prompt shows `>>>`, type `exit()` first, then run `python main.py` at the PowerShell prompt.

The application displays a role selection screen before opening the protected area. Use the default admin credentials:

* **Username:** `admin`
* **Password:** `password`

User passwords follow the simple lowercase `namesurname123` format, for example `arjunsharma123`. Credentials are written to `data/user_credentials.csv`; users sign in with their email and formatted password. New users added by an administrator receive their initial password in the confirmation dialog.

---

## 🕹️ How to Use the Application

1. **Choose a login:** Select **Admin Login** to manage profiles and financial updates, or **User Login** to view one applicant's eligibility.
2. **Admin login:** Enter `admin` and `password` to access the dashboard.
3. **User login:** Enter an email and its `namesurname123` password to see only that user's credit score, eligibility status, and maximum qualified loan amount.
4. **Log out:** Click **Log out** from either the admin dashboard or user eligibility screen to return to the login-choice screen.
5. **Change passwords:** Users can change their own password after entering the current password. Admins can change their own password or select an applicant and use **Change User Password** to set that user's password. Before saving, the new password is displayed for confirmation with **Continue** or **Cancel**.
6. **Dashboard overview:** The admin dashboard displays a grid list of all profiles. Controls are grouped into **Data Management**, **Account Management**, and **Search** sections so all actions remain visible in the window.
7. **Search and filter:** Use the **Search** field to filter rows as you type. The search checks the ID, first name, last name, email, and employment status. Click **Clear** to remove the filter.
8. **Sort entries:** Click a column header to sort by that column. Click the same header again to reverse the order. IDs are sorted numerically, while text columns are sorted alphabetically without case sensitivity.
9. **Refresh the list:** Click **Refresh List** to reload the latest users from the database. This redraws the table but does not modify database records or recalculate scores.
10. **Add a user:** Click **Add User** and provide the first name, last name, email, date of birth, and employment status. The database assigns the user's ID automatically. Email addresses must be unique. The initial password is shown after creation.
11. **Delete an entry:** Select an applicant and click **Delete Selected**. The application asks for confirmation before deleting the applicant and all linked financial records. Canceling the confirmation leaves the data unchanged.
12. **Ingest new records:** Click **Import Update CSV** in the header and select an update file. The app matches rows to users by email, adds recognized financial records, reports skipped emails, and refreshes the list.
13. **Credit analytics summary:** Double-click any applicant row to open an analysis modal. The assessment window includes a **View Details** button that opens the applicant's financial records:
   * **Financial details:** Record date, monthly income, existing loan EMI, credit card utilization, and missed payments.
   * **Calculated Credit Score:** A dynamic calculation ranging from 300 to 850 based on payment trends, utilization ratios, and income stability.
   * **Loan Approval Assessment:** Instantly determines if the client is *Approved* or *Denied* for new financing based on debt-to-income limits.
   * **Historical Trend Log:** A clean table showcasing their past record cycles.

14. **User details:** After a user logs in, the **My Loan Eligibility** window includes **View Details**, allowing that user to view their own financial records only. The window also includes **Change Password** and **Log out**.

The login protects database access through the application UI. The SQLite database file is still stored locally and is not encrypted, so operating-system file permissions are required to protect against direct access to the database file.
