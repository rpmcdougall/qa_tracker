"""
Database configuration for QA Tracker
Set the DATABASE_URL environment variable or modify the default connection string
"""

import os

# Database configuration
# Set DATABASE_URL environment variable to override
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///qa_tracker.db')

# Example connection strings for different databases:

# SQLite (default - no server needed)
# DATABASE_URL = 'sqlite:///qa_tracker.db'

# PostgreSQL
# DATABASE_URL = 'postgresql://username:password@localhost:5432/qa_tracker'
# Or with specific driver:
# DATABASE_URL = 'postgresql+psycopg2://username:password@localhost:5432/qa_tracker'

# MySQL
# DATABASE_URL = 'mysql://username:password@localhost:3306/qa_tracker'
# Or with specific driver:
# DATABASE_URL = 'mysql+pymysql://username:password@localhost:3306/qa_tracker'

# Snowflake
# DATABASE_URL = 'snowflake://username:password@account.region/database/schema?warehouse=warehouse_name&role=role_name'

# Databricks
# DATABASE_URL = 'databricks://token:your_token@workspace.cloud.databricks.com:443/default?http_path=/sql/1.0/warehouses/warehouse_id'

# Connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,  # Verify connections before using
    'pool_recycle': 3600,   # Recycle connections after 1 hour
    'pool_size': 5,         # Number of connections to maintain
    'max_overflow': 10      # Max connections above pool_size
}

# For production, use environment variables:
# export DATABASE_URL="postgresql://user:pass@host:5432/qa_tracker"
# python app.py
