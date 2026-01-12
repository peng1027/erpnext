#!/usr/bin/env python3
"""
Construction Inspection Module 數據庫遷移模擬
模擬ERPNext中DocType的創建和數據庫表結構生成
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

class MockDatabaseMigrator:
    """模擬數據庫遷移器"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.db_path = Path(__file__).parent / "test_construction_inspection.db"
        self.migration_results = {
            "tables_created": [],
            "indexes_created": [],
            "constraints_added": [],
            "errors": []
        }
    
    def create_test_database(self):
        """創建測試數據庫"""
        print("🗄️ 創建測試數據庫...")
        
        # 如果數據庫已存在，先刪除
        if self.db_path.exists():
            self.db_path.unlink()
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"  ✅ 數據庫已創建: {self.db_path}")
        return True
    
    def load_doctype_definition(self, doctype_name):
        """加載DocType定義"""
        doctype_path = self.module_path / "doctype" / doctype_name / f"{doctype_name}.json"
        
        if not doctype_path.exists():
            raise FileNotFoundError(f"DocType definition not found: {doctype_path}")
        
        with open(doctype_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def convert_field_type(self, frappe_type):
        """轉換Frappe字段類型到SQLite類型"""
        type_mapping = {
            "Data": "TEXT",
            "Text": "TEXT", 
            "Long Text": "TEXT",
            "Small Text": "TEXT",
            "Select": "TEXT",
            "Link": "TEXT",
            "Int": "INTEGER",
            "Float": "REAL",
            "Currency": "REAL",
            "Percent": "REAL",
            "Date": "DATE",
            "Datetime": "DATETIME",
            "Time": "TIME",
            "Check": "INTEGER",
            "Password": "TEXT",
            "Read Only": "TEXT",
            "Attach": "TEXT",
            "Attach Image": "TEXT",
            "Signature": "TEXT",
            "Color": "TEXT",
            "Barcode": "TEXT",
            "Geolocation": "TEXT",
            "Duration": "TEXT",
            "Rating": "INTEGER",
            "Table": "TEXT",
            "HTML Editor": "TEXT",
            "Code": "TEXT",
            "JSON": "TEXT"
        }
        return type_mapping.get(frappe_type, "TEXT")
    
    def create_table_from_doctype(self, doctype_data):
        """根據DocType定義創建數據庫表"""
        table_name = f"tab{doctype_data['name'].replace(' ', '_').lower()}"
        
        print(f"📋 創建表: {table_name}")
        
        # 構建CREATE TABLE語句
        columns = []
        
        # 添加標準字段
        standard_fields = [
            ("name", "TEXT PRIMARY KEY"),
            ("creation", "DATETIME"),
            ("modified", "DATETIME"),
            ("modified_by", "TEXT"),
            ("owner", "TEXT"),
            ("docstatus", "INTEGER DEFAULT 0"),
            ("idx", "INTEGER")
        ]
        
        for field_name, field_type in standard_fields:
            columns.append(f"{field_name} {field_type}")
        
        # 添加自定義字段
        for field in doctype_data.get("fields", []):
            if field.get("fieldname"):
                field_name = field["fieldname"]
                field_type = self.convert_field_type(field.get("fieldtype", "Data"))
                
                # 處理必填字段
                if field.get("reqd"):
                    field_type += " NOT NULL"
                
                # 處理默認值
                if field.get("default"):
                    default_value = field["default"]
                    if field.get("fieldtype") in ["Data", "Text", "Select"]:
                        field_type += f" DEFAULT '{default_value}'"
                    else:
                        field_type += f" DEFAULT {default_value}"
                
                columns.append(f"{field_name} {field_type}")
        
        # 創建表
        create_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
        
        try:
            self.cursor.execute(create_sql)
            print(f"  ✅ 表 {table_name} 創建成功")
            self.migration_results["tables_created"].append({
                "table_name": table_name,
                "doctype": doctype_data["name"],
                "fields_count": len(doctype_data.get("fields", [])),
                "sql": create_sql
            })
            
            # 創建索引
            self.create_indexes(table_name, doctype_data)
            
        except sqlite3.Error as e:
            error_msg = f"創建表 {table_name} 失敗: {e}"
            print(f"  ❌ {error_msg}")
            self.migration_results["errors"].append(error_msg)
    
    def create_indexes(self, table_name, doctype_data):
        """為表創建索引"""
        # 為常用字段創建索引
        index_fields = ["modified", "creation", "owner", "docstatus"]
        
        # 添加有索引標記的字段
        for field in doctype_data.get("fields", []):
            if field.get("search_index") or field.get("unique"):
                index_fields.append(field["fieldname"])
        
        for field in index_fields:
            try:
                index_name = f"idx_{table_name}_{field}"
                index_sql = f"CREATE INDEX {index_name} ON {table_name} ({field})"
                self.cursor.execute(index_sql)
                
                self.migration_results["indexes_created"].append({
                    "index_name": index_name,
                    "table": table_name,
                    "field": field
                })
                
            except sqlite3.Error as e:
                # 忽略已存在的索引錯誤
                if "already exists" not in str(e):
                    print(f"  ⚠️ 創建索引失敗: {e}")
    
    def migrate_all_doctypes(self):
        """遷移所有DocType"""
        print("\n🚀 開始數據庫遷移...")
        
        doctypes = ["construction_site", "supplier_inspection", "inspection_checklist_item"]
        
        for doctype_name in doctypes:
            try:
                print(f"\n📋 處理DocType: {doctype_name}")
                doctype_data = self.load_doctype_definition(doctype_name)
                self.create_table_from_doctype(doctype_data)
                
            except Exception as e:
                error_msg = f"遷移DocType {doctype_name} 失敗: {e}"
                print(f"  ❌ {error_msg}")
                self.migration_results["errors"].append(error_msg)
        
        # 提交事務
        self.conn.commit()
        print("\n✅ 數據庫遷移完成!")
    
    def verify_migration(self):
        """驗證遷移結果"""
        print("\n🔍 驗證遷移結果...")
        
        # 檢查表是否存在
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        expected_tables = [
            "tabconstruction_site",
            "tabsupplier_inspection", 
            "tabinspection_checklist_item"
        ]
        
        for table in expected_tables:
            if table in tables:
                # 檢查表結構
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = self.cursor.fetchall()
                print(f"  ✅ {table}: {len(columns)} 列")
            else:
                print(f"  ❌ {table}: 表不存在")
                self.migration_results["errors"].append(f"Table not found: {table}")
        
        return len(self.migration_results["errors"]) == 0
    
    def generate_migration_report(self):
        """生成遷移報告"""
        print("\n" + "="*60)
        print("📊 數據庫遷移報告")
        print("="*60)
        
        print(f"\n創建的表 ({len(self.migration_results['tables_created'])}):")
        for table in self.migration_results["tables_created"]:
            print(f"  - {table['table_name']} ({table['doctype']}) - {table['fields_count']} 字段")
        
        print(f"\n創建的索引 ({len(self.migration_results['indexes_created'])}):")
        for index in self.migration_results["indexes_created"]:
            print(f"  - {index['index_name']} on {index['table']}.{index['field']}")
        
        if self.migration_results["errors"]:
            print(f"\n❌ 錯誤 ({len(self.migration_results['errors'])}):")
            for error in self.migration_results["errors"]:
                print(f"  - {error}")
        else:
            print("\n✅ 沒有發現錯誤")
        
        # 保存詳細報告
        report_data = {
            "migration_time": datetime.now().isoformat(),
            "database_path": str(self.db_path),
            "results": self.migration_results
        }
        
        report_file = Path(__file__).parent / "migration_results.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細報告已保存到: {report_file}")
        
        return self.migration_results
    
    def close(self):
        """關閉數據庫連接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """主函數"""
    print("Construction Inspection Module 數據庫遷移測試")
    print("="*50)
    
    # 模組路徑
    module_path = Path(__file__).parent / "erpnext" / "construction_inspection"
    
    if not module_path.exists():
        print(f"❌ 模組路徑不存在: {module_path}")
        return False
    
    # 創建遷移器並運行
    migrator = MockDatabaseMigrator(module_path)
    
    try:
        # 創建數據庫
        migrator.create_test_database()
        
        # 執行遷移
        migrator.migrate_all_doctypes()
        
        # 驗證結果
        success = migrator.verify_migration()
        
        # 生成報告
        migrator.generate_migration_report()
        
        return success
        
    except Exception as e:
        print(f"❌ 遷移過程中發生錯誤: {e}")
        return False
        
    finally:
        migrator.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)