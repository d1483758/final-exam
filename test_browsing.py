# -*- coding: utf-8 -*-
import unittest
from app import create_app
import sqlite3
import os

class FlaskBrowsingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = os.path.join(self.app.config['BASE_DIR'], 'instance', 'test_browsing_database.db')
        self.client = self.app.test_client()
        
        # 初始化測試資料庫
        with self.app.app_context():
            db_path = self.app.config['DATABASE']
            schema_path = os.path.join(self.app.config['BASE_DIR'], 'schema.sql')
            conn = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            
            # 新增測試會員 1 (具有 email 與 contact_info)
            conn.execute(
                "INSERT INTO users (id, username, email, password, contact_info) "
                "VALUES (1, 'seller_user', 'seller@campus.edu.tw', 'hashed_pwd', 'LINE_ID_123')"
            )
            
            # 新增測試會員 2 (無 contact_info)
            conn.execute(
                "INSERT INTO users (id, username, email, password, contact_info) "
                "VALUES (2, 'no_contact_seller', 'nocontact@campus.edu.tw', 'hashed_pwd', NULL)"
            )
            
            # 商品 1: Python 教科書 (有圖片，有聯絡方式)
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, image, seller_id) "
                "VALUES (101, 'Python 程式設計指南', '適合初學者的 Python 課本', '教科書', 450, 'python_book.jpg', 1)"
            )
            # 商品 2: 二手 iPhone (無圖片，有聯絡方式)
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, image, seller_id) "
                "VALUES (102, '二手 iPhone 12', '八成新，電池健康度 85%', '電子產品', 9000, NULL, 1)"
            )
            # 商品 3: 生活用品 (無其他聯絡方式)
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, image, seller_id) "
                "VALUES (103, '二手保溫杯', '九成新', '生活用品', 150, NULL, 2)"
            )
            conn.commit()
            conn.close()

    def tearDown(self):
        test_db = self.app.config['DATABASE']
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_product_detail_anonymous_access(self):
        # 1. 測試未登入使用者存取存在商品的詳細頁面
        response = self.client.get('/product/101')
        self.assertEqual(response.status_code, 200)
        
        data = response.data.decode('utf-8')
        # 驗證顯示商品基本資訊
        self.assertIn("Python 程式設計指南", data)
        self.assertIn("適合初學者的 Python 課本", data)
        self.assertIn("教科書", data)
        self.assertIn("NT$ 450", data)
        self.assertIn("python_book.jpg", data)
        self.assertIn("seller_user", data) # 賣家名稱
        
        # 驗證 F-05 聯絡資訊有正常顯示
        self.assertIn("seller@campus.edu.tw", data)
        self.assertIn("LINE_ID_123", data)

    def test_product_detail_no_contact_info(self):
        # 2. 測試當賣家無其他聯絡資訊 (contact_info 為空)
        response = self.client.get('/product/103')
        self.assertEqual(response.status_code, 200)
        
        data = response.data.decode('utf-8')
        self.assertIn("二手保溫杯", data)
        self.assertIn("nocontact@campus.edu.tw", data)
        # 應正確提示無其他聯絡方式
        self.assertIn("賣家尚未提供其他聯絡方式", data)

    def test_product_detail_no_image(self):
        # 3. 測試無圖片商品詳細頁
        response = self.client.get('/product/102')
        self.assertEqual(response.status_code, 200)
        
        data = response.data.decode('utf-8')
        self.assertIn("二手 iPhone 12", data)
        self.assertIn("無商品圖片", data) # 顯示佔位字樣

    def test_product_detail_not_found(self):
        # 4. 測試商品不存在時重導向至商品列表頁
        response = self.client.get('/product/999', follow_redirects=True)
        # 應成功跟隨導向
        self.assertEqual(response.status_code, 200)
        
        data = response.data.decode('utf-8')
        # 應包含錯誤提示與商品列表特徵
        self.assertIn("找不到該商品，已導回商品列表頁！", data)
        self.assertIn("二手商品展示", data)

if __name__ == '__main__':
    unittest.main()
