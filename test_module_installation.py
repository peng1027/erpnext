#!/usr/bin/env python3
"""
Construction Inspection Module 安裝和測試腳本
模擬ERPNext環境中的模組安裝過程
"""

import os
import sys
import json
import importlib.util
from pathlib import Path

class MockERPNextInstaller:
    """模擬ERPNext模組安裝器"""
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.module_name = "construction_inspection"
        self.results = {
            "installation": False,
            "doctypes": [],
            "integrations": [],
            "tasks": [],
            "errors": []
        }
    
    def check_module_structure(self):
        """檢查模組結構完整性"""
        print("🔍 檢查模組結構...")
        
        required_files = [
            "__init__.py",
            "hooks.py",
            "config/construction_inspection.py"
        ]
        
        required_dirs = [
            "doctype",
            "integrations", 
            "tasks",
            "test_data",
            "tests"
        ]
        
        # 檢查必要文件
        for file_path in required_files:
            full_path = self.module_path / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} - 文件不存在")
                self.results["errors"].append(f"Missing file: {file_path}")
        
        # 檢查必要目錄
        for dir_path in required_dirs:
            full_path = self.module_path / dir_path
            if full_path.exists():
                print(f"  ✅ {dir_path}/")
            else:
                print(f"  ❌ {dir_path}/ - 目錄不存在")
                self.results["errors"].append(f"Missing directory: {dir_path}")
        
        return len(self.results["errors"]) == 0
    
    def validate_doctypes(self):
        """驗證DocType定義"""
        print("\n📋 驗證DocType定義...")
        
        doctype_dir = self.module_path / "doctype"
        if not doctype_dir.exists():
            self.results["errors"].append("DocType directory not found")
            return False
        
        doctypes = ["construction_site", "supplier_inspection", "inspection_checklist_item"]
        
        for doctype in doctypes:
            doctype_path = doctype_dir / doctype
            json_file = doctype_path / f"{doctype}.json"
            py_file = doctype_path / f"{doctype}.py"
            
            if json_file.exists() and py_file.exists():
                try:
                    # 驗證JSON格式
                    with open(json_file, 'r', encoding='utf-8') as f:
                        doctype_data = json.load(f)
                    
                    print(f"  ✅ {doctype} - JSON和Python文件都存在")
                    self.results["doctypes"].append({
                        "name": doctype,
                        "status": "valid",
                        "fields": len(doctype_data.get("fields", []))
                    })
                    
                except json.JSONDecodeError as e:
                    print(f"  ❌ {doctype} - JSON格式錯誤: {e}")
                    self.results["errors"].append(f"Invalid JSON in {doctype}: {e}")
            else:
                print(f"  ❌ {doctype} - 缺少必要文件")
                self.results["errors"].append(f"Missing files for DocType: {doctype}")
        
        return len([dt for dt in self.results["doctypes"] if dt["status"] == "valid"]) == len(doctypes)
    
    def validate_integrations(self):
        """驗證集成模組"""
        print("\n🔗 驗證集成模組...")
        
        integrations_dir = self.module_path / "integrations"
        if not integrations_dir.exists():
            self.results["errors"].append("Integrations directory not found")
            return False
        
        integration_files = [
            "project_integration.py",
            "supplier_integration.py", 
            "user_permission_integration.py"
        ]
        
        for file_name in integration_files:
            file_path = integrations_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
                self.results["integrations"].append({
                    "name": file_name.replace(".py", ""),
                    "status": "available"
                })
            else:
                print(f"  ❌ {file_name} - 文件不存在")
                self.results["errors"].append(f"Missing integration: {file_name}")
        
        return len(self.results["integrations"]) == len(integration_files)
    
    def validate_tasks(self):
        """驗證任務模組"""
        print("\n⏰ 驗證任務模組...")
        
        tasks_dir = self.module_path / "tasks"
        if not tasks_dir.exists():
            self.results["errors"].append("Tasks directory not found")
            return False
        
        task_files = ["daily.py", "weekly.py", "monthly.py"]
        
        for file_name in task_files:
            file_path = tasks_dir / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
                self.results["tasks"].append({
                    "name": file_name.replace(".py", ""),
                    "status": "available"
                })
            else:
                print(f"  ❌ {file_name} - 文件不存在")
                self.results["errors"].append(f"Missing task: {file_name}")
        
        return len(self.results["tasks"]) == len(task_files)
    
    def simulate_installation(self):
        """模擬安裝過程"""
        print("\n🚀 開始模組安裝模擬...")
        
        # 步驟1: 檢查結構
        if not self.check_module_structure():
            print("❌ 模組結構檢查失敗")
            return False
        
        # 步驟2: 驗證DocTypes
        if not self.validate_doctypes():
            print("❌ DocType驗證失敗")
            return False
        
        # 步驟3: 驗證集成
        if not self.validate_integrations():
            print("❌ 集成模組驗證失敗")
            return False
        
        # 步驟4: 驗證任務
        if not self.validate_tasks():
            print("❌ 任務模組驗證失敗")
            return False
        
        self.results["installation"] = True
        print("\n✅ 模組安裝模擬成功完成!")
        return True
    
    def generate_report(self):
        """生成安裝報告"""
        print("\n" + "="*60)
        print("📊 Construction Inspection Module 安裝報告")
        print("="*60)
        
        print(f"\n模組名稱: {self.module_name}")
        print(f"安裝狀態: {'✅ 成功' if self.results['installation'] else '❌ 失敗'}")
        
        print(f"\nDocTypes ({len(self.results['doctypes'])}):")
        for dt in self.results["doctypes"]:
            print(f"  - {dt['name']}: {dt['status']} ({dt['fields']} 字段)")
        
        print(f"\n集成模組 ({len(self.results['integrations'])}):")
        for integration in self.results["integrations"]:
            print(f"  - {integration['name']}: {integration['status']}")
        
        print(f"\n任務模組 ({len(self.results['tasks'])}):")
        for task in self.results["tasks"]:
            print(f"  - {task['name']}: {task['status']}")
        
        if self.results["errors"]:
            print(f"\n❌ 錯誤 ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  - {error}")
        else:
            print("\n✅ 沒有發現錯誤")
        
        return self.results

def main():
    """主函數"""
    print("Construction Inspection Module 安裝測試")
    print("="*50)
    
    # 模組路徑
    module_path = Path(__file__).parent / "erpnext" / "construction_inspection"
    
    if not module_path.exists():
        print(f"❌ 模組路徑不存在: {module_path}")
        return False
    
    # 創建安裝器並運行
    installer = MockERPNextInstaller(module_path)
    success = installer.simulate_installation()
    results = installer.generate_report()
    
    # 保存結果
    results_file = Path(__file__).parent / "installation_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 詳細結果已保存到: {results_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)