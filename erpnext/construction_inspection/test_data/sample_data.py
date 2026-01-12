# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, add_months, random_string
import random

def create_sample_data():
	"""Create sample data for construction inspection module"""
	
	print("Creating sample data for Construction Inspection module...")
	
	# Create sample suppliers
	suppliers = create_sample_suppliers()
	
	# Create sample construction sites
	sites = create_sample_construction_sites(suppliers)
	
	# Create sample inspections
	inspections = create_sample_inspections(sites, suppliers)
	
	# Create sample inspection templates
	create_sample_inspection_templates()
	
	print(f"Sample data created successfully:")
	print(f"- {len(suppliers)} suppliers")
	print(f"- {len(sites)} construction sites")
	print(f"- {len(inspections)} inspections")

def create_sample_suppliers():
	"""Create sample suppliers"""
	
	suppliers_data = [
		{
			"supplier_name": "ABC Construction Co.",
			"supplier_group": "Construction",
			"country": "Taiwan",
			"supplier_type": "Company"
		},
		{
			"supplier_name": "XYZ Building Services",
			"supplier_group": "Construction", 
			"country": "Taiwan",
			"supplier_type": "Company"
		},
		{
			"supplier_name": "Quality Builders Ltd.",
			"supplier_group": "Construction",
			"country": "Taiwan", 
			"supplier_type": "Company"
		},
		{
			"supplier_name": "Elite Construction Group",
			"supplier_group": "Construction",
			"country": "Taiwan",
			"supplier_type": "Company"
		},
		{
			"supplier_name": "Premier Building Solutions",
			"supplier_group": "Construction",
			"country": "Taiwan",
			"supplier_type": "Company"
		}
	]
	
	created_suppliers = []
	
	for supplier_data in suppliers_data:
		# Check if supplier already exists
		if not frappe.db.exists("Supplier", supplier_data["supplier_name"]):
			supplier_doc = frappe.get_doc({
				"doctype": "Supplier",
				**supplier_data
			})
			supplier_doc.insert(ignore_permissions=True)
			created_suppliers.append(supplier_doc.name)
		else:
			created_suppliers.append(supplier_data["supplier_name"])
	
	frappe.db.commit()
	return created_suppliers

def create_sample_construction_sites(suppliers):
	"""Create sample construction sites"""
	
	sites_data = [
		{
			"site_name": "台北101商業大樓建設",
			"site_code": "SITE-TP101",
			"supplier": suppliers[0],
			"status": "Active",
			"description": "台北市信義區商業大樓建設項目",
			"location": "台北市信義區",
			"project_type": "Commercial Building"
		},
		{
			"site_name": "新竹科學園區廠房建設",
			"site_code": "SITE-HSP01", 
			"supplier": suppliers[1],
			"status": "Active",
			"description": "新竹科學園區工業廠房建設",
			"location": "新竹市東區",
			"project_type": "Industrial Building"
		},
		{
			"site_name": "高雄港區住宅社區",
			"site_code": "SITE-KH001",
			"supplier": suppliers[2],
			"status": "Planning",
			"description": "高雄港區住宅社區開發項目",
			"location": "高雄市前鎮區",
			"project_type": "Residential Complex"
		},
		{
			"site_name": "台中水湳經貿園區辦公大樓",
			"site_code": "SITE-TC001",
			"supplier": suppliers[3],
			"status": "Active",
			"description": "台中水湳經貿園區辦公大樓建設",
			"location": "台中市西屯區",
			"project_type": "Office Building"
		},
		{
			"site_name": "桃園機場捷運站體工程",
			"site_code": "SITE-TY001",
			"supplier": suppliers[4],
			"status": "In Progress",
			"description": "桃園機場捷運延伸線站體建設",
			"location": "桃園市中壢區",
			"project_type": "Transportation Infrastructure"
		}
	]
	
	created_sites = []
	
	for site_data in sites_data:
		# Check if site already exists
		if not frappe.db.exists("Construction Site", {"site_code": site_data["site_code"]}):
			site_doc = frappe.get_doc({
				"doctype": "Construction Site",
				"start_date": add_days(today(), -random.randint(30, 180)),
				"expected_end_date": add_days(today(), random.randint(90, 365)),
				"progress_percentage": random.randint(10, 85),
				"next_inspection_date": add_days(today(), random.randint(1, 14)),
				**site_data
			})
			site_doc.insert(ignore_permissions=True)
			created_sites.append(site_doc.name)
		else:
			existing_site = frappe.get_doc("Construction Site", {"site_code": site_data["site_code"]})
			created_sites.append(existing_site.name)
	
	frappe.db.commit()
	return created_sites

def create_sample_inspections(sites, suppliers):
	"""Create sample inspections"""
	
	inspection_types = ["Routine", "Quality Check", "Safety Audit", "Progress Review", "Final Inspection"]
	inspectors = ["administrator", "guest@example.com"]  # Use existing users
	
	created_inspections = []
	
	for site in sites:
		site_doc = frappe.get_doc("Construction Site", site)
		supplier = site_doc.supplier
		
		# Create 3-5 inspections per site
		num_inspections = random.randint(3, 5)
		
		for i in range(num_inspections):
			inspection_date = add_days(today(), -random.randint(1, 60))
			
			inspection_doc = frappe.get_doc({
				"doctype": "Supplier Inspection",
				"construction_site": site,
				"supplier": supplier,
				"inspection_date": inspection_date,
				"inspector": random.choice(inspectors),
				"inspection_type": random.choice(inspection_types),
				"overall_rating": round(random.uniform(3.0, 5.0), 1),
				"issues_found": random.randint(0, 5),
				"corrective_actions_required": random.choice([0, 1]),
				"approval_status": random.choice(["Approved", "Pending", "Rejected"]),
				"description": f"定期巡檢 - {inspection_date.strftime('%Y年%m月%d日')}",
				"checklist_items": create_sample_checklist_items()
			})
			
			inspection_doc.insert(ignore_permissions=True)
			
			# Submit some inspections
			if random.choice([True, False]):
				inspection_doc.submit()
			
			created_inspections.append(inspection_doc.name)
	
	frappe.db.commit()
	return created_inspections

def create_sample_checklist_items():
	"""Create sample checklist items for inspections"""
	
	checklist_templates = [
		{
			"check_item": "安全設備檢查",
			"description": "檢查安全帽、安全帶、防護設備是否齊全",
			"is_mandatory": 1,
			"weight": 25,
			"status": random.choice(["Pass", "Fail", "N/A"]),
			"rating": random.randint(3, 5)
		},
		{
			"check_item": "施工品質評估",
			"description": "評估已完成工程的施工品質",
			"is_mandatory": 1,
			"weight": 30,
			"status": random.choice(["Pass", "Fail"]),
			"rating": random.randint(3, 5)
		},
		{
			"check_item": "現場整潔度",
			"description": "檢查施工現場的整潔和組織狀況",
			"is_mandatory": 0,
			"weight": 15,
			"status": random.choice(["Pass", "Fail"]),
			"rating": random.randint(2, 5)
		},
		{
			"check_item": "材料管理",
			"description": "檢查建材存放和管理情況",
			"is_mandatory": 1,
			"weight": 20,
			"status": random.choice(["Pass", "Fail"]),
			"rating": random.randint(3, 5)
		},
		{
			"check_item": "進度符合性",
			"description": "確認施工進度是否符合計劃",
			"is_mandatory": 1,
			"weight": 10,
			"status": random.choice(["Pass", "Fail"]),
			"rating": random.randint(3, 5)
		}
	]
	
	# Randomly select 3-5 items for each inspection
	selected_items = random.sample(checklist_templates, random.randint(3, 5))
	
	for item in selected_items:
		if item["status"] == "Fail":
			item["remarks"] = "需要改善"
		else:
			item["remarks"] = "符合標準"
	
	return selected_items

def create_sample_inspection_templates():
	"""Create sample inspection templates"""
	
	templates_data = [
		{
			"template_name": "標準建築工程巡檢模板",
			"description": "適用於一般建築工程的標準巡檢項目",
			"is_active": 1,
			"template_type": "Standard"
		},
		{
			"template_name": "安全專項檢查模板", 
			"description": "專門針對施工安全的檢查項目",
			"is_active": 1,
			"template_type": "Safety"
		},
		{
			"template_name": "品質驗收檢查模板",
			"description": "工程品質驗收專用檢查項目",
			"is_active": 1,
			"template_type": "Quality"
		}
	]
	
	for template_data in templates_data:
		if not frappe.db.exists("Inspection Template", template_data["template_name"]):
			template_doc = frappe.get_doc({
				"doctype": "Inspection Template",
				**template_data,
				"checklist_items": get_template_checklist_items(template_data["template_type"])
			})
			template_doc.insert(ignore_permissions=True)
	
	frappe.db.commit()

def get_template_checklist_items(template_type):
	"""Get checklist items based on template type"""
	
	if template_type == "Standard":
		return [
			{
				"check_item": "施工進度檢查",
				"description": "確認施工進度是否按計劃執行",
				"is_mandatory": 1,
				"weight": 20
			},
			{
				"check_item": "材料品質檢查",
				"description": "檢查使用材料是否符合規格",
				"is_mandatory": 1,
				"weight": 25
			},
			{
				"check_item": "施工工藝檢查",
				"description": "檢查施工工藝是否符合標準",
				"is_mandatory": 1,
				"weight": 25
			},
			{
				"check_item": "現場管理檢查",
				"description": "檢查現場管理和組織情況",
				"is_mandatory": 0,
				"weight": 15
			},
			{
				"check_item": "環境保護檢查",
				"description": "檢查環保措施執行情況",
				"is_mandatory": 0,
				"weight": 15
			}
		]
	elif template_type == "Safety":
		return [
			{
				"check_item": "個人防護設備",
				"description": "檢查工人個人防護設備佩戴情況",
				"is_mandatory": 1,
				"weight": 30
			},
			{
				"check_item": "安全標識設置",
				"description": "檢查安全警示標識是否完整",
				"is_mandatory": 1,
				"weight": 25
			},
			{
				"check_item": "機械設備安全",
				"description": "檢查施工機械設備安全狀況",
				"is_mandatory": 1,
				"weight": 25
			},
			{
				"check_item": "臨時用電安全",
				"description": "檢查臨時用電設施安全性",
				"is_mandatory": 1,
				"weight": 20
			}
		]
	elif template_type == "Quality":
		return [
			{
				"check_item": "混凝土強度檢測",
				"description": "檢測混凝土強度是否達標",
				"is_mandatory": 1,
				"weight": 35
			},
			{
				"check_item": "鋼筋綁紮質量",
				"description": "檢查鋼筋綁紮是否符合設計要求",
				"is_mandatory": 1,
				"weight": 30
			},
			{
				"check_item": "模板安裝質量",
				"description": "檢查模板安裝精度和穩定性",
				"is_mandatory": 1,
				"weight": 20
			},
			{
				"check_item": "表面處理質量",
				"description": "檢查表面處理效果",
				"is_mandatory": 0,
				"weight": 15
			}
		]
	
	return []

@frappe.whitelist()
def reset_sample_data():
	"""Reset all sample data (for testing purposes)"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can reset sample data"))
	
	# Delete in reverse order to avoid foreign key constraints
	doctypes_to_clear = [
		"Supplier Inspection",
		"Construction Site", 
		"Inspection Template"
	]
	
	for doctype in doctypes_to_clear:
		frappe.db.sql(f"DELETE FROM `tab{doctype}` WHERE name LIKE 'SAMPLE-%' OR name LIKE '%sample%'")
	
	# Delete sample suppliers
	sample_suppliers = [
		"ABC Construction Co.",
		"XYZ Building Services", 
		"Quality Builders Ltd.",
		"Elite Construction Group",
		"Premier Building Solutions"
	]
	
	for supplier in sample_suppliers:
		if frappe.db.exists("Supplier", supplier):
			frappe.delete_doc("Supplier", supplier, force=True)
	
	frappe.db.commit()
	
	return {"status": "success", "message": _("Sample data reset successfully")}

@frappe.whitelist()
def create_demo_user_accounts():
	"""Create demo user accounts for testing"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can create demo accounts"))
	
	demo_users = [
		{
			"email": "construction.manager@demo.com",
			"first_name": "Construction",
			"last_name": "Manager",
			"roles": ["Construction Manager", "Employee"]
		},
		{
			"email": "quality.inspector@demo.com", 
			"first_name": "Quality",
			"last_name": "Inspector",
			"roles": ["Quality Inspector", "Employee"]
		},
		{
			"email": "site.supervisor@demo.com",
			"first_name": "Site", 
			"last_name": "Supervisor",
			"roles": ["Site Supervisor", "Employee"]
		}
	]
	
	created_users = []
	
	for user_data in demo_users:
		if not frappe.db.exists("User", user_data["email"]):
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": user_data["email"],
				"first_name": user_data["first_name"],
				"last_name": user_data["last_name"],
				"send_welcome_email": 0,
				"new_password": "demo123",
				"roles": [{"role": role} for role in user_data["roles"]]
			})
			user_doc.insert(ignore_permissions=True)
			created_users.append(user_data["email"])
	
	frappe.db.commit()
	
	return {
		"status": "success", 
		"message": _("Created {0} demo user accounts").format(len(created_users)),
		"users": created_users
	}

if __name__ == "__main__":
	create_sample_data()