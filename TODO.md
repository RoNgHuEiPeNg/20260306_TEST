# 專案開發進度表

## 1. 環境建置
- [x] 建立 `requirements.txt` 與 `.gitignore` @done(2026-03-06)
- [x] 建立 Python 虛擬環境 (手動執行) @done(2026-03-06)

## 2. 資料庫模型
- [x] 實作 `models.py` (SQLAlchemy 模型定義與 `init_db`) @done(2026-03-06)
- [x] 初始化資料庫與模擬數據 (Seed data) @done(2026-03-06)

## 3. 核心業務邏輯
- [x] 實作 `engine.py` (成本計算 `calculate_and_save_cost`) @done(2026-03-06)
- [x] 實作資料查詢功能 (`get_project_summary`, `get_user_load`) @done(2026-03-06)

## 4. 報表模組
- [x] 實實作 `reports.py` (將 DataFrame 匯出為 Excel) @done(2026-03-06)

## 5. 使用者介面 (Streamlit)
- [x] 實作 `app.py` 基礎框架與登入邏輯 (Session State) @done(2026-03-06)
- [x] 實作 📊 決策儀表板 (Dashboard) @done(2026-03-06)
- [x] 實作 📁 專案管理頁面 (PM/HR View) @done(2026-03-06)
- [x] 實作 📝 我的任務與工時填報頁面 (Dev View) @done(2026-03-06)
- [x] 實作 💰 費率與人員設定頁面 (HR View) @done(2026-03-06)

## 6. 測試與驗證
- [x] 驗證權限隔離 (DEV 看不到費率) @done(2026-03-06)
- [x] 驗證費率快照邏輯 (歷史數據不變) @done(2026-03-06)
- [x] 驗證報表匯出功能 @done(2026-03-06)
