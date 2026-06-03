# -*- coding: utf-8 -*-
import unittest
from app import create_app
import sqlite3
import os

class FlaskSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = os.path.join(self.app.config['BASE_DIR'], 'instance', 'test_search_database.db')
        self.client = self.app.test_client()
        
        # 初始化測試資料庫
        with self.app.app_context():
            db_path = self.app.config['DATABASE']
            schema_path = os.path.join(self.app.config['BASE_DIR'], 'schema.sql')
            conn = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            
            # 新增一個測試會員與三個測試商品
            conn.execute("INSERT INTO users (id, username, email, password) VALUES (1, 'tester', 'test@test.com', 'pwd')")
            
            # 商品 1: Python 教科書
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, seller_id) VALUES (101, 'Python 程式設計指南', '適合初學者的 Python 課本', '教科書', 450, 1)"
            )
            # 商品 2: 二手 iPhone
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, seller_id) VALUES (102, '二手 iPhone 12', '八成新，電池健康度 85%', '電子產品', 9000, 1)"
            )
            # 商品 3: 自行車
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, seller_id) VALUES (103, '捷安特單車', '適合校園通勤', '自行車', 2000, 1)"
            )
            conn.commit()
            conn.close()

    def tearDown(self):
        test_db = self.app.config['DATABASE']
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_search_cases(self):
        # 1. 測試無任何篩選條件 (應回傳所有 3 個商品)
        response_all = self.client.get('/products')
        data_all = response_all.data.decode('utf-8')
        self.assertIn("Python 程式設計指南", data_all)
        self.assertIn("二手 iPhone 12", data_all)
        self.assertIn("捷安特單車", data_all)

        # 2. 關鍵字搜尋：搜尋標題中含有 'Python' 的商品
        response_q_title = self.client.get('/products?q=Python')
        data_q_title = response_q_title.data.decode('utf-8')
        self.assertIn("Python 程式設計指南", data_q_title)
        self.assertNotIn("二手 iPhone 12", data_q_title)
        self.assertNotIn("捷安特單車", data_q_title)

        # 3. 關鍵字搜尋：搜尋描述中含有 '健康度' 的商品 (iPhone 12)
        response_q_desc = self.client.get('/products?q=健康度')
        data_q_desc = response_q_desc.data.decode('utf-8')
        self.assertIn("二手 iPhone 12", data_q_desc)
        self.assertNotIn("Python 程式設計指南", data_q_desc)
        self.assertNotIn("捷安特單車", data_q_desc)

        # 4. 分類搜尋：搜尋分類為 '自行車' 的商品
        response_c = self.client.get('/products?c=自行車')
        data_c = response_c.data.decode('utf-8')
        self.assertIn("捷安特單車", data_c)
        self.assertNotIn("Python 程式設計指南", data_c)
        self.assertNotIn("二手 iPhone 12", data_c)

        # 5. 組合搜尋：搜尋關鍵字='單車' 且 分類='自行車' (應成功找到)
        response_combined = self.client.get('/products?q=單車&c=自行車')
        data_combined = response_combined.data.decode('utf-8')
        self.assertIn("捷安特單車", data_combined)
        self.assertNotIn("Python 程式設計指南", data_combined)

        # 6. 組合搜尋：搜尋關鍵字='單車' 且 分類='電子產品' (應查無結果)
        response_empty = self.client.get('/products?q=單車&c=電子產品')
        data_empty = response_empty.data.decode('utf-8')
        self.assertNotIn("捷安特單車", data_empty)
        self.assertIn("找不到符合條件的商品", data_empty)

        # 7. 搜尋無任何匹配結果
        response_none = self.client.get('/products?q=不存在的關鍵字')
        data_none = response_none.data.decode('utf-8')
        self.assertIn("找不到符合條件的商品", data_none)

if __name__ == '__main__':
    unittest.main()
