import tkinter as tk
from src.database import init_db
from src.gui import create_dashboard, create_login_window
from utils.mock_generator import generate_mock_data

# Starts the application and shows the login screen before exposing the database-backed dashboard.
def main():
    root = tk.Tk()

    # Replaces the login controls with the dashboard after authentication succeeds.
    def open_dashboard():
        for widget in root.winfo_children():
            widget.destroy()

        print("Setting up local SQLite instance and compiling schemas...")
        init_db()
        status_msg = generate_mock_data()
        print(status_msg)
        print("Booting Tkinter Engine Dashboard UI...")
        create_dashboard(root)

    create_login_window(root, open_dashboard)
    root.mainloop()

if __name__ == '__main__':
    main()
