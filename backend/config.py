# config.py
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:123456@127.0.0.1:3306/lsk?charset=utf8mb4"
)
