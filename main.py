import tkinter as tk
import os
from src.database import init_db
from src.gui import CreditSystemApp
from utils.mock_generator import generate_mock_data

def main():
    print("Setting up local SQLite instance and compiling schemas...")
    init_db()
    
    # Seed sample parameters & export a mock update document path
    status_msg = generate_mock_data()
    print(status_msg)
    
    print("Booting Tkinter Engine Dashboard UI...")
    root = tk.Tk()
    app = CreditSystemApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
