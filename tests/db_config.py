"""
Database configuration for tests
"""
import os
from data.db_factory import DBType

# Default to SQLite for tests
# Set TEST_DB_TYPE environment variable to "mongo" to use MongoDB
def get_test_db_type():
    """Get the database type for tests from environment variable"""
    db_type_str = os.environ.get("TEST_DB_TYPE", "sql").lower()
    if db_type_str == "mongo":
        return DBType.MONGO
    return DBType.SQL

# MongoDB connection settings - can be overridden by environment variables
def get_mongo_config():
    """Get MongoDB configuration from environment variables"""
    return {
        "connection_uri": os.environ.get("MONGO_URI", "mongodb://localhost:27017/"),
        "db_name": os.environ.get("MONGO_DB_NAME", "cool_chat_app_test")
    }

# SQLite connection settings - can be overridden by environment variables
def get_sql_config():
    """Get SQL configuration from environment variables"""
    return {
        "db_url": os.environ.get("SQL_DB_URL", "sqlite:///test_web_server.db"),
        "echo": os.environ.get("SQL_ECHO", "False").lower() == "true"
    } 