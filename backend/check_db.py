# 检查数据库结构
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 显示所有表
    result = conn.execute(text('SHOW TABLES'))
    print('现有表：')
    for row in result:
        print(row[0])
    
    # 检查users表结构（如果存在）
    try:
        result = conn.execute(text('DESCRIBE users'))
        print('\nusers表结构：')
        for row in result:
            print(row)
    except Exception as e:
        print('\nusers表不存在：', e)
