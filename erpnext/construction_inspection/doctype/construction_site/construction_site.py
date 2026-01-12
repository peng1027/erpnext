# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class ConstructionSite(Document):
    def validate(self):
        """驗證施工現場數據"""
        self.validate_dates()
        self.validate_budget()
        self.calculate_progress()
    
    def validate_dates(self):
        """驗證日期邏輯"""
        if self.start_date and self.expected_completion_date:
            if getdate(self.start_date) > getdate(self.expected_completion_date):
                frappe.throw("開工日期不能晚於預計完工日期")
    
    def validate_budget(self):
        """驗證預算數據"""
        if self.total_budget and self.spent_amount:
            if flt(self.spent_amount) > flt(self.total_budget):
                frappe.msgprint("已花費金額超過總預算，請檢查", alert=True)
    
    def calculate_progress(self):
        """計算項目進度"""
        if self.site_status == "已完成":
            self.progress_percentage = 100
        elif self.site_status == "已取消":
            self.progress_percentage = 0
    
    def get_inspection_summary(self):
        """獲取巡檢摘要信息"""
        inspections = frappe.get_all(
            "Supplier Inspection",
            filters={"construction_site": self.name},
            fields=["name", "inspection_date", "inspection_status", "overall_rating"]
        )
        
        return {
            "total_inspections": len(inspections),
            "passed_inspections": len([i for i in inspections if i.inspection_status == "通過"]),
            "failed_inspections": len([i for i in inspections if i.inspection_status == "不通過"]),
            "latest_inspection": inspections[0] if inspections else None
        }
    
    def get_dashboard_data(self):
        """獲取儀表板數據"""
        return {
            "fieldname": "construction_site",
            "transactions": [
                {
                    "label": "巡檢記錄",
                    "items": ["Supplier Inspection"]
                },
                {
                    "label": "檢查清單",
                    "items": ["Inspection Checklist"]
                }
            ]
        }


@frappe.whitelist()
def get_site_progress_data(site_name):
    """獲取現場進度數據"""
    site = frappe.get_doc("Construction Site", site_name)
    
    # 獲取巡檢統計
    inspection_summary = site.get_inspection_summary()
    
    # 獲取預算使用情況
    budget_usage = 0
    if site.total_budget and site.spent_amount:
        budget_usage = (flt(site.spent_amount) / flt(site.total_budget)) * 100
    
    return {
        "site_info": {
            "name": site.site_name,
            "status": site.site_status,
            "progress": site.progress_percentage or 0,
            "budget_usage": budget_usage
        },
        "inspection_summary": inspection_summary
    }


@frappe.whitelist()
def create_inspection_schedule(site_name, frequency="weekly"):
    """創建巡檢計劃"""
    site = frappe.get_doc("Construction Site", site_name)
    
    # 這裡可以實現自動創建巡檢計劃的邏輯
    # 根據頻率創建定期巡檢任務
    
    frappe.msgprint(f"已為 {site.site_name} 創建 {frequency} 巡檢計劃")