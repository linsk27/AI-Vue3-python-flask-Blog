from sqlalchemy import text
from database import engine

def create_articles_table():
    with engine.connect() as conn:
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
            )
        """))
        conn.commit()
        print("Articles table created successfully.")

if __name__ == "__main__":
    create_articles_table()
