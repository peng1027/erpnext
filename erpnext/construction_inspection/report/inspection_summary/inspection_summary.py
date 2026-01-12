# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today, add_days


def execute(filters=None):
	"""執行巡檢摘要報表"""
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	
	return columns, data, None, chart


def get_columns():
	"""定義報表欄位"""
	return [
		{
			"label": _("Construction Site"),
			"fieldname": "construction_site",
			"fieldtype": "Link",
			"options": "Construction Site",
			"width": 200
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},
		{
			"label": _("Inspection Date"),
			"fieldname": "inspection_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Inspector"),
			"fieldname": "inspector",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Safety Rating"),
			"fieldname": "safety_rating",
			"fieldtype": "Float",
			"width": 100,
			"precision": 1
		},
		{
			"label": _("Quality Rating"),
			"fieldname": "quality_rating",
			"fieldtype": "Float",
			"width": 100,
			"precision": 1
		},
		{
			"label": _("Progress Rating"),
			"fieldname": "progress_rating",
			"fieldtype": "Float",
			"width": 100,
			"precision": 1
		},
		{
			"label": _("Overall Rating"),
			"fieldname": "overall_rating",
			"fieldtype": "Float",
			"width": 100,
			"precision": 1
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Issues Found"),
			"fieldname": "issues_count",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Corrective Actions"),
			"fieldname": "corrective_actions_count",
			"fieldtype": "Int",
			"width": 120
		}
	]


def get_data(filters):
	"""獲取報表數據"""
	conditions = get_conditions(filters)
	
	data = frappe.db.sql(f"""
		SELECT 
			si.construction_site,
			cs.supplier,
			si.inspection_date,
			si.inspector,
			si.safety_compliance_rating as safety_rating,
			si.quality_rating,
			si.progress_rating,
			si.overall_rating,
			si.status,
			(SELECT COUNT(*) FROM `tabInspection Checklist Item` 
			 WHERE parent = si.name AND status = 'Fail') as issues_count,
			(SELECT COUNT(*) FROM `tabInspection Checklist Item` 
			 WHERE parent = si.name AND corrective_action IS NOT NULL 
			 AND corrective_action != '') as corrective_actions_count
		FROM 
			`tabSupplier Inspection` si
		LEFT JOIN 
			`tabConstruction Site` cs ON si.construction_site = cs.name
		WHERE 
			si.docstatus = 1 {conditions}
		ORDER BY 
			si.inspection_date DESC, si.overall_rating DESC
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""構建查詢條件"""
	conditions = ""
	
	if filters.get("from_date"):
		conditions += " AND si.inspection_date >= %(from_date)s"
	
	if filters.get("to_date"):
		conditions += " AND si.inspection_date <= %(to_date)s"
	
	if filters.get("construction_site"):
		conditions += " AND si.construction_site = %(construction_site)s"
	
	if filters.get("supplier"):
		conditions += " AND cs.supplier = %(supplier)s"
	
	if filters.get("inspector"):
		conditions += " AND si.inspector = %(inspector)s"
	
	if filters.get("min_rating"):
		conditions += " AND si.overall_rating >= %(min_rating)s"
	
	if filters.get("max_rating"):
		conditions += " AND si.overall_rating <= %(max_rating)s"
	
	if filters.get("status"):
		conditions += " AND si.status = %(status)s"
	
	return conditions


def get_chart_data(data):
	"""生成圖表數據"""
	if not data:
		return None
	
	# 評分分布圖表
	rating_ranges = {
		"優秀 (4.5-5.0)": 0,
		"良好 (3.5-4.4)": 0,
		"一般 (2.5-3.4)": 0,
		"待改進 (1.0-2.4)": 0
	}
	
	for row in data:
		rating = flt(row.get("overall_rating", 0))
		if rating >= 4.5:
			rating_ranges["優秀 (4.5-5.0)"] += 1
		elif rating >= 3.5:
			rating_ranges["良好 (3.5-4.4)"] += 1
		elif rating >= 2.5:
			rating_ranges["一般 (2.5-3.4)"] += 1
		elif rating >= 1.0:
			rating_ranges["待改進 (1.0-2.4)"] += 1
	
	chart = {
		"data": {
			"labels": list(rating_ranges.keys()),
			"datasets": [
				{
					"name": "巡檢次數",
					"values": list(rating_ranges.values())
				}
			]
		},
		"type": "donut",
		"height": 300,
		"colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
	}
	
	return chart


@frappe.whitelist()
def get_inspection_analytics(filters=None):
	"""獲取巡檢分析數據"""
	if isinstance(filters, str):
		import json
		filters = json.loads(filters)
	
	conditions = get_conditions(filters or {})
	
	# 基本統計
	stats = frappe.db.sql(f"""
		SELECT 
			COUNT(*) as total_inspections,
			AVG(overall_rating) as avg_rating,
			COUNT(CASE WHEN overall_rating >= 4.5 THEN 1 END) as excellent_count,
			COUNT(CASE WHEN overall_rating < 2.5 THEN 1 END) as poor_count,
			COUNT(DISTINCT construction_site) as sites_inspected,
			COUNT(DISTINCT cs.supplier) as suppliers_involved
		FROM 
			`tabSupplier Inspection` si
		LEFT JOIN 
			`tabConstruction Site` cs ON si.construction_site = cs.name
		WHERE 
			si.docstatus = 1 {conditions}
	""", filters or {}, as_dict=1)[0]
	
	# 月度趨勢
	monthly_trend = frappe.db.sql(f"""
		SELECT 
			DATE_FORMAT(inspection_date, '%Y-%m') as month,
			COUNT(*) as inspection_count,
			AVG(overall_rating) as avg_rating
		FROM 
			`tabSupplier Inspection` si
		LEFT JOIN 
			`tabConstruction Site` cs ON si.construction_site = cs.name
		WHERE 
			si.docstatus = 1 
			AND inspection_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
			{conditions}
		GROUP BY 
			DATE_FORMAT(inspection_date, '%Y-%m')
		ORDER BY 
			month
	""", filters or {}, as_dict=1)
	
	# 供應商排名
	supplier_ranking = frappe.db.sql(f"""
		SELECT 
			cs.supplier,
			COUNT(*) as inspection_count,
			AVG(si.overall_rating) as avg_rating,
			COUNT(CASE WHEN si.overall_rating >= 4.5 THEN 1 END) as excellent_count
		FROM 
			`tabSupplier Inspection` si
		LEFT JOIN 
			`tabConstruction Site` cs ON si.construction_site = cs.name
		WHERE 
			si.docstatus = 1 {conditions}
		GROUP BY 
			cs.supplier
		HAVING 
			COUNT(*) >= 3
		ORDER BY 
			avg_rating DESC, inspection_count DESC
		LIMIT 10
	""", filters or {}, as_dict=1)
	
	return {
		"stats": stats,
		"monthly_trend": monthly_trend,
		"supplier_ranking": supplier_ranking
	}


@frappe.whitelist()
def get_inspection_filters():
	"""獲取報表篩選選項"""
	
	# 獲取施工現場列表
	sites = frappe.get_all("Construction Site", 
		fields=["name", "site_name"], 
		filters={"status": ["!=", "Completed"]},
		order_by="site_name")
	
	# 獲取供應商列表
	suppliers = frappe.get_all("Supplier", 
		fields=["name", "supplier_name"],
		order_by="supplier_name")
	
	# 獲取巡檢員列表
	inspectors = frappe.db.sql("""
		SELECT DISTINCT inspector 
		FROM `tabSupplier Inspection` 
		WHERE inspector IS NOT NULL AND inspector != ''
		ORDER BY inspector
	""", as_dict=1)
	
	return {
		"sites": sites,
		"suppliers": suppliers,
		"inspectors": [{"name": i.inspector} for i in inspectors]
	}