"""
删除并重新创建数据库
"""
import pymysql

# 连接到 MySQL 服务器（不指定数据库）
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='123qweasdzxc'
)

try:
    cursor = conn.cursor()
    
    # 删除数据库
    print("正在删除数据库 new_diary...")
    cursor.execute('DROP DATABASE IF EXISTS new_diary')
    conn.commit()
    print("✓ 数据库已删除")
    
    # 重新创建数据库（使用 utf8mb4 字符集）
    print("\n正在创建数据库 new_diary...")
    cursor.execute('''
        CREATE DATABASE new_diary 
        CHARACTER SET utf8mb4 
        COLLATE utf8mb4_unicode_ci
    ''')
    conn.commit()
    print("✓ 数据库已创建")
    
    print("\n✓ 数据库重建完成！")
    
except Exception as e:
    print(f'错误：{e}')
    conn.rollback()
finally:
    conn.close()
