# 🏫 校園二手交易平台 (Campus Second-Hand Trading Platform)

專為校園學子設計的二手商品交易與物資共享平台。本專案使用 Python Flask 與 SQLite 資料庫開發，採用簡潔、直覺的 MVC 架構，並完成了全套自動化單元與回歸測試，非常適合作為期末專題報告。

---

## 🚀 系統核心功能 (F-01 ~ F-05)

本專案完全對齊專題報告之軟體需求規格，移除了所有無關的購物車、結帳與後台管理，聚焦於最純粹的校園交易流程：

* **🔒 F-01 会員登入註冊**
  * 使用 `werkzeug.security` 的 `generate_password_hash` 對密碼進行單向安全雜湊加密儲存。
  * 利用 Flask Session 追蹤登入狀態。
* **📦 F-02 商品刊登管理**
  * 會員可刊登商品並上傳實體照（上傳時採用隨機 UUID 自動重命名防檔名覆蓋）。
  * 設有**越權防護**限制：只有商品的刊登者（擁有者）才可編輯或刪除該商品。
  * **磁碟自動清理**：當刪除商品或編輯更換照片時，系統會自動在伺服器背景中刪除舊圖片，節省硬碟空間。
* **🔍 F-03 商品組合搜尋**
  * 支援關鍵字搜尋（同時對商品標題與詳細描述做模糊比對）。
  * 支援分類篩選（預設提供：教科書、電子產品、生活用品、自行車、其他）。
  * 關鍵字與分類可同時複合使用；若無符合商品，則顯示友好之空狀態提示。
* **📖 F-04 商品詳細瀏覽**
  * 公開的詳細商品介紹頁面，不需登入即可自由查閱商品的圖片、標題、分類、預估價、刊登時間與賣家帳號。
* **✉️ F-05 聯絡賣家資訊**
  * 在商品詳細頁中直接展示賣家的 Email 與其他聯絡資訊 (如 LINE ID)，供買家自行私訊或線下面交交易，完全無平台手續費。

---

## 🛠️ 技術棧 (Technology Stack)

* **後端邏輯**：Python 3.x, Flask Web Framework
* **資料庫**：SQLite3 (使用 `sqlite3.Row` 處理關聯屬性)
* **前端視覺**：HTML5 (Jinja2 樣板引擎), Vanilla CSS (現代 HSL 柔和配色與響應式格線排版)
* **單元測試**：Python `unittest` 標準庫

---

## 📂 專案目錄結構

```text
final-exam/
├── app.py                  # Flask 主應用程式 (包含 F-01 至 F-05 的所有核心控制器與路由)
├── config.py               # 專案環境組態檔 (上傳限制、金鑰及資料庫位置)
├── database.py             # SQLite 連線管理模組 (快取與 teardown 機制)
├── init_db.py              # 資料庫初始化指令碼
├── schema.sql              # 資料庫 schema (建置 users 及 products 兩張核心資料表)
├── README.md               # 專案說明文件
├── .gitignore              # Git 忽略檔案設定
├── static/                 # 靜態資源目錄
│   ├── css/
│   │   └── style.css       # 平台全域樣式表 (包含美化的首頁新手指南與商品卡片)
│   ├── js/
│   │   └── main.js         # 前端腳本
│   └── uploads/            # 使用者上傳的二手商品實照目錄 (預設忽略)
├── templates/              # HTML 樣板資料夾
│   ├── base.html           # 全站基本導覽列及頁尾布局
│   ├── index.html          # 首頁 (快捷搜尋列、最新商品、新手使用指南)
│   ├── login.html          # 會員登入
│   ├── register.html       # 會員註冊
│   ├── add_product.html    # 刊登新二手商品
│   ├── edit_product.html   # 編輯修改二手商品
│   ├── products.html       # 商品搜尋結果及列表
│   ├── my_products.html    # 我的商品管理面板
│   └── product_detail.html # 商品詳細頁面與賣家聯絡卡
└── (測試模組)
    ├── test_auth.py        # F-01 會員功能自動化測試
    ├── test_product.py     # F-02 商品刊登與越權防護測試
    ├── test_search.py      # F-03 商品關鍵字與分類搜尋測試
    └── test_browsing.py    # F-04/F-05 商品瀏覽及賣家聯絡測試
```

---

## 🚀 快速開始 (Quick Start)

### 1. 安裝依賴環境
本專案僅依賴 Flask 開發包，請先在終端機安裝：
```bash
pip install flask
```

### 2. 初始化資料庫
在專案目錄下執行初始化指令以建立 `instance/database.db`：
```bash
py init_db.py
```

### 3. 啟動本機伺服器
執行 Flask 服務：
```bash
py app.py
```
啟動後，在瀏覽器打開網址：👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🧪 執行自動化測試

本專案附帶完整的單元測試覆蓋。由於包含中文商品字元，在 Windows 下建議以 **UTF-8 模式** 執行測試套件：

```bash
py -X utf8 -m unittest test_auth.py test_product.py test_search.py test_browsing.py
```

執行後如顯示 `OK` 即代表所有 8 大回歸測試場景均成功通過！

---

## 🔒 系統安全性亮點

1. **防 SQL 注入 (SQL Injection)**：所有的資料庫 Query (包含動態 SQL 搜尋比對) 均嚴格採用參數化 Prepared Statements 佔位符比對，防範 SQL 注入代碼。
2. **越權存取防護**：編輯與刪除商品時，後端會強制對比當前 Session `user_id` 是否與資料庫中的商品發布者 `seller_id` 一致，防範繞過前端直接發送 Delete 請求的惡意竄改。
3. **密碼不可逆雜湊**：帳戶註冊採用 `PBKDF2-SHA256` 進行加密雜湊，伺服器不存儲任何明文密碼，即使資料庫洩露也能保障用戶安全。
