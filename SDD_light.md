這是一份根據您的 PRD 內容，專為初學者與 AI 輔助開發設計的**精簡版系統設計文件 (SDD)**。

---

# 系統設計文件 (SDD)：跨部門專案管理與成本控制系統 (MVP)

| 文件版本 | 狀態 | 作者 | 日期 | 備註 |
| :--- | :--- | :--- | :--- | :--- |
| v1.0 | 初稿 | 系統架構師 | 2024-05-23 | 針對 Streamlit + SQLite 優化 |

---

## 1. 簡介

### 1.1 專案概述
本專案旨在開發一個輕量級的專案管理系統，核心目標是將「開發工時」與「財務成本」自動掛鉤。透過系統化的工時回報與敏感費率隔離機制，解決 HR 與開發團隊之間的資訊斷層。

### 1.2 系統目標
*   **自動化成本核算**：利用「成本快照」機制，實現工時提交即計算成本。
*   **嚴格權限隔離**：確保薪資費率僅限 HR 角色存取，開發者介面完全屏蔽金額。
*   **歷史數據保護**：費率變更不影響已結算的歷史專案成本。
*   **決策視覺化**：提供資源負載與預算執行率的即時儀表板。
*   **報表一鍵化**：支持標準化 Excel 財務報表匯出。

### 1.3 技術選型
*   **程式語言**：Python 3.9+
*   **Web UI 框架**：**Streamlit** (負責前端介面呈現與後端邏輯調用)
*   **資料處理**：Pandas (用於報表生成與數據分析)
*   **資料庫**：SQLite (單一 `.db` 檔案，便於快速驗證與本機運行)
*   **資料庫 ORM**：SQLAlchemy (簡化資料表關聯操作)

---

## 2. 系統架構與運作流程

### 2.1 整體架構
```
[ 使用者瀏覽器 ] 
       ^
       | (HTTPS/HTTP)
       v
[ Streamlit Web App ] <--- (Session State 處理權限)
       ^
       | (SQLAlchemy ORM)
       v
[ SQLite Database (.db 檔案) ]
```

### 2.2 運作流程詳解
1.  **管理設定**：HR 登入後，在後台設定員工的「時薪費率」。
2.  **專案啟動**：PM 建立專案，設定預算上限與優先級。
3.  **任務指派**：PM 在專案下建立任務並指派給開發人員。
4.  **工時回報**：開發人員看到任務後，輸入實際執行工時。
5.  **觸發快照計算**：系統在工時提交瞬間，**抓取該員工當下的費率**，計算總額並寫入 `TimeLogs` 表。
6.  **數據分析**：儀表板即時讀取 `TimeLogs` 與 `Projects` 數據，更新圖表。

---

## 3. 核心模組設計

### 3.1 資料庫模型模組 (`models.py`)
*   **職責**：定義系統的資料結構與關聯性。
*   **核心功能**：使用 SQLAlchemy 定義 User, Project, Task, Rate, TimeLog 五個物件模型。

### 3.2 業務邏輯模組 (`engine.py`)
*   **職責**：處理核心計算與快照邏輯。
*   **核心功能**：
    *   `calculate_and_save_cost()`: 結合工時與費率，生成成本快照。
    *   `get_project_summary()`: 計算專案總支出與預算百分比。
    *   `get_user_load()`: 統計特定期間的人員負載。

### 3.3 報表模組 (`reports.py`)
*   **職責**：數據轉化與文件導出。
*   **核心功能**：將資料庫 Query 結果轉換為 Pandas DataFrame，並匯出為 Excel。

### 3.4 使用者介面模組 (`app.py`)
*   **職責**：主要入口點，處理路由與頁面渲染。
*   **核心功能**：側邊欄導航、RBAC 權限過濾、各功能頁面 (Dashboard, PM, Dev, HR)。

---

## 4. 資料庫設計

### 4.1 資料庫選型
選用 **SQLite**。原因：零配置、跨平台兼容性極佳、單一檔案易於備份，完全滿足 MVP 階段的單機/內網驗證需求。

### 4.2 資料表設計

#### Table: `users` (使用者表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| id | INTEGER | 唯一識別碼 | 主鍵 |
| username | VARCHAR | 登入帳號 | 唯一 |
| role | VARCHAR | 角色 (HR, PM, DEV) | 權限控制核心 |

#### Table: `projects` (專案表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| id | INTEGER | 唯一識別碼 | 主鍵 |
| name | VARCHAR | 專案名稱 | |
| budget | FLOAT | 預算上限 | |
| priority | VARCHAR | 優先級 (H/M/L) | |
| status | VARCHAR | 專案狀態 | |

#### Table: `rates` (費率表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| id | INTEGER | 唯一識別碼 | 主鍵 |
| user_id | INTEGER | 對應使用者 | 外鍵 |
| hourly_rate | FLOAT | 每小時薪資 | **敏感數據** |
| effective_date| DATE | 生效日期 | |

#### Table: `time_logs` (工時紀錄與成本快照表)
| 欄位名稱 | 資料型態 | 說明 | 備註 |
|----------|----------|------|------|
| id | INTEGER | 唯一識別碼 | 主鍵 |
| task_id | INTEGER | 對應任務 | 外鍵 |
| user_id | INTEGER | 填寫人 | |
| hours | FLOAT | 投入工時 | |
| applied_rate | FLOAT | **回報時的費率快照** | 確保歷史數據不變 |
| total_cost | FLOAT | **計算後的成本快照** | hours * applied_rate |
| created_at | DATETIME | 記錄時間 | |

---

## 5. 使用者介面與互動規劃

### 5.1 頁面結構 (Streamlit Sidebar)
1.  **📊 決策儀表板** (所有人可看，內容依權限遮罩金額)
2.  **📁 專案管理** (PM/HR 專屬)
3.  **📝 我的任務與工時** (開發者專屬)
4.  **💰 費率與人員設定** (HR 專屬)

### 5.2 核心互動流程
*   **工時錄入流程**：
    1. 開發者進入「我的任務」頁面。
    2. 選擇一個任務，輸入工時（如：3.5 小時）。
    3. 點擊「提交」。
    4. 系統後台自動查詢 `rates` 表獲取該 User 費率，計算後存入 `time_logs`。
    5. UI 顯示「提交成功」，不顯示金額。

---

## 6. API 設計 / 功能函數

### 6.1 `get_current_rate(user_id)`
*   **輸入**：User ID
*   **輸出**：Float (該用戶當前最新的費率)
*   **職責**：確保工時錄入時抓取正確的成本基數。

### 6.2 `generate_excel_report(project_id)`
*   **輸入**：Project ID
*   **輸出**：Excel File Binary
*   **職責**：將 `time_logs` 關聯 `users` 與 `projects` 進行 Aggregation。

---

## 7. 錯誤處理策略

| 錯誤情境 | 處理策略 | UI 呈現 |
|----------|----------|------|
| 未登入存取敏感頁面 | 強制跳轉至登入頁或顯示權限不足訊息 | Streamlit `st.warning` 或 `st.stop` |
| 工時輸入負數 | 前端校驗攔截 | 彈出紅框提示「工時必須大於 0」 |
| HR 未設定費率即回報工時 | 自動回退至 0 或預設值，並發送系統通知給 HR | 提示「請聯繫 HR 初始化費率資料」 |

---

## 8. 實作路徑 (Implementation Roadmap)

### 8.1 環境建置與依賴安裝
```bash
mkdir cost_control_system
cd cost_control_system
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
```

**requirements.txt:**
```text
streamlit==1.32.0
pandas==2.2.0
sqlalchemy==2.0.25
openpyxl==3.1.2
```

**安裝指令：**
```bash
pip install -r requirements.txt
```

**.gitignore:**
```text
venv/
*.db
__pycache__/
.streamlit/
```

### 8.2 資料庫模組開發 (`models.py`)
1. 使用 `sqlalchemy.orm.DeclarativeBase` 建立基類。
2. 定義 `User`, `Project`, `Task`, `Rate`, `TimeLog` 五個類別。
3. 實作 `init_db()` 函數，若資料庫檔案不存在則自動 `create_all()`。

### 8.3 核心業務邏輯開發 (`engine.py`)
1. 實作 `add_time_log(user_id, task_id, hours)`：
   - 查詢該 `user_id` 在 `rates` 表中最新的 `hourly_rate`。
   - 計算 `total_cost = hours * hourly_rate`。
   - 寫入 `time_logs` 表。

### 8.4 使用者介面開發 (`app.py`)
1. **Login Session 管理**：利用 `st.session_state` 模擬簡易登入。
2. **多頁面邏輯**：
   - `if st.session_state.role == 'HR':` 顯示費率管理。
   - `if st.session_state.role == 'DEV':` 顯示工時填報。
3. **視覺化元件**：
   - 使用 `st.metric` 顯示預算餘額。
   - 使用 `st.bar_chart` 顯示資源負載。

### 8.5 測試與驗證
1. **功能測試**：
   - [ ] 驗證開發者是否真的看不到「費率管理」頁面。
   - [ ] 填寫工時後，檢查 SQLite 資料庫中 `applied_rate` 是否已正確填入。
   - [ ] 修改費率後，檢查舊的 `time_logs` 成本是否保持不變。
2. **報表測試**：
   - [ ] 點擊「匯出報表」，檢查 Excel 欄位是否包含預期數據。

### 8.6 部署與運行說明
```bash
# 在專案根目錄執行
streamlit run app.py
```
*訪問地址：http://localhost:8501*