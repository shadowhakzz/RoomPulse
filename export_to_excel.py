"""
This file is responsible for exporting database tables to Excel files.
"""

# 📂 File name: export_to_excel.py
# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
from datetime import datetime
from database_setup import DATABASE_NAME
import os


def export_to_excel():
    """
    Export each database table to a separate Excel file.

    This function:
    1. Connects to the database
    2. Retrieves the list of tables
    3. Creates an Excel file for each table
    4. Uses English names for worksheets and files
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Retrieve list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        # Create export folder in the project directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_folder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"iot_database_export_{timestamp}")
        os.makedirs(export_folder, exist_ok=True)

        # English names for tables
        table_names = {
            'sensors': 'Sensors',
            'measurements': 'Measurements',
            'alerts': 'Alerts'
        }

        print("📊 Exporting database tables to Excel files...\n")

        # Save each table to a separate Excel file
        for table in tables:
            table_name = table[0]
            if table_name not in table_names:
                continue

            # Read table data into DataFrame
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

            # Prepare Excel file name
            english_name = table_names[table_name]
            excel_filename = os.path.join(
                export_folder, f"{english_name}.xlsx")

            # Save DataFrame to Excel
            df.to_excel(excel_filename, index=False)

            # Display export details
            print(f"✓ Table: {english_name}")
            print(f"  - Record count: {len(df)}")
            print(f"  - File path: {excel_filename}")
            print(f"  - Columns: {', '.join(df.columns)}")
            print()

        print(f"✅ All Excel files successfully created in folder '{export_folder}'.")

    except Exception as e:
        print(f"❌ Error during Excel export: {e}")

    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    export_to_excel()
