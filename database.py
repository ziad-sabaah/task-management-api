from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables from .env file (no defaults - .env is source of truth)
DATABASE_URL = os.environ["DATABASE_URL"]
DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

# Create engine using the database URL from environment
engine = create_engine(DATABASE_URL, echo=DEBUG)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session
