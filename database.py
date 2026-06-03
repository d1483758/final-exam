import sqlite3
from flask import g, current_app

def get_db():
    """取得資料庫連線，並將連線快取在 Flask g 物件中"""
    if 'db' not in g:
        # 讀取設定檔中的資料庫路徑
        db_path = current_app.config['DATABASE']
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 讓查詢結果可以像字典一樣以鍵值 (Column Name) 讀取
        g.db.row_factory = sqlite3.Row
        # 啟用外鍵約束
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    """關閉資料庫連線"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """在 Flask App 中註冊資料庫關閉的清理函式"""
    app.teardown_appcontext(close_db)
