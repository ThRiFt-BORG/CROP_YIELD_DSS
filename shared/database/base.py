from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database connection details for PostgreSQL/PostGIS
# Note the 'postgresql+psycopg2' driver
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@postgres/dss_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
