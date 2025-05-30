"""
This file is responsible for generating and logging sensor data.
"""

# 📂 File name: data_logger.py
# -*- coding: utf-8 -*-
import sqlite3
import random
import time
import datetime
import threading
import queue
from database_setup import DATABASE_NAME, SAMPLING_CONFIG


class DataLogger:
    """Class for generating and logging sensor data"""

    def __init__(self):
        """Initialize the data logger"""
        self.is_running = False
        self.threads = {}  # Dictionary to store threads for each sensor
        self.data_queue = queue.Queue()
        self.last_values = {}  # Store the last value for each sensor
        self.value_lock = threading.Lock()  # Lock for accessing last_values
        self.db_lock = threading.Lock()  # Separate lock for database operations

        # Sampling intervals (50% slower than configured)
        self.sampling_intervals = {
            sensor: config["interval"] * 2
            for sensor, config in SAMPLING_CONFIG.items()
        }

    def start_logging(self):
        """Start the data logging process"""
        if not self.is_running:
            self.is_running = True

            # Start database writer thread
            self.db_thread = threading.Thread(target=self._database_writer_loop)
            self.db_thread.daemon = True
            self.db_thread.start()

            # Start sensor data generation threads
            self._start_sensor_threads()

            print("Data logging started successfully!")

    def _start_sensor_threads(self):
        """Start data generation threads for each sensor"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(DATABASE_NAME, timeout=20)
                cursor = conn.cursor()

                # Retrieve sensor configurations
                cursor.execute(
                    '''
                    SELECT id, type, min_warning, max_warning, min_critical, max_critical
                    FROM sensors
                    '''
                )
                sensors = cursor.fetchall()
                conn.close()

            # Create a thread for each sensor
            for sensor_id, sensor_type, min_w, max_w, min_c, max_c in sensors:
                thread = threading.Thread(
                    target=self._sensor_data_loop,
                    args=(sensor_id, sensor_type, min_w, max_w, min_c, max_c)
                )
                thread.daemon = True
                thread.start()
                self.threads[sensor_id] = thread

        except sqlite3.Error as e:
            print(f"❌ Error starting sensor threads: {e}")
            self.stop_logging()

    def _sensor_data_loop(self, sensor_id, sensor_type, min_warning, max_warning, min_critical, max_critical):
        """Data generation loop for a single sensor"""
        while self.is_running:
            try:
                # Generate a new value
                value = self._generate_value(
                    sensor_id, sensor_type, min_warning, max_warning, min_critical, max_critical
                )

                # Determine status
                status = self._determine_status(value, min_warning, max_warning, min_critical, max_critical)

                # Put data into queue
                self.data_queue.put({
                    'sensor_id': sensor_id,
                    'value': value,
                    'status': status,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                # Wait for next sample
                interval = self.sampling_intervals.get(sensor_type, 1)
                time.sleep(interval)

            except Exception as e:
                print(f"❌ Error generating data for sensor {sensor_id}: {e}")
                time.sleep(1)

    def _database_writer_loop(self):
        """Loop for writing data to the database"""
        while self.is_running:
            try:
                data = self.data_queue.get(timeout=1)

                with self.db_lock:
                    conn = sqlite3.connect(DATABASE_NAME, timeout=20)
                    cursor = conn.cursor()

                    # Update last sensor reading
                    cursor.execute(
                        '''
                        UPDATE sensors
                        SET last_reading = ?, status = ?, last_reading_time = ?
                        WHERE id = ?
                        ''',
                        (data['value'], data['status'], data['timestamp'], data['sensor_id'])
                    )

                    # Insert measurement record
                    cursor.execute(
                        '''
                        INSERT INTO measurements (sensor_id, timestamp, value, status)
                        VALUES (?, ?, ?, ?)
                        ''',
                        (data['sensor_id'], data['timestamp'], data['value'], data['status'])
                    )

                    # Insert an alert if necessary
                    if data['status'] != 0:
                        severity = "critical" if data['status'] == 2 else "warning"
                        cursor.execute(
                            'SELECT type FROM sensors WHERE id = ?',
                            (data['sensor_id'],)
                        )
                        sensor_type = cursor.fetchone()[0]
                        description = self._generate_alert_description(sensor_type, data['value'], severity)

                        cursor.execute(
                            '''
                            INSERT INTO alerts (sensor_id, timestamp, value, severity, description)
                            VALUES (?, ?, ?, ?, ?)
                            ''',
                            (data['sensor_id'], data['timestamp'], data['value'], severity, description)
                        )

                    conn.commit()
                    conn.close()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error writing to database: {e}")
                time.sleep(1)

    def _generate_value(self, sensor_id, sensor_type, min_warning, max_warning, min_critical, max_critical):
        """Generate a new sensor value with gradual change"""
        with self.value_lock:
            # Initialize last value if not present
            if sensor_id not in self.last_values:
                self.last_values[sensor_id] = self._get_initial_value(sensor_type)

            last = self.last_values[sensor_id]
            change_range, min_val, max_val = self._get_value_ranges(
                sensor_type, min_warning, max_warning, min_critical, max_critical
            )
            change = random.uniform(-change_range, change_range)
            new_value = max(min_val, min(max_val, last + change))
            new_value = self._round_value(new_value, sensor_type)

            self.last_values[sensor_id] = new_value
            return new_value

    def _get_initial_value(self, sensor_type):
        """Get initial value for a sensor type"""
        defaults = {
            'temperature': random.uniform(20, 25),
            'humidity': random.uniform(40, 60),
            'air_quality': random.uniform(400, 800),
            'smoke': random.uniform(0, 10),
            'gas': random.uniform(0, 20),
            'motion': 0,
            'sound': random.uniform(30, 50),
            'tampering': random.uniform(0.1, 0.2),
            'water_leak': 0,
            'light': random.uniform(300, 400)
        }
        return defaults.get(sensor_type, random.uniform(0, 50))

    def _get_value_ranges(self, sensor_type, min_warning, max_warning, min_critical, max_critical):
        """Get change range and allowed value bounds for sensor type"""
        ranges = {
            'temperature': (0.5, min_warning or 15, max_warning or 35),
            'humidity': (2, min_warning or 20, max_warning or 80),
            'air_quality': (50, min_warning or 400, max_warning or 1500),
            'smoke': (5, 0, max_warning or 100),
            'gas': (10, 0, max_warning or 200),
            'sound': (5, min_warning or 20, max_warning or 80),
            'tampering': (0.05, min_warning or 0.1, max_warning or 0.4),
            'water_leak': (1, 0, 1),
            'light': (20, min_warning or 300, max_warning or 600)
        }
        return ranges.get(sensor_type, (5, min_warning or 0, max_warning or 100))

    def _round_value(self, value, sensor_type):
        """Round the value based on sensor type"""
        if sensor_type in ['temperature', 'humidity', 'sound']:
            return round(value, 1)
        elif sensor_type == 'tampering':
            return round(value, 4)
        else:
            return round(value, 2)

    def _determine_status(self, value, min_warning, max_warning, min_critical, max_critical):
        """Determine status based on value and thresholds"""
        if min_critical is not None and value <= min_critical:
            return 2  # Critical
        if max_critical is not None and value >= max_critical:
            return 2  # Critical
        if min_warning is not None and value <= min_warning:
            return 1  # Warning
        if max_warning is not None and value >= max_warning:
            return 1  # Warning
        return 0  # Normal

    def _generate_alert_description(self, sensor_type, value, severity):
        """Generate alert description based on sensor type and severity"""
        descriptions = {
            'temperature': (
                lambda v: f"High temperature: {v}°C" if v > SAMPLING_CONFIG['temperature']['normal_range'][1]
                else f"Low temperature: {v}°C"
            ),
            'humidity': (
                lambda v: f"High humidity: {v}%" if v > SAMPLING_CONFIG['humidity']['normal_range'][1]
                else f"Low humidity: {v}%"
            ),
            'air_quality': lambda v: f"High CO2 level: {v} ppm",
            'smoke': lambda v: f"High smoke level: {v} ppm",
            'gas': lambda v: f"High gas level: {v} ppm",
            'motion': lambda v: "Unauthorized motion detected",
            'sound': lambda v: f"High sound level: {v} dB",
            'tampering': lambda v: f"Abnormal vibration: {v} g/deg/s",
            'water_leak': lambda v: "Water leak detected",
            'light': (
                lambda v: f"High light level: {v} lux" if v > SAMPLING_CONFIG['light']['normal_range'][1]
                else f"Low light level: {v} lux"
            )
        }
        return descriptions.get(sensor_type, lambda v: f"Abnormal reading: {v}")(value)

    def stop_logging(self):
        """Stop the data logging process"""
        self.is_running = False

        # Wait for database thread to finish
        if hasattr(self, 'db_thread'):
            self.db_thread.join()

        # Wait for sensor threads to finish
        for thread in self.threads.values():
            thread.join()

        print("Data logging stopped.")


if __name__ == "__main__":
    print(r"""
  _____                           _____                     
 / ____|                         |  __ \                    
| (___   ___ _ ____   _____ _ __| |__) |___ _ __ ___   ___ 
 \___ \ / _ \ '__\ \ / / _ \ '__|  _  // _ \\ '_ ` _ \ / _ \
 ____) |  __/ |   \ V /  __/ |  | | \ \  __/ | | | | |  __/
|_____/ \___|_|    \_/ \___|_|  |_|  \_\___|_| |_| |_|\___|
""")

    logger = DataLogger()
    logger.start_logging()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.stop_logging()