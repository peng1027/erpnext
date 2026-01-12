# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate

def sync_project_data():
	"""Sync construction sites with project data"""
	
	# Get all projects that should have construction sites
	projects = frappe.get_all("Project",
		filters={
			"status": ["in", ["Open", "Working"]],
			"project_type": ["in", ["External", "Internal"]]
		},
		fields=["name", "project_name", "customer", "status", "expected_start_date", "expected_end_date"]
	)
	
	for project in projects:
		sync_project_construction_sites(project)

def sync_project_construction_sites(project):
	"""Sync construction sites for a specific project"""
	
	# Check if construction site already exists for this project
	existing_sites = frappe.get_all("Construction Site",
		filters={"project": project.name},
		fields=["name", "status"]
	)
	
	if not existing_sites:
		# Create construction site if project involves construction
		if is_construction_project(project):
			create_construction_site_from_project(project)
	else:
		# Update existing construction sites
		for site in existing_sites:
			update_construction_site_from_project(site.name, project)

def is_construction_project(project):
	"""Check if project involves construction work"""
	
	# Check project name for construction keywords
	construction_keywords = ["construction", "building", "施工", "建設", "工程", "建築"]
	project_name_lower = project.project_name.lower()
	
	for keyword in construction_keywords:
		if keyword in project_name_lower:
			return True
	
	# Check if project has tasks related to construction
	construction_tasks = frappe.get_all("Task",
		filters={
			"project": project.name,
			"subject": ["like", "%construction%"]
		}
	)
	
	return len(construction_tasks) > 0

def create_construction_site_from_project(project):
	"""Create construction site from project data"""
	
	try:
		# Generate site code
		site_code = f"SITE-{project.name}"
		
		# Get project customer as potential supplier
		supplier = None
		if project.customer:
			# Check if customer is also a supplier
			supplier_exists = frappe.db.exists("Supplier", project.customer)
			if supplier_exists:
				supplier = project.customer
		
		construction_site = frappe.get_doc({
			"doctype": "Construction Site",
			"site_name": f"{project.project_name} - Construction Site",
			"site_code": site_code,
			"project": project.name,
			"supplier": supplier,
			"status": "Planning" if project.status == "Open" else "Active",
			"start_date": project.expected_start_date or today(),
			"expected_end_date": project.expected_end_date,
			"description": f"Construction site for project: {project.project_name}",
			"created_from_project": 1
		})
		
		construction_site.insert(ignore_permissions=True)
		
		# Create initial inspection schedule
		create_initial_inspection_schedule(construction_site.name)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error creating construction site from project {project.name}: {str(e)}")

def update_construction_site_from_project(site_name, project):
	"""Update construction site based on project changes"""
	
	try:
		site_doc = frappe.get_doc("Construction Site", site_name)
		
		# Update status based on project status
		if project.status == "Completed" and site_doc.status != "Completed":
			site_doc.status = "Completed"
			site_doc.actual_end_date = today()
		elif project.status == "Cancelled" and site_doc.status != "Cancelled":
			site_doc.status = "Cancelled"
		
		# Update dates
		if project.expected_end_date and site_doc.expected_end_date != project.expected_end_date:
			site_doc.expected_end_date = project.expected_end_date
		
		site_doc.save(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error updating construction site {site_name} from project: {str(e)}")

def create_initial_inspection_schedule(site_name):
	"""Create initial inspection schedule for new construction site"""
	
	try:
		site_doc = frappe.get_doc("Construction Site", site_name)
		
		# Set next inspection date to 3 days from start
		if site_doc.start_date:
			next_inspection = add_days(site_doc.start_date, 3)
		else:
			next_inspection = add_days(today(), 3)
		
		site_doc.db_set("next_inspection_date", next_inspection)
		
	except Exception as e:
		frappe.log_error(f"Error creating inspection schedule for site {site_name}: {str(e)}")

@frappe.whitelist()
def get_project_construction_sites(project_name):
	"""Get construction sites for a specific project"""
	
	sites = frappe.get_all("Construction Site",
		filters={"project": project_name},
		fields=["name", "site_name", "status", "supplier", "progress_percentage", "next_inspection_date"]
	)
	
	# Get recent inspections for each site
	for site in sites:
		recent_inspections = frappe.get_all("Supplier Inspection",
			filters={
				"construction_site": site.name,
				"docstatus": 1
			},
			fields=["name", "inspection_date", "overall_rating"],
			order_by="inspection_date desc",
			limit=3
		)
		site["recent_inspections"] = recent_inspections
	
	return sites

@frappe.whitelist()
def create_inspection_from_project_task(task_name):
	"""Create inspection based on project task"""
	
	task_doc = frappe.get_doc("Task", task_name)
	
	if not task_doc.project:
		frappe.throw(_("Task must be linked to a project"))
	
	# Get construction site for this project
	construction_sites = frappe.get_all("Construction Site",
		filters={"project": task_doc.project},
		fields=["name", "site_name"]
	)
	
	if not construction_sites:
		frappe.throw(_("No construction site found for project {0}").format(task_doc.project))
	
	# Use first construction site
	site = construction_sites[0]
	
	# Create inspection
	inspection = frappe.get_doc({
		"doctype": "Supplier Inspection",
		"construction_site": site.name,
		"inspection_date": today(),
		"inspector": frappe.session.user,
		"inspection_type": "Task-based",
		"description": f"Inspection for task: {task_doc.subject}",
		"related_task": task_name
	})
	
	inspection.insert()
	
	return inspection.name

def update_project_progress_from_inspections():
	"""Update project progress based on construction site inspections"""
	
	# Get all active projects with construction sites
	projects_with_sites = frappe.db.sql("""
		SELECT DISTINCT p.name, p.project_name, p.percent_complete
		FROM `tabProject` p
		INNER JOIN `tabConstruction Site` cs ON cs.project = p.name
		WHERE p.status IN ('Open', 'Working')
		AND cs.status IN ('Active', 'In Progress')
	""", as_dict=True)
	
	for project in projects_with_sites:
		try:
			update_single_project_progress(project)
		except Exception as e:
			frappe.log_error(f"Error updating progress for project {project.name}: {str(e)}")

def update_single_project_progress(project):
	"""Update progress for a single project based on construction inspections"""
	
	# Get construction sites for this project
	sites = frappe.get_all("Construction Site",
		filters={"project": project.name},
		fields=["name", "progress_percentage"]
	)
	
	if not sites:
		return
	
	# Calculate average progress from all sites
	total_progress = sum([site.progress_percentage or 0 for site in sites])
	avg_progress = total_progress / len(sites)
	
	# Update project progress if significantly different
	current_progress = project.percent_complete or 0
	if abs(avg_progress - current_progress) > 5:  # Update if difference > 5%
		project_doc = frappe.get_doc("Project", project.name)
		project_doc.db_set("percent_complete", min(avg_progress, 100))
		
		# Add comment about progress update
		project_doc.add_comment("Info", 
			f"Progress updated to {avg_progress:.1f}% based on construction site inspections")

@frappe.whitelist()
def get_project_inspection_summary(project_name):
	"""Get inspection summary for a project"""
	
	# Get construction sites for project
	sites = frappe.get_all("Construction Site",
		filters={"project": project_name},
		fields=["name", "site_name"]
	)
	
	if not sites:
		return {"message": _("No construction sites found for this project")}
	
	site_names = [site.name for site in sites]
	
	# Get inspection statistics
	inspection_stats = frappe.db.sql("""
		SELECT 
			COUNT(*) as total_inspections,
			AVG(overall_rating) as avg_rating,
			SUM(issues_found) as total_issues,
			COUNT(CASE WHEN approval_status = 'Approved' THEN 1 END) as approved_inspections
		FROM `tabSupplier Inspection`
		WHERE construction_site IN %(sites)s
		AND docstatus = 1
	""", {"sites": site_names}, as_dict=True)
	
	stats = inspection_stats[0] if inspection_stats else {}
	
	# Get recent inspections
	recent_inspections = frappe.get_all("Supplier Inspection",
		filters={
			"construction_site": ["in", site_names],
			"docstatus": 1
		},
		fields=["name", "construction_site", "inspection_date", "inspector", "overall_rating", "approval_status"],
		order_by="inspection_date desc",
		limit=10
	)
	
	# Get inspection trend (last 30 days)
	trend_data = frappe.db.sql("""
		SELECT 
			DATE(inspection_date) as date,
			AVG(overall_rating) as avg_rating,
			COUNT(*) as inspection_count
		FROM `tabSupplier Inspection`
		WHERE construction_site IN %(sites)s
		AND docstatus = 1
		AND inspection_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
		GROUP BY DATE(inspection_date)
		ORDER BY date
	""", {"sites": site_names}, as_dict=True)
	
	return {
		"project_name": project_name,
		"construction_sites": sites,
		"statistics": {
			"total_inspections": stats.get("total_inspections", 0),
			"average_rating": round(stats.get("avg_rating", 0), 1),
			"total_issues": stats.get("total_issues", 0),
			"approval_rate": round((stats.get("approved_inspections", 0) / max(stats.get("total_inspections", 1), 1)) * 100, 1)
		},
		"recent_inspections": recent_inspections,
		"trend_data": trend_data
	}

# Hook functions for project events
def on_project_update(doc, method):
	"""Handle project update events"""
	
	if method == "on_update":
		# Sync construction sites when project is updated
		sync_project_construction_sites(doc)

def on_task_completion(doc, method):
	"""Handle task completion events"""
	
	if method == "on_update" and doc.status == "Completed":
		# Check if this task is related to construction inspection
		if "inspection" in doc.subject.lower() or "巡檢" in doc.subject:
			# Update related construction site progress
			if doc.project:
				update_single_project_progress({"name": doc.project})

@frappe.whitelist()
def link_existing_projects_to_sites():
	"""Link existing projects to construction sites (one-time setup)"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can run this function"))
	
	projects = frappe.get_all("Project",
		filters={"status": ["in", ["Open", "Working"]]},
		fields=["name", "project_name"]
	)
	
	linked_count = 0
	
	for project in projects:
		if is_construction_project(project):
			existing_site = frappe.db.exists("Construction Site", {"project": project.name})
			if not existing_site:
				create_construction_site_from_project(project)
				linked_count += 1
	
	return {
		"status": "success",
		"message": _("Linked {0} projects to construction sites").format(linked_count)
	}