"""
This is the main file that coordinates all modules.
"""

import sys
import threading
from database_setup import DatabaseSetup
from data_logger import DataLogger
from error_manager import ErrorManager
from export_to_excel import export_to_excel
from gui import MainWindow
from PyQt5.QtWidgets import QApplication
import time
import os

# Initialize error manager
error_manager = ErrorManager()

def ask_data_mode():
    """Ask user for data mode selection"""
    try:
        print("Do you want to use a real database? (y/n)")
        answer = input("Your choice: ").strip().lower()
        if answer == 'y':
            # Suggest default path
            default_db = os.path.join(os.getcwd(), "server_room.db")
            print(f"\nSuggested database path: {default_db}")
            print("You can copy this path or enter your desired path.")
            
            while True:
                db_path = input("\nPlease enter the database path: ").strip()
                
                # If user leaves path empty, use default path
                if not db_path:
                    db_path = default_db
                    print(f"Using default path: {db_path}")
                
                # Check if path is a file not a directory
                if os.path.isdir(db_path):
                    print("⚠️ The entered path is a directory.")
                    print("Do you want to create the database file in this directory? (y/n)")
                    create_choice = input("Your choice: ").strip().lower()
                    if create_choice == 'y':
                        db_path = os.path.join(db_path, "server_room.db")
                        print(f"Database file will be created at: {db_path}")
                    else:
                        print("Please enter the complete database file path (e.g., server_room.db)")
                        continue
                    
                # If file doesn't exist, warn but allow continuation
                if not os.path.isfile(db_path):
                    print("⚠️ Database file does not exist.")
                    print("If you continue, a new database will be created at this path.")
                    
                return db_path
        return None
    except Exception as e:
        error_manager.handle_error("Error in data mode selection", str(e))
        return None

def setup_database():
    """Initial database setup"""
    try:
        # Server Room banner (exact, bold & block)
        print(r"""
  _____                           _____                     
 / ____|                         |  __ \                    
| (___   ___ _ ____   _____ _ __| |__) |___ _ __ ___   ___ 
 \___ \ / _ \ '__\ \ / / _ \ '__|  _  // _ \ '_ ` _ \ / _ \
 ____) |  __/ |   \ V /  __/ |  | | \ \  __/ | | | | |  __/
|_____/ \___|_|    \_/ \___|_|  |_|  \_\___|_| |_| |_|\___|
                                                               
""")

        # Create database
        print("🔨 Creating database...")
        db = DatabaseSetup()
        db.create_database()
        
        # Initialize sensors
        print("📡 Initializing sensors...")
        db.initialize_sensors()
        
        # Generate historical data
        print("📊 Generating historical data...")
        db.generate_historical_data(days=1)  # Generate 1 day of historical data

        print("\n✅ Initial setup completed successfully!")
    except Exception as e:
        error_manager.handle_error("Error in database setup", str(e))
        raise

def main():
    """Main function"""
    try:
        # Setup database
        setup_database()
        
        # Create application
        app = QApplication(sys.argv)
        
        # Create main window
        window = MainWindow()
        window.show()
        
        # Start data generation
        logger = DataLogger()
        logger.start_logging()
        
        # Run application
        sys.exit(app.exec_())
    except Exception as e:
        error_manager.handle_error("Critical error in main function", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
