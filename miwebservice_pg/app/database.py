
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Por defecto usa SQLite local; en Render define DATABASE_URL a PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demo.db")

# Para SQLite es necesario connect_args, para otros motores no.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
