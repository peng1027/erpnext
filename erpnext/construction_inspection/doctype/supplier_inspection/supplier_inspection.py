# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today, add_days
from frappe.model.mapper import get_mapped_doc


class SupplierInspection(Document):
    def validate(self):
        """驗證巡檢數據"""
        self.validate_dates()
        self.calculate_overall_rating()
        self.set_supplier_from_site()
    
    def validate_dates(self):
        """驗證日期邏輯"""
        if self.inspection_date and getdate(self.inspection_date) > getdate(today()):
            frappe.throw("巡檢日期不能是未來日期")
        
        if self.approval_date and self.inspection_date:
            if getdate(self.approval_date) < getdate(self.inspection_date):
                frappe.throw("審批日期不能早於巡檢日期")
    
    def set_supplier_from_site(self):
        """從施工現場自動設置供應商"""
        if self.construction_site and not self.supplier:
            site_doc = frappe.get_doc("Construction Site", self.construction_site)
            if site_doc.supplier:
                self.supplier = site_doc.supplier
    
    def calculate_overall_rating(self):
        """計算總體評分"""
        ratings = []
        
        if self.safety_compliance:
            ratings.append(flt(self.safety_compliance))
        if self.quality_rating:
            ratings.append(flt(self.quality_rating))
        if self.progress_rating:
            ratings.append(flt(self.progress_rating))
        
        if ratings:
            self.overall_rating = sum(ratings) / len(ratings)
    
    def on_submit(self):
        """提交時的操作"""
        self.update_inspection_status()
        self.create_follow_up_tasks()
        self.update_site_progress()
    
    def update_inspection_status(self):
        """更新巡檢狀態"""
        if self.overall_rating >= 4:
            self.inspection_status = "通過"
        elif self.overall_rating >= 3:
            self.inspection_status = "需要整改"
        else:
            self.inspection_status = "不通過"
    
    def create_follow_up_tasks(self):
        """創建跟進任務"""
        if self.follow_up_required and self.corrective_actions:
            # 創建任務來跟進糾正措施
            task_doc = frappe.new_doc("Task")
            task_doc.subject = f"巡檢跟進 - {self.inspection_title}"
            task_doc.description = self.corrective_actions
            task_doc.project = frappe.db.get_value("Construction Site", self.construction_site, "project")
            task_doc.exp_start_date = today()
            task_doc.exp_end_date = add_days(today(), 7)  # 7天內完成
            task_doc.priority = "High" if self.inspection_status == "不通過" else "Medium"
            task_doc.save()
            
            frappe.msgprint(f"已創建跟進任務: {task_doc.name}")
    
    def update_site_progress(self):
        """更新現場進度"""
        # 這裡可以根據巡檢結果更新施工現場的進度
        pass
    
    def get_checklist_summary(self):
        """獲取檢查清單摘要"""
        if not self.checklist_items:
            return {}
        
        total_items = len(self.checklist_items)
        passed_items = len([item for item in self.checklist_items if item.status == "通過"])
        failed_items = len([item for item in self.checklist_items if item.status == "不通過"])
        
        return {
            "total_items": total_items,
            "passed_items": passed_items,
            "failed_items": failed_items,
            "pass_rate": (passed_items / total_items * 100) if total_items > 0 else 0
        }


@frappe.whitelist()
def create_inspection_from_template(construction_site, template_name):
    """從模板創建巡檢記錄"""
    template = frappe.get_doc("Inspection Template", template_name)
    
    inspection = frappe.new_doc("Supplier Inspection")
    inspection.construction_site = construction_site
    inspection.inspection_title = f"{template.template_name} - {construction_site}"
    inspection.inspection_type = template.inspection_type
    inspection.inspection_category = template.inspection_category
    inspection.inspection_date = today()
    
    # 複製檢查清單項目
    for item in template.checklist_items:
        inspection.append("checklist_items", {
            "check_item": item.check_item,
            "description": item.description,
            "is_mandatory": item.is_mandatory,
            "weight": item.weight
        })
    
    return inspection


@frappe.whitelist()
def get_inspection_analytics(construction_site=None, supplier=None, from_date=None, to_date=None):
    """獲取巡檢分析數據"""
    filters = {}
    
    if construction_site:
        filters["construction_site"] = construction_site
    if supplier:
        filters["supplier"] = supplier
    if from_date:
        filters["inspection_date"] = [">=", from_date]
    if to_date:
        if "inspection_date" in filters:
            filters["inspection_date"] = ["between", [from_date, to_date]]
        else:
            filters["inspection_date"] = ["<=", to_date]
    
    inspections = frappe.get_all(
        "Supplier Inspection",
        filters=filters,
        fields=["name", "inspection_date", "inspection_status", "overall_rating", 
                "safety_compliance", "quality_rating", "progress_rating"]
    )
    
    # 計算統計數據
    total_inspections = len(inspections)
    passed_inspections = len([i for i in inspections if i.inspection_status == "通過"])
    failed_inspections = len([i for i in inspections if i.inspection_status == "不通過"])
    
    avg_overall_rating = sum([flt(i.overall_rating) for i in inspections]) / total_inspections if total_inspections > 0 else 0
    avg_safety_rating = sum([flt(i.safety_compliance) for i in inspections if i.safety_compliance]) / total_inspections if total_inspections > 0 else 0
    avg_quality_rating = sum([flt(i.quality_rating) for i in inspections if i.quality_rating]) / total_inspections if total_inspections > 0 else 0
    
    return {
        "summary": {
            "total_inspections": total_inspections,
            "passed_inspections": passed_inspections,
            "failed_inspections": failed_inspections,
            "pass_rate": (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
        },
        "ratings": {
            "avg_overall_rating": avg_overall_rating,
            "avg_safety_rating": avg_safety_rating,
            "avg_quality_rating": avg_quality_rating
        },
        "inspections": inspections
    }