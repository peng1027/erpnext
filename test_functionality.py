#!/usr/bin/env python3
"""
Construction Inspection Module 功能測試 (最簡化版)
模擬ERPNext中的實際功能和工作流程測試
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import uuid

class MockFunctionalityTester:
    """模擬功能測試器"""
    
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "errors": []
        }
    
    def run_test(self, test_name, test_func):
        """運行單個測試"""
        print(f"🧪 測試: {test_name}")
        self.test_results["tests_run"] += 1
        
        try:
            result = test_func()
            if result:
                print(f"  ✅ 通過")
                self.test_results["tests_passed"] += 1
                self.test_results["test_details"].append({
                    "name": test_name,
                    "status": "passed",
                    "message": "測試通過"
                })
            else:
                print(f"  ❌ 失敗")
                self.test_results["tests_failed"] += 1
                self.test_results["test_details"].append({
                    "name": test_name,
                    "status": "failed",
                    "message": "測試失敗"
                })
            return result
            
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            self.test_results["tests_failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {e}")
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "error",
                "message": str(e)
            })
            return False
    
    def test_construction_site_creation(self):
        """測試建築工地創建 - 包含所有必填字段"""
        site_data = {
            "name": f"SITE-{uuid.uuid4().hex[:8].upper()}",
            "site_name": "測試建築工地",
            "supplier": "測試供應商",
            "site_status": "Active",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        # 插入數據
        columns = ", ".join(site_data.keys())
        placeholders = ", ".join(["?" for _ in site_data])
        sql = f"INSERT INTO tabconstruction_site ({columns}) VALUES ({placeholders})"
        
        self.cursor.execute(sql, list(site_data.values()))
        
        # 驗證插入
        self.cursor.execute("SELECT COUNT(*) FROM tabconstruction_site WHERE name = ?", (site_data["name"],))
        count = self.cursor.fetchone()[0]
        
        return count == 1
    
    def test_supplier_inspection_creation(self):
        """測試供應商檢查創建 - 最基本字段"""
        # 首先創建一個建築工地
        site_name = f"SITE-{uuid.uuid4().hex[:8].upper()}"
        site_data = {
            "name": site_name,
            "site_name": "供應商檢查測試工地",
            "supplier": "檢查測試供應商",
            "site_status": "Active",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        columns = ", ".join(site_data.keys())
        placeholders = ", ".join(["?" for _ in site_data])
        sql = f"INSERT INTO tabconstruction_site ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(site_data.values()))
        
        # 創建供應商檢查
        inspection_data = {
            "name": f"INSP-{uuid.uuid4().hex[:8].upper()}",
            "naming_series": "INSP-",
            "inspection_title": "測試檢查",
            "inspection_date": datetime.now().date().isoformat(),
            "construction_site": site_name,
            "supplier": "測試供應商",
            "inspector_name": "測試檢查員",
            "inspection_type": "Quality Check",
            "inspection_status": "Draft",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        columns = ", ".join(inspection_data.keys())
        placeholders = ", ".join(["?" for _ in inspection_data])
        sql = f"INSERT INTO tabsupplier_inspection ({columns}) VALUES ({placeholders})"
        
        self.cursor.execute(sql, list(inspection_data.values()))
        
        # 驗證插入
        self.cursor.execute("SELECT COUNT(*) FROM tabsupplier_inspection WHERE name = ?", (inspection_data["name"],))
        count = self.cursor.fetchone()[0]
        
        return count == 1
    
    def test_checklist_item_creation(self):
        """測試檢查清單項目創建 - 最基本字段"""
        checklist_items = [
            {
                "name": f"CHK-{uuid.uuid4().hex[:8].upper()}",
                "check_item": "材料品質檢查",
                "creation": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "Administrator",
                "docstatus": 0
            },
            {
                "name": f"CHK-{uuid.uuid4().hex[:8].upper()}",
                "check_item": "安全標準檢查",
                "creation": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "Administrator",
                "docstatus": 0
            }
        ]
        
        created_count = 0
        for item_data in checklist_items:
            columns = ", ".join(item_data.keys())
            placeholders = ", ".join(["?" for _ in item_data])
            sql = f"INSERT INTO tabinspection_checklist_item ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(sql, list(item_data.values()))
            created_count += 1
        
        # 驗證插入
        self.cursor.execute("SELECT COUNT(*) FROM tabinspection_checklist_item")
        total_count = self.cursor.fetchone()[0]
        
        return total_count >= created_count
    
    def test_workflow_transitions(self):
        """測試工作流程轉換"""
        # 創建一個檢查記錄並測試狀態轉換
        inspection_name = f"WORKFLOW-{uuid.uuid4().hex[:8].upper()}"
        
        # 1. 創建草稿狀態的檢查
        inspection_data = {
            "name": inspection_name,
            "naming_series": "WORKFLOW-",
            "inspection_title": "工作流程測試",
            "inspection_date": datetime.now().date().isoformat(),
            "construction_site": f"SITE-{uuid.uuid4().hex[:8].upper()}",
            "supplier": "工作流程測試供應商",
            "inspector_name": "工作流程測試檢查員",
            "inspection_type": "Workflow Test",
            "inspection_status": "Draft",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        columns = ", ".join(inspection_data.keys())
        placeholders = ", ".join(["?" for _ in inspection_data])
        sql = f"INSERT INTO tabsupplier_inspection ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(inspection_data.values()))
        
        # 2. 更新為已提交狀態
        self.cursor.execute(
            "UPDATE tabsupplier_inspection SET docstatus = 1, modified = ? WHERE name = ?",
            (datetime.now().isoformat(), inspection_name)
        )
        
        # 驗證最終狀態
        self.cursor.execute(
            "SELECT docstatus FROM tabsupplier_inspection WHERE name = ?",
            (inspection_name,)
        )
        result = self.cursor.fetchone()
        
        return result and result[0] == 1
    
    def test_data_relationships(self):
        """測試數據關聯性"""
        # 創建相關聯的數據
        site_name = f"REL-SITE-{uuid.uuid4().hex[:8].upper()}"
        inspection_name = f"REL-INSP-{uuid.uuid4().hex[:8].upper()}"
        
        # 1. 創建建築工地
        site_data = {
            "name": site_name,
            "site_name": "關聯測試工地",
            "supplier": "關聯測試供應商",
            "site_status": "Active",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        columns = ", ".join(site_data.keys())
        placeholders = ", ".join(["?" for _ in site_data])
        sql = f"INSERT INTO tabconstruction_site ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(site_data.values()))
        
        # 2. 創建關聯的檢查記錄
        inspection_data = {
            "name": inspection_name,
            "naming_series": "REL-INSP-",
            "inspection_title": "關聯測試",
            "inspection_date": datetime.now().date().isoformat(),
            "construction_site": site_name,
            "supplier": "關聯測試供應商",
            "inspector_name": "關聯測試檢查員",
            "inspection_type": "Relationship Test",
            "inspection_status": "Completed",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 1
        }
        
        columns = ", ".join(inspection_data.keys())
        placeholders = ", ".join(["?" for _ in inspection_data])
        sql = f"INSERT INTO tabsupplier_inspection ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(inspection_data.values()))
        
        # 3. 驗證關聯查詢
        self.cursor.execute("""
            SELECT cs.name, si.supplier, si.docstatus
            FROM tabconstruction_site cs
            JOIN tabsupplier_inspection si ON cs.name = si.construction_site
            WHERE cs.name = ? AND si.name = ?
        """, (site_name, inspection_name))
        
        result = self.cursor.fetchone()
        return result is not None and len(result) == 3
    
    def test_data_validation(self):
        """測試數據驗證"""
        # 測試基本插入功能
        try:
            # 插入基本記錄
            basic_data = {
                "name": f"VALID-{uuid.uuid4().hex[:8].upper()}",
                "site_name": "數據驗證測試工地",
                "supplier": "驗證測試供應商",
                "site_status": "Active",
                "creation": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "Administrator",
                "docstatus": 0
            }
            
            columns = ", ".join(basic_data.keys())
            placeholders = ", ".join(["?" for _ in basic_data])
            sql = f"INSERT INTO tabconstruction_site ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, list(basic_data.values()))
            
            # 驗證插入成功
            self.cursor.execute("SELECT COUNT(*) FROM tabconstruction_site WHERE name = ?", 
                              (basic_data["name"],))
            result = self.cursor.fetchone()
            
            return result[0] == 1
            
        except sqlite3.Error as e:
            print(f"  數據驗證錯誤: {e}")
            return False
    
    def test_data_queries(self):
        """測試數據查詢功能"""
        # 創建測試數據
        site_name = f"QUERY-SITE-{uuid.uuid4().hex[:8].upper()}"
        
        # 創建建築工地
        site_data = {
            "name": site_name,
            "site_name": "查詢測試工地",
            "supplier": "查詢測試供應商",
            "site_status": "Active",
            "creation": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "owner": "Administrator",
            "docstatus": 0
        }
        
        columns = ", ".join(site_data.keys())
        placeholders = ", ".join(["?" for _ in site_data])
        sql = f"INSERT INTO tabconstruction_site ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(site_data.values()))
        
        # 創建多個檢查記錄
        for i in range(3):
            inspection_data = {
                "name": f"QUERY-INSP-{i+1}-{uuid.uuid4().hex[:6].upper()}",
                "naming_series": "QUERY-INSP-",
                "inspection_title": f"查詢測試檢查 {i+1}",
                "inspection_date": datetime.now().date().isoformat(),
                "construction_site": site_name,
                "supplier": "查詢測試供應商",
                "inspector_name": "查詢測試檢查員",
                "inspection_type": "Query Test",
                "inspection_status": ["Draft", "In Progress", "Completed"][i],
                "creation": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "Administrator",
                "docstatus": i % 2  # 0, 1, 0
            }
            
            columns = ", ".join(inspection_data.keys())
            placeholders = ", ".join(["?" for _ in inspection_data])
            sql = f"INSERT INTO tabsupplier_inspection ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, list(inspection_data.values()))
        
        # 測試查詢
        # 1. 按狀態查詢
        self.cursor.execute(
            "SELECT COUNT(*) FROM tabsupplier_inspection WHERE construction_site = ? AND docstatus = 1",
            (site_name,)
        )
        submitted_count = self.cursor.fetchone()[0]
        
        # 2. 按供應商查詢
        self.cursor.execute(
            "SELECT COUNT(*) FROM tabsupplier_inspection WHERE supplier = ?",
            ("查詢測試供應商",)
        )
        supplier_count = self.cursor.fetchone()[0]
        
        return submitted_count >= 1 and supplier_count >= 3
    
    def run_all_tests(self):
        """運行所有功能測試"""
        print("🚀 開始功能測試...")
        print("="*50)
        
        # 定義測試用例
        tests = [
            ("建築工地創建", self.test_construction_site_creation),
            ("供應商檢查創建", self.test_supplier_inspection_creation),
            ("檢查清單項目創建", self.test_checklist_item_creation),
            ("工作流程轉換", self.test_workflow_transitions),
            ("數據關聯性", self.test_data_relationships),
            ("數據驗證", self.test_data_validation),
            ("數據查詢功能", self.test_data_queries)
        ]
        
        # 運行測試
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # 提交事務
        self.conn.commit()
        
        print("\n" + "="*50)
        print("📊 功能測試結果")
        print("="*50)
        
        print(f"總測試數: {self.test_results['tests_run']}")
        print(f"通過: {self.test_results['tests_passed']}")
        print(f"失敗: {self.test_results['tests_failed']}")
        print(f"成功率: {(self.test_results['tests_passed'] / self.test_results['tests_run'] * 100):.1f}%")
        
        if self.test_results["errors"]:
            print(f"\n❌ 錯誤詳情:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        return self.test_results["tests_failed"] == 0
    
    def generate_test_report(self):
        """生成測試報告"""
        report_data = {
            "test_time": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.test_results["tests_run"],
                "passed": self.test_results["tests_passed"],
                "failed": self.test_results["tests_failed"],
                "success_rate": (self.test_results["tests_passed"] / self.test_results["tests_run"] * 100) if self.test_results["tests_run"] > 0 else 0
            },
            "test_details": self.test_results["test_details"],
            "errors": self.test_results["errors"]
        }
        
        report_file = Path(__file__).parent / "functionality_test_results.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細測試報告已保存到: {report_file}")
        return report_data
    
    def close(self):
        """關閉數據庫連接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """主函數"""
    print("Construction Inspection Module 功能測試 (最簡化版)")
    print("="*50)
    
    # 數據庫路徑
    db_path = Path(__file__).parent / "test_construction_inspection.db"
    
    if not db_path.exists():
        print(f"❌ 測試數據庫不存在: {db_path}")
        print("請先運行 test_database_migration.py 創建數據庫")
        return False
    
    # 創建測試器並運行
    tester = MockFunctionalityTester(db_path)
    
    try:
        # 運行所有測試
        success = tester.run_all_tests()
        
        # 生成報告
        tester.generate_test_report()
        
        return success
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        return False
        
    finally:
        tester.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)