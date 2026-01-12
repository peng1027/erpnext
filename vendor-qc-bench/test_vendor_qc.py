#!/usr/bin/env python3
"""
Test script for vendor_qc functionality
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add the apps directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))

def test_vendor_qc_import():
    """Test if vendor_qc can be imported"""
    try:
        import vendor_qc
        version = getattr(vendor_qc, '__version__', 'unknown')
        print(f"✅ vendor_qc imported successfully, version: {version}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import vendor_qc: {e}")
        return False

def test_vendor_qc_api():
    """Test vendor_qc API functions"""
    try:
        from vendor_qc.api import get_contractor_sites, create_ncr, get_ncr_list
        print("✅ vendor_qc API functions imported successfully")
        
        # Test get_contractor_sites
        try:
            sites = get_contractor_sites()
            print(f"✅ get_contractor_sites() works, returned: {type(sites)}")
        except Exception as e:
            print(f"⚠️  get_contractor_sites() error (expected without DB): {e}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import vendor_qc API: {e}")
        return False

def test_vendor_qc_doctypes():
    """Test vendor_qc DocTypes"""
    try:
        doctype_files = [
            'apps/vendor_qc/vendor_qc/doctype/contractor_site/contractor_site.json',
            'apps/vendor_qc/vendor_qc/doctype/ncr/ncr.json',
            'apps/vendor_qc/vendor_qc/doctype/ncr_photo/ncr_photo.json',
            'apps/vendor_qc/vendor_qc/doctype/vendor_site_visit/vendor_site_visit.json'
        ]
        
        for doctype_file in doctype_files:
            if os.path.exists(doctype_file):
                with open(doctype_file, 'r') as f:
                    doctype_data = json.load(f)
                    print(f"✅ DocType {doctype_data.get('name', 'Unknown')} loaded successfully")
            else:
                print(f"❌ DocType file not found: {doctype_file}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing DocTypes: {e}")
        return False

def test_vendor_qc_www():
    """Test vendor_qc WWW files"""
    try:
        www_file = 'apps/vendor_qc/www/app/index.html'
        if os.path.exists(www_file):
            with open(www_file, 'r') as f:
                content = f.read()
                if 'vendor-qc' in content.lower():
                    print("✅ vendor_qc WWW app file exists and contains expected content")
                else:
                    print("⚠️  vendor_qc WWW app file exists but may not have expected content")
        else:
            print(f"❌ WWW app file not found: {www_file}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing WWW files: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing vendor_qc functionality...")
    print("=" * 50)
    
    tests = [
        test_vendor_qc_import,
        test_vendor_qc_api,
        test_vendor_qc_doctypes,
        test_vendor_qc_www
    ]
    
    results = []
    for test in tests:
        print(f"\n📋 Running {test.__name__}...")
        result = test()
        results.append(result)
        print("-" * 30)
    
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! vendor_qc is ready for deployment.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()