# Server Room Monitoring System (SRMS)

A comprehensive real-time monitoring system designed specifically for server rooms and data centers. This system provides precise monitoring of various environmental parameters, security conditions, and equipment status to ensure optimal operation and early detection of potential issues.

## Version Information
- Current Version: 1.0.0
- Last Updated: 2024-03-19
- Status: Development

## System Requirements
- **Operating System**
  - Ubuntu 20.04 LTS or newer
  - Windows 10/11
  - macOS 11.0 or newer

- **Hardware Requirements**
  - CPU: Intel Core i3 or equivalent
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 100GB SSD
  - Network: 1Gbps Ethernet

## Core Features
- Real-time environmental monitoring
- Security condition tracking
- Equipment status monitoring
- Alert management system
- Data visualization and reporting
- Export capabilities to Excel
- Database logging and management

## 📁 Project Structure

server-room-monitoring/
├── main.py                    # Main entry point of the application
├── gui.py                     # Graphical User Interface using PyQt5
├── data_logger.py             # Handles data logging and storage
├── error_manager.py           # Manages error handling and logging
├── database_setup.py          # Sets up and initializes the database
├── export_to_excel.py         # Exports logged data to Excel
│
├── requirements.txt           # Project dependencies
├── setup.py                   # Installation and packaging configuration
├── pyproject.toml             # Project metadata and build system settings
│
└── README.md                  # Project documentation

### 📦 Core Components

1. **Main Application (`main.py`)**
   - Application entry point
   - System initialization
   - Main event loop
   - Configuration loading

2. **GUI Implementation (`gui.py`)**
   - Main window interface
   - Sensor data visualization
   - Real-time monitoring panels
   - Alert management interface

3. **Data Management**
   - `data_generator.py`: Simulates sensor data for testing
   - `data_logger.py`: Handles data logging and storage
   - `error_manager.py`: Manages error handling and recovery
   - `database_setup.py`: Database initialization and management
   - `export_to_excel.py`: Data export functionality

### 🔧 Configuration Files

1. **Package Configuration**
   - `setup.py`: Package installation configuration
   - `setup.cfg`: Additional package settings
   - `pyproject.toml`: Project metadata and build system
   - `MANIFEST.in`: Package file inclusion rules

2. **Development Configuration**
   - `Makefile`: Build and development tasks
   - `pytest.ini`: Testing configuration
   - `.editorconfig`: Code style settings
   - `.pre-commit-config.yaml`: Pre-commit hooks

3. **Docker Configuration**
   - `Dockerfile`: Container definition
   - `docker-compose.yml`: Multi-container setup
   - `.dockerignore`: Docker build exclusions

4. **Version Control**
   - `.gitignore`: Git exclusions
   - `.gitattributes`: Git file attributes
   - `.gitmodules`: Submodule configuration

### 📊 Data Flow

1. **Data Collection**
   ```
   Sensors → data_generator.py → data_logger.py → Database
   ```

2. **Data Processing**
   ```
   Database → gui.py → Visualization
   Database → export_to_excel.py → Excel Files
   ```

3. **Error Handling**
   ```
   Any Component → error_manager.py → Logging/Alerting
   ```

### 🔄 Development Workflow

1. **Local Development**
   ```bash
   # Setup development environment
   make install-dev
   
   # Run tests
   make test
   
   # Run linting
   make lint
   ```

2. **Docker Development**
   ```bash
   # Build and run with Docker
   docker-compose up --build
   ```

3. **CI/CD Pipeline**
   - GitHub Actions workflows in `.github/workflows/`
   - Automated testing and deployment
   - Code quality checks
   - Security scanning

## 🔄 Data Flow Architecture

### 1. Data Collection Layer
- **Sensor Interface**
  - Direct hardware communication
  - Protocol handlers (I2C, SPI, UART)
  - Data validation and preprocessing
  - Error detection and recovery

- **Data Acquisition**
  - Real-time sampling
  - Batch processing
  - Data buffering
  - Timestamp synchronization

### 2. Processing Layer
- **Data Processing**
  - Signal filtering
  - Calibration
  - Unit conversion
  - Statistical analysis

- **Alert Processing**
  - Threshold monitoring
  - Pattern recognition
  - Alert prioritization
  - Alert aggregation

### 3. Storage Layer
- **Database Management**
  - Real-time data storage
  - Historical data archiving
  - Data compression
  - Backup management

- **File System**
  - Log files
  - Configuration files
  - Export files
  - Cache management

### 4. Presentation Layer
- **User Interface**
  - Real-time monitoring
  - Data visualization
  - Alert management
  - Configuration interface

- **Reporting**
  - Automated reports
  - Custom reports
  - Data export
  - Analytics dashboard

## 📦 Dependencies

### Core Dependencies
```python
# Core functionality
PyQt5==5.15.9            # GUI framework
matplotlib==3.8.2        # Data visualization
numpy==1.26.4           # Numerical computations
pandas==2.2.0           # Data manipulation
openpyxl==3.1.2         # Excel file handling
SQLAlchemy==2.0.27      # Database ORM
psycopg2-binary==2.9.9  # PostgreSQL adapter
```

### Development Dependencies
```python
# Testing
pytest==7.4.4           # Testing framework
pytest-cov==4.1.0       # Coverage reporting
pytest-mock==3.12.0     # Mocking support

# Code Quality
black==24.1.1           # Code formatting
flake8==7.0.0           # Code linting
mypy==1.8.0            # Type checking
isort==5.13.2           # Import sorting

# Documentation
Sphinx==7.2.6           # Documentation generator
sphinx-rtd-theme==2.0.0 # Documentation theme
```

### System Dependencies
```bash
# Required system packages
build-essential          # Compilation tools
python3-dev             # Python development headers
libpq-dev              # PostgreSQL development files
libffi-dev             # Foreign Function Interface
```

## 📄 Installation Guide

### 1. System Requirements
- **Operating System**
  - Ubuntu 20.04 LTS or newer
  - Windows 10/11
  - macOS 11.0 or newer

- **Hardware Requirements**
  - CPU: Intel Core i3 or equivalent
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 100GB SSD
  - Network: 1Gbps Ethernet

### 2. Installation Steps

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev libpq-dev libffi-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
python src/database/migrations/init_db.py

# Run tests
pytest tests/
```

#### Windows
```powershell
# Install Python 3.8 or newer
# Download from https://www.python.org/downloads/

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
python src\database\migrations\init_db.py

# Run tests
pytest tests/
```

### 3. Configuration
1. Copy `config/settings.example.json` to `config/settings.json`
2. Update configuration values:
   - Database connection
   - Sensor settings
   - Alert thresholds
   - Logging preferences

### 4. Running the Application
```bash
# Development mode
python src/main.py --dev

# Production mode
python src/main.py --prod

# With specific config
python src/main.py --config custom_config.json
```

## 📊 Database Schema

### Tables Structure

#### 1. sensors
```sql
CREATE TABLE sensors (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(30) NOT NULL,
    location VARCHAR(100),
    calibration_date TIMESTAMP,
    last_maintenance TIMESTAMP,
    status VARCHAR(20),
    threshold_min FLOAT,
    threshold_max FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. measurements
```sql
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER,
    value FLOAT NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_score FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);
```

#### 3. alerts
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER,
    type VARCHAR(20),
    severity VARCHAR(10),
    message TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);
```

## 🔍 Monitoring and Logging

### Logging Configuration
```json
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 5
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": true
        }
    }
}
```

### Performance Monitoring
- CPU Usage tracking
- Memory utilization
- Disk I/O monitoring
- Network traffic analysis
- Database performance metrics

## 🔐 Security Implementation

### Authentication
```python
# JWT-based authentication
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
PASSWORD_HASH_ALGORITHM = "bcrypt"
SALT_ROUNDS = 12
```

### Data Encryption
```python
# AES-256 encryption
ENCRYPTION_KEY = "your-encryption-key"
ENCRYPTION_ALGORITHM = "AES-256-GCM"
```

### API Security
- Rate limiting
- CORS configuration
- Input validation
- SQL injection prevention

## 📈 Performance Optimization

### Database Optimization
- Indexing strategy
- Query optimization
- Connection pooling
- Caching implementation

### Application Optimization
- Memory management
- Thread pooling
- Async operations
- Resource cleanup

## 🔄 Backup and Recovery

### Backup Strategy
```bash
# Daily backup
0 0 * * * /scripts/backup.sh daily

# Weekly backup
0 0 * * 0 /scripts/backup.sh weekly

# Monthly backup
0 0 1 * * /scripts/backup.sh monthly
```

### Recovery Procedures
1. Database restoration
2. Configuration recovery
3. Log file recovery
4. System state verification

## 🤝 Contributing Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings
- Include unit tests

### Git Workflow
1. Create feature branch
2. Write tests
3. Implement feature
4. Run tests
5. Submit PR

### Documentation
- Update README
- Add API docs
- Update user guides
- Document changes

## 👨‍💻 Developer Information

### Lead Developer
- **Name**: shadowhakzz
- **Role**: Lead Developer & Project Manager
- **Email**: shadow.hakzz@gmail.com
- **GitHub**: [shadowhakzz](https://github.com/shadowhakzz)

### Support Channels
- **Technical Support**: shadow.hakzz@gmail.com
- **Bug Reports**: [GitHub Issues](https://github.com/shadowhakzz/server-room-monitoring/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/shadowhakzz/server-room-monitoring/issues)

### Maintenance Schedule
- **Daily**: Database backups and system health checks
- **Weekly**: System updates and performance monitoring
- **Monthly**: Security patches and feature updates
- **Quarterly**: Major version updates and security audits

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Updates

### Version History
- v1.0.0 (2024-05-31)
  - Initial release
  - Basic monitoring features
  - Real-time alerts
  - Data visualization
  - Database integration
  - Excel export functionality
  - ASCII art welcome screen
  - Automatic database creation
  - Data logging system

### Planned Features
- Mobile app integration
- AI-powered anomaly detection
- Advanced analytics dashboard
- Cloud synchronization
- Multi-language support
- Custom alert rules
- API documentation
- User management system
