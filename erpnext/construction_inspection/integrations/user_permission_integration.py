# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.permissions import add_user_permission, remove_user_permission, get_user_permissions

def setup_construction_inspection_permissions():
	"""Setup user permissions for construction inspection module"""
	
	# Setup role-based permissions
	setup_role_permissions()
	
	# Setup user-specific permissions
	setup_user_specific_permissions()
	
	# Setup supplier-based permissions
	setup_supplier_permissions()

def setup_role_permissions():
	"""Setup permissions based on user roles"""
	
	role_permissions = {
		"Construction Manager": {
			"Construction Site": ["read", "write", "create", "delete"],
			"Supplier Inspection": ["read", "write", "create", "delete", "submit", "cancel"],
			"Inspection Checklist Item": ["read", "write", "create", "delete"]
		},
		"Quality Inspector": {
			"Construction Site": ["read"],
			"Supplier Inspection": ["read", "write", "create", "submit"],
			"Inspection Checklist Item": ["read", "write", "create"]
		},
		"Site Supervisor": {
			"Construction Site": ["read"],
			"Supplier Inspection": ["read", "create"],
			"Inspection Checklist Item": ["read", "write", "create"]
		},
		"Supplier": {
			"Construction Site": ["read"],
			"Supplier Inspection": ["read"],
			"Inspection Checklist Item": ["read"]
		}
	}
	
	for role, doctypes in role_permissions.items():
		for doctype, permissions in doctypes.items():
			setup_doctype_permissions(role, doctype, permissions)

def setup_doctype_permissions(role, doctype, permissions):
	"""Setup permissions for a specific doctype and role"""
	
	try:
		# Check if permission already exists
		existing_perm = frappe.get_all("Custom DocPerm",
			filters={
				"parent": doctype,
				"role": role
			},
			limit=1
		)
		
		if existing_perm:
			return  # Permission already exists
		
		# Create permission document
		perm_doc = frappe.get_doc({
			"doctype": "Custom DocPerm",
			"parent": doctype,
			"parenttype": "DocType",
			"parentfield": "permissions",
			"role": role,
			"read": 1 if "read" in permissions else 0,
			"write": 1 if "write" in permissions else 0,
			"create": 1 if "create" in permissions else 0,
			"delete": 1 if "delete" in permissions else 0,
			"submit": 1 if "submit" in permissions else 0,
			"cancel": 1 if "cancel" in permissions else 0,
			"amend": 1 if "amend" in permissions else 0
		})
		
		perm_doc.insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error setting up permissions for {role} on {doctype}: {str(e)}")

def setup_user_specific_permissions():
	"""Setup user-specific permissions based on their assignments"""
	
	# Get all users with construction-related roles
	construction_users = frappe.db.sql("""
		SELECT DISTINCT ur.parent as user
		FROM `tabHas Role` ur
		WHERE ur.role IN ('Construction Manager', 'Quality Inspector', 'Site Supervisor', 'Supplier')
		AND ur.parenttype = 'User'
	""", as_dict=True)
	
	for user_data in construction_users:
		setup_single_user_permissions(user_data.user)

def setup_single_user_permissions(user):
	"""Setup permissions for a single user"""
	
	try:
		user_doc = frappe.get_doc("User", user)
		user_roles = [role.role for role in user_doc.roles]
		
		# Setup construction site permissions based on user assignment
		if "Site Supervisor" in user_roles:
			setup_site_supervisor_permissions(user)
		elif "Quality Inspector" in user_roles:
			setup_quality_inspector_permissions(user)
		elif "Supplier" in user_roles:
			setup_supplier_user_permissions(user)
		
	except Exception as e:
		frappe.log_error(f"Error setting up user permissions for {user}: {str(e)}")

def setup_site_supervisor_permissions(user):
	"""Setup permissions for site supervisors"""
	
	# Get construction sites assigned to this supervisor
	assigned_sites = frappe.get_all("Construction Site",
		filters={"site_supervisor": user},
		fields=["name"]
	)
	
	for site in assigned_sites:
		# Add user permission for construction site
		add_user_permission("Construction Site", site.name, user)
		
		# Add permission for inspections at this site
		site_inspections = frappe.get_all("Supplier Inspection",
			filters={"construction_site": site.name},
			fields=["name"]
		)
		
		for inspection in site_inspections:
			add_user_permission("Supplier Inspection", inspection.name, user)

def setup_quality_inspector_permissions(user):
	"""Setup permissions for quality inspectors"""
	
	# Quality inspectors can access inspections they created or are assigned to
	user_inspections = frappe.get_all("Supplier Inspection",
		filters={
			"$or": [
				{"inspector": user},
				{"owner": user}
			]
		},
		fields=["name", "construction_site"]
	)
	
	for inspection in user_inspections:
		add_user_permission("Supplier Inspection", inspection.name, user)
		add_user_permission("Construction Site", inspection.construction_site, user)

def setup_supplier_user_permissions(user):
	"""Setup permissions for supplier users"""
	
	# Get supplier linked to this user
	supplier = get_user_supplier(user)
	
	if supplier:
		# Add permission for supplier's construction sites
		supplier_sites = frappe.get_all("Construction Site",
			filters={"supplier": supplier},
			fields=["name"]
		)
		
		for site in supplier_sites:
			add_user_permission("Construction Site", site.name, user)
		
		# Add permission for supplier's inspections
		supplier_inspections = frappe.get_all("Supplier Inspection",
			filters={"supplier": supplier},
			fields=["name"]
		)
		
		for inspection in supplier_inspections:
			add_user_permission("Supplier Inspection", inspection.name, user)

def setup_supplier_permissions():
	"""Setup supplier-based permissions"""
	
	suppliers = frappe.get_all("Supplier",
		filters={"disabled": 0},
		fields=["name"]
	)
	
	for supplier in suppliers:
		setup_single_supplier_permissions(supplier.name)

def setup_single_supplier_permissions(supplier_name):
	"""Setup permissions for a single supplier"""
	
	# Get users associated with this supplier
	supplier_users = get_supplier_users(supplier_name)
	
	for user in supplier_users:
		# Add user permission for this supplier
		add_user_permission("Supplier", supplier_name, user)
		
		# Setup related permissions
		setup_supplier_user_permissions(user)

def get_user_supplier(user):
	"""Get supplier associated with a user"""
	
	# Check if user email matches supplier contact
	supplier = frappe.db.sql("""
		SELECT s.name
		FROM `tabSupplier` s
		INNER JOIN `tabDynamic Link` dl ON dl.parent = s.name
		INNER JOIN `tabContact` c ON c.name = dl.parent
		WHERE dl.link_doctype = 'Supplier'
		AND c.email_id = %(email)s
		LIMIT 1
	""", {"email": user}, as_dict=True)
	
	return supplier[0].name if supplier else None

def get_supplier_users(supplier_name):
	"""Get users associated with a supplier"""
	
	users = frappe.db.sql("""
		SELECT DISTINCT c.email_id
		FROM `tabContact` c
		INNER JOIN `tabDynamic Link` dl ON dl.parent = c.name
		WHERE dl.link_doctype = 'Supplier'
		AND dl.link_name = %(supplier)s
		AND c.email_id IS NOT NULL
	""", {"supplier": supplier_name}, as_dict=True)
	
	return [user.email_id for user in users if user.email_id]

@frappe.whitelist()
def assign_user_to_construction_site(user, site_name, role="Site Supervisor"):
	"""Assign a user to a construction site with specific role"""
	
	if not frappe.has_permission("Construction Site", "write"):
		frappe.throw(_("Insufficient permissions to assign users"))
	
	# Update construction site with user assignment
	site_doc = frappe.get_doc("Construction Site", site_name)
	
	if role == "Site Supervisor":
		site_doc.site_supervisor = user
	elif role == "Quality Inspector":
		# Add to a custom field for quality inspectors
		if not hasattr(site_doc, "quality_inspectors"):
			site_doc.quality_inspectors = []
		site_doc.append("quality_inspectors", {"user": user})
	
	site_doc.save()
	
	# Setup user permissions
	add_user_permission("Construction Site", site_name, user)
	
	# Send notification
	send_assignment_notification(user, site_name, role)
	
	return {"status": "success", "message": _("User assigned successfully")}

@frappe.whitelist()
def remove_user_from_construction_site(user, site_name):
	"""Remove user assignment from construction site"""
	
	if not frappe.has_permission("Construction Site", "write"):
		frappe.throw(_("Insufficient permissions to remove user assignments"))
	
	# Remove user permission
	remove_user_permission("Construction Site", site_name, user)
	
	# Update construction site
	site_doc = frappe.get_doc("Construction Site", site_name)
	
	if site_doc.site_supervisor == user:
		site_doc.site_supervisor = None
		site_doc.save()
	
	return {"status": "success", "message": _("User assignment removed successfully")}

@frappe.whitelist()
def get_user_accessible_sites(user=None):
	"""Get construction sites accessible to a user"""
	
	if not user:
		user = frappe.session.user
	
	# Get user permissions
	user_permissions = get_user_permissions(user)
	site_permissions = user_permissions.get("Construction Site", [])
	
	if not site_permissions:
		# If no specific permissions, check role-based access
		user_roles = frappe.get_roles(user)
		
		if "Construction Manager" in user_roles:
			# Construction managers can access all sites
			sites = frappe.get_all("Construction Site",
				fields=["name", "site_name", "status", "supplier"]
			)
		else:
			# Limited access based on assignments
			sites = get_user_assigned_sites(user)
	else:
		# Get sites based on user permissions
		sites = frappe.get_all("Construction Site",
			filters={"name": ["in", site_permissions]},
			fields=["name", "site_name", "status", "supplier"]
		)
	
	return sites

def get_user_assigned_sites(user):
	"""Get sites assigned to a user"""
	
	sites = frappe.get_all("Construction Site",
		filters={
			"$or": [
				{"site_supervisor": user},
				{"owner": user}
			]
		},
		fields=["name", "site_name", "status", "supplier"]
	)
	
	return sites

@frappe.whitelist()
def get_user_accessible_inspections(user=None):
	"""Get inspections accessible to a user"""
	
	if not user:
		user = frappe.session.user
	
	user_roles = frappe.get_roles(user)
	
	if "Construction Manager" in user_roles:
		# Construction managers can access all inspections
		inspections = frappe.get_all("Supplier Inspection",
			fields=["name", "construction_site", "inspection_date", "inspector", "approval_status"]
		)
	else:
		# Get inspections based on user access
		accessible_sites = get_user_accessible_sites(user)
		site_names = [site.name for site in accessible_sites]
		
		inspections = frappe.get_all("Supplier Inspection",
			filters={
				"$or": [
					{"construction_site": ["in", site_names]},
					{"inspector": user},
					{"owner": user}
				]
			},
			fields=["name", "construction_site", "inspection_date", "inspector", "approval_status"]
		)
	
	return inspections

def send_assignment_notification(user, site_name, role):
	"""Send notification when user is assigned to a site"""
	
	try:
		site_doc = frappe.get_doc("Construction Site", site_name)
		
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"for_user": user,
			"type": "Assignment",
			"document_type": "Construction Site",
			"document_name": site_name,
			"subject": _("Assigned to Construction Site: {0}").format(site_doc.site_name),
			"email_content": _("You have been assigned as {0} for construction site: {1}").format(role, site_doc.site_name)
		})
		
		notification.insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error sending assignment notification: {str(e)}")

@frappe.whitelist()
def bulk_setup_permissions():
	"""Bulk setup permissions for all users (admin function)"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can run this function"))
	
	try:
		setup_construction_inspection_permissions()
		return {"status": "success", "message": _("Permissions setup completed successfully")}
	except Exception as e:
		frappe.log_error(f"Error in bulk permission setup: {str(e)}")
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def check_user_inspection_permission(inspection_name, user=None):
	"""Check if user has permission to access an inspection"""
	
	if not user:
		user = frappe.session.user
	
	if user == "Administrator":
		return True
	
	user_roles = frappe.get_roles(user)
	
	if "Construction Manager" in user_roles:
		return True
	
	inspection_doc = frappe.get_doc("Supplier Inspection", inspection_name)
	
	# Check if user is inspector or owner
	if inspection_doc.inspector == user or inspection_doc.owner == user:
		return True
	
	# Check if user has access to the construction site
	accessible_sites = get_user_accessible_sites(user)
	site_names = [site.name for site in accessible_sites]
	
	return inspection_doc.construction_site in site_names

# Hook functions for permission management
def on_user_update(doc, method):
	"""Handle user update events"""
	
	if method == "on_update":
		# Update user permissions when roles change
		setup_single_user_permissions(doc.name)

def on_construction_site_update(doc, method):
	"""Handle construction site update events"""
	
	if method == "on_update":
		# Update permissions when site assignments change
		if doc.site_supervisor:
			setup_site_supervisor_permissions(doc.site_supervisor)

def validate_inspection_access(doc, method):
	"""Validate user access to inspection"""
	
	if method == "validate":
		user = frappe.session.user
		
		if not check_user_inspection_permission(doc.name, user):
			frappe.throw(_("You don't have permission to access this inspection"))