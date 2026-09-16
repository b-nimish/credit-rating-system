import tkinter as tk
from src.database import init_db
from src.gui import create_dashboard, create_login_window
from src.auth import ensure_user_passwords
from utils.mock_generator import generate_mock_data

# Starts the application and shows the login screen before exposing the database-backed dashboard.
def main():
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    init_db()
    generate_mock_data()
    credentials = ensure_user_passwords()
    if credentials:
        print("Generated initial user passwords in data/user_credentials.csv")

    def open_admin_dashboard():
        for widget in root.winfo_children():
            widget.destroy()

        print("Booting Tkinter Engine Dashboard UI...")
        create_dashboard(root)

    def open_user_report(user):
        for widget in root.winfo_children():
            widget.destroy()
        from src.gui import create_user_view
        create_user_view(root, user)

    create_login_window(root, open_admin_dashboard, open_user_report)
    root.mainloop()
    root.destroy()

if __name__ == '__main__':
    main()
