import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG, save_database_config

class DatabaseManager:
    def __init__(self, host=None, database=None, user=None, password=None, port=None):
        # 使用配置檔案或傳入的參數
        self.host = host or DATABASE_CONFIG.get('host', 'localhost')
        self.database = database or DATABASE_CONFIG.get('database', 'chinese_medicine_db')
        self.user = user or DATABASE_CONFIG.get('user', 'root')
        self.password = password or DATABASE_CONFIG.get('password', '')
        self.port = port or DATABASE_CONFIG.get('port', 3306)
        self.charset = DATABASE_CONFIG.get('charset', 'utf8mb4')
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """連接到MySQL資料庫"""
        try:
            connection_config = {
                'host': self.host,
                'database': self.database,
                'user': self.user,
                'password': self.password,
                'port': self.port,
                'charset': self.charset,
                'autocommit': True
            }
            
            self.connection = mysql.connector.connect(**connection_config)
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                db_info = self.connection.get_server_info()
                print(f"成功連接到MySQL資料庫 (版本: {db_info})")
#                 print(f"連接資訊: {self.user}@{self.host}:{self.port}/{self.database}")
                return True
                
        except Error as e:
            error_msg = f"無法連接到MySQL資料庫: {e}"
            print(error_msg)
            
            # 如果是認證失敗，提供更友善的錯誤訊息
            if "Access denied" in str(e):
                print("請檢查以下設定：")
                print(f"1. 使用者名稱: {self.user}")
                print(f"2. 密碼: {'*' * len(self.password)}")
                print(f"3. 主機: {self.host}")
                print(f"4. 連接埠: {self.port}")
                print(f"5. 資料庫: {self.database}")
                print("\n請修改 database_config.json 檔案中的設定")
            
            return False
    
    def test_connection(self):
        """測試資料庫連接"""
        try:
            if self.connect():
                print("資料庫連接測試成功")
                self.disconnect()
                return True
            else:
                print("資料庫連接測試失敗")
                return False
        except Exception as e:
            print(f"連接測試發生錯誤: {e}")
            return False
    
    def disconnect(self):
        """斷開資料庫連接"""
        try:
            if hasattr(self, 'connection') and self.connection and self.connection.is_connected():
                if self.cursor:
                    self.cursor.close()
                self.connection.close()
                print("MySQL資料庫連接已關閉")
        except Error as e:
            print(f"關閉資料庫連接時發生錯誤: {e}")
    
    def execute_query(self, query, params=None):
        """執行查詢"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"查詢執行錯誤: {e}")
            print(f"SQL: {query}")
            if params:
                print(f"參數: {params}")
            return None
    
    def execute_insert_update_delete(self, query, params=None):
        """執行插入、更新或刪除操作"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # 由於設定了 autocommit=True，這裡不需要手動 commit
            return True
        except Error as e:
            print(f"操作執行錯誤: {e}")
            print(f"SQL: {query}")
            if params:
                print(f"參數: {params}")
            return False
    
    def get_last_insert_id(self):
        """獲取最後插入的ID"""
        return self.cursor.lastrowid
    
    def get_connection_info(self):
        """獲取連接資訊"""
        return {
            'host': self.host,
            'database': self.database,
            'user': self.user,
            'port': self.port,
            'charset': self.charset,
            'connected': self.connection.is_connected() if self.connection else False
        }

# 提供一個便利的函數來更新設定檔
def update_database_config(host=None, database=None, user=None, password=None, port=None):
    """更新資料庫設定檔"""
    new_config = DATABASE_CONFIG.copy()
    
    if host is not None:
        new_config['host'] = host
    if database is not None:
        new_config['database'] = database
    if user is not None:
        new_config['user'] = user
    if password is not None:
        new_config['password'] = password
    if port is not None:
        new_config['port'] = port
    
    return save_database_config(new_config)