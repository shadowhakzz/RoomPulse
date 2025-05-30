"""
Setup script for the Sensor Monitoring System.
"""

from setuptools import setup, find_packages

setup(
    name="sensor-monitoring",
    version="1.0.0",
    description="A comprehensive server room monitoring system",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.9",
        "matplotlib>=3.10.3",
        "numpy>=1.26.4",
        "pandas>=2.1.4",
        "openpyxl>=3.1.2",
        "SQLAlchemy>=2.0.0",
        "psycopg2-binary>=2.9.9"
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
            "isort>=5.12.0",
            "Sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0"
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sensor-monitor=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
    ],
) 