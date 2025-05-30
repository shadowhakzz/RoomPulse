"""
This file is responsible for the graphical user interface of the application.
"""

# 📂 File name: gui.py
# -*- coding: utf-8 -*-
import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QComboBox, QPushButton,
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QGroupBox, QGridLayout, QMessageBox, QFrame, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from database_setup import DATABASE_NAME
import matplotlib.dates as mdates

# Set dark theme for matplotlib
plt.style.use('dark_background')

class MainWindow(QMainWindow):
    """Main window class of the application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Monitoring System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create timer for automatic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        self.update_timer.start(1000)  # Update every 1 second
        
        self.init_ui()

    def set_dark_theme(self):
        """Set dark theme for the application"""
        # Set main colors
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(palette)
        
        # Set general styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #353535;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                background: #2D2D2D;
            }
            QTabBar::tab {
                background: #2D2D2D;
                color: #B1B1B1;
                padding: 8px 20px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3A3A3A;
                color: white;
            }
            QTableWidget {
                background-color: #2D2D2D;
                alternate-background-color: #353535;
                color: white;
                gridline-color: #3A3A3A;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2A82DA;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                color: white;
                padding: 5px;
                border: 1px solid #3A3A3A;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #3A3A3A;
                padding: 5px;
                min-width: 6em;
            }
            QComboBox:hover {
                border: 1px solid #2A82DA;
            }
            QPushButton {
                background-color: #2A82DA;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2B7FD9;
            }
            QPushButton:pressed {
                background-color: #2468B0;
            }
            QLabel {
                color: white;
            }
        """)

    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tabs
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        main_layout.addWidget(tabs)
        
        # Real-time display tab
        realtime_tab = QWidget()
        tabs.addTab(realtime_tab, "📊 Real-time Display")
        self.setup_realtime_tab(realtime_tab)
        
        # Alerts tab
        alerts_tab = QWidget()
        tabs.addTab(alerts_tab, "⚠️ Alerts")
        self.setup_alerts_tab(alerts_tab)
        
        # History tab
        history_tab = QWidget()
        tabs.addTab(history_tab, "📜 History")
        self.setup_history_tab(history_tab)
        
        # Graphs tab
        graphs_tab = QWidget()
        tabs.addTab(graphs_tab, "📈 Graphs")
        self.setup_graphs_tab(graphs_tab)

    def setup_realtime_tab(self, tab):
        """Setup real-time display tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Real-time Sensor Status")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Real-time table
        self.realtime_table = QTableWidget()
        self.realtime_table.setColumnCount(5)
        self.realtime_table.setHorizontalHeaderLabels([
            "Sensor ID", "Sensor Type", "Last Value", "Status", "Last Reading Time"
        ])
        self.realtime_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.realtime_table.verticalHeader().setVisible(False)
        layout.addWidget(self.realtime_table)
        
        # Initial update
        self.update_realtime_display()

    def setup_alerts_tab(self, tab):
        """Setup alerts tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("System Alerts")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(6)
        self.alerts_table.setHorizontalHeaderLabels([
            "Sensor ID", "Sensor Type", "Value", "Severity", "Description", "Time"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.verticalHeader().setVisible(False)
        layout.addWidget(self.alerts_table)
        
        # Initial update
        self.update_alerts_display()

    def setup_history_tab(self, tab):
        """Setup history tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Measurement History")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Sensor ID", "Sensor Type", "Value", "Status", "Time"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        layout.addWidget(self.history_table)
        
        # Initial update
        self.update_history_display()

    def setup_graphs_tab(self, tab):
        """Setup graphs tab"""
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Analytical Graphs")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sensor and time range selection
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)
        
        # Sensor selection
        sensor_label = QLabel("Sensor:")
        sensor_label.setFont(QFont('Arial', 10))
        self.sensor_combo = QComboBox()
        self.load_sensors()
        controls_layout.addWidget(sensor_label)
        controls_layout.addWidget(self.sensor_combo)
        
        # Time range selection
        time_label = QLabel("Time Range:")
        time_label.setFont(QFont('Arial', 10))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["1 Hour", "6 Hours", "12 Hours", "24 Hours", "7 Days"])
        controls_layout.addWidget(time_label)
        controls_layout.addWidget(self.time_range_combo)
        
        # Update button
        update_btn = QPushButton("🔄 Update")
        update_btn.clicked.connect(self.update_graph)
        controls_layout.addWidget(update_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Graph
        self.figure = Figure(figsize=(8, 6), facecolor='#2D2D2D')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Initial update
        self.update_graph()

    def load_sensors(self):
        """Load sensor list"""
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute('SELECT id, type FROM sensors')
            sensors = cursor.fetchall()
            
            self.sensor_combo.clear()
            for sensor_id, sensor_type in sensors:
                self.sensor_combo.addItem(f"{sensor_type} (ID: {sensor_id})", sensor_id)
            
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error loading sensors: {e}")

    def update_all(self):
        """Update all sections"""
        self.update_realtime_display()
        self.update_alerts_display()
        self.update_history_display()
        self.update_graph()

    def update_realtime_display(self):
        """Update real-time display"""
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            
            # Get sensor information
            cursor.execute('''
            SELECT s.id, s.type, s.last_reading, s.status, s.last_reading_time
            FROM sensors s
            ORDER BY s.id
            ''')
            sensors = cursor.fetchall()
            
            # Update table
            self.realtime_table.setRowCount(len(sensors))
            for row, sensor in enumerate(sensors):
                # Convert status to text
                status_text = "Normal" if sensor[3] == 0 else "Warning" if sensor[3] == 1 else "Critical"
                
                # Set text color based on status
                status_item = QTableWidgetItem(status_text)
                if sensor[3] == 2:
                    status_item.setForeground(QColor('#FF4444'))  # Red
                elif sensor[3] == 1:
                    status_item.setForeground(QColor('#FFA500'))  # Orange
                else:
                    status_item.setForeground(QColor('#00FF00'))  # Green
                
                self.realtime_table.setItem(row, 0, QTableWidgetItem(str(sensor[0])))
                self.realtime_table.setItem(row, 1, QTableWidgetItem(sensor[1]))
                self.realtime_table.setItem(row, 2, QTableWidgetItem(str(sensor[2])))
                self.realtime_table.setItem(row, 3, status_item)
                self.realtime_table.setItem(row, 4, QTableWidgetItem(str(sensor[4])))
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error updating real-time display: {e}")

    def update_alerts_display(self):
        """Update alerts display"""
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            
            # Get recent alerts
            cursor.execute('''
            SELECT a.sensor_id, s.type, a.value, a.severity, a.description, a.timestamp
            FROM alerts a
            JOIN sensors s ON a.sensor_id = s.id
            ORDER BY a.timestamp DESC
            LIMIT 100
            ''')
            alerts = cursor.fetchall()
            
            # Update table
            self.alerts_table.setRowCount(len(alerts))
            for row, alert in enumerate(alerts):
                # Set text color based on alert severity
                severity_item = QTableWidgetItem(alert[3])
                if alert[3] == "critical":
                    severity_item.setForeground(QColor('#FF4444'))  # Red
                else:
                    severity_item.setForeground(QColor('#FFA500'))  # Orange
                
                self.alerts_table.setItem(row, 0, QTableWidgetItem(str(alert[0])))
                self.alerts_table.setItem(row, 1, QTableWidgetItem(alert[1]))
                self.alerts_table.setItem(row, 2, QTableWidgetItem(str(alert[2])))
                self.alerts_table.setItem(row, 3, severity_item)
                self.alerts_table.setItem(row, 4, QTableWidgetItem(alert[4]))
                self.alerts_table.setItem(row, 5, QTableWidgetItem(str(alert[5])))
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error updating alerts: {e}")

    def update_history_display(self):
        """Update history display"""
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            
            # Get recent history
            cursor.execute('''
            SELECT m.sensor_id, s.type, m.value, m.status, m.timestamp
            FROM measurements m
            JOIN sensors s ON m.sensor_id = s.id
            ORDER BY m.timestamp DESC
            LIMIT 100
            ''')
            history = cursor.fetchall()
            
            # Update table
            self.history_table.setRowCount(len(history))
            for row, record in enumerate(history):
                # Convert status to text
                status_text = "Normal" if record[3] == 0 else "Warning" if record[3] == 1 else "Critical"
                
                # Set text color based on status
                status_item = QTableWidgetItem(status_text)
                if record[3] == 2:
                    status_item.setForeground(QColor('#FF4444'))  # Red
                elif record[3] == 1:
                    status_item.setForeground(QColor('#FFA500'))  # Orange
                else:
                    status_item.setForeground(QColor('#00FF00'))  # Green
                
                self.history_table.setItem(row, 0, QTableWidgetItem(str(record[0])))
                self.history_table.setItem(row, 1, QTableWidgetItem(record[1]))
                self.history_table.setItem(row, 2, QTableWidgetItem(str(record[2])))
                self.history_table.setItem(row, 3, status_item)
                self.history_table.setItem(row, 4, QTableWidgetItem(str(record[4])))
            
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error updating history: {e}")

    def update_graph(self):
        """Update graph"""
        try:
            # Get selected sensor ID
            sensor_id = self.sensor_combo.currentData()
            if not sensor_id:
                return
            
            # Get selected time range
            time_range = self.time_range_combo.currentText()
            end_time = datetime.now()
            
            if time_range == "1 Hour":
                start_time = end_time - timedelta(hours=1)
            elif time_range == "6 Hours":
                start_time = end_time - timedelta(hours=6)
            elif time_range == "12 Hours":
                start_time = end_time - timedelta(hours=12)
            elif time_range == "24 Hours":
                start_time = end_time - timedelta(hours=24)
            else:  # 7 Days
                start_time = end_time - timedelta(days=7)
            
            # Get sensor data
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            
            # Get sensor information
            cursor.execute('SELECT type, min_warning, max_warning, min_critical, max_critical FROM sensors WHERE id = ?', (sensor_id,))
            sensor_info = cursor.fetchone()
            
            # Get measurements
            cursor.execute('''
            SELECT timestamp, value, status
            FROM measurements
            WHERE sensor_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
            ''', (sensor_id, start_time.strftime("%Y-%m-%d %H:%M:%S"), 
                  end_time.strftime("%Y-%m-%d %H:%M:%S")))
            measurements = cursor.fetchall()
            
            conn.close()
            
            # Clear previous graph
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            if measurements:
                # Convert data
                timestamps = [datetime.strptime(m[0], "%Y-%m-%d %H:%M:%S") for m in measurements]
                values = [m[1] for m in measurements]
                statuses = [m[2] for m in measurements]
                
                # Plot graph
                ax.plot(timestamps, values, 'b-', label='Value', linewidth=2)
                
                # Add warning and critical lines
                if sensor_info[1] is not None:  # min_warning
                    ax.axhline(y=sensor_info[1], color='#FFA500', linestyle='--', label='Lower Warning', alpha=0.7)
                if sensor_info[2] is not None:  # max_warning
                    ax.axhline(y=sensor_info[2], color='#FFA500', linestyle='--', label='Upper Warning', alpha=0.7)
                if sensor_info[3] is not None:  # min_critical
                    ax.axhline(y=sensor_info[3], color='#FF4444', linestyle='--', label='Lower Critical', alpha=0.7)
                if sensor_info[4] is not None:  # max_critical
                    ax.axhline(y=sensor_info[4], color='#FF4444', linestyle='--', label='Upper Critical', alpha=0.7)
                
                # Set X-axis format
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                if time_range in ["7 Days"]:
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                
                # Set title and labels
                ax.set_title(f"Graph for {sensor_info[0]} (ID: {sensor_id})", color='white', pad=20)
                ax.set_xlabel("Time", color='white')
                ax.set_ylabel("Value", color='white')
                
                # Set axis colors
                ax.tick_params(colors='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                
                # Set grid
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # Show legend
                ax.legend(facecolor='#2D2D2D', edgecolor='white', labelcolor='white')
                
                # Rotate X-axis labels
                plt.setp(ax.get_xticklabels(), rotation=45)
                
                # Adjust layout
                self.figure.tight_layout()
            
            # Update graph
            self.canvas.draw()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error updating graph: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 