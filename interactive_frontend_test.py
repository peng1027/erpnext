#!/usr/bin/env python3
"""
Construction Inspection Module 互動式前端測試
提供互動式命令行界面來測試前端功能
"""

import requests
import json
import time
from datetime import datetime
import os
import webbrowser

class InteractiveFrontendTest:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def check_server_status(self):
        """檢查服務器狀態"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ Web 服務器運行正常")
                return True
            else:
                print(f"⚠️ 服務器響應異常，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 無法連接到服務器: {e}")
            return False
    
    def open_browser(self):
        """在瀏覽器中打開界面"""
        try:
            print(f"🌐 正在瀏覽器中打開: {self.base_url}")
            webbrowser.open(self.base_url)
            print("✅ 瀏覽器已打開")
        except Exception as e:
            print(f"❌ 無法打開瀏覽器: {e}")
    
    def test_dashboard_api(self):
        """測試儀表板 API"""
        print("\n📊 測試儀表板 API...")
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard")
            if response.status_code == 200:
                data = response.json()
                stats = data['stats']
                
                print("✅ 儀表板數據載入成功:")
                print(f"   📍 總工地數: {stats['total_sites']}")
                print(f"   📋 總檢查數: {stats['total_inspections']}")
                print(f"   ✅ 已完成檢查: {stats['completed_inspections']}")
                print(f"   📈 完成率: {stats['completion_rate']:.1f}%")
                
                print(f"\n📝 最近活動 (前5項):")
                for i, activity in enumerate(data['recent_activities'][:5]):
                    print(f"   {i+1}. {activity['description']} - {activity['status']}")
                
                return True
            else:
                print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return False
    
    def test_sites_api(self):
        """測試工地 API"""
        print("\n🏗️ 測試工地 API...")
        try:
            response = self.session.get(f"{self.base_url}/api/sites")
            if response.status_code == 200:
                data = response.json()
                sites = data['sites']
                
                print(f"✅ 工地數據載入成功，共 {len(sites)} 個工地")
                
                if sites:
                    print("\n📋 工地列表 (前5個):")
                    for i, site in enumerate(sites[:5]):
                        print(f"   {i+1}. {site['site_name']} - {site['supplier']} ({site['site_status']})")
                
                return True
            else:
                print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return False
    
    def test_inspections_api(self):
        """測試檢查記錄 API"""
        print("\n📋 測試檢查記錄 API...")
        try:
            response = self.session.get(f"{self.base_url}/api/inspections")
            if response.status_code == 200:
                data = response.json()
                inspections = data['inspections']
                
                print(f"✅ 檢查記錄載入成功，共 {len(inspections)} 個記錄")
                
                if inspections:
                    print("\n📝 檢查記錄 (前5個):")
                    for i, inspection in enumerate(inspections[:5]):
                        print(f"   {i+1}. {inspection['inspection_title']} - {inspection['inspector_name']} ({inspection['inspection_status']})")
                
                return True
            else:
                print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 測試失敗: {e}")
            return False
    
    def test_system_test_api(self):
        """測試系統測試 API"""
        print("\n🧪 測試系統測試 API...")
        print("⏳ 正在運行系統測試，請稍候...")
        
        try:
            response = self.session.post(f"{self.base_url}/api/run-test", timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                print("✅ 系統測試完成:")
                print(f"   📊 總體結果: {data['overall_result']}")
                print(f"   📈 成功率: {data['success_rate']}%")
                print(f"   ✅ 通過測試: {data['passed_tests']}/{data['total_tests']}")
                
                print("\n📋 詳細測試結果:")
                for test in data['test_details']:
                    status_icon = "✅" if test['status'] == 'passed' else "❌"
                    print(f"   {status_icon} {test['name']}: {test['status']}")
                
                return True
            else:
                print(f"❌ API 請求失敗，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 系統測試失敗: {e}")
            return False
    
    def performance_test(self):
        """性能測試"""
        print("\n⚡ 執行性能測試...")
        
        endpoints = [
            ("/", "主頁面"),
            ("/api/dashboard", "儀表板 API"),
            ("/api/sites", "工地 API"),
            ("/api/inspections", "檢查記錄 API")
        ]
        
        print("📊 測試各端點響應時間:")
        total_time = 0
        successful_requests = 0
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                total_time += response_time
                successful_requests += 1
                
                status_icon = "✅" if response.status_code == 200 else "⚠️"
                print(f"   {status_icon} {name}: {response_time:.0f}ms (狀態: {response.status_code})")
                
            except Exception as e:
                print(f"   ❌ {name}: 錯誤 - {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"\n📈 平均響應時間: {avg_time:.0f}ms")
            
            if avg_time < 100:
                print("🚀 性能優秀！")
            elif avg_time < 500:
                print("✅ 性能良好")
            else:
                print("⚠️ 性能需要優化")
    
    def show_menu(self):
        """顯示主菜單"""
        print("\n" + "=" * 60)
        print("🏗️ Construction Inspection Module - 互動式前端測試")
        print("=" * 60)
        print("1. 檢查服務器狀態")
        print("2. 在瀏覽器中打開界面")
        print("3. 測試儀表板 API")
        print("4. 測試工地 API")
        print("5. 測試檢查記錄 API")
        print("6. 測試系統測試 API")
        print("7. 執行性能測試")
        print("8. 執行所有測試")
        print("9. 查看測試報告")
        print("0. 退出")
        print("=" * 60)
    
    def run_all_tests(self):
        """運行所有測試"""
        print("\n🚀 執行所有前端測試...")
        
        tests = [
            ("檢查服務器狀態", self.check_server_status),
            ("測試儀表板 API", self.test_dashboard_api),
            ("測試工地 API", self.test_sites_api),
            ("測試檢查記錄 API", self.test_inspections_api),
            ("測試系統測試 API", self.test_system_test_api),
            ("執行性能測試", self.performance_test)
        ]
        
        passed_tests = 0
        total_tests = len(tests) - 1  # 性能測試不計入通過/失敗
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}...")
            try:
                if test_name == "執行性能測試":
                    test_func()  # 性能測試沒有返回值
                else:
                    if test_func():
                        passed_tests += 1
            except Exception as e:
                print(f"💥 {test_name} 發生錯誤: {e}")
        
        print(f"\n📊 測試總結: {passed_tests}/{total_tests} 通過 ({(passed_tests/total_tests*100):.1f}%)")
    
    def show_test_reports(self):
        """顯示測試報告"""
        print("\n📋 查看測試報告...")
        
        reports = [
            ("frontend_test_report.json", "前端自動化測試報告"),
            ("system_test_report.json", "系統測試報告"),
            ("comprehensive_test_results.json", "綜合功能測試報告")
        ]
        
        for filename, description in reports:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"\n📄 {description}:")
                    if 'test_time' in data:
                        print(f"   ⏰ 測試時間: {data['test_time']}")
                    if 'total_tests' in data and 'passed_tests' in data:
                        success_rate = (data['passed_tests'] / data['total_tests']) * 100
                        print(f"   📊 測試結果: {data['passed_tests']}/{data['total_tests']} 通過 ({success_rate:.1f}%)")
                    
                except Exception as e:
                    print(f"   ❌ 無法讀取報告: {e}")
            else:
                print(f"\n📄 {description}: 文件不存在")
    
    def run(self):
        """運行互動式測試"""
        print("🚀 啟動 Construction Inspection Module 互動式前端測試")
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\n請選擇操作 (0-9): ").strip()
                
                if choice == "0":
                    print("👋 感謝使用！再見！")
                    break
                elif choice == "1":
                    self.check_server_status()
                elif choice == "2":
                    self.open_browser()
                elif choice == "3":
                    self.test_dashboard_api()
                elif choice == "4":
                    self.test_sites_api()
                elif choice == "5":
                    self.test_inspections_api()
                elif choice == "6":
                    self.test_system_test_api()
                elif choice == "7":
                    self.performance_test()
                elif choice == "8":
                    self.run_all_tests()
                elif choice == "9":
                    self.show_test_reports()
                else:
                    print("❌ 無效選擇，請輸入 0-9")
                
                input("\n按 Enter 鍵繼續...")
                
            except KeyboardInterrupt:
                print("\n\n👋 用戶中斷，再見！")
                break
            except Exception as e:
                print(f"❌ 發生錯誤: {e}")
                input("\n按 Enter 鍵繼續...")

if __name__ == "__main__":
    tester = InteractiveFrontendTest()
    tester.run()