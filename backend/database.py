
import os
DATABASE_URL = os.getenv("DATABASE_URL")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Format: postgresql://username:password@localhost:port/dbname
# Change 'yourpassword' to what you chose during installation!
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/Safebank_id"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()