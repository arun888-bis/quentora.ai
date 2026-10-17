import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME', 'quentora'),
    'port': int(os.getenv('DB_PORT', '5432'))
}