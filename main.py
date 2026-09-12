import tkinter as tk
import os
from src.database import init_db
from src.gui import CreditSystemApp
from utils.mock_generator import generate_mock_data

def main():
    root = tk.Tk()

    def open_dashboard():
        for widget in root.winfo_children():
            widget.destroy()

        print("Setting up local SQLite instance and compiling schemas...")
        init_db()
        status_msg = generate_mock_data()
        print(status_msg)
        print("Booting Tkinter Engine Dashboard UI...")
        CreditSystemApp(root)

    from src.gui import LoginWindow
    LoginWindow(root, open_dashboard)
    root.mainloop()

if __name__ == '__main__':
    main()
