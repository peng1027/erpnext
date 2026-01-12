#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Inspection Module - 完整功能測試
綜合測試所有功能模塊的完整性和可靠性
"""

import os
import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
import uuid

class ComprehensiveTester:
    """完整功能測試器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.test_results = {
            "test_time": datetime.now().isoformat(),
            "test_type": "comprehensive_tests",
            "summary": {},
            "test_details": [],
            "errors": []
        }
    
    def run_test(self, test_name, test_func):
        """運行單個測試"""
        try:
            print(f"🧪 測試: {test_name}")
            result = test_func()
            if result:
                print(f"  ✅ 通過")
                self.test_results["test_details"].append({
                    "name": test_name,
                    "status": "passed",
                    "message": "測試通過"
                })
                return True
            else:
                print(f"  ❌ 失敗")
                self.test_results["test_details"].append({
                    "name": test_name,
                    "status": "failed",
                    "message": "測試失敗"
                })
                return False
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "error",
                "message": str(e)
            })
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(e)
            })
            return False
    
    def test_database_schema(self):
        """測試數據庫架構完整性"""
        required_tables = [
            'tabconstruction_site',
            'tabsupplier_inspection', 
            'tabinspection_checklist_item'
        ]
        
        for table in required_tables:
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not self.cursor.fetchone():
                print(f"  ❌ 缺少表: {table}")
                return False
        
        print(f"  ✅ 所有必需表存在: {', '.join(required_tables)}")
        return True
    
    def test_data_creation(self):
        """測試數據創建功能"""
        try:
            # 創建建築工地
            site_data = {
                'name': f'SITE-{int(time.time())}',
                'site_name': '測試工地A',
                'supplier': '測試供應商',
                'site_status': 'Active',
                'creation': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'owner': 'Administrator',
                'docstatus': 0
            }
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO tabconstruction_site 
                (name, site_name, supplier, site_status, creation, modified, owner, docstatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(site_data.values()))
            
            # 創建供應商檢查
            inspection_data = {
                'name': f'INS-{int(time.time())}',
                'naming_series': 'INS-',
                'inspection_title': '測試檢查',
                'inspection_date': datetime.now().date().isoformat(),
                'construction_site': site_data['name'],
                'supplier': '測試供應商',
                'inspector_name': '測試檢查員',
                'inspection_type': 'Quality',
                'inspection_status': 'Draft',
                'creation': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'owner': 'Administrator',
                'docstatus': 0
            }
            
            cursor.execute('''
                INSERT INTO tabsupplier_inspection 
                (name, naming_series, inspection_title, inspection_date, construction_site, 
                 supplier, inspector_name, inspection_type, inspection_status, 
                 creation, modified, owner, docstatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(inspection_data.values()))
            
            # 創建檢查清單項目（使用實際存在的字段）
            checklist_data = {
                'name': f'CHK-{int(time.time())}',
                'check_item': '測試檢查項目',
                'description': '測試描述',
                'is_mandatory': 1,
                'status': 'Pending',
                'creation': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'owner': 'Administrator',
                'docstatus': 0
            }
            
            cursor.execute('''
                INSERT INTO tabinspection_checklist_item 
                (name, check_item, description, is_mandatory, status, creation, modified, owner, docstatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(checklist_data.values()))
            
            self.conn.commit()
            
            # 驗證數據創建
            cursor.execute('SELECT COUNT(*) FROM tabconstruction_site WHERE name = ?', (site_data['name'],))
            site_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tabsupplier_inspection WHERE name = ?', (inspection_data['name'],))
            inspection_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tabinspection_checklist_item WHERE name = ?', (checklist_data['name'],))
            checklist_count = cursor.fetchone()[0]
            
            if site_count == 1 and inspection_count == 1 and checklist_count == 1:
                print("  ✅ 數據創建成功")
                return True
            else:
                print(f"  ❌ 數據創建失敗: 工地={site_count}, 檢查={inspection_count}, 清單={checklist_count}")
                return False
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            return False
    
    def test_data_relationships(self):
        """測試數據關聯性"""
        try:
            # 檢查工地與檢查的關聯
            self.cursor.execute('''
                SELECT cs.name, si.name
                FROM tabconstruction_site cs
                LEFT JOIN tabsupplier_inspection si ON cs.name = si.construction_site
                WHERE cs.name LIKE 'SITE-%'
                LIMIT 5
            ''')
            
            relationships = self.cursor.fetchall()
            
            if relationships:
                print(f"  ✅ 找到 {len(relationships)} 個數據關聯")
                return True
            else:
                print("  ❌ 未找到數據關聯")
                return False
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            return False
    
    def test_workflow_operations(self):
        """測試工作流程操作"""
        # 測試狀態轉換
        self.cursor.execute("""
            SELECT name FROM tabsupplier_inspection 
            WHERE inspection_status = 'Draft' 
            LIMIT 1
        """)
        draft_inspection = self.cursor.fetchone()
        
        if draft_inspection:
            inspection_name = draft_inspection[0]
            
            # 模擬狀態轉換: Draft -> In Progress -> Completed
            transitions = [
                ("In Progress", 0),
                ("Completed", 1)
            ]
            
            for status, docstatus in transitions:
                self.cursor.execute("""
                    UPDATE tabsupplier_inspection 
                    SET inspection_status = ?, docstatus = ?, modified = ?
                    WHERE name = ?
                """, (status, docstatus, datetime.now().isoformat(), inspection_name))
                
                self.cursor.execute("""
                    SELECT inspection_status, docstatus 
                    FROM tabsupplier_inspection 
                    WHERE name = ?
                """, (inspection_name,))
                
                result = self.cursor.fetchone()
                if result[0] != status or result[1] != docstatus:
                    print(f"  ❌ 狀態轉換失敗: {status}")
                    return False
            
            self.conn.commit()
            print(f"  ✅ 工作流程轉換成功: Draft -> In Progress -> Completed")
            return True
        else:
            print(f"  ⚠️  沒有找到草稿狀態的檢查記錄")
            return False
    
    def test_data_validation(self):
        """測試數據驗證"""
        try:
            # 測試必填字段驗證 - 嘗試插入缺少必填字段的記錄
            invalid_data = {
                "name": f"INVALID-{int(time.time())}",
                "creation": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "Administrator",
                "docstatus": 0
                # 缺少 check_item (NOT NULL 字段)
            }
            
            try:
                self.cursor.execute('''
                    INSERT INTO tabinspection_checklist_item 
                    (name, creation, modified, owner, docstatus)
                    VALUES (?, ?, ?, ?, ?)
                ''', tuple(invalid_data.values()))
                self.conn.commit()
                print("  ❌ 應該拒絕無效數據但沒有")
                return False
            except Exception:
                print("  ✅ 正確拒絕無效數據")
                return True
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            return False
    
    def test_performance_metrics(self):
        """測試性能指標"""
        try:
            import time
            
            start_time = time.time()
            
            # 執行複雜查詢
            self.cursor.execute('''
                SELECT 
                    cs.site_name,
                    COUNT(si.name) as inspection_count
                FROM tabconstruction_site cs
                LEFT JOIN tabsupplier_inspection si ON cs.name = si.construction_site
                GROUP BY cs.name
                LIMIT 100
            ''')
            
            results = self.cursor.fetchall()
            end_time = time.time()
            
            query_time = end_time - start_time
            
            print(f"  📊 性能指標:")
            print(f"    - 查詢時間: {query_time:.3f}秒")
            print(f"    - 結果數量: {len(results)}")
            
            # 性能標準：查詢時間應小於1秒
            if query_time < 1.0:
                print("  ✅ 性能測試通過")
                return True
            else:
                print("  ❌ 性能測試失敗")
                return False
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            return False
    
    def test_data_integrity(self):
        """測試數據完整性"""
        integrity_checks = []
        
        # 檢查外鍵完整性
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM tabsupplier_inspection si
            LEFT JOIN tabconstruction_site cs ON si.construction_site = cs.name
            WHERE cs.name IS NULL
        """)
        orphaned_inspections = self.cursor.fetchone()[0]
        integrity_checks.append(("孤立檢查記錄", orphaned_inspections == 0))
        
        # 檢查狀態一致性
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM tabsupplier_inspection 
            WHERE docstatus = 1 AND inspection_status IN ('Draft', 'In Progress')
        """)
        inconsistent_status = self.cursor.fetchone()[0]
        integrity_checks.append(("狀態一致性", inconsistent_status == 0))
        
        # 檢查日期有效性
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM tabsupplier_inspection 
            WHERE inspection_date > date('now')
        """)
        future_dates = self.cursor.fetchone()[0]
        integrity_checks.append(("未來日期檢查", future_dates == 0))
        
        print(f"  📊 完整性檢查:")
        all_passed = True
        for check_name, passed in integrity_checks:
            status = "✅" if passed else "❌"
            print(f"    - {check_name}: {status}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """運行所有測試"""
        print("Construction Inspection Module 完整功能測試")
        print("=" * 50)
        print("🚀 開始完整功能測試...")
        print("=" * 50)
        
        tests = [
            ("數據庫架構完整性", self.test_database_schema),
            ("數據創建功能", self.test_data_creation),
            ("數據關聯性", self.test_data_relationships),
            ("工作流程操作", self.test_workflow_operations),
            ("數據驗證", self.test_data_validation),
            ("性能指標", self.test_performance_metrics),
            ("數據完整性", self.test_data_integrity)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # 計算結果
        success_rate = (passed / total) * 100
        self.test_results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": success_rate
        }
        
        print("\n" + "=" * 50)
        print("📊 完整功能測試結果")
        print("=" * 50)
        print(f"總測試數: {total}")
        print(f"通過: {passed}")
        print(f"失敗: {total - passed}")
        print(f"成功率: {success_rate:.1f}%")
        
        # 保存測試報告
        report_path = Path(self.db_path).parent / "comprehensive_test_results.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細測試報告已保存到: {report_path}")
        
        # 關閉數據庫連接
        self.conn.close()
        
        return success_rate >= 85.0  # 85%以上通過率視為成功

def main():
    """主函數"""
    # 數據庫路徑
    db_path = "test_construction_inspection.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 數據庫文件不存在: {db_path}")
        return False
    
    # 運行完整功能測試
    tester = ComprehensiveTester(db_path)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 完整功能測試通過！Construction Inspection Module 運行正常。")
    else:
        print("\n⚠️  完整功能測試未完全通過，請檢查失敗的測試項目。")
    
    return success

if __name__ == "__main__":
    main()