from flask import Flask, render_template
from config import Config
import database

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 註冊資料庫關閉機制
    database.init_app(app)
    
    @app.route('/')
    def index():
        # 首頁，渲染修正後的校園二手交易平台規劃頁面
        return render_template('index.html')

    # F-01 會員登入註冊
    @app.route('/login')
    def login():
        return "F-01 會員登入頁面：待第二階段開發"

    @app.route('/register')
    def register():
        return "F-01 會員註冊頁面：待第二階段開發"

    @app.route('/logout')
    def logout():
        return "F-01 會員登出功能：待第二階段開發"

    # F-03 & F-04 商品搜尋與瀏覽
    @app.route('/products')
    def products():
        return "F-03 & F-04 商品列表與搜尋頁面：待第三階段開發"

    @app.route('/product/<int:product_id>')
    def product_detail(product_id):
        return f"F-04 & F-05 商品詳細頁 (ID: {product_id}) 與聯絡賣家資訊：待第四階段開發"

    # F-02 商品刊登管理
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
