# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	"""返回模組配置數據"""
	return [
		{
			"label": _("Construction Management"),
			"items": [
				{
					"type": "doctype",
					"name": "Construction Site",
					"label": _("Construction Site"),
					"description": _("Manage construction sites and their details"),
					"onboard": 1,
				},
				{
					"type": "doctype", 
					"name": "Supplier Inspection",
					"label": _("Supplier Inspection"),
					"description": _("Record and manage supplier inspections"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Inspection Checklist Item", 
					"label": _("Inspection Checklist Item"),
					"description": _("Manage inspection checklist items"),
				}
			]
		},
		{
			"label": _("Mobile & Web Apps"),
			"items": [
				{
					"type": "page",
					"name": "mobile-inspection",
					"label": _("Mobile Inspection App"),
					"description": _("Mobile-optimized inspection interface"),
					"route": "/construction_inspection/www/mobile-inspection.html"
				},
				{
					"type": "page", 
					"name": "inspection-dashboard",
					"label": _("Inspection Dashboard"),
					"description": _("Real-time inspection analytics and monitoring"),
					"route": "/construction_inspection/www/inspection-dashboard.html"
				}
			]
		},
		{
			"label": _("Reports & Analytics"),
			"items": [
				{
					"type": "report",
					"name": "Inspection Summary",
					"label": _("Inspection Summary"),
					"description": _("Comprehensive inspection summary report"),
					"is_query_report": True,
					"onboard": 1,
				},
				{
					"type": "report",
					"name": "Site Progress Report", 
					"label": _("Site Progress Report"),
					"description": _("Track construction site progress"),
					"is_query_report": True,
				},
				{
					"type": "report",
					"name": "Supplier Performance Report",
					"label": _("Supplier Performance Report"), 
					"description": _("Analyze supplier performance metrics"),
					"is_query_report": True,
				}
			]
		},
		{
			"label": _("Setup & Configuration"),
			"items": [
				{
					"type": "doctype",
					"name": "Construction Inspection Settings",
					"label": _("Construction Inspection Settings"),
					"description": _("Configure inspection parameters and workflows"),
				}
			]
		}
	]


def get_permissions():
	"""返回權限配置"""
	return {
		"Construction Site": {
			"System Manager": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
			"Construction Manager": ["read", "write", "create", "submit", "cancel"],
			"Quality Inspector": ["read", "write", "create"],
			"Site Supervisor": ["read", "write"],
			"Supplier": ["read"]
		},
		"Supplier Inspection": {
			"System Manager": ["read", "write", "create", "delete", "submit", "cancel", "amend"],
			"Construction Manager": ["read", "write", "create", "submit", "cancel"],
			"Quality Inspector": ["read", "write", "create", "submit"],
			"Site Supervisor": ["read", "write", "create"],
			"Supplier": ["read"]
		},
		"Inspection Checklist Item": {
			"System Manager": ["read", "write", "create", "delete"],
			"Construction Manager": ["read", "write", "create"],
			"Quality Inspector": ["read", "write", "create"],
			"Site Supervisor": ["read", "write"]
		}
	}


def get_workflows():
	"""返回工作流程配置"""
	return {
		"Supplier Inspection": {
			"states": [
				{
					"state": "Draft",
					"doc_status": 0,
					"allow_edit": ["Construction Manager", "Quality Inspector", "Site Supervisor"],
					"next_action_email_template": "Inspection Draft Created"
				},
				{
					"state": "Under Review", 
					"doc_status": 0,
					"allow_edit": ["Construction Manager", "Quality Inspector"],
					"next_action_email_template": "Inspection Under Review"
				},
				{
					"state": "Approved",
					"doc_status": 1,
					"allow_edit": [],
					"next_action_email_template": "Inspection Approved"
				},
				{
					"state": "Rejected",
					"doc_status": 0,
					"allow_edit": ["Construction Manager", "Quality Inspector", "Site Supervisor"],
					"next_action_email_template": "Inspection Rejected"
				},
				{
					"state": "Cancelled",
					"doc_status": 2,
					"allow_edit": [],
					"next_action_email_template": "Inspection Cancelled"
				}
			],
			"transitions": [
				{
					"state": "Draft",
					"action": "Submit for Review",
					"next_state": "Under Review",
					"allowed": ["Construction Manager", "Quality Inspector", "Site Supervisor"],
					"condition": "doc.overall_rating > 0"
				},
				{
					"state": "Under Review",
					"action": "Approve",
					"next_state": "Approved", 
					"allowed": ["Construction Manager"],
					"condition": "doc.overall_rating >= 2.5"
				},
				{
					"state": "Under Review",
					"action": "Reject",
					"next_state": "Rejected",
					"allowed": ["Construction Manager"],
					"condition": ""
				},
				{
					"state": "Rejected",
					"action": "Resubmit",
					"next_state": "Under Review",
					"allowed": ["Quality Inspector", "Site Supervisor"],
					"condition": "doc.corrective_actions"
				},
				{
					"state": "Draft",
					"action": "Cancel",
					"next_state": "Cancelled",
					"allowed": ["Construction Manager"],
					"condition": ""
				},
				{
					"state": "Under Review", 
					"action": "Cancel",
					"next_state": "Cancelled",
					"allowed": ["Construction Manager"],
					"condition": ""
				}
			]
		}
	}


def get_notification_config():
	"""返回通知配置"""
	return [
		{
			"doctype": "Supplier Inspection",
			"subject": "New Inspection Created: {{ doc.name }}",
			"message": """
				<p>A new supplier inspection has been created:</p>
				<ul>
					<li><strong>Site:</strong> {{ doc.construction_site }}</li>
					<li><strong>Inspector:</strong> {{ doc.inspector }}</li>
					<li><strong>Date:</strong> {{ doc.inspection_date }}</li>
					<li><strong>Overall Rating:</strong> {{ doc.overall_rating }}</li>
				</ul>
				<p><a href="/app/supplier-inspection/{{ doc.name }}">View Inspection</a></p>
			""",
			"event": "on_submit",
			"method": "Email",
			"recipients": [
				{"role": "Construction Manager"},
				{"role": "Quality Inspector"}
			],
			"condition": "doc.overall_rating < 3.0"
		},
		{
			"doctype": "Supplier Inspection", 
			"subject": "Inspection Approved: {{ doc.name }}",
			"message": """
				<p>Supplier inspection has been approved:</p>
				<ul>
					<li><strong>Site:</strong> {{ doc.construction_site }}</li>
					<li><strong>Overall Rating:</strong> {{ doc.overall_rating }}</li>
					<li><strong>Status:</strong> {{ doc.status }}</li>
				</ul>
			""",
			"event": "on_update_after_submit",
			"method": "Email",
			"recipients": [
				{"field": "inspector"},
				{"role": "Site Supervisor"}
			],
			"condition": "doc.status == 'Approved'"
		},
		{
			"doctype": "Construction Site",
			"subject": "Site Progress Update: {{ doc.site_name }}",
			"message": """
				<p>Construction site progress has been updated:</p>
				<ul>
					<li><strong>Site:</strong> {{ doc.site_name }}</li>
					<li><strong>Progress:</strong> {{ doc.progress_percentage }}%</li>
					<li><strong>Status:</strong> {{ doc.status }}</li>
				</ul>
			""",
			"event": "on_update",
			"method": "Email", 
			"recipients": [
				{"role": "Construction Manager"},
				{"field": "project_manager"}
			],
			"condition": "doc.progress_percentage >= 25 and doc.progress_percentage % 25 == 0"
		}
	]


def get_dashboard_charts():
	"""返回儀表板圖表配置"""
	return [
		{
			"chart_name": "Inspection Rating Trend",
			"chart_type": "Line",
			"doctype": "Supplier Inspection",
			"based_on": "inspection_date",
			"value_based_on": "overall_rating",
			"time_interval": "Monthly",
			"timeseries": 1,
			"filters_json": '{"docstatus": 1}',
			"custom_options": {
				"type": "line",
				"colors": ["#667eea"],
				"axisOptions": {
					"xIsSeries": 1
				}
			}
		},
		{
			"chart_name": "Supplier Performance",
			"chart_type": "Bar", 
			"doctype": "Supplier Inspection",
			"based_on": "supplier",
			"value_based_on": "overall_rating",
			"aggregate_function": "Average",
			"filters_json": '{"docstatus": 1}',
			"custom_options": {
				"type": "bar",
				"colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
			}
		},
		{
			"chart_name": "Inspection Status Distribution",
			"chart_type": "Donut",
			"doctype": "Supplier Inspection", 
			"based_on": "status",
			"filters_json": '{"docstatus": 1}',
			"custom_options": {
				"type": "donut",
				"colors": ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
			}
		}
	]