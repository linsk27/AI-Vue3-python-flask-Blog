from sqlalchemy import create_engine, text
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        # Create ai_configs table
        print("Creating ai_configs table...")
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
            )
        """))
        
        # Insert default config if table is empty
        result = conn.execute(text("SELECT COUNT(*) FROM ai_configs")).fetchone()
        if result[0] == 0:
            print("Inserting default config...")
            conn.execute(text("""
                INSERT INTO ai_configs (provider, api_key, base_url, model, system_prompt, is_active)
                VALUES (
                    'volcano',
                    '450530a8-5088-431d-b482-f2c0611b49b7',
                    'https://ark.cn-beijing.volces.com/api/v3',
                    'ep-20260125005850-g97x2',
                    'You are a helpful assistant. Please respond briefly and directly without deep thinking. Keep answers concise and to the point.',
                    TRUE
                )
            """))
            
        conn.commit()
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
