# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import today, add_days

class TestSupplierInspection(unittest.TestCase):
	
	def setUp(self):
		"""Set up test data"""
		self.test_supplier = self.create_test_supplier()
		self.test_site = self.create_test_construction_site()
		
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
	
	def create_test_supplier(self):
		"""Create a test supplier"""
		supplier_name = "Test Supplier for Inspection"
		
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
	
	def create_test_construction_site(self):
		"""Create a test construction site"""
		site_code = "TEST-SITE-INSPECTION"
		
		if not frappe.db.exists("Construction Site", {"site_code": site_code}):
			site = frappe.get_doc({
				"doctype": "Construction Site",
				"site_name": "Test Site for Inspection",
				"site_code": site_code,
				"supplier": self.test_supplier,
				"status": "Active"
			})
			site.insert(ignore_permissions=True)
			return site.name
		
		existing_site = frappe.get_doc("Construction Site", {"site_code": site_code})
		return existing_site.name
	
	def test_inspection_creation(self):
		"""Test supplier inspection creation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"inspection_type": "Routine",
			"description": "Test inspection for unit testing"
		})
		
		inspection_doc.insert()
		
		# Verify the document was created
		self.assertTrue(frappe.db.exists("Supplier Inspection", inspection_doc.name))
		
		# Verify default values
		self.assertEqual(inspection_doc.approval_status, "Pending")
		self.assertEqual(inspection_doc.overall_rating, 0)
	
	def test_inspection_validation(self):
		"""Test inspection validation logic"""
		
		# Test future inspection date
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": add_days(today(), 5),  # Future date
			"inspector": "Administrator"
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			inspection_doc.insert()
	
	def test_supplier_site_validation(self):
		"""Test supplier and site consistency validation"""
		
		# Create another supplier
		other_supplier = frappe.get_doc({
			"doctype": "Supplier",
			"supplier_name": "Other Test Supplier",
			"supplier_group": "Construction"
		})
		other_supplier.insert(ignore_permissions=True)
		
		# Try to create inspection with mismatched supplier and site
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": other_supplier.name,  # Different supplier than site's supplier
			"inspection_date": today(),
			"inspector": "Administrator"
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			inspection_doc.insert()
	
	def test_rating_calculation(self):
		"""Test overall rating calculation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"checklist_items": [
				{
					"check_item": "Safety Check",
					"weight": 30,
					"rating": 4,
					"status": "Pass"
				},
				{
					"check_item": "Quality Check",
					"weight": 40,
					"rating": 5,
					"status": "Pass"
				},
				{
					"check_item": "Cleanliness",
					"weight": 30,
					"rating": 3,
					"status": "Pass"
				}
			]
		})
		
		inspection_doc.insert()
		
		# Calculate overall rating
		inspection_doc.calculate_overall_rating()
		
		# Expected rating: (4*30 + 5*40 + 3*30) / 100 = 4.1
		expected_rating = (4*30 + 5*40 + 3*30) / 100
		self.assertEqual(inspection_doc.overall_rating, expected_rating)
	
	def test_issues_calculation(self):
		"""Test issues found calculation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"checklist_items": [
				{
					"check_item": "Safety Check",
					"status": "Pass"
				},
				{
					"check_item": "Quality Check",
					"status": "Fail"
				},
				{
					"check_item": "Cleanliness",
					"status": "Fail"
				},
				{
					"check_item": "Documentation",
					"status": "N/A"
				}
			]
		})
		
		inspection_doc.insert()
		
		# Calculate issues
		inspection_doc.calculate_issues_found()
		
		# Should find 2 issues (2 failed items)
		self.assertEqual(inspection_doc.issues_found, 2)
		
		# Should require corrective actions
		self.assertEqual(inspection_doc.corrective_actions_required, 1)
	
	def test_inspection_submission(self):
		"""Test inspection submission workflow"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"overall_rating": 4.5,
			"approval_status": "Approved"
		})
		
		inspection_doc.insert()
		inspection_doc.submit()
		
		# Verify submission
		self.assertEqual(inspection_doc.docstatus, 1)
		
		# Should update construction site progress
		site_doc = frappe.get_doc("Construction Site", self.test_site)
		self.assertIsNotNone(site_doc.last_inspection_date)
	
	def test_inspection_cancellation(self):
		"""Test inspection cancellation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"overall_rating": 4.0
		})
		
		inspection_doc.insert()
		inspection_doc.submit()
		
		# Cancel the inspection
		inspection_doc.cancel()
		
		# Verify cancellation
		self.assertEqual(inspection_doc.docstatus, 2)
	
	def test_create_follow_up_task(self):
		"""Test follow-up task creation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"issues_found": 3,
			"corrective_actions_required": 1
		})
		
		inspection_doc.insert()
		
		# Create follow-up task
		task_name = inspection_doc.create_follow_up_task()
		
		# Verify task was created
		self.assertTrue(frappe.db.exists("Task", task_name))
		
		task_doc = frappe.get_doc("Task", task_name)
		self.assertIn("Follow-up", task_doc.subject)
	
	def test_update_site_progress(self):
		"""Test site progress update"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"overall_rating": 4.5
		})
		
		inspection_doc.insert()
		
		# Get initial progress
		site_doc = frappe.get_doc("Construction Site", self.test_site)
		initial_progress = site_doc.progress_percentage
		
		# Update site progress
		inspection_doc.update_site_progress()
		
		# Reload site document
		site_doc.reload()
		
		# Progress should be updated
		self.assertGreaterEqual(site_doc.progress_percentage, initial_progress)
	
	def test_checklist_summary(self):
		"""Test checklist summary generation"""
		
		inspection_doc = frappe.get_doc({
			"doctype": "Supplier Inspection",
			"construction_site": self.test_site,
			"supplier": self.test_supplier,
			"inspection_date": today(),
			"inspector": "Administrator",
			"checklist_items": [
				{
					"check_item": "Safety Check",
					"status": "Pass",
					"is_mandatory": 1
				},
				{
					"check_item": "Quality Check", 
					"status": "Fail",
					"is_mandatory": 1
				},
				{
					"check_item": "Cleanliness",
					"status": "Pass",
					"is_mandatory": 0
				}
			]
		})
		
		inspection_doc.insert()
		
		# Get checklist summary
		summary = inspection_doc.get_checklist_summary()
		
		# Verify summary structure
		self.assertIn("total_items", summary)
		self.assertIn("passed_items", summary)
		self.assertIn("failed_items", summary)
		self.assertIn("mandatory_failed", summary)
		
		# Verify counts
		self.assertEqual(summary["total_items"], 3)
		self.assertEqual(summary["passed_items"], 2)
		self.assertEqual(summary["failed_items"], 1)
		self.assertEqual(summary["mandatory_failed"], 1)
	
	def test_inspection_analytics(self):
		"""Test inspection analytics functions"""
		
		# Create multiple inspections
		for i in range(3):
			inspection_doc = frappe.get_doc({
				"doctype": "Supplier Inspection",
				"construction_site": self.test_site,
				"supplier": self.test_supplier,
				"inspection_date": add_days(today(), -i),
				"inspector": "Administrator",
				"overall_rating": 4.0 + i * 0.2,
				"approval_status": "Approved"
			})
			inspection_doc.insert()
			inspection_doc.submit()
		
		# Test analytics functions
		from erpnext.construction_inspection.doctype.supplier_inspection.supplier_inspection import get_inspection_analytics
		
		analytics = get_inspection_analytics(self.test_site)
		
		# Verify analytics structure
		self.assertIn("total_inspections", analytics)
		self.assertIn("average_rating", analytics)
		self.assertIn("approval_rate", analytics)
		
		# Verify data
		self.assertEqual(analytics["total_inspections"], 3)
		self.assertGreater(analytics["average_rating"], 0)

if __name__ == "__main__":
	unittest.main()