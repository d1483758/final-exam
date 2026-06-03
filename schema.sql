-- SQLite 資料庫綱要 (Database Schema)
-- 用於期末考專案：校園二手交易平台

-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- 1. 會員資料表 (F-01 會員登入註冊)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 商品資料表 (F-02 商品刊登管理, F-03 商品搜尋, F-04 商品瀏覽, F-05 聯絡賣家)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- 商品分類 (如: 書籍、電子產品、生活用品等)
    price REAL NOT NULL,
    image TEXT, -- 商品圖片檔案名稱或網址
    seller_id INTEGER NOT NULL, -- 關聯到刊登商品的賣家 (users.id)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users (id) ON DELETE CASCADE
);
