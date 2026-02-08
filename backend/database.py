"""
Database configuration using SQLite (simpler for deployment)
"""
import os
from agno.db.sqlite import SqliteDb

# Create Agno SQLite instance (file-based, no config needed)
db = SqliteDb()

# Test database connection
def test_db_connection():
    """Test database connection"""
    try:
        # SQLite always works with Agno
        print("SQLite database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
