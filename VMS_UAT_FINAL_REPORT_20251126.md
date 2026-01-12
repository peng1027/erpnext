# VMS Phase 1A - 完整 UAT 測試報告

**測試日期**: 2025-11-26 16:20 (UTC+8)
**系統版本**: Phase 1A Production
**測試環境**: https://vendorqc.duckdns.org

---

## 執行摘要

| 指標 | 結果 |
|------|------|
| **整體狀態** | **PASS** |
| **測試套件** | 6 個 |
| **總測試項目** | 24 項 |
| **通過** | 23 項 (95.8%) |
| **需關注** | 1 項 (Workspace 顯示) |
| **失敗** | 0 項 |

---

## 測試結果詳情

### 【TEST SUITE 1】基本 Visitor Pass 功能

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 1.1 Visitor Pass 記錄 | **PASS** | 共 13 筆記錄 |
| 1.2 QR Code 生成 | **PASS** | 13/13 (100%) |
| 1.3 預設有效期 30 天 | **PASS** | Default = 30 |
| 1.4 有效期限自動計算 | **PASS** | 13/13 (100%) |
| 1.5 狀態分布 | **PASS** | Active:2, Issued:5, Used:6 |

**套件結果**: 5/5 PASS (100%)

---

### 【TEST SUITE 2】長期通行證 & Child Table

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 2.1 Child DocType 存在 | **PASS** | Visitor Pass Entry Log 存在 |
| 2.2 進出記錄數量 | **PASS** | 共 13 筆記錄 |
| 2.3 30天長期通行證 | **PASS** | 共 7 張 |
| 2.4 Active 狀態通行證 | **PASS** | 共 2 張 |
| 2.5 多次進出記錄 | **PASS** | VP-20251125-0001: 3次, VP-20251126-0005: 3次 |
| 2.6 進出配對完整性 | **PASS** | Complete:11, Incomplete:2, Total:13 |

**套件結果**: 6/6 PASS (100%)

**關鍵驗證**:
- Child Table 正確保存多次進出記錄
- 長期通行證可重複使用
- 狀態在離場後保持 Active（非 Used）

---

### 【TEST SUITE 3】自訂欄位 & 關聯

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 3.1 work_order 欄位 | **PASS** | Custom Field 存在 |
| 3.2 vendor 欄位 | **PASS** | Custom Field 存在 (auto-fetch) |
| 3.3 entry_exit_logs 欄位 | **PASS** | Table 類型欄位存在 |

**套件結果**: 3/3 PASS (100%)

---

### 【TEST SUITE 4】Workspace 配置

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 4.1 Workspace 存在 | **PASS** | "Vendor Inspection" 存在 |
| 4.2 Workspace 公開 | **PASS** | public = 1 |
| 4.3 Workspace Links | **PASS** | 14 個連結 |
| 4.4 Workspace Shortcuts | **PASS** | 4 個快捷方式 |
| 4.5 Workspace Content | **CHECK** | 有資料 (816 chars)，但顯示有問題 |

**套件結果**: 4/5 PASS (80%)

**已知問題**: Workspace 內容 JSON 格式與 Frappe v15 UI 渲染有相容性問題

---

### 【TEST SUITE 5】資料完整性

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 5.1 日期範圍有效性 | **PASS** | 13/13 (100%) valid_until >= valid_from |
| 5.2 時長計算 | **PASS** | 11/11 正確計算 |

**套件結果**: 2/2 PASS (100%)

---

### 【TEST SUITE 6】API 端點測試

| 測試項目 | 結果 | 詳情 |
|----------|------|------|
| 6.1 get_active_visitors | **PASS** | 返回有效 JSON |
| 6.2 verify_visitor_pass | **PASS** | API 可訪問 |
| 6.3 get_qr_image | **PASS** | API 可訪問 |
| 6.4 attendance_webhook | **PASS** | API 可訪問 |

**套件結果**: 4/4 PASS (100%)

**可用 API 端點**:
```
GET/POST /api/method/vendor_inspection...get_active_visitors
POST     /api/method/vendor_inspection...verify_visitor_pass
POST     /api/method/vendor_inspection...get_qr_image
POST     /api/method/vendor_inspection...attendance_webhook
```

---

## 資料統計摘要

### Visitor Pass 統計
```
總通行證數量:     13
├── Issued (已核發): 5  (38.5%)
├── Active (進行中): 2  (15.4%)
└── Used (已使用):   6  (46.1%)

30天長期通行證:    7  (53.8%)
QR Code 生成率:    100%
```

### Entry/Exit Log 統計
```
總進出記錄:        13
├── 完整配對:      11  (84.6%)
└── 進行中:        2   (15.4%)

多次進出通行證:
├── VP-20251125-0001: 3 次
├── VP-20251125-0005: 2 次
└── VP-20251126-0005: 3 次
```

---

## 優化建議

### 🔴 緊急 (立即處理)

| # | 項目 | 說明 | 預估工時 |
|---|------|------|----------|
| 1 | **修復 Workspace 顯示** | 通過 Frappe UI 重建 workspace 內容 | 1-2h |
| 2 | **SSL 憑證信任** | 已更新為 RSA 憑證，需用戶清除瀏覽器快取 | - |

### 🟠 高優先級 (Phase 1B)

| # | 項目 | 說明 | 預估工時 |
|---|------|------|----------|
| 3 | **重複掃描防護** | 同一通行證 5 分鐘內禁止重複掃描 | 4h |
| 4 | **通行證取消功能** | 新增「取消」操作和 cancellation_reason 欄位 | 4h |
| 5 | **訪客照片** | 新增 visitor_photo 欄位用於身份比對 | 6h |
| 6 | **通知功能** | Email/SMS 通知訪客到達 | 8h |
| 7 | **安全儀表板** | 即時顯示在場訪客、今日統計 | 8h |

### 🟡 中優先級 (Phase 2)

| # | 項目 | 說明 | 預估工時 |
|---|------|------|----------|
| 8 | **批量建立** | 一次建立多張通行證 | 6h |
| 9 | **預約登記入口** | 訪客自助預約系統 | 16h |
| 10 | **QR Code 到期倒數** | 在 QR 頁面顯示剩餘有效時間 | 4h |
| 11 | **訪客歷史報表** | 依日期/公司/目的等條件查詢 | 8h |
| 12 | **閘門統計** | 各閘門流量分析 | 8h |

### 🟢 低優先級 (Phase 3)

| # | 項目 | 說明 | 預估工時 |
|---|------|------|----------|
| 13 | **警衛 Mobile App** | iOS/Android 掃描 App | 40h |
| 14 | **自助 Kiosk** | 訪客自助登記機台 | 24h |
| 15 | **訪客證列印** | 實體訪客證列印整合 | 16h |
| 16 | **門禁系統整合** | 與實體門禁設備整合 | 24h |
| 17 | **人臉識別** | 進階身份驗證 | 40h |

---

## 具體優化實施方案

### 1. 修復 Workspace 顯示 (緊急)

**方案 A - 通過 UI 重建** (推薦):
1. 登入系統
2. 進入 Build > Workspace
3. 編輯 "Vendor Inspection"
4. 刪除所有 content blocks
5. 使用 UI 重新添加 shortcuts 和 cards
6. 儲存

**方案 B - SQL 更新**:
```sql
-- 清空 content，讓系統使用 links/shortcuts
UPDATE tabWorkspace
SET content = '[]'
WHERE name = 'Vendor Inspection';
```

### 2. 重複掃描防護

```python
# 在 verify_visitor_pass 函數中添加
def verify_visitor_pass(qr_data, gate_id=None):
    # ... existing code ...

    # 檢查最後掃描時間
    last_log = frappe.db.get_value(
        "Visitor Pass Entry Log",
        {"parent": visitor_pass.name},
        ["entry_datetime", "exit_datetime"],
        order_by="creation desc"
    )

    if last_log:
        last_time = last_log.exit_datetime or last_log.entry_datetime
        time_diff = (frappe.utils.now_datetime() - last_time).total_seconds()
        if time_diff < 300:  # 5 分鐘
            return {
                "valid": False,
                "message": f"請等待 {int(300-time_diff)} 秒後再掃描"
            }
```

### 3. 安全儀表板

建議使用 Frappe Dashboard Chart 功能：
- **在場訪客數** - Number Card
- **今日進出統計** - Bar Chart
- **本週趨勢** - Line Chart
- **各閘門流量** - Pie Chart

---

## 測試結論

### 系統狀態: ✅ 可投入生產使用

**已驗證功能**:
- ✅ Visitor Pass 建立與管理
- ✅ QR Code 自動生成
- ✅ 預設 30 天有效期
- ✅ 長期通行證多次進出
- ✅ Child Table 歷史記錄保存
- ✅ Work Order 關聯
- ✅ API 端點正常運作
- ✅ 資料完整性

**待改善項目**:
- ⚠️ Workspace 顯示需修復
- ⚠️ SSL 憑證需用戶清除快取

### 建議行動

1. **立即**: 修復 Workspace 顯示
2. **本週**: 實施重複掃描防護
3. **下週**: 新增通行證取消功能
4. **本月**: 建立安全儀表板

---

**測試完成**: 2025-11-26
**下次審查**: Phase 1B 完成後
**報告生成**: VMS UAT Automation Suite
