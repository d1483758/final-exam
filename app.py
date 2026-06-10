from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
import uuid
import database
from database import get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 註冊資料庫關閉機制
    database.init_app(app)
    
    # 確保上傳目錄存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # ==========================================
    # 會員權限驗證裝飾器 (login_required)
    # ==========================================
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('請先登入系統！', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    # 檢查上傳副檔名是否合法
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    @app.route('/')
    def index():
        # 首頁，查詢最新 4 筆商品並渲染
        db = get_db()
        try:
            latest_products = db.execute(
                "SELECT * FROM products ORDER BY created_at DESC LIMIT 4"
            ).fetchall()
        except sqlite3.OperationalError:
            latest_products = []
        return render_template('index.html', products=latest_products)

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
    # F-02 商品刊登管理模組
    # ==========================================

    @app.route('/my-products')
    @login_required
    def my_products():
        db = get_db()
        # 僅查詢當前登入使用者的商品
        user_products = db.execute(
            "SELECT * FROM products WHERE seller_id = ? ORDER BY created_at DESC",
            (session['user_id'],)
        ).fetchall()
        return render_template('my_products.html', products=user_products)

    @app.route('/product/add', methods=['GET', 'POST'])
    @login_required
    def add_product():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            price_str = request.form.get('price', '').strip()
            description = request.form.get('description', '').strip()
            
            if not title or not category or not price_str:
                flash('請填寫所有必要欄位！', 'danger')
                return render_template('add_product.html')
                
            try:
                price = float(price_str)
            except ValueError:
                flash('價格欄位必須是數字！', 'danger')
                return render_template('add_product.html')
                
            # 處理圖片上傳
            filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        # 為避免檔名重複，使用隨機 UUID 作為新檔名
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    else:
                        flash('不允許的檔案格式！只接受 png, jpg, jpeg, gif。', 'danger')
                        return render_template('add_product.html')

            db = get_db()
            try:
                db.execute(
                    "INSERT INTO products (title, description, category, price, image, seller_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (title, description, category, price, filename, session['user_id'])
                )
                db.commit()
                flash('商品成功刊登！', 'success')
                return redirect(url_for('my_products'))
            except Exception as e:
                flash('商品刊登失敗，資料庫寫入錯誤。', 'danger')
                
        return render_template('add_product.html')

    @app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(product_id):
        db = get_db()
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        
        if not product:
            flash('找不到該商品！', 'danger')
            return redirect(url_for('my_products'))
            
        # 權限驗證：只能編輯自己的商品
        if product['seller_id'] != session['user_id']:
            flash('您無權修改此商品！', 'danger')
            return redirect(url_for('my_products'))
            
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            price_str = request.form.get('price', '').strip()
            description = request.form.get('description', '').strip()
            
            if not title or not category or not price_str:
                flash('請填寫所有必要欄位！', 'danger')
                return render_template('edit_product.html', product=product)
                
            try:
                price = float(price_str)
            except ValueError:
                flash('價格欄位必須是數字！', 'danger')
                return render_template('edit_product.html', product=product)
                
            filename = product['image']
            
            # 處理圖片更換
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        # 刪除舊圖片檔案
                        if product['image']:
                            old_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
                            if os.path.exists(old_path):
                                os.remove(old_path)
                                
                        # 儲存新圖片
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    else:
                        flash('不允許的檔案格式！只接受 png, jpg, jpeg, gif。', 'danger')
                        return render_template('edit_product.html', product=product)

            try:
                db.execute(
                    "UPDATE products SET title = ?, description = ?, category = ?, price = ?, image = ? WHERE id = ?",
                    (title, description, category, price, filename, product_id)
                )
                db.commit()
                flash('商品資訊修改成功！', 'success')
                return redirect(url_for('my_products'))
            except Exception as e:
                flash('商品修改失敗，資料庫寫入錯誤。', 'danger')
                
        return render_template('edit_product.html', product=product)

    @app.route('/product/delete/<int:product_id>', methods=['POST'])
    @login_required
    def delete_product(product_id):
        db = get_db()
        product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        
        if not product:
            flash('找不到該商品！', 'danger')
            return redirect(url_for('my_products'))
            
        # 權限驗證：只能刪除自己的商品
        if product['seller_id'] != session['user_id']:
            flash('您無權刪除此商品！', 'danger')
            return redirect(url_for('my_products'))
            
        try:
            # 刪除硬碟中的商品照
            if product['image']:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
                if os.path.exists(image_path):
                    os.remove(image_path)
                    
            db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            db.commit()
            flash('商品下架成功！', 'success')
        except Exception as e:
            flash('下架商品失敗。', 'danger')
            
        return redirect(url_for('my_products'))

    # ==========================================
    # F-03 商品搜尋模組
    # ==========================================
    @app.route('/products')
    def products():
        q = request.args.get('q', '').strip()
        c = request.args.get('c', '').strip()
        
        db = get_db()
        sql = "SELECT * FROM products"
        clauses = []
        parameters = []
        
        if q:
            clauses.append("(title LIKE ? OR description LIKE ?)")
            parameters.append(f"%{q}%")
            parameters.append(f"%{q}%")
            
        if c:
            clauses.append("category = ?")
            parameters.append(c)
            
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
            
        sql += " ORDER BY created_at DESC"
        
        products_list = db.execute(sql, parameters).fetchall()
        return render_template('products.html', products=products_list, q=q, c=c)

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        db = get_db()
        product = db.execute(
            """
            SELECT p.*, 
                   u.username AS seller_name, 
                   u.email AS seller_email, 
                   u.contact_info AS seller_contact
            FROM products p
            INNER JOIN users u ON p.seller_id = u.id
            WHERE p.id = ?
            """,
            (product_id,)
        ).fetchone()
        
        if not product:
            flash('找不到該商品，已導回商品列表頁！', 'danger')
            return redirect(url_for('products'))
            
        return render_template('product_detail.html', product=product)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
