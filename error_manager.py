"""
This file is responsible for managing error detection and alerts.
"""

# 📂 File name: error_manager.py
# -*- coding: utf-8 -*-
import sqlite3
from datetime import datetime
from database_setup import DATABASE_NAME


class ErrorManager:
    """Class for managing error detection and alerts"""

    def __init__(self, conn=None):
        """Initialize error manager"""
        self.conn = conn or sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()

    def check_value(self, sensor_id, value, timestamp):
        """
        Check sensor reading and create alerts if thresholds are exceeded.

        Args:
            sensor_id (int): Sensor ID
            value (float): Sensor reading value
            timestamp (str): Timestamp of the reading

        Returns:
            list: List of created alert dictionaries
        """
        alerts = []
        try:
            # Retrieve sensor thresholds
            self.cursor.execute(
                '''
                SELECT min_warning, max_warning, min_critical, max_critical
                FROM sensors WHERE id = ?
                ''', (sensor_id,)
            )
            result = self.cursor.fetchone()

            if result:
                min_warning, max_warning, min_critical, max_critical = result

                # Critical threshold checks
                if min_critical is not None and value <= min_critical:
                    alert = self._create_alert(
                        sensor_id, value, timestamp, "critical",
                        f"Value {value} is below critical threshold {min_critical}"
                    )
                    alerts.append(alert)
                elif max_critical is not None and value >= max_critical:
                    alert = self._create_alert(
                        sensor_id, value, timestamp, "critical",
                        f"Value {value} is above critical threshold {max_critical}"
                    )
                    alerts.append(alert)

                # Warning threshold checks
                elif min_warning is not None and value <= min_warning:
                    alert = self._create_alert(
                        sensor_id, value, timestamp, "warning",
                        f"Value {value} is below warning threshold {min_warning}"
                    )
                    alerts.append(alert)
                elif max_warning is not None and value >= max_warning:
                    alert = self._create_alert(
                        sensor_id, value, timestamp, "warning",
                        f"Value {value} is above warning threshold {max_warning}"
                    )
                    alerts.append(alert)

            return alerts

        except sqlite3.Error as e:
            print(f"❌ Error checking value: {e}")
            return []

    def _create_alert(self, sensor_id, value, timestamp, severity, description):
        """
        Insert an alert record into the database.

        Args:
            sensor_id (int): Sensor ID
            value (float): Sensor reading value
            timestamp (str): Timestamp of the reading
            severity (str): Alert severity ('warning'/'critical')
            description (str): Alert description message

        Returns:
            dict: Dictionary containing alert details
        """
        try:
            self.cursor.execute(
                '''
                INSERT INTO alerts (sensor_id, timestamp, value, severity, description)
                VALUES (?, ?, ?, ?, ?)
                ''', (sensor_id, timestamp, value, severity, description)
            )
            self.conn.commit()

            return {
                'sensor_id': sensor_id,
                'timestamp': timestamp,
                'value': value,
                'severity': severity,
                'description': description
            }

        except sqlite3.Error as e:
            print(f"❌ Error creating alert: {e}")
            return None

    def get_sensor_alerts(self, sensor_id=None, limit=10):
        """
        Retrieve alert records for a specific sensor or all sensors.

        Args:
            sensor_id (int, optional): ID of the sensor to filter alerts. If None, returns all alerts.
            limit (int): Maximum number of alert records to return.

        Returns:
            list: List of tuples containing alert records
        """
        cursor = self.conn.cursor()

        if sensor_id:
            cursor.execute(
                '''
                SELECT a.description, a.severity, a.timestamp, a.value, s.name
                FROM alerts a
                JOIN sensors s ON a.sensor_id = s.id
                WHERE a.sensor_id = ?
                ORDER BY a.timestamp DESC
                LIMIT ?
                ''', (sensor_id, limit)
            )
        else:
            cursor.execute(
                '''
                SELECT a.description, a.severity, a.timestamp, a.value, s.name
                FROM alerts a
                JOIN sensors s ON a.sensor_id = s.id
                ORDER BY a.timestamp DESC
                LIMIT ?
                ''', (limit,)
            )

        return cursor.fetchall()

    def __del__(self):
        """Close database connection when the object is deleted"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Test the ErrorManager functionality
    error_manager = ErrorManager()

    # Sample test values for sensors
    test_values = [
        (1, 60),   # Critical temperature
        (2, 20),   # Low humidity
        (3, 1200), # High CO2
        (4, 400),  # High smoke
        (5, 1500), # High gas
        (6, 1),    # Motion detected
        (7, 90),   # Loud noise
        (8, 0.8),  # Tampering detected
        (9, 1),    # Water leak
        (10, 1200) # Bright light
    ]

    print("\n🔍 Testing ErrorManager:")
    for sensor_id, value in test_values:
        alerts = error_manager.check_value(
            sensor_id, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        if alerts:
            print(f"\n⚠️ Alert for sensor {sensor_id}:")
            for alert in alerts:
                print(f"- {alert['description']} (Severity: {alert['severity']})")
