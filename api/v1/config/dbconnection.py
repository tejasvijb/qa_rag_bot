"""
Database connection configuration for the QA RAG Bot API
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'qa_rag_bot')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Use DATABASE_URL if provided, otherwise construct from components
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# Create SQLAlchemy engine
# Using QueuePool for connection pooling in production
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to keep in pool
    max_overflow=20,  # Maximum overflow connections
    pool_pre_ping=True,  # Test connections before using them
    echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'  # Enable SQL logging if needed
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session
    
    Usage in routes:
        from fastapi import Depends
        
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - creates all tables from Base metadata
    Call this once when the application starts
    """
    Base.metadata.create_all(bind=engine)


def test_connection():
    """
    Test the database connection
    Returns True if successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
