#!/usr/bin/env python3
"""
Setup script to create sample data for vendor_qc app
"""

import json
import os
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample data for vendor_qc testing"""
    
    # Sample Contractor Sites
    contractor_sites = [
        {
            "doctype": "Contractor Site",
            "site_name": "台北信義工地A",
            "address": "台北市信義區信義路五段7號",
            "latitude": 25.0330,
            "longitude": 121.5654,
            "geofence_radius": 200,
            "project": "信義區商業大樓建設案"
        },
        {
            "doctype": "Contractor Site", 
            "site_name": "新北板橋工地B",
            "address": "新北市板橋區中山路一段161號",
            "latitude": 25.0138,
            "longitude": 121.4627,
            "geofence_radius": 150,
            "project": "板橋住宅社區開發案"
        },
        {
            "doctype": "Contractor Site",
            "site_name": "桃園中壢工地C", 
            "address": "桃園市中壢區中正路100號",
            "latitude": 24.9537,
            "longitude": 121.2257,
            "geofence_radius": 300,
            "project": "中壢工業園區擴建案"
        }
    ]
    
    # Sample NCRs
    today = datetime.now()
    ncrs = [
        {
            "doctype": "NCR",
            "title": "混凝土強度不符合規範要求",
            "site": "台北信義工地A",
            "supplier": "台灣混凝土股份有限公司",
            "severity": "High",
            "due_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "Open",
            "description": "經檢測發現混凝土強度低於設計要求，需要立即處理",
            "project": "信義區商業大樓建設案"
        },
        {
            "doctype": "NCR", 
            "title": "鋼筋間距不符合圖面規範",
            "site": "新北板橋工地B",
            "supplier": "豐國鋼鐵股份有限公司",
            "severity": "Medium",
            "due_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "Under Review",
            "description": "鋼筋間距與設計圖面不符，需要重新調整",
            "project": "板橋住宅社區開發案"
        },
        {
            "doctype": "NCR",
            "title": "防水層施工品質不良",
            "site": "桃園中壢工地C", 
            "supplier": "永豐防水工程有限公司",
            "severity": "High",
            "due_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "status": "Overdue",
            "description": "防水層出現多處破損，可能影響建築物防水性能",
            "project": "中壢工業園區擴建案"
        }
    ]
    
    # Sample Vendor Site Visits
    vendor_visits = [
        {
            "doctype": "Vendor Site Visit",
            "site": "台北信義工地A",
            "supplier": "台灣混凝土股份有限公司",
            "visit_date": today.strftime("%Y-%m-%d"),
            "visit_time": "09:30:00",
            "purpose": "混凝土澆置品質檢查",
            "inspector": "張工程師",
            "status": "Completed"
        },
        {
            "doctype": "Vendor Site Visit",
            "site": "新北板橋工地B", 
            "supplier": "豐國鋼鐵股份有限公司",
            "visit_date": today.strftime("%Y-%m-%d"),
            "visit_time": "14:00:00",
            "purpose": "鋼筋綁紮檢驗",
            "inspector": "李工程師",
            "status": "In Progress"
        }
    ]
    
    return {
        "contractor_sites": contractor_sites,
        "ncrs": ncrs,
        "vendor_visits": vendor_visits
    }

def save_sample_data():
    """Save sample data to JSON files"""
    data = create_sample_data()
    
    # Create data directory
    data_dir = "sample_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Save each data type to separate files
    for data_type, records in data.items():
        filename = f"{data_dir}/{data_type}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅ Created {filename} with {len(records)} records")
    
    # Create a combined file
    combined_file = f"{data_dir}/all_data.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Created {combined_file} with all sample data")
    
    return data

def create_frappe_fixtures():
    """Create Frappe-compatible fixture files"""
    data = create_sample_data()
    
    # Create fixtures directory
    fixtures_dir = "apps/vendor_qc/fixtures"
    os.makedirs(fixtures_dir, exist_ok=True)
    
    # Create fixture files for each DocType
    for data_type, records in data.items():
        if records:
            doctype = records[0]["doctype"]
            filename = f"{fixtures_dir}/{doctype.lower().replace(' ', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            print(f"✅ Created fixture {filename}")

def print_summary():
    """Print summary of created data"""
    data = create_sample_data()
    
    print("\n📊 Sample Data Summary:")
    print("=" * 50)
    
    for data_type, records in data.items():
        print(f"\n{data_type.replace('_', ' ').title()}:")
        for i, record in enumerate(records, 1):
            if data_type == "contractor_sites":
                print(f"  {i}. {record['site_name']} - {record['address']}")
            elif data_type == "ncrs":
                print(f"  {i}. {record['title']} ({record['severity']}) - {record['status']}")
            elif data_type == "vendor_visits":
                print(f"  {i}. {record['site']} - {record['purpose']}")
    
    print(f"\n🎯 Total Records: {sum(len(records) for records in data.values())}")

if __name__ == "__main__":
    print("🚀 Setting up vendor_qc sample data...")
    
    # Save sample data
    save_sample_data()
    
    # Create Frappe fixtures
    create_frappe_fixtures()
    
    # Print summary
    print_summary()
    
    print("\n✅ Setup completed successfully!")
    print("\n📝 Next steps:")
    print("1. Use the JSON files in sample_data/ for testing")
    print("2. Import fixtures into Frappe using: bench --site [site-name] import-doc [fixture-file]")
    print("3. Test the vendor_qc Portal at http://localhost:8090/app/test.html")