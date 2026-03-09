"""
检查数据库中的所有表
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
    
    # 查询所有表
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print(f"数据库 new_diary 中的所有表 ({len(tables)} 个):")
    for table in tables:
        print(f"  - {table[0]}")
    
finally:
    conn.close()
