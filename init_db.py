import os
import sqlite3

def init_db():
    # 確保 instance 資料夾存在
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    db_path = os.path.join(instance_dir, 'database.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    print(f"正在初始化資料庫：{db_path}...")
    
    # 連線並執行 schema.sql 中的語法
    conn = sqlite3.connect(db_path)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        print("資料庫初始化完成，資料表已成功建立！")
    except Exception as e:
        print(f"初始化資料庫失敗：{e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
