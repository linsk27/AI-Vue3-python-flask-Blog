# 创建AI配置表
import os

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 创建ai_config表
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS ai_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        config_key VARCHAR(50) NOT NULL UNIQUE,
        value TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """))
    
    # 插入默认配置
    default_configs = [
        ('api_key', os.getenv('ARK_API_KEY', '')),
        ('default_model', os.getenv('ARK_MODEL', 'ep-20260125005850-g97x2')),
        ('default_provider', 'volcano'),
        ('base_url', os.getenv('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')),
    ]
    
    for config_key, value in default_configs:
        # 检查配置是否存在
        existing = conn.execute(
            text("SELECT id FROM ai_config WHERE config_key = :config_key"),
            {"config_key": config_key}
        ).fetchone()
        
        if not existing:
            conn.execute(
                text("INSERT INTO ai_config (config_key, value) VALUES (:config_key, :value)"),
                {"config_key": config_key, "value": value}
            )
    
    # 提交事务
    conn.commit()
    
    print("AI配置表创建成功并插入默认数据")
    
    # 查看表结构
    result = conn.execute(text("DESCRIBE ai_config"))
    print("\nai_config表结构：")
    for row in result:
        print(row)
    
    # 查看数据
    result = conn.execute(text("SELECT * FROM ai_config"))
    print("\nai_config表数据：")
    for row in result:
        print(row)
