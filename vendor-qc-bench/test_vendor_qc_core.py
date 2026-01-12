#!/usr/bin/env python3
"""
Comprehensive test script for vendor_qc core functionality
"""

import json
import os
import sys
from datetime import datetime

def load_sample_data():
    """Load sample data from JSON files"""
    try:
        with open('sample_data/all_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Sample data not found. Please run setup_vendor_qc_data.py first")
        return None

def test_doctype_structure():
    """Test DocType JSON structure"""
    print("📋 Testing DocType Structure...")
    
    doctypes = [
        'apps/vendor_qc/vendor_qc/doctype/contractor_site/contractor_site.json',
        'apps/vendor_qc/vendor_qc/doctype/ncr/ncr.json',
        'apps/vendor_qc/vendor_qc/doctype/ncr_photo/ncr_photo.json',
        'apps/vendor_qc/vendor_qc/doctype/vendor_site_visit/vendor_site_visit.json'
    ]
    
    results = []
    for doctype_path in doctypes:
        try:
            with open(doctype_path, 'r', encoding='utf-8') as f:
                doctype_data = json.load(f)
                
            # Validate required fields
            required_fields = ['doctype', 'name', 'module', 'fields']
            missing_fields = [field for field in required_fields if field not in doctype_data]
            
            if missing_fields:
                print(f"❌ {doctype_path}: Missing fields {missing_fields}")
                results.append(False)
            else:
                print(f"✅ {doctype_data['name']}: Valid structure")
                results.append(True)
                
        except Exception as e:
            print(f"❌ {doctype_path}: Error loading - {e}")
            results.append(False)
    
    return all(results)

def test_api_structure():
    """Test API module structure"""
    print("\n📋 Testing API Structure...")
    
    try:
        # Check if api.py exists and has required functions
        api_path = 'apps/vendor_qc/vendor_qc/api.py'
        with open(api_path, 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        required_functions = [
            'def dashboard()',
            'def list_sites()',
            'def list_ncrs(',
            'def create_inspection(',
            'def create_ncr(',
            'def upload_image('
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in api_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ API missing functions: {missing_functions}")
            return False
        else:
            print("✅ API structure is complete")
            return True
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_hooks_configuration():
    """Test hooks.py configuration"""
    print("\n📋 Testing Hooks Configuration...")
    
    try:
        hooks_path = 'apps/vendor_qc/vendor_qc/hooks.py'
        with open(hooks_path, 'r', encoding='utf-8') as f:
            hooks_content = f.read()
        
        required_configs = [
            'app_name = "vendor_qc"',
            'required_apps = ["erpnext"]',
            'doc_events',
            'scheduler_events'
        ]
        
        missing_configs = []
        for config in required_configs:
            if config not in hooks_content:
                missing_configs.append(config)
        
        if missing_configs:
            print(f"❌ Hooks missing configurations: {missing_configs}")
            return False
        else:
            print("✅ Hooks configuration is complete")
            return True
            
    except Exception as e:
        print(f"❌ Hooks test failed: {e}")
        return False

def test_portal_files():
    """Test Portal/PWA files"""
    print("\n📋 Testing Portal Files...")
    
    portal_files = [
        'apps/vendor_qc/www/app/index.html',
        'apps/vendor_qc/www/app/test.html'
    ]
    
    results = []
    for file_path in portal_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for essential HTML elements
                if 'html' in content.lower() and 'vendor qc' in content.lower():
                    print(f"✅ {file_path}: Valid HTML structure")
                    results.append(True)
                else:
                    print(f"❌ {file_path}: Invalid HTML structure")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ {file_path}: Error reading - {e}")
                results.append(False)
        else:
            print(f"❌ {file_path}: File not found")
            results.append(False)
    
    return all(results)

def test_sample_data_integrity():
    """Test sample data integrity"""
    print("\n📋 Testing Sample Data Integrity...")
    
    data = load_sample_data()
    if not data:
        return False
    
    # Test data structure
    expected_keys = ['contractor_sites', 'ncrs', 'vendor_visits']
    missing_keys = [key for key in expected_keys if key not in data]
    
    if missing_keys:
        print(f"❌ Sample data missing keys: {missing_keys}")
        return False
    
    # Test data content
    results = []
    
    # Test contractor sites
    sites = data['contractor_sites']
    if len(sites) >= 3:
        print(f"✅ Contractor Sites: {len(sites)} records")
        results.append(True)
    else:
        print(f"❌ Contractor Sites: Only {len(sites)} records (expected >= 3)")
        results.append(False)
    
    # Test NCRs
    ncrs = data['ncrs']
    if len(ncrs) >= 3:
        print(f"✅ NCRs: {len(ncrs)} records")
        results.append(True)
    else:
        print(f"❌ NCRs: Only {len(ncrs)} records (expected >= 3)")
        results.append(False)
    
    # Test vendor visits
    visits = data['vendor_visits']
    if len(visits) >= 2:
        print(f"✅ Vendor Visits: {len(visits)} records")
        results.append(True)
    else:
        print(f"❌ Vendor Visits: Only {len(visits)} records (expected >= 2)")
        results.append(False)
    
    return all(results)

def test_module_import():
    """Test vendor_qc module import"""
    print("\n📋 Testing Module Import...")
    
    try:
        import vendor_qc
        print("✅ vendor_qc module imported successfully")
        
        # Test API import
        try:
            import vendor_qc.api
            print("✅ vendor_qc.api imported successfully")
            return True
        except ImportError as e:
            print(f"❌ vendor_qc.api import failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ vendor_qc module import failed: {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("📊 VENDOR QC CORE FUNCTIONALITY TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"\n📈 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 All tests passed! vendor_qc is ready for use.")
        print(f"\n📝 Next Steps:")
        print(f"   1. Start ERPNext server: bench start")
        print(f"   2. Install vendor_qc app: bench --site [site-name] install-app vendor_qc")
        print(f"   3. Import sample data: bench --site [site-name] import-doc [fixture-file]")
        print(f"   4. Access Portal: http://localhost:8000/app/vendor_qc")
    else:
        print(f"\n⚠️  Some tests failed. Please review the issues above.")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Ensure all files are in correct locations")
        print(f"   2. Check JSON syntax in DocType files")
        print(f"   3. Verify Python import paths")
        print(f"   4. Run setup_vendor_qc_data.py if sample data is missing")

def main():
    """Run all tests"""
    print("🧪 Starting vendor_qc Core Functionality Tests...")
    print("="*60)
    
    # Run all tests
    results = {
        "DocType Structure": test_doctype_structure(),
        "API Structure": test_api_structure(),
        "Hooks Configuration": test_hooks_configuration(),
        "Portal Files": test_portal_files(),
        "Sample Data Integrity": test_sample_data_integrity(),
        "Module Import": test_module_import()
    }
    
    # Generate report
    generate_test_report(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)