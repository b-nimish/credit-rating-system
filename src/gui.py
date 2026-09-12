import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from src.database import get_connection
from src.credit_engine import calculate_credit_score
from src.csv_parser import import_csv_update

class CreditSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Rating & Loan Eligibility System")
        self.root.geometry("850x550")
        
        # Configure Grid Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        self.create_top_panel()
        self.create_main_table()
        self.refresh_table()

    def create_top_panel(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.grid(row=0, column=0, sticky="ew")
        
        # Actions
        btn_import = ttk.Button(top_frame, text="📥 Import Update CSV", command=self.upload_csv)
        btn_import.pack(side="left", padx=5)
        
        btn_refresh = ttk.Button(top_frame, text="🔄 Refresh List", command=self.refresh_table)
        btn_refresh.pack(side="left", padx=5)
        
        lbl_hint = ttk.Label(top_frame, text="Double-click any applicant row to compute Credit Rating & Loan Limits", font=("Arial", 9, "italic"))
        lbl_hint.pack(side="right", padx=10)

    def create_main_table(self):
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.grid(row=1, column=0, sticky="nsew")
        
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        columns = ("id", "first_name", "last_name", "email", "employment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("email", text="Email ID")
        self.tree.heading("employment", text="Employment Status")
        
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
        # Clear entries
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, first_name, last_name, email, employment_status FROM users")
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load users: {str(e)}")

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
