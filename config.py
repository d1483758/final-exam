import os

class Config:
    # 專案根目錄
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite 資料庫路徑
    DATABASE = os.path.join(BASE_DIR, 'instance', 'database.db')
    
    # Session 加密金鑰 (開發用預設金鑰)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
