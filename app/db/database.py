from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Initialize the database connection
DATABASE_URL = "postgresql://postgres:David.j.r.3@db.iqkwhjgqohvsxfzzkokd.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

# Base Model
Base = declarative_base()

# ORM Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Import models to ensure tables are created
from app.db.models.muscles import Muscle
from app.db.models.exercises import Exercise
from app.db.models.splits import Split
from app.db.models.split_muscle import SplitMuscle

# ✅ Create tables in the database
Base.metadata.create_all(bind=engine)

# ✅ Fix: Add session_scope to manage database transactions
@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
