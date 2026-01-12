# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from . import __version__ as app_version

app_name = "construction_inspection"
app_title = "Construction Inspection"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Supplier Construction Site Inspection Management System"
app_icon = "fa fa-hard-hat"
app_color = "blue"
app_email = "developers@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/construction_inspection/css/construction_inspection.css"
# app_include_js = "/assets/construction_inspection/js/construction_inspection.js"

# include js, css files in header of web template
# web_include_css = "/assets/construction_inspection/css/construction_inspection.css"
# web_include_js = "/assets/construction_inspection/js/construction_inspection.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "construction_inspection/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Construction Site": "public/js/construction_site.js",
	"Supplier Inspection": "public/js/supplier_inspection.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "construction_inspection.utils.jinja_methods",
# 	"filters": "construction_inspection.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "construction_inspection.install.before_install"
# after_install = "construction_inspection.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "construction_inspection.uninstall.before_uninstall"
# after_uninstall = "construction_inspection.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "construction_inspection.config.construction_inspection.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Supplier Inspection": {
		"on_submit": "construction_inspection.construction_inspection.doctype.supplier_inspection.supplier_inspection.on_inspection_submit",
		"on_cancel": "construction_inspection.construction_inspection.doctype.supplier_inspection.supplier_inspection.on_inspection_cancel",
		"validate": "construction_inspection.construction_inspection.doctype.supplier_inspection.supplier_inspection.validate_inspection"
	},
	"Construction Site": {
		"on_update": "construction_inspection.construction_inspection.doctype.construction_site.construction_site.update_site_progress",
		"validate": "construction_inspection.construction_inspection.doctype.construction_site.construction_site.validate_site_data"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"construction_inspection.tasks.daily.send_inspection_reminders",
		"construction_inspection.tasks.daily.update_site_progress_summary"
	],
	"weekly": [
		"construction_inspection.tasks.weekly.generate_weekly_reports",
		"construction_inspection.tasks.weekly.cleanup_old_inspection_photos"
	],
	"monthly": [
		"construction_inspection.tasks.monthly.generate_monthly_analytics",
		"construction_inspection.tasks.monthly.archive_completed_inspections"
	]
}

# Testing
# -------

# before_tests = "construction_inspection.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "construction_inspection.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "construction_inspection.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"partial": 1,
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"construction_inspection.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []

# Website
# --------

# website_route_rules = [
# 	{"from_route": "/construction-inspection/<path:app_path>", "to_route": "construction-inspection"},
# ]

# Website context
# ----------------
# provide a context for website pages
# website_context = {
# 	"favicon": "/assets/construction_inspection/images/favicon.png",
# 	"splash_image": "/assets/construction_inspection/images/splash.png"
# }

# Boot Session
# ----------------
# boot_session = "construction_inspection.boot.boot_session"

# Fixtures
# --------
# fixtures = ["Custom Field", "Property Setter", "Custom Script"]

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": [
			["module", "=", "Construction Inspection"]
		]
	},
	{
		"doctype": "Property Setter", 
		"filters": [
			["module", "=", "Construction Inspection"]
		]
	},
	{
		"doctype": "Workflow",
		"filters": [
			["document_type", "in", ["Supplier Inspection", "Construction Site"]]
		]
	},
	{
		"doctype": "Workflow State",
		"filters": [
			["workflow", "in", ["Supplier Inspection Workflow", "Construction Site Workflow"]]
		]
	},
	{
		"doctype": "Workflow Action Master",
		"filters": [
			["workflow_state", "in", ["Draft", "Under Review", "Approved", "Rejected"]]
		]
	}
]

# Migrating
# ---------
# before_migrate = "construction_inspection.migrate.before_migrate"
# after_migrate = "construction_inspection.migrate.after_migrate"

# Website
# --------
# website_route_rules = [
# 	{"from_route": "/mobile-inspection", "to_route": "construction_inspection/www/mobile-inspection.html"},
# 	{"from_route": "/inspection-dashboard", "to_route": "construction_inspection/www/inspection-dashboard.html"}
# ]

# Regional
# --------
# regional_overrides = {
# 	"France": {
# 		"erpnext.tests.test_regional.test_method": "erpnext.regional.france.utils.test_method"
# 	}
# }

# Bootinfo
# --------
# boot_session = "construction_inspection.boot.get_bootinfo"

# Standard Portal Items
# ---------------------
# To add custom portal items, uncomment and add to the list
# standard_portal_menu_items = [
# 	{
# 		"title": _("Construction Inspections"),
# 		"route": "/construction-inspections",
# 		"reference_doctype": "Supplier Inspection",
# 		"role": "Supplier"
# 	}
# ]

# Has Permission
# --------------
# has_permission = {
# 	"Construction Site": "construction_inspection.construction_inspection.doctype.construction_site.construction_site.has_permission",
# 	"Supplier Inspection": "construction_inspection.construction_inspection.doctype.supplier_inspection.supplier_inspection.has_permission"
# }

# Override standard portal items
# -------------------------------
# standard_portal_menu_items = [
# 	{
# 		"title": _("Projects"),
# 		"route": "/projects",
# 		"reference_doctype": "Project",
# 		"role": "Customer"
# 	}
# ]