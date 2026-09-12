import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from src.database import get_connection
from src.credit_engine import calculate_credit_score
from src.csv_parser import import_csv_update
from src.auth import DEFAULT_USERNAME, authenticate


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Credit Rating System - Login")
        self.root.geometry("360x220")
        self.root.resizable(False, False)

        frame = ttk.Frame(root, padding=30)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Sign in", font=("Arial", 16, "bold")).pack(pady=(0, 18))

        ttk.Label(frame, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(fill="x", pady=(2, 10))
        self.username_entry.insert(0, DEFAULT_USERNAME)

        ttk.Label(frame, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill="x", pady=(2, 12))

        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack()

        ttk.Button(frame, text="Log in", command=self.login).pack(pady=6)
        self.password_entry.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if authenticate(username, password):
            self.on_success()
            return

        self.status_label.configure(text="Invalid username or password")
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus_set()

class CreditSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Rating & Loan Eligibility System")
        self.root.geometry("850x550")
        self.all_rows = []
        self.sort_column = None
        self.sort_reverse = False
        
        # Configure Grid Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        self.create_top_panel()
        self.create_main_table()
        self.refresh_table()

    def create_top_panel(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(2, weight=1)
        
        # Actions
        btn_import = ttk.Button(top_frame, text="📥 Import Update CSV", command=self.upload_csv)
        btn_import.pack(side="left", padx=5)
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh List", command=self.refresh_table)
        btn_refresh.pack(side="left", padx=5)

        ttk.Label(top_frame, text="Search:").pack(side="left", padx=(18, 4))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=28)
        self.search_entry.pack(side="left", padx=4)
        self.search_var.trace_add("write", lambda *_: self.display_rows())
        ttk.Button(top_frame, text="Clear", command=self.clear_search).pack(side="left", padx=4)
        
        lbl_hint = ttk.Label(top_frame, text="Double-click any applicant row to compute Credit Rating & Loan Limits", font=("Arial", 9, "italic"))
        lbl_hint.pack(side="right", padx=10)

    def create_main_table(self):
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.grid(row=1, column=0, sticky="nsew")
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        columns = ("id", "first_name", "last_name", "email", "employment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        headings = {
            "id": "ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email ID",
            "employment": "Employment Status",
        }
        for column, heading in headings.items():
            self.tree.heading(
                column,
                text=heading,
                command=lambda selected_column=column: self.sort_rows(selected_column),
            )
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("first_name", width=120)
        self.tree.column("last_name", width=120)
        self.tree.column("email", width=250)
        self.tree.column("employment", width=150)
        
        # Scrollbars
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.tree.bind("<Double-1>", self.on_row_double_click)

    def refresh_table(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, first_name, last_name, email, employment_status FROM users")
            self.all_rows = cursor.fetchall()
            conn.close()
            self.display_rows()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load users: {str(e)}")

    def display_rows(self):
        search_text = self.search_var.get().strip().casefold()
        rows = self.all_rows
        if search_text:
            rows = [
                row for row in rows
                if search_text in " ".join(str(value) for value in row).casefold()
            ]

        if self.sort_column is not None:
            column_index = self.tree["columns"].index(self.sort_column)
            if self.sort_column == "id":
                sort_key = lambda row: int(row[column_index])
            else:
                sort_key = lambda row: str(row[column_index]).casefold()
            rows = sorted(
                rows,
                key=sort_key,
                reverse=self.sort_reverse,
            )

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

    def sort_rows(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.display_rows()

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()

    def upload_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            success, message = import_csv_update(file_path)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_table()
            else:
                messagebox.showerror("Import Failed", message)

    def on_row_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        user_vals = self.tree.item(selected_item, "values")
        user_id = user_vals[0]
        full_name = f"{user_vals[1]} {user_vals[2]}"
        
        # Calculate scores
        score, status, max_loan = calculate_credit_score(user_id)
        
        # Pop up window with evaluation summary
        pop = tk.Toplevel(self.root)
        pop.title(f"Credit Score Assessment: {full_name}")
        pop.geometry("450x300")
        pop.resizable(False, False)
        
        lbl_title = ttk.Label(pop, text=f"Assessment Report", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=15)
        
        lbl_name = ttk.Label(pop, text=f"Applicant: {full_name}", font=("Arial", 11))
        lbl_name.pack(pady=5)
        
        lbl_score = ttk.Label(pop, text=f"Credit Score: {score} / 850", font=("Arial", 12, "bold"), foreground="green" if score>=650 else "red")
        lbl_score.pack(pady=8)
        
        lbl_status = ttk.Label(pop, text=f"Eligibility Status: {status}", font=("Arial", 10))
        lbl_status.pack(pady=5)
        
        lbl_loan = ttk.Label(pop, text=f"Maximum Qualified Loan Amount: ₹{max_loan:,}", font=("Arial", 11, "bold"), foreground="navy")
        lbl_loan.pack(pady=10)
        
        btn_close = ttk.Button(pop, text="Close", command=pop.destroy)
        btn_close.pack(pady=15)
