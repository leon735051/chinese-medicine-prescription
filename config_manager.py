#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料庫設定檔管理工具
可以用來檢視、修改和測試資料庫連接設定
"""

import sys
from pathlib import Path
import json
from database_manager import DatabaseManager, update_database_config
from config import DATABASE_CONFIG, get_config_path

def show_current_config():
    """顯示當前設定"""
    print("=" * 50)
    print("當前資料庫設定:")
    print("=" * 50)
    print(f"主機地址: {DATABASE_CONFIG['host']}")
    print(f"連接埠: {DATABASE_CONFIG.get('port', 3306)}")
    print(f"資料庫名稱: {DATABASE_CONFIG['database']}")
    print(f"使用者名稱: {DATABASE_CONFIG['user']}")
    print(f"密碼: {'*' * len(DATABASE_CONFIG['password'])}")
    print(f"字元編碼: {DATABASE_CONFIG.get('charset', 'utf8mb4')}")
    print(f"設定檔位置: {get_config_path()}")
    print("=" * 50)

def test_connection():
    """測試資料庫連接"""
    print("\n正在測試資料庫連接...")
    db = DatabaseManager()
    if db.test_connection():
        print("✓ 資料庫連接測試成功！")
        return True
    else:
        print("✗ 資料庫連接測試失敗！")
        return False

def modify_config():
    """修改設定"""
    print("\n修改資料庫設定 (直接按 Enter 保持原設定):")
    print("-" * 30)
    
    # 輸入新設定
    host = input(f"主機地址 (目前: {DATABASE_CONFIG['host']}): ").strip()
    port = input(f"連接埠 (目前: {DATABASE_CONFIG.get('port', 3306)}): ").strip()
    database = input(f"資料庫名稱 (目前: {DATABASE_CONFIG['database']}): ").strip()
    user = input(f"使用者名稱 (目前: {DATABASE_CONFIG['user']}): ").strip()
    password = input(f"密碼 (目前: {'*' * len(DATABASE_CONFIG['password'])}): ").strip()
    
    # 準備更新的設定
    updates = {}
    if host:
        updates['host'] = host
    if port:
        try:
            updates['port'] = int(port)
        except ValueError:
            print("警告: 連接埠必須是數字，使用原設定")
    if database:
        updates['database'] = database
    if user:
        updates['user'] = user
    if password:
        updates['password'] = password
    
    # 如果有更新，儲存設定
    if updates:
        print("\n正在儲存新設定...")
        if update_database_config(**updates):
            print("✓ 設定已成功儲存！")
            
            # 測試新設定
            answer = input("\n是否要測試新的連接設定？ (y/N): ").strip().lower()
            if answer in ['y', 'yes']:
                test_connection()
        else:
            print("✗ 儲存設定失敗！")
    else:
        print("沒有變更任何設定")

def create_sample_config():
    """建立範例設定檔"""
    config_file = get_config_path()
    if config_file.exists():
        answer = input(f"設定檔 {config_file} 已存在，是否要覆蓋？ (y/N): ").strip().lower()
        if answer not in ['y', 'yes']:
            print("已取消")
            return
    
    sample_config = {
        "host": "localhost",
        "port": 3306,
        "database": "chinese_medicine_db",
        "user": "root",
        "password": "your_password_here",
        "charset": "utf8mb4"
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=4, ensure_ascii=False)
        print(f"✓ 範例設定檔已建立: {config_file}")
        print("請修改其中的密碼和其他設定")
    except Exception as e:
        print(f"✗ 建立範例設定檔失敗: {e}")

def main():
    """主程式"""
    print("中醫處方好幫手 - 資料庫設定管理工具")
    
    while True:
        print("\n請選擇操作:")
        print("1. 顯示當前設定")
        print("2. 測試資料庫連接")
        print("3. 修改設定")
        print("4. 建立範例設定檔")
        print("5. 離開")
        
        choice = input("\n請輸入選項 (1-5): ").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            test_connection()
        elif choice == '3':
            modify_config()
        elif choice == '4':
            create_sample_config()
        elif choice == '5':
            print("再見！")
            break
        else:
            print("無效的選項，請重新選擇")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        sys.exit(1)