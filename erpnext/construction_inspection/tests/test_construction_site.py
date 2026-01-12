# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import unittest
import frappe
from frappe.utils import today, add_days

class TestConstructionSite(unittest.TestCase):
	
	def setUp(self):
		"""Set up test data"""
		self.test_supplier = self.create_test_supplier()
		
	def tearDown(self):
		"""Clean up test data"""
		# Clean up test documents
		frappe.db.rollback()
	
	def create_test_supplier(self):
		"""Create a test supplier"""
		supplier_name = "Test Supplier for Construction"
		
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
	
	def test_construction_site_creation(self):
		"""Test construction site creation"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Construction Site",
			"site_code": "TEST-SITE-001",
			"supplier": self.test_supplier,
			"status": "Planning",
			"start_date": today(),
			"expected_end_date": add_days(today(), 180),
			"description": "Test construction site for unit testing"
		})
		
		site_doc.insert()
		
		# Verify the document was created
		self.assertTrue(frappe.db.exists("Construction Site", site_doc.name))
		
		# Verify default values
		self.assertEqual(site_doc.progress_percentage, 0)
		self.assertEqual(site_doc.status, "Planning")
		
	def test_site_code_validation(self):
		"""Test site code uniqueness validation"""
		
		# Create first site
		site1 = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Site 1",
			"site_code": "DUPLICATE-CODE",
			"supplier": self.test_supplier,
			"status": "Planning"
		})
		site1.insert()
		
		# Try to create second site with same code
		site2 = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Site 2", 
			"site_code": "DUPLICATE-CODE",
			"supplier": self.test_supplier,
			"status": "Planning"
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			site2.insert()
	
	def test_date_validation(self):
		"""Test date validation logic"""
		
		# Test end date before start date
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Date Validation",
			"site_code": "TEST-DATE-001",
			"supplier": self.test_supplier,
			"start_date": today(),
			"expected_end_date": add_days(today(), -30)  # End date before start date
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			site_doc.insert()
	
	def test_progress_percentage_validation(self):
		"""Test progress percentage validation"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Progress Validation",
			"site_code": "TEST-PROGRESS-001",
			"supplier": self.test_supplier,
			"progress_percentage": 150  # Invalid percentage > 100
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError):
			site_doc.insert()
	
	def test_status_workflow(self):
		"""Test status workflow transitions"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Status Workflow",
			"site_code": "TEST-STATUS-001",
			"supplier": self.test_supplier,
			"status": "Planning"
		})
		site_doc.insert()
		
		# Test valid status transitions
		valid_transitions = [
			("Planning", "Active"),
			("Active", "In Progress"),
			("In Progress", "Completed"),
			("Active", "On Hold"),
			("On Hold", "Active")
		]
		
		for from_status, to_status in valid_transitions:
			site_doc.status = from_status
			site_doc.save()
			
			site_doc.status = to_status
			site_doc.save()  # Should not raise error
			
			self.assertEqual(site_doc.status, to_status)
	
	def test_next_inspection_date_calculation(self):
		"""Test automatic next inspection date calculation"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Inspection Date",
			"site_code": "TEST-INSPECTION-001",
			"supplier": self.test_supplier,
			"status": "Active",
			"start_date": today()
		})
		site_doc.insert()
		
		# Should automatically set next inspection date
		self.assertIsNotNone(site_doc.next_inspection_date)
		
		# Should be within reasonable range (1-7 days from start)
		days_diff = (site_doc.next_inspection_date - site_doc.start_date).days
		self.assertTrue(1 <= days_diff <= 7)
	
	def test_supplier_assignment(self):
		"""Test supplier assignment and validation"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Supplier Assignment",
			"site_code": "TEST-SUPPLIER-001",
			"supplier": self.test_supplier
		})
		site_doc.insert()
		
		# Verify supplier is correctly assigned
		self.assertEqual(site_doc.supplier, self.test_supplier)
		
		# Test invalid supplier assignment
		site_doc.supplier = "Non-existent Supplier"
		
		with self.assertRaises(frappe.ValidationError):
			site_doc.save()
	
	def test_site_completion(self):
		"""Test site completion logic"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Site Completion",
			"site_code": "TEST-COMPLETION-001",
			"supplier": self.test_supplier,
			"status": "In Progress",
			"progress_percentage": 95
		})
		site_doc.insert()
		
		# Mark as completed
		site_doc.status = "Completed"
		site_doc.progress_percentage = 100
		site_doc.save()
		
		# Should automatically set actual end date
		self.assertIsNotNone(site_doc.actual_end_date)
		self.assertEqual(site_doc.actual_end_date, today())
	
	def test_site_methods(self):
		"""Test custom methods of Construction Site"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Site Methods",
			"site_code": "TEST-METHODS-001",
			"supplier": self.test_supplier,
			"status": "Active"
		})
		site_doc.insert()
		
		# Test update_progress method
		site_doc.update_progress(75)
		self.assertEqual(site_doc.progress_percentage, 75)
		
		# Test get_recent_inspections method
		recent_inspections = site_doc.get_recent_inspections()
		self.assertIsInstance(recent_inspections, list)
		
		# Test calculate_next_inspection_date method
		next_date = site_doc.calculate_next_inspection_date()
		self.assertIsNotNone(next_date)
	
	def test_site_dashboard_data(self):
		"""Test dashboard data generation"""
		
		site_doc = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": "Test Dashboard Data",
			"site_code": "TEST-DASHBOARD-001",
			"supplier": self.test_supplier,
			"status": "Active",
			"progress_percentage": 60
		})
		site_doc.insert()
		
		# Test get_dashboard_data method
		dashboard_data = site_doc.get_dashboard_data()
		
		self.assertIn("progress_percentage", dashboard_data)
		self.assertIn("status", dashboard_data)
		self.assertIn("days_since_start", dashboard_data)
		self.assertIn("inspection_summary", dashboard_data)

if __name__ == "__main__":
	unittest.main()