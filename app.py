from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import database
from database import get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 註冊資料庫關閉機制
    database.init_app(app)
    
    @app.route('/')
    def index():
        # 首頁，渲染校園二手交易平台規劃與進度頁面
        return render_template('index.html')

    # ==========================================
    # F-01 會員登入註冊模組
    # ==========================================
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if session.get('user_id'):
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            contact_info = request.form.get('contact_info', '').strip()
            
            if not username or not email or not password:
                flash('請填寫所有必要欄位！', 'danger')
                return render_template('register.html')
                
            db = get_db()
            try:
                # 密碼雜湊加密
                hashed_password = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, email, password, contact_info) VALUES (?, ?, ?, ?)",
                    (username, email, hashed_password, contact_info if contact_info else None)
                )
                db.commit()
                flash('註冊成功！請使用您的帳號進行登入。', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('此帳號名稱已有人使用！', 'danger')
            except Exception as e:
                flash('註冊失敗，發生系統錯誤，請稍後再試。', 'danger')
                
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if session.get('user_id'):
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash('請填寫帳號及密碼！', 'danger')
                return render_template('login.html')
                
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            
            if user and check_password_hash(user['password'], password):
                # 登入成功，寫入 Session 狀態
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'歡迎回來，{username}！', 'success')
                return redirect(url_for('index'))
            else:
                flash('帳號或密碼錯誤，請重試！', 'danger')
                
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('您已成功登出系統。', 'success')
        return redirect(url_for('index'))

    # ==========================================
    # 其他功能佔位 (F-02, F-03, F-04, F-05) - 本階段不實作核心邏輯
    # ==========================================
    
    @app.route('/products')
    def products():
        return "F-03 & F-04 商品列表與搜尋頁面：待第三階段開發"

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        return f"F-04 & F-05 商品詳細頁 (ID: {product_id}) 與聯絡賣家資訊：待第四階段開發"

    @app.route('/product/add')
    def add_product():
        return "F-02 商品刊登頁面：待第五階段開發"

    @app.route('/product/edit/<int:product_id>')
    def edit_product(product_id):
        return f"F-02 商品編輯頁面 (ID: {product_id})：待第五階段開發"

    @app.route('/my-products')
    def my_products():
        return "F-02 我的商品管理頁面：待第五階段開發"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
