import pymysql
from config import Config

def init_mysql_db():
    print(f"Connecting to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_PORT} with user '{Config.MYSQL_USER}'...")
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"✅ Success: Database '{Config.MYSQL_DB}' is created and ready!")
        conn.close()
    except Exception as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return False
    return True

if __name__ == '__main__':
    init_mysql_db()
