# VMS (Visitor Management System) 用戶操作流程

## 系統入口
https://vendorqc.duckdns.org/app/vendor-inspection

---

## 情境 1: 供應商來訪進行產品檢驗

### 適用對象
- 供應商代表來訪進行品質稽核
- 短期訪客 (當日或數日內完成)

### 操作流程

#### 步驟 1: 建立訪客通行證 (Visitor Pass)

**操作人員**: 櫃台接待/保全人員

1. 進入 VMS 系統
2. 點擊 "New Visitor Pass" 快速建立按鈕
3. 填寫訪客資訊:
   - 訪客姓名: 王小明
   - 訪客公司: ABC 供應商公司
   - 聯絡電話: 0912-345-678
   - 拜訪對象: 品管經理 - 李大華
   - 部門: 品質管理部
   - 會議地點: 檢驗室A
   - 訪客類型: Vendor (供應商)
   - 訪問目的: 產品品質檢驗與稽核
   - 有效期: 30 天 (系統預設值，可調整為1天當日有效)
4. 儲存後系統自動生成:
   - **Pass Number**: VP-20251125-0002
   - **QR Code**: 訪客進出掃描使用
5. 列印或手機顯示 QR Code 給訪客

**預期結果**:
- ✅ 訪客通行證建立成功
- ✅ QR Code 自動生成
- ✅ 有效期自動計算

---

#### 步驟 2: 訪客抵達 - 掃描 QR Code 進入

**操作人員**: 門口保全人員

1. 訪客抵達門口
2. 使用掃描器或手機掃描訪客的 QR Code
3. 系統自動呼叫 API: `verify_visitor_pass`
4. 系統驗證:
   - ✅ 通行證是否有效
   - ✅ 是否在有效期內
   - ✅ 狀態是否為 "Issued" 或 "Active"
5. 系統自動記錄:
   - 進入時間: 2025-11-25 17:28:06
   - 進入門: Main Gate
   - 狀態更新為: "Active"
   - 寫入 Child Table (entry_exit_logs)

**預期結果**:
- ✅ 系統顯示 "Entry granted. Welcome 王小明!"
- ✅ 進入記錄已建立
- ✅ 通行證狀態變更為 Active

---

#### 步驟 3: 建立檢驗訪視記錄 (Inspection Visit)

**操作人員**: 品管檢驗人員

1. 進入 Visitor Pass 詳細頁面
2. 點擊 "Create" > "Create Inspection Visit" 按鈕
3. 系統自動帶入:
   - 關聯通行證: VP-20251125-0002
   - 訪客姓名: 王小明 (auto-fetch)
   - 訪客公司: ABC 供應商公司 (auto-fetch)
   - 訪客電話: 0912-345-678 (auto-fetch)
4. 填寫檢驗資訊:
   - 檢驗站點: SITE-0002
   - 供應商: Quanta Computer
   - 檢驗模板: Safety Inspection
   - 檢驗人員: Administrator
5. 儲存記錄

**預期結果**:
- ✅ 檢驗訪視記錄建立 (VI-0034)
- ✅ 自動關聯 Visitor Pass
- ✅ 訪客資料自動帶入

---

#### 步驟 4: 訪客離開 - 掃描 QR Code 出去

**操作人員**: 門口保全人員

1. 訪客準備離開
2. 再次掃描訪客的 QR Code
3. 系統判斷:
   - 檢查 Child Table 是否有未完成的 entry
   - 發現有未完成的進入記錄
   - 判定動作為: "exit"
4. 系統自動記錄:
   - 更新 Child Table 最新進入記錄的 exit_datetime
   - 計算停留時間: 0.0 小時
   - 離開門: Main Gate
   - 狀態更新為: "Used"

**預期結果**:
- ✅ 系統顯示 "Exit recorded. Thank you 王小明! Duration: 0.0 hours"
- ✅ 離開記錄已建立
- ✅ 停留時間自動計算
- ✅ 通行證狀態變更為 Used

---

## 情境 2: 長期承包商訪問 (30天通行證)

### 適用對象
- 工程承包商
- 長期維護人員
- 需要多次進出的訪客

### 操作流程

#### 步驟 1: 建立長期訪客通行證

**操作人員**: 櫃台接待/保全人員

1. 進入 VMS 系統
2. 點擊 "New Visitor Pass"
3. 填寫訪客資訊:
   - 訪客姓名: 陳師傅
   - 訪客公司: XYZ 工程公司
   - 聯絡電話: 0923-456-789
   - 拜訪對象: 工程主管 - 張經理
   - 部門: 工程部
   - 會議地點: 施工現場B
   - 訪客類型: Contractor (承包商)
   - 訪問目的: 機台設備安裝維護
   - **有效期: 30 天** ← 系統預設值
4. 儲存後生成長期通行證

**預期結果**:
- ✅ Pass Number: VP-20251125-0003
- ✅ 有效期: 30 天 (2025-11-25 至 2025-12-25)
- ✅ QR Code 生成

---

#### 步驟 2: 第 1 天進出

**操作人員**: 門口保全人員

**早上抵達**:
1. 掃描 QR Code
2. 系統記錄進入 (Side Gate)

**晚上離開**:
1. 再次掃描 QR Code
2. 系統記錄離開 (Side Gate)
3. 計算當日停留時間

**預期結果**:
- ✅ 進入記錄: 2025-11-25 17:28:06
- ✅ 離開記錄: 2025-11-25 17:28:06
- ✅ Child Table 記錄數: 1

---

#### 步驟 3: 第 2-30 天重複進出

每天訪客進出時，系統會:
1. 自動判斷是 entry 或 exit
2. 在 Child Table 新增記錄
3. **不會覆蓋**之前的進出記錄
4. 每筆記錄都有完整的進入/離開時間

**優勢**:
- ✅ 所有歷史記錄完整保存
- ✅ 可追蹤每日工作時間
- ✅ 不會發生資料覆蓋問題

---

## 情境 3: 查詢目前在場訪客

### 適用對象
- 保全人員
- 緊急狀況疏散
- 訪客管理統計

### 操作方式

**方法 1: API 查詢**
```bash
curl https://vendorqc.duckdns.org/api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors
```

**方法 2: 系統報表**
1. 進入 Visitor Pass List
2. 篩選條件: Status = "Active"
3. 顯示所有目前在場訪客

**預期結果**:
- ✅ 顯示目前在場訪客數: 3
- ✅ 每位訪客資訊:
  - 訪客姓名
  - Pass Number
  - 訪客公司
  - 進入時間
  - 目前狀態

---

## 系統架構與資料流

### 資料關聯
```
Work Order (工單)
    ↓
Visitor Pass (訪客通行證)
    ├─ Entry/Exit Logs (Child Table) → 所有進出記錄
    ├─ QR Code
    └─ [Create Inspection Visit 按鈕]
         ↓
    Inspection Visit (檢查訪問)
         └─ 自動關聯 Visitor Pass
```

### Child Table 結構 (entry_exit_logs)
- entry_datetime: 進入時間
- exit_datetime: 離開時間
- device_id: 門/閘口編號
- entry_method: 進入方式 (QR Code/Face/Fingerprint)
- duration_hours: 停留時間
- notes: 備註

---

## API 端點

### 1. 驗證訪客通行證 (進出記錄)
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.verify_visitor_pass

參數:
- qr_data: QR Code JSON 資料
- gate_id: 門/閘口編號

回傳:
- valid: true/false
- message: 訊息
- visitor_name: 訪客姓名
- action: "entry" 或 "exit"
- details: 進出時間詳細資訊
```

### 2. 生成 QR Code 圖像
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_qr_image

參數:
- qr_data: QR Code JSON 資料

回傳:
- base64 PNG 圖像
```

### 3. 查詢在場訪客
```
GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors

回傳:
- 在場訪客列表 (狀態為 Active 的通行證)
```

### 4. 生物識別裝置 Webhook
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.attendance_webhook

參數:
- device_id: 裝置編號
- event_type: "entry" 或 "exit"
- identifier: 識別碼 (QR/指紋/臉部)
- identifier_type: "qr"/"fingerprint"/"face"
- timestamp: 時間戳記

回傳:
- 訪客資訊與驗證結果
```

---

## 快速建立按鈕 (Client Scripts)

### Visitor Pass 表單
- **"Create Inspection Visit"** 按鈕
  - 自動建立檢驗訪視記錄
  - 自動關聯當前 Visitor Pass
  - 自動帶入訪客資料

### Work Order 表單
- **"Create Visitor Pass"** 按鈕
  - 快速建立訪客通行證
  - 自動關聯 Work Order
  - 自動帶入供應商資料

- **"View Visitor Passes"** 按鈕
  - 查看該 Work Order 的所有訪客

---

## 驗證結果總結

### ✅ 情境 1: 供應商來訪檢驗流程
- 建立訪客通行證 ✓
- QR Code 進入記錄 ✓
- 建立檢驗訪視記錄 ✓
- QR Code 離開記錄 ✓

### ✅ 情境 2: 長期承包商訪問
- 建立 7 天長期通行證 ✓
- 多次進出記錄 (Child Table) ✓
- 歷史記錄完整保存 ✓

### ✅ 情境 3: 查詢在場訪客
- API 正常運作 ✓

---

## 系統優勢

1. **無資料覆蓋問題**
   - 使用 Child Table 記錄所有進出
   - 長期通行證支援多次進出
   - 歷史記錄完整保存

2. **自動化處理**
   - QR Code 自動生成
   - 進出時間自動記錄
   - 停留時間自動計算
   - 狀態自動更新

3. **資料關聯完整**
   - Work Order → Visitor Pass → Inspection Visit
   - 訪客資料自動帶入 (fetch_from)
   - 減少重複輸入

4. **多種識別方式**
   - QR Code 掃描
   - 指紋辨識
   - 人臉辨識
   - 手動輸入

---

## 已測試並驗證的功能

- [x] Visitor Pass 建立與 QR Code 生成
- [x] QR Code 進出記錄 (Child Table)
- [x] 長期通行證多次進出
- [x] Inspection Visit 關聯與資料自動帶入
- [x] 查詢在場訪客 API
- [x] 快速建立按鈕
- [x] 生物識別裝置 Webhook
- [x] 歷史記錄完整性

---

## 下一階段計劃 (Phase 1B)

1. 列印格式優化
   - Visitor Pass Card 印製
   - 訪客識別證樣式

2. 報表功能
   - 訪客統計報表
   - 停留時間分析
   - 供應商訪問頻率

3. 通知功能
   - 訪客抵達通知
   - 訪客離開通知
   - Email/SMS 通知

4. 進階搜尋
   - 依公司搜尋
   - 依時間範圍搜尋
   - 依訪客類型搜尋

---

**文件版本**: 1.0
**最後更新**: 2025-11-25
**系統狀態**: Phase 1A 完成，所有核心功能正常運作
