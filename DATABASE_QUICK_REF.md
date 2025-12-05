# Database Quick Reference

## Connection Strings by Database Type

### SQLite (Default)
```bash
DATABASE_URL="sqlite:///qa_tracker.db"
```
- ✅ No server required
- ✅ Zero configuration
- ✅ Single file
- ⚠️ Limited concurrency
- 📦 Driver: Built-in

### PostgreSQL
```bash
DATABASE_URL="postgresql+psycopg2://username:password@host:5432/qa_tracker"
```
- ✅ Excellent for teams
- ✅ Great performance
- ✅ ACID compliant
- ✅ Open source
- 📦 Driver: `pip install psycopg2-binary`

### MySQL
```bash
DATABASE_URL="mysql+pymysql://username:password@host:3306/qa_tracker"
```
- ✅ Widely supported
- ✅ Good performance
- ✅ Large community
- 📦 Driver: `pip install PyMySQL`

### Snowflake
```bash
DATABASE_URL="snowflake://user:pass@account.region/database/schema?warehouse=wh_name&role=role_name"
```
- ✅ Cloud data warehouse
- ✅ Auto-scaling
- ✅ Zero maintenance
- 💰 Usage-based pricing
- 📦 Driver: `pip install snowflake-sqlalchemy`

### Databricks
```bash
DATABASE_URL="databricks://token:your_token@workspace.cloud.databricks.com:443/catalog.schema?http_path=/sql/1.0/warehouses/id"
```
- ✅ Unified analytics platform
- ✅ Delta Lake integration
- ✅ Spark compatibility
- 💰 Compute-based pricing
- 📦 Driver: `pip install databricks-sql-connector`

## Installation Commands

```bash
# Install all drivers
pip install -r requirements.txt

# Or install individually:
pip install psycopg2-binary      # PostgreSQL
pip install PyMySQL               # MySQL
pip install snowflake-sqlalchemy  # Snowflake
pip install databricks-sql-connector  # Databricks
```

## Setting DATABASE_URL

### Option 1: Environment Variable (Recommended)
```bash
export DATABASE_URL="your_connection_string"
python app.py
```

### Option 2: .env File
```bash
# Create .env file
echo 'DATABASE_URL="postgresql://user:pass@localhost/qa_tracker"' > .env

# Install python-dotenv
pip install python-dotenv

# Add to config.py:
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Edit config.py
```python
# config.py
DATABASE_URL = 'postgresql://user:pass@localhost/qa_tracker'
```

## Testing Connection

```bash
python test_db_connection.py
```

This will:
- ✅ Verify connection
- ✅ Create test data
- ✅ Test CRUD operations
- ✅ Clean up test data

## Common Connection Parameters

### PostgreSQL
```
host=localhost              # Database server
port=5432                   # Default PostgreSQL port
sslmode=require            # Use SSL
connect_timeout=10         # Connection timeout
```

### MySQL
```
host=localhost              # Database server
port=3306                   # Default MySQL port
charset=utf8mb4            # Character set
ssl=true                   # Use SSL
```

### Snowflake
```
warehouse=COMPUTE_WH        # Warehouse name
role=SYSADMIN              # Role to use
schema=PUBLIC              # Schema name
database=QA_TRACKER        # Database name
```

### Databricks
```
http_path=/sql/1.0/warehouses/abc123  # SQL warehouse path
catalog=main               # Unity Catalog
schema=default             # Schema name
```

## Production Checklist

- [ ] Use environment variables for credentials
- [ ] Never commit credentials to version control
- [ ] Use strong passwords
- [ ] Enable SSL/TLS for connections
- [ ] Restrict database user permissions
- [ ] Set up connection pooling
- [ ] Configure backups
- [ ] Monitor connection pool usage
- [ ] Set up logging
- [ ] Test failover scenarios

## Troubleshooting Quick Fixes

### "Module not found"
```bash
pip install <database-driver>
```

### "Could not connect"
```bash
# Verify database is running
# Check firewall rules
# Verify credentials
python test_db_connection.py
```

### "Permission denied"
```sql
-- Grant permissions (PostgreSQL)
GRANT ALL PRIVILEGES ON DATABASE qa_tracker TO username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO username;

-- Grant permissions (MySQL)
GRANT ALL PRIVILEGES ON qa_tracker.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

### "Table does not exist"
```python
# Force table creation
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

## Performance Tips

### Small Team (< 10 users)
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'max_overflow': 10
}
```

### Medium Team (10-50 users)
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20
}
```

### Large Deployment (50+ users)
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 40,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
```

## Database Recommendations

| Use Case | Recommended DB | Why |
|----------|---------------|-----|
| Local development | SQLite | Zero setup |
| Small team | PostgreSQL | Best balance |
| Enterprise | PostgreSQL/MySQL | Proven at scale |
| Already using Snowflake | Snowflake | Leverage existing platform |
| Already using Databricks | Databricks | Keep everything together |
| High concurrency | PostgreSQL | Better concurrent write handling |
| Need analytics | Snowflake/Databricks | Built for analytics |

## Support

- Full documentation: `DATABASE_SETUP.md`
- Test connection: `python test_db_connection.py`
- Check setup: `python check_setup.py`

## Example: Switching from SQLite to PostgreSQL

```bash
# 1. Install driver
pip install psycopg2-binary

# 2. Create PostgreSQL database
createdb qa_tracker

# 3. Set connection string
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost/qa_tracker"

# 4. Test connection
python test_db_connection.py

# 5. Run application
python app.py

# Tables are created automatically on first run!
```
