"""
This file is responsible for setting up and initializing the database.
"""

# 📂 File name: database_setup.py
# -*- coding: utf-8 -*-
import sqlite3
import os
import random
from datetime import datetime, timedelta

# Default database settings
DATABASE_NAME = "server_room.db"

# Sampling configuration for each sensor type:
# Includes: sampling interval, unit, normal range, warning range, and critical range
SAMPLING_CONFIG = {
    "temperature": {
        "interval": 1,  # 1 Hz
        "unit": "°C",
        "normal_range": (18, 25),
        "warning_range": (15, 35),
        "critical_range": (None, 58)
    },
    "humidity": {
        "interval": 1,  # 1 Hz
        "unit": "%",
        "normal_range": (30, 50),
        "warning_range": (None, 60),
        "critical_range": (None, None)
    },
    "air_quality": {
        "interval": 1,  # 1 Hz
        "unit": "ppm",
        "normal_range": (400, 1000),
        "warning_range": (None, 1000),
        "critical_range": (None, None)
    },
    "smoke": {
        "interval": 1,  # 1 Hz
        "unit": "ppm",
        "normal_range": (0, 300),
        "warning_range": (300, None),
        "critical_range": (None, None)
    },
    "gas": {
        "interval": 1,  # 1 Hz
        "unit": "ppm",
        "normal_range": (0, 1000),
        "warning_range": (1000, None),
        "critical_range": (None, None)
    },
    "motion": {
        "interval": 0.1,  # 10 Hz
        "unit": "binary",
        "normal_range": (0, 1),
        "warning_range": (None, None),
        "critical_range": (None, None)
    },
    "sound": {
        "interval": 0.05,  # 20 Hz
        "unit": "dB",
        "normal_range": (0, 70),
        "warning_range": (80, None),
        "critical_range": (None, None)
    },
    "tampering": {
        "interval": 0.01,  # 100 Hz
        "unit": "g/deg/s",
        "normal_range": (0, 0.5),
        "warning_range": (0.5, None),
        "critical_range": (None, None)
    },
    "water_leak": {
        "interval": 1,  # 1 Hz
        "unit": "binary",
        "normal_range": (0, 1),
        "warning_range": (None, None),
        "critical_range": (None, None)
    },
    "light": {
        "interval": 1,  # 1 Hz
        "unit": "lux",
        "normal_range": (300, 500),
        "warning_range": (100, 1000),
        "critical_range": (None, None)
    }
}


class DatabaseSetup:
    """Class for database setup and initialization"""

    def __init__(self, db_path=DATABASE_NAME):
        """Initialize setup with the given database path"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def create_database(self):
        """Create database file and required tables"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            # Create sensors table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY,
                type TEXT NOT NULL,
                last_reading REAL,
                status INTEGER DEFAULT 0,
                last_reading_time TIMESTAMP,
                min_warning REAL,
                max_warning REAL,
                min_critical REAL,
                max_critical REAL
            )
            ''')

            # Create measurements table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER,
                value REAL,
                status INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (sensor_id) REFERENCES sensors (id)
            )
            ''')

            # Create alerts table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id INTEGER,
                value REAL,
                severity TEXT,
                description TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (sensor_id) REFERENCES sensors (id)
            )
            ''')

            self.conn.commit()
            print("Database created successfully!")

        except sqlite3.Error as e:
            print(f"Error creating database: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def initialize_sensors(self):
        """Insert default sensor records with initial thresholds"""
        try:
            sensor_types = {
                'temperature': {'min_warning': 20, 'max_warning': 30, 'min_critical': 15, 'max_critical': 35},
                'humidity': {'min_warning': 30, 'max_warning': 70, 'min_critical': 20, 'max_critical': 80},
                'air_quality': {'min_warning': 500, 'max_warning': 1000, 'min_critical': 400, 'max_critical': 1500},
                'smoke': {'min_warning': 20, 'max_warning': 50, 'min_critical': 0, 'max_critical': 100},
                'gas': {'min_warning': 20, 'max_warning': 50, 'min_critical': 0, 'max_critical': 100},
                'motion': {'min_warning': 0, 'max_warning': 1, 'min_critical': 0, 'max_critical': 1},
                'sound': {'min_warning': 50, 'max_warning': 70, 'min_critical': 0, 'max_critical': 100},
                'tampering': {'min_warning': 0, 'max_warning': 1, 'min_critical': 0, 'max_critical': 1},
                'water_leak': {'min_warning': 0, 'max_warning': 1, 'min_critical': 0, 'max_critical': 1},
                'light': {'min_warning': 200, 'max_warning': 800, 'min_critical': 0, 'max_critical': 1000}
            }

            for sensor_type, thresholds in sensor_types.items():
                self.cursor.execute('''
                INSERT OR IGNORE INTO sensors 
                (type, last_reading, status, last_reading_time, 
                 min_warning, max_warning, min_critical, max_critical)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sensor_type,
                    random.uniform(thresholds['min_warning'], thresholds['max_warning']),
                    0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    thresholds['min_warning'],
                    thresholds['max_warning'],
                    thresholds['min_critical'],
                    thresholds['max_critical']
                ))

            self.conn.commit()
            print("Sensors initialized successfully!")

        except sqlite3.Error as e:
            print(f"Error initializing sensors: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def generate_historical_data(self, days=7):
        """Generate and insert synthetic historical data for the past given days"""
        try:
            self.cursor.execute('SELECT id, type FROM sensors')
            sensors = self.cursor.fetchall()

            for sensor_id, sensor_type in sensors:
                self.cursor.execute('''
                SELECT min_warning, max_warning, min_critical, max_critical
                FROM sensors WHERE id = ?
                ''', (sensor_id,))
                thresholds = self.cursor.fetchone()

                if not thresholds:
                    continue

                min_warning, max_warning, min_critical, max_critical = thresholds
                start_time = datetime.now() - timedelta(days=days)
                current_time = start_time

                while current_time <= datetime.now():
                    if sensor_type in ['motion', 'tampering', 'water_leak']:
                        value = random.choice([0, 1])
                    else:
                        value = random.uniform(min_critical or min_warning, max_critical or max_warning)

                    if value <= (min_critical or -float('inf')) or value >= (max_critical or float('inf')):
                        status = 2
                    elif value <= (min_warning or -float('inf')) or value >= (max_warning or float('inf')):
                        status = 1
                    else:
                        status = 0

                    self.cursor.execute('''
                    INSERT INTO measurements (sensor_id, value, status, timestamp)
                    VALUES (?, ?, ?, ?)
                    ''', (sensor_id, value, status, current_time.strftime("%Y-%m-%d %H:%M:%S")))

                    if status > 0:
                        severity = "critical" if status == 2 else "warning"
                        description = f"{severity.title()} {sensor_type}: {value:.2f}"
                        self.cursor.execute('''
                        INSERT INTO alerts (sensor_id, value, severity, description, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (sensor_id, value, severity, description, current_time.strftime("%Y-%m-%d %H:%M:%S")))

                    current_time += timedelta(minutes=5)

            self.conn.commit()
            print(f"Historical data generated for the past {days} days!")

        except sqlite3.Error as e:
            print(f"Error generating historical data: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None


if __name__ == "__main__":
    # Display a banner
    print(r"""
  _____                           _____                     
 / ____|                         |  __ \                    
| (___   ___ _ ____   _____ _ __| |__) |___ _ __ ___   ___ 
 \___ \ / _ \ '__\ \ / / _ \ '__|  _  // _ \\ '_ ` _ \ / _ \
 ____) |  __/ |   \ V /  __/ |  | | \ \  __/ | | | | |  __/
|_____/ \___|_|    \_/ \___|_|  |_|  \_\___|_| |_| |_|\___|
""")

    db = DatabaseSetup()
    db.create_database()
    db.initialize_sensors()
    db.generate_historical_data()
    print("✅ Database setup and initialization complete!")
    print("🔍 Created tables:")
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in cursor.fetchall():
        print(f"- {table[0]}")
