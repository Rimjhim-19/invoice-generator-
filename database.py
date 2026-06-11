from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

# Get database URL from .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create connection to PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session factory (used to talk to DB)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all database models (tables)
Base = declarative_base()


# Dependency to get DB session (used later in FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()