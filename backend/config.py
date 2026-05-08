# config.py
import os
from urllib.parse import quote_plus


def _load_local_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)


_load_local_env()


def _build_database_url():
    raw_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
    if raw_url:
        if raw_url.startswith("mysql://"):
            raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
        return raw_url

    host = os.getenv("MYSQLHOST")
    port = os.getenv("MYSQLPORT", "3306")
    user = os.getenv("MYSQLUSER")
    password = os.getenv("MYSQLPASSWORD")
    database = os.getenv("MYSQLDATABASE")

    if all([host, user, password, database]):
        return (
            f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
            f"@{host}:{port}/{database}?charset=utf8mb4"
        )

    return "mysql+pymysql://root:123456@127.0.0.1:3306/lsk?charset=utf8mb4"


DATABASE_URL = _build_database_url()
SECRET_KEY = os.getenv("SECRET_KEY", "contextforge-dev-secret-change-me")
