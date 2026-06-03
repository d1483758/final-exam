# -*- coding: utf-8 -*-
import unittest
from app import create_app
import sqlite3
import os
from werkzeug.security import generate_password_hash

class FlaskProductTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = os.path.join(self.app.config['BASE_DIR'], 'instance', 'test_prod_database.db')
        self.client = self.app.test_client()
        
        # 初始化測試資料庫
        with self.app.app_context():
            db_path = self.app.config['DATABASE']
            schema_path = os.path.join(self.app.config['BASE_DIR'], 'schema.sql')
            conn = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            
            # 建立兩個測試會員
            p1 = generate_password_hash('pass123')
            p2 = generate_password_hash('pass456')
            conn.execute("INSERT INTO users (id, username, email, password) VALUES (1, 'sellerA', 'sellerA@ntu.edu.tw', ?)", (p1,))
            conn.execute("INSERT INTO users (id, username, email, password) VALUES (2, 'sellerB', 'sellerB@ntu.edu.tw', ?)", (p2,))
            
            # 會員 A 預先刊登一個商品
            conn.execute(
                "INSERT INTO products (id, title, description, category, price, seller_id) VALUES (10, 'A Book', 'Good book', '教科書', 300, 1)",
            )
            conn.commit()
            conn.close()

    def tearDown(self):
        test_db = self.app.config['DATABASE']
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_unauthenticated_access(self):
        # 1. 未登入訪問我的商品，應跳轉至登入頁 (302)
        response = self.client.get('/my-products', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
        # 2. 未登入訪問刊登商品，應跳轉至登入頁 (302)
        response_add = self.client.get('/product/add', follow_redirects=False)
        self.assertEqual(response_add.status_code, 302)

    def test_product_publishing_management(self):
        # A. 登入會員 A
        self.client.post('/login', data={
            'username': 'sellerA',
            'password': 'pass123'
        }, follow_redirects=False)
        
        # 1. 刊登新商品 (F-02)
        response = self.client.post('/product/add', data={
            'title': '二手腳踏車',
            'category': '自行車',
            'price': '1500',
            'description': '車況良好，台大水源校區面交'
        }, follow_redirects=True)
        
        self.assertIn("商品成功刊登", response.data.decode('utf-8'))
        
        # 驗證資料庫是否寫入
        conn = sqlite3.connect(self.app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT title, category, price, seller_id FROM products WHERE title = ?", ('二手腳踏車',))
        product = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(product)
        self.assertEqual(product[0], '二手腳踏車')
        self.assertEqual(product[1], '自行車')
        self.assertEqual(product[2], 1500.0)
        self.assertEqual(product[3], 1) # seller_id 應為 1 (sellerA)

        # 2. 修改自己(A)的商品
        response_edit = self.client.post('/product/edit/10', data={
            'title': 'A Book (已降價)',
            'category': '教科書',
            'price': '200',
            'description': '急售！'
        }, follow_redirects=True)
        
        self.assertIn("商品資訊修改成功", response_edit.data.decode('utf-8'))

        # B. 登出會員 A，改登入會員 B
        self.client.get('/logout')
        self.client.post('/login', data={
            'username': 'sellerB',
            'password': 'pass456'
        }, follow_redirects=False)

        # 3. 越權修改他人商品 (B 修改 A 的商品 10)
        response_wrong_edit = self.client.post('/product/edit/10', data={
            'title': 'Hacked Title',
            'category': '其他',
            'price': '10',
            'description': 'Hack'
        }, follow_redirects=True)
        
        self.assertIn("您無權修改此商品", response_wrong_edit.data.decode('utf-8'))
        
        # 4. 越權刪除他人商品 (B 刪除 A 的商品 10)
        response_wrong_delete = self.client.post('/product/delete/10', follow_redirects=True)
        self.assertIn("您無權刪除此商品", response_wrong_delete.data.decode('utf-8'))

        # C. 登出會員 B，重新登入會員 A
        self.client.get('/logout')
        self.client.post('/login', data={
            'username': 'sellerA',
            'password': 'pass123'
        }, follow_redirects=False)

        # 5. 刪除自己(A)的商品 10
        response_delete = self.client.post('/product/delete/10', follow_redirects=True)
        self.assertIn("商品下架成功", response_delete.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
