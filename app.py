from flask import Flask, render_template
from config import Config
import database

def create_app():
    app = Flask(__name__)
    # 載入設定
    app.config.from_object(Config)
    
    # 註冊資料庫關閉機制
    database.init_app(app)
    
    @app.route('/')
    def index():
        # 首頁，渲染基本規劃首頁
        return render_template('index.html')

    # 以下路由為規劃之架構預留佔位，目前不撰寫業務邏輯程式碼
    @app.route('/login')
    def login_placeholder():
        return "F-01 會員登入功能：待第二階段開發"

    @app.route('/register')
    def register_placeholder():
        return "F-01 會員註冊功能：待第二階段開發"

    @app.route('/products')
    def products_placeholder():
        return "F-02 商品瀏覽功能：待第三階段開發"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
