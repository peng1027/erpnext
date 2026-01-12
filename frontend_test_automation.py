#!/usr/bin/env python3
"""
Construction Inspection Module 前端自動化測試
測試 Web 界面的各項功能和 API 端點
"""

import requests
import json
import time
from datetime import datetime
import sys

class FrontendTestSuite:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, details="", error=""):
        """記錄測試結果"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   詳情: {details}")
        if error:
            print(f"   錯誤: {error}")
    
    def test_server_connectivity(self):
        """測試服務器連接性"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                self.log_test("服務器連接測試", "PASS", f"狀態碼: {response.status_code}")
                return True
            else:
                self.log_test("服務器連接測試", "FAIL", f"狀態碼: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("服務器連接測試", "FAIL", error=str(e))
            return False
    
    def test_main_page_load(self):
        """測試主頁面載入"""
        try:
            response = self.session.get(self.base_url)
            
            # 檢查基本 HTML 結構
            content = response.text
            required_elements = [
                "Construction Inspection Module",
                "儀表板",
                "工地管理", 
                "檢查記錄",
                "系統測試"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                self.log_test("主頁面載入測試", "PASS", "所有必要元素都存在")
                return True
            else:
                self.log_test("主頁面載入測試", "FAIL", f"缺少元素: {missing_elements}")
                return False
                
        except Exception as e:
            self.log_test("主頁面載入測試", "FAIL", error=str(e))
            return False
    
    def test_api_dashboard(self):
        """測試儀表板 API"""
        try:
            response = self.session.get(f"{self.base_url}/api/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                # 檢查必要的數據結構
                required_keys = ['stats', 'recent_activities']
                stats_keys = ['total_sites', 'total_inspections', 'completed_inspections', 'completion_rate']
                
                missing_keys = []
                for key in required_keys:
                    if key not in data:
                        missing_keys.append(key)
                
                for key in stats_keys:
                    if 'stats' in data and key not in data['stats']:
                        missing_keys.append(f"stats.{key}")
                
                if not missing_keys:
                    stats = data['stats']
                    self.log_test("儀表板 API 測試", "PASS", 
                                f"工地: {stats['total_sites']}, 檢查: {stats['total_inspections']}, 完成率: {stats['completion_rate']:.1f}%")
                    return True
                else:
                    self.log_test("儀表板 API 測試", "FAIL", f"缺少數據鍵: {missing_keys}")
                    return False
            else:
                self.log_test("儀表板 API 測試", "FAIL", f"HTTP 狀態碼: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("儀表板 API 測試", "FAIL", error=str(e))
            return False
    
    def test_api_sites(self):
        """測試工地 API"""
        try:
            response = self.session.get(f"{self.base_url}/api/sites")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'sites' in data and isinstance(data['sites'], list):
                    sites_count = len(data['sites'])
                    
                    # 檢查工地數據結構
                    if sites_count > 0:
                        site = data['sites'][0]
                        required_fields = ['site_name', 'supplier', 'site_status', 'creation']
                        missing_fields = [field for field in required_fields if field not in site]
                        
                        if not missing_fields:
                            self.log_test("工地 API 測試", "PASS", f"成功載入 {sites_count} 個工地")
                            return True
                        else:
                            self.log_test("工地 API 測試", "FAIL", f"工地數據缺少字段: {missing_fields}")
                            return False
                    else:
                        self.log_test("工地 API 測試", "PASS", "API 正常但無工地數據")
                        return True
                else:
                    self.log_test("工地 API 測試", "FAIL", "響應格式不正確")
                    return False
            else:
                self.log_test("工地 API 測試", "FAIL", f"HTTP 狀態碼: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("工地 API 測試", "FAIL", error=str(e))
            return False
    
    def test_api_inspections(self):
        """測試檢查記錄 API"""
        try:
            response = self.session.get(f"{self.base_url}/api/inspections")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'inspections' in data and isinstance(data['inspections'], list):
                    inspections_count = len(data['inspections'])
                    
                    # 檢查檢查記錄數據結構
                    if inspections_count > 0:
                        inspection = data['inspections'][0]
                        required_fields = ['inspection_title', 'construction_site', 'inspector_name', 'inspection_status']
                        missing_fields = [field for field in required_fields if field not in inspection]
                        
                        if not missing_fields:
                            self.log_test("檢查記錄 API 測試", "PASS", f"成功載入 {inspections_count} 個檢查記錄")
                            return True
                        else:
                            self.log_test("檢查記錄 API 測試", "FAIL", f"檢查記錄數據缺少字段: {missing_fields}")
                            return False
                    else:
                        self.log_test("檢查記錄 API 測試", "PASS", "API 正常但無檢查記錄")
                        return True
                else:
                    self.log_test("檢查記錄 API 測試", "FAIL", "響應格式不正確")
                    return False
            else:
                self.log_test("檢查記錄 API 測試", "FAIL", f"HTTP 狀態碼: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("檢查記錄 API 測試", "FAIL", error=str(e))
            return False
    
    def test_api_system_test(self):
        """測試系統測試 API"""
        try:
            print("   正在運行系統測試 API (這可能需要幾秒鐘)...")
            response = self.session.post(f"{self.base_url}/api/run-test", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['timestamp', 'overall_result', 'passed_tests', 'total_tests', 'success_rate']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("系統測試 API 測試", "PASS", 
                                f"測試結果: {data['overall_result']}, 成功率: {data['success_rate']}%")
                    return True
                else:
                    self.log_test("系統測試 API 測試", "FAIL", f"響應缺少字段: {missing_fields}")
                    return False
            else:
                self.log_test("系統測試 API 測試", "FAIL", f"HTTP 狀態碼: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("系統測試 API 測試", "FAIL", error=str(e))
            return False
    
    def test_response_times(self):
        """測試響應時間性能"""
        endpoints = [
            ("/", "主頁面"),
            ("/api/dashboard", "儀表板 API"),
            ("/api/sites", "工地 API"),
            ("/api/inspections", "檢查記錄 API")
        ]
        
        performance_results = []
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 轉換為毫秒
                performance_results.append((name, response_time, response.status_code))
                
            except Exception as e:
                performance_results.append((name, -1, f"錯誤: {e}"))
        
        # 評估性能
        avg_response_time = sum(r[1] for r in performance_results if r[1] > 0) / len([r for r in performance_results if r[1] > 0])
        
        details = "\n".join([f"   {name}: {time:.0f}ms (狀態: {status})" 
                           for name, time, status in performance_results])
        
        if avg_response_time < 1000:  # 小於 1 秒
            self.log_test("響應時間性能測試", "PASS", f"平均響應時間: {avg_response_time:.0f}ms\n{details}")
            return True
        else:
            self.log_test("響應時間性能測試", "FAIL", f"平均響應時間過慢: {avg_response_time:.0f}ms\n{details}")
            return False
    
    def test_error_handling(self):
        """測試錯誤處理"""
        try:
            # 測試不存在的端點
            response = self.session.get(f"{self.base_url}/api/nonexistent")
            
            if response.status_code == 404:
                self.log_test("錯誤處理測試", "PASS", "正確處理 404 錯誤")
                return True
            else:
                self.log_test("錯誤處理測試", "FAIL", f"未正確處理 404，返回狀態碼: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("錯誤處理測試", "FAIL", error=str(e))
            return False
    
    def run_all_tests(self):
        """運行所有前端測試"""
        print("🚀 開始 Construction Inspection Module 前端測試")
        print("=" * 60)
        
        tests = [
            ("服務器連接測試", self.test_server_connectivity),
            ("主頁面載入測試", self.test_main_page_load),
            ("儀表板 API 測試", self.test_api_dashboard),
            ("工地 API 測試", self.test_api_sites),
            ("檢查記錄 API 測試", self.test_api_inspections),
            ("系統測試 API 測試", self.test_api_system_test),
            ("響應時間性能測試", self.test_response_times),
            ("錯誤處理測試", self.test_error_handling)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 執行: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "ERROR", error=str(e))
                print(f"💥 {test_name} 發生錯誤: {e}")
        
        # 生成測試報告
        self.generate_report()
        
        # 總結
        print("\n" + "=" * 60)
        print("📊 前端測試結果總結")
        print("=" * 60)
        print(f"總測試數: {total_tests}")
        print(f"通過: {passed_tests}")
        print(f"失敗: {total_tests - passed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 所有前端測試通過！Web 界面運行完美。")
        elif passed_tests >= total_tests * 0.8:
            print("\n✅ 大部分前端測試通過，Web 界面基本正常。")
        else:
            print("\n⚠️ 部分前端測試失敗，需要檢查問題。")
        
        return passed_tests == total_tests
    
    def generate_report(self):
        """生成測試報告"""
        report = {
            "test_time": datetime.now().isoformat(),
            "test_type": "frontend_automation_test",
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r['status'] == 'PASS']),
            "failed_tests": len([r for r in self.test_results if r['status'] == 'FAIL']),
            "error_tests": len([r for r in self.test_results if r['status'] == 'ERROR']),
            "test_results": self.test_results
        }
        
        with open("frontend_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 前端測試報告已保存到: frontend_test_report.json")

def main():
    # 檢查服務器是否運行
    print("🔍 檢查 Web 服務器狀態...")
    
    tester = FrontendTestSuite()
    
    # 等待服務器啟動
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            if response.status_code == 200:
                print("✅ Web 服務器已就緒")
                break
        except:
            if i < max_retries - 1:
                print(f"⏳ 等待服務器啟動... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ 無法連接到 Web 服務器，請確保服務器正在運行")
                sys.exit(1)
    
    # 運行測試
    tester.run_all_tests()

if __name__ == "__main__":
    main()