# config.py
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:lsk040911@127.0.0.1:3306/test?charset=utf8mb4"
)
