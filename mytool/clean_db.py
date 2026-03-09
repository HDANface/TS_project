"""
彻底清理数据库中的 courses 相关表
"""
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='123qweasdzxc',
    database='new_diary'
)

try:
    cursor = conn.cursor()
    
    # 禁用外键检查
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    
    # 查询所有 courses 相关的表
    cursor.execute("SHOW TABLES LIKE 'courses_%'")
    tables = cursor.fetchall()
    
    if tables:
        print("找到以下 courses 相关的表:")
        for table in tables:
            table_name = table[0]
            print(f"  删除表：{table_name}")
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        conn.commit()
        print(f'\n✓ 已删除 {len(tables)} 个表')
    else:
        print("数据库中没有 courses 相关的表")
    
    # 恢复外键检查
    cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
    
finally:
    conn.close()
