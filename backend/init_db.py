from sqlalchemy import text
from werkzeug.security import generate_password_hash

from database import engine


PERMISSIONS = [
    ("user:manage", "用户管理"),
    ("role:manage", "角色管理"),
    ("article:manage", "文章管理"),
    ("ai:manage", "AI配置管理"),
]


def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INT NOT NULL,
                permission_id INT NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                avatar VARCHAR(255) DEFAULT '',
                role VARCHAR(50) DEFAULT 'user',
                role_id INT,
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content LONGTEXT NOT NULL,
                summary TEXT,
                category VARCHAR(50),
                tags JSON,
                author_id INT,
                cover_image VARCHAR(255),
                views INT DEFAULT 0,
                likes INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'published',
                ai_analysis JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                article_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS article_likes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                article_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_like (user_id, article_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                provider VARCHAR(50) NOT NULL,
                api_key VARCHAR(255) NOT NULL,
                base_url VARCHAR(255) NOT NULL,
                model VARCHAR(100) NOT NULL,
                system_prompt TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

        for role_name, description in [
            ("admin", "系统管理员"),
            ("user", "普通用户"),
        ]:
            conn.execute(
                text("""
                    INSERT IGNORE INTO roles (name, description)
                    VALUES (:name, :description)
                """),
                {"name": role_name, "description": description},
            )

        for code, name in PERMISSIONS:
            conn.execute(
                text("""
                    INSERT IGNORE INTO permissions (code, name)
                    VALUES (:code, :name)
                """),
                {"code": code, "name": name},
            )

        conn.execute(text("""
            INSERT IGNORE INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id FROM roles r
            JOIN permissions p ON r.name = 'admin'
        """))

        admin_role_id = conn.execute(
            text("SELECT id FROM roles WHERE name = 'admin'")
        ).scalar()
        user_role_id = conn.execute(
            text("SELECT id FROM roles WHERE name = 'user'")
        ).scalar()

        existing_admin = conn.execute(
            text("SELECT id FROM users WHERE username = 'admin'")
        ).scalar()
        if not existing_admin:
            conn.execute(
                text("""
                    INSERT INTO users (username, password, avatar, role, role_id, email)
                    VALUES (:username, :password, '', 'admin', :role_id, :email)
                """),
                {
                    "username": "admin",
                    "password": generate_password_hash("admin123"),
                    "role_id": admin_role_id,
                    "email": "admin@example.com",
                },
            )

        conn.execute(text("""
            INSERT INTO ai_configs (provider, api_key, base_url, model, system_prompt, is_active)
            SELECT 'volcano', '', 'https://ark.cn-beijing.volces.com/api/v3',
                   'ep-20260125005850-g97x2', 'You are a helpful assistant.', 1
            WHERE NOT EXISTS (SELECT 1 FROM ai_configs)
        """))

        conn.commit()
        print("Database initialized.")
        print(f"Default user role id: {user_role_id}")
        print("Default admin login: admin / admin123")


if __name__ == "__main__":
    init_db()
