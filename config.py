import os
import json
from pathlib import Path

# 預設資料庫配置
DEFAULT_DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'chinese_medicine_db',
    'user': 'root',
    'password': 'Great23515757'  # 預設密碼
}

# 應用程式配置
APP_CONFIG = {
    'window_title': '中醫處方好幫手',
    'window_width': 1000,
    'window_height': 700
}

# UI配置
UI_CONFIG = {
    'readonly_background_color': 'rgb(240, 240, 240)',
    'highlight_background_color': 'rgb(255, 255, 0)'
}

def get_config_path():
    """取得設定檔路徑"""
    # 獲取執行檔所在目錄
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包後的路徑
        base_path = Path(sys.executable).parent
    else:
        # 開發環境路徑
        base_path = Path(__file__).parent
    
    return base_path / 'database_config.json'

def load_database_config():
    """載入資料庫設定檔"""
    config_file = get_config_path()
    
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"已載入設定檔: {config_file}")
            return config
        else:
            # 如果設定檔不存在，建立預設設定檔
            create_default_config_file()
            print(f"已建立預設設定檔: {config_file}")
            return DEFAULT_DATABASE_CONFIG.copy()
    
    except Exception as e:
        print(f"載入設定檔錯誤: {e}")
        print("使用預設設定")
        return DEFAULT_DATABASE_CONFIG.copy()

def create_default_config_file():
    """建立預設設定檔"""
    config_file = get_config_path()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_DATABASE_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"已建立預設設定檔: {config_file}")
    except Exception as e:
        print(f"建立設定檔失敗: {e}")

def save_database_config(config):
    """儲存資料庫設定檔"""
    config_file = get_config_path()
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"設定檔已儲存: {config_file}")
        return True
    except Exception as e:
        print(f"儲存設定檔失敗: {e}")
        return False

# 載入資料庫配置
import sys
DATABASE_CONFIG = load_database_config()