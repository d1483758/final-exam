# -*- coding: utf-8 -*-
import unittest
from app import create_app
import sqlite3
import os

class FlaskAuthTestCase(unittest.TestCase):
    def setUp(self):
        # 設定為測試模式，使用獨立的測試資料庫
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = os.path.join(self.app.config['BASE_DIR'], 'instance', 'test_database.db')
        self.client = self.app.test_client()
        
        # 初始化測試資料庫
        with self.app.app_context():
            db_path = self.app.config['DATABASE']
            schema_path = os.path.join(self.app.config['BASE_DIR'], 'schema.sql')
            conn = sqlite3.connect(db_path)
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()

    def tearDown(self):
        # 移除測試資料庫檔案
        test_db = self.app.config['DATABASE']
        if os.path.exists(test_db):
            os.remove(test_db)

    def test_registration_and_login(self):
        # 1. 測試會員註冊 (POST /register)
        response = self.client.post('/register', data={
            'username': 'student123',
            'email': 'student123@ntu.edu.tw',
            'password': 'mysecurepassword',
            'contact_info': 'LINE ID: student_line'
        }, follow_redirects=False)
        
        # 註冊成功應重導向到登入頁面 (302)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])
        
        # 驗證資料庫是否已成功寫入
        conn = sqlite3.connect(self.app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, contact_info FROM users WHERE username = ?", ('student123',))
        user = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[0], 'student123')
        self.assertEqual(user[1], 'student123@ntu.edu.tw')
        self.assertEqual(user[2], 'LINE ID: student_line')
        
        # 2. 測試重複註冊
        response_dup = self.client.post('/register', data={
            'username': 'student123',
            'email': 'dup@ntu.edu.tw',
            'password': 'password1',
            'contact_info': ''
        }, follow_redirects=True)
        self.assertIn("此帳號名稱已有人使用", response_dup.data.decode('utf-8'))
        
        # 3. 測試密碼錯誤登入 (此時尚未登入)
        response_wrong = self.client.post('/login', data={
            'username': 'student123',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn("帳號或密碼錯誤", response_wrong.data.decode('utf-8'))
        
        # 4. 測試正常會員登入 (POST /login)
        response_login = self.client.post('/login', data={
            'username': 'student123',
            'password': 'mysecurepassword'
        }, follow_redirects=False)
        
        # 登入成功應重導向到首頁 (302)
        self.assertEqual(response_login.status_code, 302)
        
        # 5. 測試登出 (GET /logout)
        response_logout = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response_logout.status_code, 302)

if __name__ == '__main__':
    unittest.main()
