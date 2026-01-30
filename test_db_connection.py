#!/usr/bin/env python3
"""
Test PostgreSQL database connection using SQLAlchemy
"""
import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    
    # Configure PostgreSQL connection string
    # You can modify these defaults or set environment variables:
    # DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'qa_rag_bot')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    # Or use DATABASE_URL if set
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        connection_string = database_url
        print(f"Using DATABASE_URL: {database_url.split('@')[0]}@...")
    else:
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(f"Using connection: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    
    try:
        # Create engine
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✓ Connection successful!")
            print(f"✓ Query result: {result.fetchone()}")
        
        # Get database info
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {tables if tables else 'No tables yet'}")
        
        # Get server version
        with engine.connect() as connection:
            version = connection.execute(text("SELECT version()"))
            print(f"✓ PostgreSQL version: {version.fetchone()[0]}")
        
        print("\n✓ All tests passed! Database connection is working.")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {type(e).__name__}")
        print(f"✗ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD environment variables")
        print("3. Verify the database exists and user has access")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
