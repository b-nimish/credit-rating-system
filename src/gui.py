import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.auth import (
    DEFAULT_USERNAME,
    authenticate_admin,
    authenticate_user,
    generate_user_password,
    hash_user_password,
)
from src.credit_engine import calculate_credit_score
from src.csv_parser import import_csv_update
from src.database import get_connection


# Creates the login form and connects it to the dashboard callback.
def create_login_window(root, on_admin_success, on_user_success):
    root.title("Credit Rating System - Login")
    root.geometry("420x300")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=30)
    frame.pack(expand=True, fill="both")

    ttk.Label(frame, text="Choose login type", font=("Arial", 16, "bold")).pack(pady=(0, 22))
    ttk.Button(frame, text="Admin Login", command=lambda: show_login_form(
        root, "Admin Login", "Username", DEFAULT_USERNAME, on_admin_success, False
    )).pack(fill="x", pady=6)
    ttk.Button(frame, text="User Login", command=lambda: show_login_form(
        root, "User Login", "Email", "", on_user_success, True
    )).pack(fill="x", pady=6)


def show_login_form(root, title, identity_label, default_identity, on_success, is_user):
    for widget in root.winfo_children():
        widget.destroy()
    root.title(f"Credit Rating System - {title}")
    frame = ttk.Frame(root, padding=30)
    frame.pack(expand=True, fill="both")
    ttk.Label(frame, text=title, font=("Arial", 16, "bold")).pack(pady=(0, 18))
    ttk.Label(frame, text=identity_label).pack(anchor="w")
    identity_entry = ttk.Entry(frame)
    identity_entry.pack(fill="x", pady=(2, 10))
    identity_entry.insert(0, default_identity)
    ttk.Label(frame, text="Password").pack(anchor="w")
    password_entry = ttk.Entry(frame, show="*")
    password_entry.pack(fill="x", pady=(2, 12))
    status_label = ttk.Label(frame, text="")
    status_label.pack()
    ttk.Button(
        frame,
        text="Log in",
        command=lambda: login(
            root, identity_entry, password_entry, status_label, on_success, is_user
        ),
    ).pack(pady=6)
    ttk.Button(frame, text="Back", command=lambda: create_login_window(
        root, on_success if not is_user else lambda: None, on_success if is_user else lambda _: None
    )).pack()
    password_entry.bind(
        "<Return>",
        lambda event: login(root, identity_entry, password_entry, status_label, on_success, is_user),
    )
    identity_entry.focus_set()


# Validates login fields and opens the protected dashboard after successful authentication.
def login(root, identity_entry, password_entry, status_label, on_success, is_user):
    identity = identity_entry.get().strip()
    password = password_entry.get()
    result = authenticate_user(identity, password) if is_user else authenticate_admin(identity, password)
    if result:
        on_success(result) if is_user else on_success()
        return

    status_label.configure(text="Invalid username or password")
    password_entry.delete(0, tk.END)
    password_entry.focus_set()


def create_user_view(root, user):
    root.title("My Loan Eligibility")
    root.geometry("480x360")
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=30)
    frame.pack(expand=True, fill="both")

    score, status, max_loan = calculate_credit_score(user["user_id"])
    full_name = f"{user['first_name']} {user['last_name']}"
    ttk.Label(frame, text="Loan Eligibility", font=("Arial", 18, "bold")).pack(pady=(0, 18))
    ttk.Label(frame, text=f"Applicant: {full_name}", font=("Arial", 11)).pack(pady=5)
    ttk.Label(frame, text=f"Email: {user['email']}").pack(pady=5)
    ttk.Label(
        frame,
        text=f"Credit Score: {score} / 850",
        font=("Arial", 14, "bold"),
        foreground="green" if score >= 650 else "red",
    ).pack(pady=10)
    ttk.Label(frame, text=f"Eligibility Status: {status}", font=("Arial", 11)).pack(pady=5)
    ttk.Label(
        frame,
        text=f"Maximum Qualified Loan Amount: Rs.{max_loan:,}",
        font=("Arial", 12, "bold"),
        foreground="navy",
    ).pack(pady=10)
    ttk.Button(frame, text="Close", command=root.quit).pack(pady=15)


# Builds the dashboard controls and table, then loads the initial user list.
def create_dashboard(root):
    state = {
        "root": root,
        "all_rows": [],
        "sort_column": None,
        "sort_reverse": False,
    }
    root.title("Credit Rating & Loan Eligibility System")
    root.geometry("850x550")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    create_top_panel(state)
    create_main_table(state)
    refresh_table(state)
    return state


# Creates controls for importing, refreshing, adding, deleting, and searching users.
def create_top_panel(state):
    root = state["root"]
    top_frame = ttk.Frame(root, padding=10)
    top_frame.grid(row=0, column=0, sticky="ew")
    top_frame.columnconfigure(2, weight=1)

    ttk.Button(
        top_frame,
        text="Import Update CSV",
        command=lambda: upload_csv(state),
    ).pack(side="left", padx=5)
    ttk.Button(
        top_frame,
        text="Refresh List",
        command=lambda: refresh_table(state),
    ).pack(side="left", padx=5)
    ttk.Button(
        top_frame,
        text="Delete Selected",
        command=lambda: delete_selected(state),
    ).pack(side="left", padx=5)
    ttk.Button(
        top_frame,
        text="Add User",
        command=lambda: add_user(state),
    ).pack(side="left", padx=5)

    ttk.Label(top_frame, text="Search:").pack(side="left", padx=(18, 4))
    state["search_var"] = tk.StringVar()
    state["search_entry"] = ttk.Entry(top_frame, textvariable=state["search_var"], width=28)
    state["search_entry"].pack(side="left", padx=4)
    state["search_var"].trace_add("write", lambda *_: display_rows(state))
    ttk.Button(
        top_frame,
        text="Clear",
        command=lambda: clear_search(state),
    ).pack(side="left", padx=4)
    ttk.Label(
        top_frame,
        text="Double-click any applicant row to compute Credit Rating & Loan Limits",
        font=("Arial", 9, "italic"),
    ).pack(side="right", padx=10)


# Creates the sortable applicant table and binds double-click assessment behavior.
def create_main_table(state):
    root = state["root"]
    table_frame = ttk.Frame(root, padding=10)
    table_frame.grid(row=1, column=0, sticky="nsew")
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)

    columns = ("id", "first_name", "last_name", "email", "employment")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    state["tree"] = tree
    headings = {
        "id": "ID",
        "first_name": "First Name",
        "last_name": "Last Name",
        "email": "Email ID",
        "employment": "Employment Status",
    }
    for column, heading in headings.items():
        tree.heading(
            column,
            text=heading,
            command=lambda selected_column=column: sort_rows(state, selected_column),
        )

    tree.column("id", width=50, anchor="center")
    tree.column("first_name", width=120)
    tree.column("last_name", width=120)
    tree.column("email", width=250)
    tree.column("employment", width=150)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.bind("<Double-1>", lambda event: on_row_double_click(event, state))


# Loads users from SQLite into memory and redraws the visible table.
def refresh_table(state):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name, email, employment_status FROM users")
        state["all_rows"] = cursor.fetchall()
        display_rows(state)
    except Exception as error:
        messagebox.showerror("Error", f"Could not load users: {error}")
    finally:
        if conn is not None:
            conn.close()


# Applies the current search and sort settings, then redraws the table rows.
def display_rows(state):
    search_text = state["search_var"].get().strip().casefold()
    rows = state["all_rows"]
    tree = state["tree"]
    if search_text:
        rows = [
            row for row in rows
            if search_text in " ".join(str(value) for value in row).casefold()
        ]

    sort_column = state["sort_column"]
    if sort_column is not None:
        column_index = tree["columns"].index(sort_column)
        if sort_column == "id":
            sort_key = lambda row: int(row[column_index])
        else:
            sort_key = lambda row: str(row[column_index]).casefold()
        rows = sorted(rows, key=sort_key, reverse=state["sort_reverse"])

    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)


# Sorts by a selected column and toggles direction on repeated header clicks.
def sort_rows(state, column):
    if state["sort_column"] == column:
        state["sort_reverse"] = not state["sort_reverse"]
    else:
        state["sort_column"] = column
        state["sort_reverse"] = False
    display_rows(state)


# Clears the search field and returns focus to it.
def clear_search(state):
    state["search_var"].set("")
    state["search_entry"].focus_set()


# Confirms deletion, removes a selected profile and its financial history, then reloads the table.
def delete_selected(state):
    tree = state["tree"]
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Select an applicant before deleting.")
        return

    user_values = tree.item(selected_items[0], "values")
    user_id = user_values[0]
    full_name = f"{user_values[1]} {user_values[2]}"
    confirmed = messagebox.askyesno(
        "Confirm Deletion",
        f"Delete {full_name} and all of their financial records?\n\nThis action cannot be undone.",
    )
    if not confirmed:
        return

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM financial_records WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"{full_name} was deleted.")
        refresh_table(state)
    except Exception as error:
        if conn is not None:
            conn.rollback()
        messagebox.showerror("Delete Failed", f"Could not delete {full_name}: {error}")
    finally:
        if conn is not None:
            conn.close()


# Opens a form for entering and saving a new user profile.
def add_user(state):
    dialog = tk.Toplevel(state["root"])
    dialog.title("Add New User")
    dialog.geometry("380x300")
    dialog.resizable(False, False)
    dialog.transient(state["root"])
    dialog.grab_set()

    fields = (
        ("First Name", "first_name"),
        ("Last Name", "last_name"),
        ("Email", "email"),
        ("Date of Birth", "date_of_birth"),
        ("Employment Status", "employment_status"),
    )
    entries = {}
    form = ttk.Frame(dialog, padding=20)
    form.pack(fill="both", expand=True)
    for row_index, (label, field_name) in enumerate(fields):
        ttk.Label(form, text=label).grid(row=row_index, column=0, sticky="w", padx=(0, 10), pady=5)
        entry = ttk.Entry(form, width=30)
        entry.grid(row=row_index, column=1, sticky="ew", pady=5)
        entries[field_name] = entry
    form.columnconfigure(1, weight=1)
    ttk.Button(
        form,
        text="Save User",
        command=lambda: save_user(dialog, entries, state),
    ).grid(row=len(fields), column=1, sticky="e", pady=(15, 0))
    entries["first_name"].focus_set()


# Validates and inserts a new profile, handling duplicate emails and database errors.
def save_user(dialog, entries, state):
    values = {field_name: entry.get().strip() for field_name, entry in entries.items()}
    if any(not value for value in values.values()):
        messagebox.showwarning("Incomplete Details", "Please complete every field.", parent=dialog)
        return

    generated_password = generate_user_password(values["first_name"], values["last_name"])
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, email, date_of_birth, employment_status, password_hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                values["first_name"],
                values["last_name"],
                values["email"].lower(),
                values["date_of_birth"],
                values["employment_status"],
                hash_user_password(generated_password),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        if conn is not None:
            conn.rollback()
        messagebox.showerror("Could Not Add User", "That email address already exists.", parent=dialog)
        return
    except Exception as error:
        if conn is not None:
            conn.rollback()
        messagebox.showerror("Could Not Add User", str(error), parent=dialog)
        return
    finally:
        if conn is not None:
            conn.close()

    dialog.destroy()
    refresh_table(state)
    messagebox.showinfo(
        "User Added",
        f"The new user was added successfully.\n\nUser email: {values['email'].lower()}\nInitial password: {generated_password}",
        parent=state["root"],
    )


# Opens a CSV picker, imports the selected update file, and refreshes the table on success.
def upload_csv(state):
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    success, message = import_csv_update(file_path)
    if success:
        messagebox.showinfo("Success", message)
        refresh_table(state)
    else:
        messagebox.showerror("Import Failed", message)


# Calculates and displays the selected applicant's credit score and loan eligibility report.
def on_row_double_click(event, state):
    selected_item = state["tree"].selection()
    if not selected_item:
        return

    user_values = state["tree"].item(selected_item[0], "values")
    user_id = user_values[0]
    full_name = f"{user_values[1]} {user_values[2]}"
    score, status, max_loan = calculate_credit_score(user_id)

    pop = tk.Toplevel(state["root"])
    pop.title(f"Credit Score Assessment: {full_name}")
    pop.geometry("450x300")
    pop.resizable(False, False)
    ttk.Label(pop, text="Assessment Report", font=("Arial", 14, "bold")).pack(pady=15)
    ttk.Label(pop, text=f"Applicant: {full_name}", font=("Arial", 11)).pack(pady=5)
    ttk.Label(
        pop,
        text=f"Credit Score: {score} / 850",
        font=("Arial", 12, "bold"),
        foreground="green" if score >= 650 else "red",
    ).pack(pady=8)
    ttk.Label(pop, text=f"Eligibility Status: {status}", font=("Arial", 10)).pack(pady=5)
    ttk.Label(
        pop,
        text=f"Maximum Qualified Loan Amount: Rs.{max_loan:,}",
        font=("Arial", 11, "bold"),
        foreground="navy",
    ).pack(pady=10)
    ttk.Button(pop, text="Close", command=pop.destroy).pack(pady=15)
