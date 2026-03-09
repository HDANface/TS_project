"""
数据库配置示例 - MySQL 配置
将此配置复制到 myproject/settings.py 的 DATABASES 部分

注意：需要先安装 mysqlclient 或 pymysql
"""

# 安装依赖：
# pip install mysqlclient
# 或者
# pip install pymysql

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'teaching_assistant',  # 数据库名称
        'USER': 'root',                 # MySQL 用户名
        'PASSWORD': 'your_password',    # MySQL 密码
        'HOST': 'localhost',            # 数据库主机
        'PORT': '3306',                 # MySQL 端口
        
        # MySQL 特定配置
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
            
            # 连接池配置（生产环境建议）
            # 'connect_timeout': 10,
            # 'read_timeout': 10,
            # 'write_timeout': 10,
        },
        
        # 事务配置
        'ATOMIC_REQUESTS': True,  # 每个请求在一个事务中执行
        
        # 时区支持
        'TIME_ZONE': 'UTC',
    }
}

# 如果你使用环境变量管理配置（推荐），可以这样写：
"""
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'teaching_assistant'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'ATOMIC_REQUESTS': True,
    }
}
"""
