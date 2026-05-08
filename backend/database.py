# database.py
import os
from sqlalchemy import create_engine
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "0") == "1",
    pool_pre_ping=True,
    pool_recycle=280,
)
