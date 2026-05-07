import os
from urllib.parse import quote_plus


def normalize_mysql_url(url):
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def build_mysql_url_from_env():
    host = os.getenv("MYSQLHOST")
    user = os.getenv("MYSQLUSER")
    password = os.getenv("MYSQLPASSWORD")
    database = os.getenv("MYSQLDATABASE")
    port = os.getenv("MYSQLPORT", "3306")

    if not all([host, user, password, database]):
        return None

    return (
        "mysql+pymysql://"
        f"{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{database}"
        "?charset=utf8mb4"
    )


DATABASE_URL = normalize_mysql_url(
    os.getenv("DATABASE_URL")
    or os.getenv("MYSQL_URL")
    or build_mysql_url_from_env()
    or "mysql+pymysql://root:123456@127.0.0.1:3306/lsk?charset=utf8mb4"
)
