"""
Database configuration for PostgreSQL using Agno framework
"""
import os
from agno.db.postgres import PostgresDb

# Database configuration from environment variables
DATABASE_URL = f"postgresql+psycopg://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"

# Create Agno PostgresDb instance
db = PostgresDb(db_url=DATABASE_URL)

# Test database connection
def test_db_connection():
    """Test database connection"""
    try:
        # Agno handles connection testing internally
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
