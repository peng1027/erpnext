# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, flt, cint

def sync_supplier_data():
	"""Sync supplier data with construction inspection module"""
	
	# Get all suppliers
	suppliers = frappe.get_all("Supplier",
		filters={"disabled": 0},
		fields=["name", "supplier_name", "supplier_group", "country", "is_frozen"]
	)
	
	for supplier in suppliers:
		update_supplier_inspection_metrics(supplier.name)

def update_supplier_inspection_metrics(supplier_name):
	"""Update inspection metrics for a supplier"""
	
	try:
		# Calculate inspection statistics
		inspection_stats = frappe.db.sql("""
			SELECT 
				COUNT(*) as total_inspections,
				AVG(overall_rating) as avg_rating,
				SUM(issues_found) as total_issues,
				COUNT(CASE WHEN approval_status = 'Approved' THEN 1 END) as approved_inspections,
				MAX(inspection_date) as last_inspection_date
			FROM `tabSupplier Inspection`
			WHERE supplier = %(supplier)s
			AND docstatus = 1
		""", {"supplier": supplier_name}, as_dict=True)
		
		stats = inspection_stats[0] if inspection_stats else {}
		
		# Update supplier document with inspection metrics
		supplier_doc = frappe.get_doc("Supplier", supplier_name)
		
		# Add custom fields if they don't exist
		add_supplier_custom_fields()
		
		# Update metrics
		supplier_doc.db_set("total_inspections", stats.get("total_inspections", 0))
		supplier_doc.db_set("average_inspection_rating", flt(stats.get("avg_rating", 0), 2))
		supplier_doc.db_set("total_inspection_issues", stats.get("total_issues", 0))
		supplier_doc.db_set("last_inspection_date", stats.get("last_inspection_date"))
		
		# Calculate approval rate
		total = stats.get("total_inspections", 0)
		approved = stats.get("approved_inspections", 0)
		approval_rate = (approved / total * 100) if total > 0 else 0
		supplier_doc.db_set("inspection_approval_rate", flt(approval_rate, 2))
		
		# Update supplier rating based on inspection performance
		update_supplier_rating(supplier_name, stats)
		
	except Exception as e:
		frappe.log_error(f"Error updating supplier inspection metrics for {supplier_name}: {str(e)}")

def add_supplier_custom_fields():
	"""Add custom fields to Supplier DocType for inspection metrics"""
	
	custom_fields = [
		{
			"fieldname": "inspection_metrics_section",
			"label": "Inspection Metrics",
			"fieldtype": "Section Break",
			"insert_after": "supplier_details"
		},
		{
			"fieldname": "total_inspections",
			"label": "Total Inspections",
			"fieldtype": "Int",
			"read_only": 1,
			"insert_after": "inspection_metrics_section"
		},
		{
			"fieldname": "average_inspection_rating",
			"label": "Average Inspection Rating",
			"fieldtype": "Float",
			"precision": 2,
			"read_only": 1,
			"insert_after": "total_inspections"
		},
		{
			"fieldname": "column_break_inspection",
			"fieldtype": "Column Break",
			"insert_after": "average_inspection_rating"
		},
		{
			"fieldname": "total_inspection_issues",
			"label": "Total Issues Found",
			"fieldtype": "Int",
			"read_only": 1,
			"insert_after": "column_break_inspection"
		},
		{
			"fieldname": "inspection_approval_rate",
			"label": "Inspection Approval Rate (%)",
			"fieldtype": "Float",
			"precision": 2,
			"read_only": 1,
			"insert_after": "total_inspection_issues"
		},
		{
			"fieldname": "last_inspection_date",
			"label": "Last Inspection Date",
			"fieldtype": "Date",
			"read_only": 1,
			"insert_after": "inspection_approval_rate"
		}
	]
	
	for field in custom_fields:
		if not frappe.db.exists("Custom Field", {"dt": "Supplier", "fieldname": field["fieldname"]}):
			custom_field = frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Supplier",
				**field
			})
			custom_field.insert(ignore_permissions=True)

def update_supplier_rating(supplier_name, inspection_stats):
	"""Update supplier rating based on inspection performance"""
	
	try:
		total_inspections = inspection_stats.get("total_inspections", 0)
		avg_rating = inspection_stats.get("avg_rating", 0)
		total_issues = inspection_stats.get("total_issues", 0)
		approved_inspections = inspection_stats.get("approved_inspections", 0)
		
		if total_inspections == 0:
			return
		
		# Calculate performance score (0-100)
		rating_score = (avg_rating / 5.0) * 40  # 40% weight for rating
		approval_score = (approved_inspections / total_inspections) * 30  # 30% weight for approval rate
		issue_score = max(0, 30 - (total_issues / total_inspections) * 10)  # 30% weight for issue rate
		
		performance_score = rating_score + approval_score + issue_score
		
		# Determine supplier grade
		if performance_score >= 90:
			grade = "A+"
		elif performance_score >= 80:
			grade = "A"
		elif performance_score >= 70:
			grade = "B"
		elif performance_score >= 60:
			grade = "C"
		else:
			grade = "D"
		
		# Update supplier document
		supplier_doc = frappe.get_doc("Supplier", supplier_name)
		supplier_doc.db_set("inspection_performance_score", flt(performance_score, 2))
		supplier_doc.db_set("inspection_grade", grade)
		
	except Exception as e:
		frappe.log_error(f"Error updating supplier rating for {supplier_name}: {str(e)}")

@frappe.whitelist()
def get_supplier_inspection_history(supplier_name, limit=20):
	"""Get inspection history for a supplier"""
	
	inspections = frappe.get_all("Supplier Inspection",
		filters={
			"supplier": supplier_name,
			"docstatus": 1
		},
		fields=[
			"name", "construction_site", "inspection_date", "inspector", 
			"overall_rating", "approval_status", "issues_found", "corrective_actions_required"
		],
		order_by="inspection_date desc",
		limit=limit
	)
	
	# Get construction site names
	for inspection in inspections:
		site_doc = frappe.get_doc("Construction Site", inspection.construction_site)
		inspection["site_name"] = site_doc.site_name
	
	return inspections

@frappe.whitelist()
def get_supplier_performance_analytics(supplier_name):
	"""Get detailed performance analytics for a supplier"""
	
	# Basic statistics
	stats = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_inspections,
			AVG(overall_rating) as avg_rating,
			SUM(issues_found) as total_issues,
			COUNT(CASE WHEN approval_status = 'Approved' THEN 1 END) as approved_inspections,
			MIN(inspection_date) as first_inspection,
			MAX(inspection_date) as last_inspection
		FROM `tabSupplier Inspection`
		WHERE supplier = %(supplier)s
		AND docstatus = 1
	""", {"supplier": supplier_name}, as_dict=True)
	
	basic_stats = stats[0] if stats else {}
	
	# Monthly trend data
	monthly_trend = frappe.db.sql("""
		SELECT 
			DATE_FORMAT(inspection_date, '%%Y-%%m') as month,
			COUNT(*) as inspection_count,
			AVG(overall_rating) as avg_rating,
			SUM(issues_found) as total_issues
		FROM `tabSupplier Inspection`
		WHERE supplier = %(supplier)s
		AND docstatus = 1
		AND inspection_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
		GROUP BY DATE_FORMAT(inspection_date, '%%Y-%%m')
		ORDER BY month
	""", {"supplier": supplier_name}, as_dict=True)
	
	# Rating distribution
	rating_distribution = frappe.db.sql("""
		SELECT 
			CASE 
				WHEN overall_rating >= 4.5 THEN 'Excellent (4.5-5.0)'
				WHEN overall_rating >= 3.5 THEN 'Good (3.5-4.4)'
				WHEN overall_rating >= 2.5 THEN 'Average (2.5-3.4)'
				WHEN overall_rating >= 1.5 THEN 'Poor (1.5-2.4)'
				ELSE 'Very Poor (0-1.4)'
			END as rating_range,
			COUNT(*) as count
		FROM `tabSupplier Inspection`
		WHERE supplier = %(supplier)s
		AND docstatus = 1
		GROUP BY rating_range
		ORDER BY MIN(overall_rating) DESC
	""", {"supplier": supplier_name}, as_dict=True)
	
	# Site performance
	site_performance = frappe.db.sql("""
		SELECT 
			cs.site_name,
			COUNT(si.name) as inspection_count,
			AVG(si.overall_rating) as avg_rating,
			SUM(si.issues_found) as total_issues
		FROM `tabSupplier Inspection` si
		INNER JOIN `tabConstruction Site` cs ON cs.name = si.construction_site
		WHERE si.supplier = %(supplier)s
		AND si.docstatus = 1
		GROUP BY si.construction_site, cs.site_name
		ORDER BY avg_rating DESC
	""", {"supplier": supplier_name}, as_dict=True)
	
	return {
		"supplier_name": supplier_name,
		"basic_statistics": basic_stats,
		"monthly_trend": monthly_trend,
		"rating_distribution": rating_distribution,
		"site_performance": site_performance
	}

@frappe.whitelist()
def create_supplier_performance_report(supplier_name):
	"""Create a detailed performance report for a supplier"""
	
	analytics = get_supplier_performance_analytics(supplier_name)
	
	# Create report document
	report_doc = frappe.get_doc({
		"doctype": "Supplier Performance Report",
		"supplier": supplier_name,
		"report_date": today(),
		"total_inspections": analytics["basic_statistics"].get("total_inspections", 0),
		"average_rating": flt(analytics["basic_statistics"].get("avg_rating", 0), 2),
		"total_issues": analytics["basic_statistics"].get("total_issues", 0),
		"approval_rate": calculate_approval_rate(analytics["basic_statistics"]),
		"performance_grade": get_supplier_grade(supplier_name),
		"report_data": frappe.as_json(analytics)
	})
	
	report_doc.insert()
	return report_doc.name

def calculate_approval_rate(stats):
	"""Calculate approval rate from statistics"""
	total = stats.get("total_inspections", 0)
	approved = stats.get("approved_inspections", 0)
	return flt((approved / total * 100) if total > 0 else 0, 2)

def get_supplier_grade(supplier_name):
	"""Get current supplier grade"""
	supplier_doc = frappe.get_doc("Supplier", supplier_name)
	return getattr(supplier_doc, "inspection_grade", "Not Rated")

@frappe.whitelist()
def get_top_performing_suppliers(limit=10):
	"""Get top performing suppliers based on inspection metrics"""
	
	suppliers = frappe.db.sql("""
		SELECT 
			s.name,
			s.supplier_name,
			s.average_inspection_rating,
			s.total_inspections,
			s.inspection_approval_rate,
			s.inspection_grade
		FROM `tabSupplier` s
		WHERE s.disabled = 0
		AND s.total_inspections > 0
		ORDER BY s.average_inspection_rating DESC, s.inspection_approval_rate DESC
		LIMIT %(limit)s
	""", {"limit": limit}, as_dict=True)
	
	return suppliers

@frappe.whitelist()
def get_suppliers_needing_attention():
	"""Get suppliers that need attention based on poor performance"""
	
	suppliers = frappe.db.sql("""
		SELECT 
			s.name,
			s.supplier_name,
			s.average_inspection_rating,
			s.total_inspections,
			s.inspection_approval_rate,
			s.last_inspection_date,
			DATEDIFF(CURDATE(), s.last_inspection_date) as days_since_last_inspection
		FROM `tabSupplier` s
		WHERE s.disabled = 0
		AND (
			s.average_inspection_rating < 3.0
			OR s.inspection_approval_rate < 70
			OR DATEDIFF(CURDATE(), s.last_inspection_date) > 30
		)
		ORDER BY s.average_inspection_rating ASC
	""", as_dict=True)
	
	return suppliers

def update_supplier_on_inspection_submit(inspection_doc):
	"""Update supplier metrics when inspection is submitted"""
	
	if inspection_doc.supplier:
		update_supplier_inspection_metrics(inspection_doc.supplier)

def update_supplier_on_inspection_cancel(inspection_doc):
	"""Update supplier metrics when inspection is cancelled"""
	
	if inspection_doc.supplier:
		update_supplier_inspection_metrics(inspection_doc.supplier)

@frappe.whitelist()
def bulk_update_supplier_metrics():
	"""Bulk update all supplier inspection metrics (admin function)"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can run this function"))
	
	suppliers = frappe.get_all("Supplier", 
		filters={"disabled": 0},
		fields=["name"]
	)
	
	updated_count = 0
	
	for supplier in suppliers:
		try:
			update_supplier_inspection_metrics(supplier.name)
			updated_count += 1
		except Exception as e:
			frappe.log_error(f"Error updating metrics for supplier {supplier.name}: {str(e)}")
	
	return {
		"status": "success",
		"message": _("Updated metrics for {0} suppliers").format(updated_count)
	}

@frappe.whitelist()
def create_supplier_inspection_template(supplier_name, template_name):
	"""Create inspection template specific to a supplier"""
	
	# Get recent inspections for this supplier to create template
	recent_inspections = frappe.get_all("Supplier Inspection",
		filters={
			"supplier": supplier_name,
			"docstatus": 1
		},
		fields=["name"],
		order_by="inspection_date desc",
		limit=5
	)
	
	if not recent_inspections:
		frappe.throw(_("No approved inspections found for supplier {0}").format(supplier_name))
	
	# Get common checklist items from recent inspections
	common_items = get_common_checklist_items(recent_inspections)
	
	# Create template document
	template_doc = frappe.get_doc({
		"doctype": "Inspection Template",
		"template_name": template_name,
		"supplier": supplier_name,
		"is_active": 1,
		"checklist_items": common_items
	})
	
	template_doc.insert()
	return template_doc.name

def get_common_checklist_items(inspection_list):
	"""Get common checklist items from multiple inspections"""
	
	# This would analyze checklist items from multiple inspections
	# and return the most commonly used items
	# Implementation would depend on the specific checklist structure
	
	common_items = []
	
	# Placeholder implementation
	default_items = [
		{
			"check_item": "Safety Equipment Check",
			"description": "Verify all safety equipment is available and functional",
			"is_mandatory": 1,
			"weight": 20
		},
		{
			"check_item": "Work Quality Assessment",
			"description": "Assess the quality of completed work",
			"is_mandatory": 1,
			"weight": 30
		},
		{
			"check_item": "Site Cleanliness",
			"description": "Check site cleanliness and organization",
			"is_mandatory": 0,
			"weight": 15
		}
	]
	
	return default_items