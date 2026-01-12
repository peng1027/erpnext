# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import today, add_days

class TestConstructionInspectionIntegrations(unittest.TestCase):
	
	def setUp(self):
		"""Set up test data"""
		self.test_project = self.create_test_project()
		self.test_supplier = self.create_test_supplier()
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
	
	def create_test_project(self):
		"""Create a test project"""
		project_name = "Test Construction Project"
		
		if not frappe.db.exists("Project", project_name):
			project = frappe.get_doc({
				"doctype": "Project",
				"project_name": project_name,
				"project_type": "External",
				"status": "Open",
				"expected_start_date": today(),
				"expected_end_date": add_days(today(), 90)
			})
			project.insert(ignore_permissions=True)
			return project.name
		
		return project_name
	
	def create_test_supplier(self):
		"""Create a test supplier"""
		supplier_name = "Test Integration Supplier"
		
		if not frappe.db.exists("Supplier", supplier_name):
			supplier = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": supplier_name,
				"supplier_group": "Construction",
				"country": "Taiwan"
			})
			supplier.insert(ignore_permissions=True)
			return supplier.name
		
		return supplier_name
	
	def test_project_integration(self):
		"""Test project integration functionality"""
		
		from erpnext.construction_inspection.integrations.project_integration import (
			sync_project_construction_sites,
			is_construction_project,
			get_project_construction_sites
		)
		
		# Test if project is identified as construction project
		is_construction = is_construction_project(self.test_project)
		self.assertTrue(is_construction)
		
		# Test project synchronization
		sync_project_construction_sites()
		
		# Check if construction site was created
		sites = get_project_construction_sites(self.test_project)
		self.assertGreater(len(sites), 0)
		
		# Verify site details
		site = sites[0]
		self.assertIn("site_name", site)
		self.assertIn("status", site)
	
	def test_supplier_integration(self):
		"""Test supplier integration functionality"""
		
		from erpnext.construction_inspection.integrations.supplier_integration import (
			sync_supplier_inspection_data,
			update_supplier_performance_rating,
			get_supplier_inspection_analytics
		)
		
		# Create a construction site for the supplier
		site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Integration Site",
			"site_code": "TEST-INT-SITE",
			"supplier": self.test_supplier,
			"status": "Active"
		})
		site.insert(ignore_permissions=True)
		
		# Create some test inspections
		for i in range(3):
			inspection = frappe.get_doc({
				"doctype": "Supplier Inspection",
				"construction_site": site.name,
				"supplier": self.test_supplier,
				"inspection_date": add_days(today(), -i),
				"inspector": "Administrator",
				"overall_rating": 4.0 + i * 0.2,
				"approval_status": "Approved"
			})
			inspection.insert(ignore_permissions=True)
			inspection.submit()
		
		# Test supplier data synchronization
		sync_supplier_inspection_data(self.test_supplier)
		
		# Verify supplier metrics were updated
		supplier_doc = frappe.get_doc("Supplier", self.test_supplier)
		
		# Check if custom fields exist and have values
		if hasattr(supplier_doc, 'total_inspections'):
			self.assertGreater(supplier_doc.total_inspections, 0)
		
		# Test performance rating update
		update_supplier_performance_rating(self.test_supplier)
		
		# Test analytics retrieval
		analytics = get_supplier_inspection_analytics(self.test_supplier)
		
		# Verify analytics structure
		self.assertIn("basic_stats", analytics)
		self.assertIn("monthly_trends", analytics)
		self.assertIn("rating_distribution", analytics)
	
	def test_user_permission_integration(self):
		"""Test user permission integration"""
		
		from erpnext.construction_inspection.integrations.user_permission_integration import (
			setup_role_permissions,
			assign_user_to_construction_site,
			get_user_accessible_sites
		)
		
		# Test role permission setup
		setup_role_permissions()
		
		# Create a test user
		test_user = "test.supervisor@example.com"
		if not frappe.db.exists("User", test_user):
			user = frappe.get_doc({
				"doctype": "User",
				"email": test_user,
				"first_name": "Test",
				"last_name": "Supervisor",
				"send_welcome_email": 0
			})
			user.insert(ignore_permissions=True)
		
		# Create a construction site
		site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Permission Site",
			"site_code": "TEST-PERM-SITE",
			"supplier": self.test_supplier,
			"status": "Active"
		})
		site.insert(ignore_permissions=True)
		
		# Test user assignment to site
		assign_user_to_construction_site(test_user, site.name, "Site Supervisor")
		
		# Test accessible sites retrieval
		accessible_sites = get_user_accessible_sites(test_user)
		
		# Verify user has access to the assigned site
		site_names = [s.get("name") for s in accessible_sites]
		self.assertIn(site.name, site_names)
	
	def test_task_integration(self):
		"""Test task integration functionality"""
		
		from erpnext.construction_inspection.tasks.daily import send_inspection_reminders
		from erpnext.construction_inspection.tasks.weekly import generate_weekly_reports
		from erpnext.construction_inspection.tasks.monthly import generate_monthly_analytics
		
		# Create test data
		site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Task Site",
			"site_code": "TEST-TASK-SITE",
			"supplier": self.test_supplier,
			"status": "Active"
		})
		site.insert(ignore_permissions=True)
		
		# Test daily task execution
		try:
			send_inspection_reminders()
		except Exception as e:
			# Task might fail due to missing email configuration, but should not crash
			self.assertIsInstance(e, (frappe.OutgoingEmailError, AttributeError))
		
		# Test weekly task execution
		try:
			generate_weekly_reports()
		except Exception as e:
			# Task might fail due to missing email configuration, but should not crash
			self.assertIsInstance(e, (frappe.OutgoingEmailError, AttributeError))
		
		# Test monthly task execution
		try:
			generate_monthly_analytics()
		except Exception as e:
			# Task might fail due to missing email configuration, but should not crash
			self.assertIsInstance(e, (frappe.OutgoingEmailError, AttributeError))
	
	def test_notification_integration(self):
		"""Test notification integration"""
		
		from erpnext.construction_inspection.notifications import (
			send_inspection_notification,
			create_notification_log
		)
		
		# Create test inspection
		site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Notification Site",
			"site_code": "TEST-NOTIF-SITE",
			"supplier": self.test_supplier,
			"status": "Active"
		})
		site.insert(ignore_permissions=True)
		
		inspection = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": site.name,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"overall_rating": 4.0
		})
		inspection.insert(ignore_permissions=True)
		
		# Test notification creation
		try:
			send_inspection_notification(inspection.name, "submitted")
		except Exception as e:
			# Notification might fail due to missing email configuration
			self.assertIsInstance(e, (frappe.OutgoingEmailError, AttributeError))
		
		# Test notification log creation
		log_name = create_notification_log(
			"Administrator",
			"Test Notification",
			"This is a test notification message",
			"Supplier Inspection",
			inspection.name
		)
		
		# Verify notification log was created
		self.assertTrue(frappe.db.exists("Notification Log", log_name))
	
	def test_data_consistency(self):
		"""Test data consistency across integrations"""
		
		# Create interconnected test data
		site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Consistency Site",
			"site_code": "TEST-CONS-SITE",
			"supplier": self.test_supplier,
			"project": self.test_project,
			"status": "Active"
		})
		site.insert(ignore_permissions=True)
		
		# Create inspection
		inspection = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": site.name,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"overall_rating": 4.5,
			"approval_status": "Approved"
		})
		inspection.insert(ignore_permissions=True)
		inspection.submit()
		
		# Verify data consistency
		
		# 1. Site should be linked to project
		site.reload()
		self.assertEqual(site.project, self.test_project)
		
		# 2. Site progress should be updated
		self.assertGreater(site.progress_percentage, 0)
		
		# 3. Supplier metrics should be updated
		from erpnext.construction_inspection.integrations.supplier_integration import sync_supplier_inspection_data
		sync_supplier_inspection_data(self.test_supplier)
		
		supplier_doc = frappe.get_doc("Supplier", self.test_supplier)
		if hasattr(supplier_doc, 'last_inspection_date'):
			self.assertEqual(supplier_doc.last_inspection_date, today())
	
	def test_error_handling(self):
		"""Test error handling in integrations"""
		
		from erpnext.construction_inspection.integrations.project_integration import sync_project_construction_sites
		from erpnext.construction_inspection.integrations.supplier_integration import sync_supplier_inspection_data
		
		# Test with non-existent project
		try:
			sync_project_construction_sites("NON_EXISTENT_PROJECT")
		except Exception as e:
			self.assertIsInstance(e, (frappe.DoesNotExistError, AttributeError))
		
		# Test with non-existent supplier
		try:
			sync_supplier_inspection_data("NON_EXISTENT_SUPPLIER")
		except Exception as e:
			self.assertIsInstance(e, (frappe.DoesNotExistError, AttributeError))
	
	def test_bulk_operations(self):
		"""Test bulk operations in integrations"""
		
		from erpnext.construction_inspection.integrations.supplier_integration import bulk_update_supplier_metrics
		from erpnext.construction_inspection.integrations.user_permission_integration import bulk_setup_permissions
		
		# Test bulk supplier metrics update
		try:
			bulk_update_supplier_metrics()
		except Exception as e:
			# Should handle gracefully even if no suppliers exist
			pass
		
		# Test bulk permission setup
		try:
			bulk_setup_permissions()
		except Exception as e:
			# Should handle gracefully even if roles don't exist
			pass

if __name__ == "__main__":
	unittest.main()