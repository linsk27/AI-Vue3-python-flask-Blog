from sqlalchemy import text


def ensure_ai_config_table(conn):
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


def ensure_context_pack_tables(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_packs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            type VARCHAR(50) DEFAULT 'project',
            stage VARCHAR(50) DEFAULT 'Draft',
            description TEXT,
            intent TEXT,
            summary TEXT,
            next_action TEXT,
            key_points LONGTEXT,
            tags LONGTEXT,
            quality INT DEFAULT 40,
            token_budget VARCHAR(40) DEFAULT '0.8k',
            freshness VARCHAR(40) DEFAULT '刚刚',
            user_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pack_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            source_type VARCHAR(80) DEFAULT '文档',
            ref_type VARCHAR(80) DEFAULT 'custom',
            ref_id INT NULL,
            content LONGTEXT,
            weight VARCHAR(20) DEFAULT '中',
            status VARCHAR(40) DEFAULT '已收集',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS context_pack_source_chunks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            source_id INT NOT NULL,
            pack_id INT NOT NULL,
            chunk_index INT NOT NULL,
            content LONGTEXT NOT NULL,
            tokens_estimate INT DEFAULT 0,
            content_hash CHAR(64) NOT NULL,
            embedding LONGTEXT NULL,
            embedding_provider VARCHAR(80) NULL,
            embedding_model VARCHAR(160) NULL,
            embedding_dimension INT DEFAULT 0,
            embedded_at TIMESTAMP NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uniq_source_chunk (source_id, chunk_index),
            INDEX idx_pack_chunks (pack_id),
            FOREIGN KEY (source_id) REFERENCES context_pack_sources(id) ON DELETE CASCADE,
            FOREIGN KEY (pack_id) REFERENCES context_packs(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))

    ensure_chunk_embedding_columns(conn)
    ensure_embedding_config_table(conn)


def ensure_chunk_embedding_columns(conn):
    rows = conn.execute(
        text("""
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'context_pack_source_chunks'
        """)
    ).mappings().fetchall()
    columns = {row["COLUMN_NAME"] for row in rows}
    column_sql = {
        "embedding": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding LONGTEXT NULL",
        "embedding_provider": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_provider VARCHAR(80) NULL",
        "embedding_model": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_model VARCHAR(160) NULL",
        "embedding_dimension": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedding_dimension INT DEFAULT 0",
        "embedded_at": "ALTER TABLE context_pack_source_chunks ADD COLUMN embedded_at TIMESTAMP NULL",
    }

    for column, sql in column_sql.items():
        if column not in columns:
            conn.execute(text(sql))


def ensure_embedding_config_table(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS ai_embedding_configs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider VARCHAR(80) DEFAULT 'openai',
            api_key TEXT,
            base_url VARCHAR(255),
            model VARCHAR(160) NOT NULL,
            enabled TINYINT DEFAULT 0,
            is_active TINYINT DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
