# Vendor QC ERPNext App 增強功能規劃

## 🎯 概覽

基於對您的 Vendor QC ERPNext App 的深度分析，以下是建議的增強功能規劃，按優先級和實現複雜度分類。

---

## 🔥 高優先級增強功能

### 1. Workflow 系統 ⭐⭐⭐⭐⭐

#### 📋 功能描述
為 NCR 添加完整的工作流程管理，實現狀態自動轉換和通知機制。

#### 🎯 實現目標
```
NCR 狀態流程:
Open → Under Review → Closed/Cancelled

Quality Inspection 狀態流程:
Draft → In Process → Accepted/Rejected
```

#### 💻 技術實現
```python
# hooks.py 添加
workflows = [
    {
        "doctype": "NCR",
        "workflow_name": "NCR Workflow",
        "states": [
            {"state": "Open", "allow_edit": "Inspector"},
            {"state": "Under Review", "allow_edit": "Supplier Supervisor"},
            {"state": "Closed", "allow_edit": "System Manager"},
            {"state": "Cancelled", "allow_edit": "System Manager"}
        ],
        "transitions": [
            {
                "state": "Open",
                "action": "Submit for Review",
                "next_state": "Under Review",
                "allowed": "Inspector"
            },
            {
                "state": "Under Review", 
                "action": "Close",
                "next_state": "Closed",
                "allowed": "Supplier Supervisor"
            }
        ]
    }
]

# 通知配置
notification_config = [
    {
        "subject": "New NCR Created",
        "document_type": "NCR",
        "event": "New",
        "recipients": ["supplier_supervisor"]
    },
    {
        "subject": "NCR Overdue",
        "document_type": "NCR", 
        "event": "Days After",
        "days": 1,
        "condition": "doc.status == 'Open'"
    }
]
```

#### 📊 預期效益
- ✅ 標準化流程管理
- ✅ 自動通知機制
- ✅ 權限控制優化
- ✅ 審計追蹤完整

---

### 2. 地理圍欄驗證 🗺️⭐⭐⭐⭐

#### 📋 功能描述
實現基於 GPS 位置的簽到和提交限制，確保現場作業的真實性。

#### 🎯 實現目標
```
位置驗證功能:
✅ 距離工地 200m 內才能簽到
✅ 支援圓形和多邊形圍欄
✅ GPS 精度檢查
✅ 離線位置緩存
```

#### 💻 技術實現
```python
# vendor_qc/utils/geofence.py
import math
from geopy.distance import geodesic
import json

def validate_location(user_lat, user_lng, site_doc):
    """驗證用戶位置是否在工地圍欄內"""
    site_lat = site_doc.latitude
    site_lng = site_doc.longitude
    
    # 圓形圍欄檢查
    if site_doc.geofence_radius:
        distance = geodesic((user_lat, user_lng), (site_lat, site_lng)).meters
        if distance <= site_doc.geofence_radius:
            return True, f"距離工地 {distance:.1f}m"
    
    # 多邊形圍欄檢查
    if site_doc.polygon_json:
        polygon = json.loads(site_doc.polygon_json)
        if point_in_polygon(user_lat, user_lng, polygon):
            return True, "位於工地圍欄內"
    
    return False, f"距離工地過遠 ({distance:.1f}m > {site_doc.geofence_radius}m)"

# API 增強
@frappe.whitelist()
def create_inspection_with_location(site, supplier, remarks, latitude, longitude):
    """帶位置驗證的檢查創建"""
    site_doc = frappe.get_doc("Contractor Site", site)
    
    # 位置驗證
    is_valid, message = validate_location(latitude, longitude, site_doc)
    if not is_valid:
        frappe.throw(f"位置驗證失敗: {message}")
    
    # 創建檢查記錄
    return create_inspection(site, supplier, remarks)
```

#### 📱 前端實現
```javascript
// 獲取用戶位置
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject('瀏覽器不支援地理定位');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                });
            },
            error => reject('無法獲取位置: ' + error.message),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    });
}

// 位置驗證提交
async function submitInspectionWithLocation() {
    try {
        const location = await getCurrentLocation();
        
        if (location.accuracy > 50) {
            if (!confirm('GPS 精度較低，是否繼續提交？')) {
                return;
            }
        }
        
        const response = await frappe.call({
            method: 'vendor_qc.api.create_inspection_with_location',
            args: {
                site: selectedSite,
                supplier: supplierInput.value,
                remarks: remarksInput.value,
                latitude: location.latitude,
                longitude: location.longitude
            }
        });
        
        showSuccess('檢查記錄已創建');
    } catch (error) {
        showError('提交失敗: ' + error.message);
    }
}
```

#### 📊 預期效益
- ✅ 防止虛假簽到
- ✅ 提升數據可信度
- ✅ 符合現場管理要求
- ✅ 支援離線操作

---

### 3. 檢查清單模板化 📋⭐⭐⭐⭐

#### 📋 功能描述
從 Quality Inspection Template 自動渲染檢查項目，支援動態表單生成。

#### 🎯 實現目標
```
模板功能:
✅ 從 QI Template 讀取檢查項目
✅ 動態生成表單界面
✅ 支援多種輸入類型
✅ 自動評分計算
```

#### 💻 技術實現
```python
# vendor_qc/api.py 增強
@frappe.whitelist()
def get_inspection_template(template_name):
    """獲取檢查模板"""
    template = frappe.get_doc("Quality Inspection Template", template_name)
    
    checklist_items = []
    for item in template.quality_inspection_template_readings:
        checklist_items.append({
            "specification": item.specification,
            "value_based_on": item.value_based_on,
            "acceptance_criteria": item.acceptance_criteria,
            "numeric": item.numeric,
            "formula_based_criteria": item.formula_based_criteria,
            "min_value": item.min_value,
            "max_value": item.max_value
        })
    
    return {
        "template_name": template.quality_inspection_template,
        "description": template.description,
        "checklist_items": checklist_items
    }

@frappe.whitelist()
def create_inspection_from_template(site, supplier, template_name, checklist_results, remarks=""):
    """從模板創建檢查記錄"""
    # 創建 Quality Inspection
    qi = frappe.new_doc("Quality Inspection")
    qi.inspection_type = "Incoming"
    qi.reference_type = "Contractor Site"
    qi.reference_name = site
    qi.quality_inspection_template = template_name
    qi.supplier = supplier
    qi.remarks = remarks
    
    # 添加檢查結果
    for result in checklist_results:
        qi.append("readings", {
            "specification": result["specification"],
            "value": result["value"],
            "status": result["status"],  # Accepted/Rejected
            "reading_1": result.get("reading_1"),
            "reading_2": result.get("reading_2")
        })
    
    # 計算整體狀態
    rejected_count = sum(1 for r in checklist_results if r["status"] == "Rejected")
    qi.status = "Rejected" if rejected_count > 0 else "Accepted"
    
    qi.insert()
    qi.submit()
    
    return qi.name
```

#### 📱 前端實現
```javascript
// 動態表單生成
async function loadInspectionTemplate(templateName) {
    const response = await frappe.call({
        method: 'vendor_qc.api.get_inspection_template',
        args: { template_name: templateName }
    });
    
    const template = response.message;
    const formContainer = document.getElementById('checklist-form');
    formContainer.innerHTML = '';
    
    template.checklist_items.forEach((item, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'checklist-item';
        
        let inputHtml = '';
        if (item.numeric) {
            inputHtml = `
                <input type="number" 
                       id="item_${index}" 
                       min="${item.min_value || ''}" 
                       max="${item.max_value || ''}"
                       placeholder="輸入數值">
                <span class="criteria">範圍: ${item.min_value} - ${item.max_value}</span>
            `;
        } else {
            inputHtml = `
                <select id="item_${index}">
                    <option value="">請選擇</option>
                    <option value="Accepted">合格</option>
                    <option value="Rejected">不合格</option>
                </select>
            `;
        }
        
        itemDiv.innerHTML = `
            <div class="item-header">
                <h4>${item.specification}</h4>
                <span class="criteria">${item.acceptance_criteria}</span>
            </div>
            <div class="item-input">
                ${inputHtml}
            </div>
        `;
        
        formContainer.appendChild(itemDiv);
    });
}

// 提交檢查結果
async function submitTemplateInspection() {
    const templateName = document.getElementById('template-select').value;
    const checklistItems = document.querySelectorAll('.checklist-item');
    const results = [];
    
    checklistItems.forEach((item, index) => {
        const input = item.querySelector(`#item_${index}`);
        const specification = item.querySelector('h4').textContent;
        
        results.push({
            specification: specification,
            value: input.value,
            status: input.type === 'number' ? 
                    (validateNumericValue(input.value, item) ? 'Accepted' : 'Rejected') :
                    input.value
        });
    });
    
    const response = await frappe.call({
        method: 'vendor_qc.api.create_inspection_from_template',
        args: {
            site: selectedSite,
            supplier: supplierInput.value,
            template_name: templateName,
            checklist_results: results,
            remarks: remarksInput.value
        }
    });
    
    showSuccess('檢查記錄已創建: ' + response.message);
}
```

#### 📊 預期效益
- ✅ 標準化檢查流程
- ✅ 提升檢查效率
- ✅ 減少人為錯誤
- ✅ 支援複雜評分邏輯

---

## ⭐ 中優先級增強功能

### 4. 進階通知系統 📧

#### 功能特點
- Email 通知模板
- 系統內通知
- 移動推送 (PWA)
- 通知偏好設定

### 5. 報表與分析 📊

#### 功能特點
- NCR 統計儀表板
- 供應商績效分析
- 工地檢查趨勢
- 導出功能 (PDF/Excel)

### 6. 批量操作 🔄

#### 功能特點
- 批量創建檢查
- 批量狀態更新
- 批量導出數據
- 批量分配任務

---

## 💡 低優先級增強功能

### 7. 高級分析 📈

#### 功能特點
- 預測性分析
- 風險評估模型
- 趨勢預測
- AI 輔助決策

### 8. 第三方整合 🔗

#### 功能特點
- 外部系統 API
- 數據同步
- 雲端備份
- IoT 設備整合

---

## 🚀 實施建議

### 階段一 (1-2 週)
1. **Workflow 系統** - 核心業務流程
2. **地理圍欄驗證** - 數據可信度

### 階段二 (2-3 週)  
1. **檢查清單模板化** - 標準化作業
2. **進階通知系統** - 用戶體驗

### 階段三 (3-4 週)
1. **報表與分析** - 管理決策支持
2. **批量操作** - 效率提升

### 階段四 (長期)
1. **高級分析** - 智能化升級
2. **第三方整合** - 生態系統擴展

---

## 💻 技術實現路徑

### 1. 開發環境準備
```bash
# 安裝開發依賴
pip install geopy
pip install Pillow
pip install qrcode
```

### 2. 代碼結構擴展
```
vendor_qc/
├── utils/
│   ├── geofence.py      # 地理圍欄工具
│   ├── workflow.py      # 工作流工具
│   └── templates.py     # 模板工具
├── notifications/
│   ├── email.py         # 郵件通知
│   └── push.py          # 推送通知
└── reports/
    ├── ncr_analysis.py  # NCR 分析報表
    └── performance.py   # 績效報表
```

### 3. 數據庫擴展
```sql
-- 添加位置記錄表
CREATE TABLE `tabLocation Log` (
    `name` varchar(140) NOT NULL,
    `user` varchar(140),
    `latitude` decimal(10,8),
    `longitude` decimal(11,8),
    `accuracy` decimal(10,2),
    `timestamp` datetime,
    `site` varchar(140),
    `action` varchar(50)
);
```

---

## 📊 投資回報分析

### 開發成本估算
- **高優先級功能**: 40-60 工時
- **中優先級功能**: 60-80 工時  
- **低優先級功能**: 80-120 工時

### 預期收益
- **效率提升**: 30-50%
- **錯誤減少**: 60-80%
- **合規性**: 90%+
- **用戶滿意度**: 顯著提升

---

## 🎯 結論

您的 Vendor QC ERPNext App 已經具備了堅實的基礎，建議優先實施 **Workflow 系統**、**地理圍欄驗證** 和 **檢查清單模板化** 這三個高價值功能。

這些增強功能將顯著提升系統的實用性、可靠性和用戶體驗，使其成為一個完整的企業級建築檢查管理解決方案。

---

*增強規劃報告生成時間: 2025-11-01*  
*規劃工具: Vendor QC Enhancement Planning Suite*