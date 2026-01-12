# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate
from datetime import datetime, timedelta

def send_inspection_reminders():
	"""Send daily inspection reminders to relevant users"""
	
	# Get construction sites that need inspection
	sites_needing_inspection = frappe.db.sql("""
		SELECT 
			cs.name, cs.site_name, cs.supplier, cs.project,
			cs.construction_manager, cs.site_supervisor,
			DATEDIFF(CURDATE(), COALESCE(
				(SELECT MAX(inspection_date) 
				 FROM `tabSupplier Inspection` 
				 WHERE construction_site = cs.name 
				 AND docstatus = 1), 
				cs.start_date
			)) as days_since_last_inspection
		FROM `tabConstruction Site` cs
		WHERE cs.status IN ('Active', 'In Progress')
		AND (
			cs.next_inspection_date <= %s
			OR DATEDIFF(CURDATE(), COALESCE(
				(SELECT MAX(inspection_date) 
				 FROM `tabSupplier Inspection` 
				 WHERE construction_site = cs.name 
				 AND docstatus = 1), 
				cs.start_date
			)) >= 7
		)
	""", (today(),), as_dict=True)
	
	for site in sites_needing_inspection:
		# Send notification to construction manager
		if site.construction_manager:
			create_inspection_reminder_notification(
				site.construction_manager,
				site.name,
				site.site_name,
				site.days_since_last_inspection
			)
		
		# Send notification to site supervisor
		if site.site_supervisor and site.site_supervisor != site.construction_manager:
			create_inspection_reminder_notification(
				site.site_supervisor,
				site.name,
				site.site_name,
				site.days_since_last_inspection
			)
		
		# Send email reminder
		send_inspection_reminder_email(site)

def create_inspection_reminder_notification(user, site_name, site_display_name, days_since_last):
	"""Create a notification for inspection reminder"""
	
	frappe.get_doc({
		"doctype": "Notification Log",
		"subject": _("Inspection Reminder: {0}").format(site_display_name),
		"email_content": _("Construction site {0} needs inspection. Last inspection was {1} days ago.").format(
			site_display_name, days_since_last
		),
		"for_user": user,
		"type": "Alert",
		"document_type": "Construction Site",
		"document_name": site_name,
		"from_user": "Administrator"
	}).insert(ignore_permissions=True)

def send_inspection_reminder_email(site):
	"""Send email reminder for inspection"""
	
	recipients = []
	if site.construction_manager:
		recipients.append(site.construction_manager)
	if site.site_supervisor and site.site_supervisor not in recipients:
		recipients.append(site.site_supervisor)
	
	if not recipients:
		return
	
	# Get email addresses
	email_recipients = []
	for user in recipients:
		user_email = frappe.db.get_value("User", user, "email")
		if user_email:
			email_recipients.append(user_email)
	
	if not email_recipients:
		return
	
	subject = _("Inspection Reminder: {0}").format(site.site_name)
	message = _("""
	<p>Dear Team,</p>
	
	<p>This is a reminder that construction site <strong>{0}</strong> requires inspection.</p>
	
	<p><strong>Site Details:</strong></p>
	<ul>
		<li>Site Name: {0}</li>
		<li>Supplier: {1}</li>
		<li>Project: {2}</li>
		<li>Days since last inspection: {3}</li>
	</ul>
	
	<p>Please schedule and conduct the inspection as soon as possible.</p>
	
	<p>You can access the mobile inspection app at: <a href="/mobile-inspection">Mobile Inspection</a></p>
	
	<p>Best regards,<br>Construction Inspection System</p>
	""").format(
		site.site_name,
		site.supplier or "N/A",
		site.project or "N/A", 
		site.days_since_last_inspection
	)
	
	frappe.sendmail(
		recipients=email_recipients,
		subject=subject,
		message=message,
		delayed=False
	)

def update_site_progress_summary():
	"""Update daily progress summary for all active construction sites"""
	
	active_sites = frappe.get_all("Construction Site", 
		filters={"status": ["in", ["Active", "In Progress"]]},
		fields=["name"]
	)
	
	for site in active_sites:
		try:
			site_doc = frappe.get_doc("Construction Site", site.name)
			
			# Calculate progress based on recent inspections
			recent_inspections = frappe.get_all("Supplier Inspection",
				filters={
					"construction_site": site.name,
					"docstatus": 1,
					"inspection_date": [">=", add_days(today(), -30)]
				},
				fields=["overall_rating", "progress_rating"]
			)
			
			if recent_inspections:
				avg_progress = sum([insp.progress_rating or 0 for insp in recent_inspections]) / len(recent_inspections)
				site_doc.db_set("progress_percentage", min(avg_progress * 20, 100))  # Convert 5-point scale to percentage
			
			# Update next inspection date if not set
			if not site_doc.next_inspection_date:
				last_inspection = frappe.db.get_value("Supplier Inspection",
					filters={
						"construction_site": site.name,
						"docstatus": 1
					},
					fieldname="inspection_date",
					order_by="inspection_date desc"
				)
				
				if last_inspection:
					site_doc.db_set("next_inspection_date", add_days(last_inspection, 7))
				else:
					site_doc.db_set("next_inspection_date", add_days(today(), 1))
			
		except Exception as e:
			frappe.log_error(f"Error updating site progress for {site.name}: {str(e)}")

@frappe.whitelist()
def get_inspection_reminders():
	"""Get inspection reminders for current user"""
	
	user_roles = frappe.get_roles()
	
	if "Construction Manager" in user_roles or "Site Supervisor" in user_roles:
		# Get sites assigned to current user
		sites = frappe.db.sql("""
			SELECT 
				name, site_name, supplier, project,
				DATEDIFF(CURDATE(), COALESCE(
					(SELECT MAX(inspection_date) 
					 FROM `tabSupplier Inspection` 
					 WHERE construction_site = cs.name 
					 AND docstatus = 1), 
					cs.start_date
				)) as days_since_last_inspection,
				next_inspection_date
			FROM `tabConstruction Site` cs
			WHERE cs.status IN ('Active', 'In Progress')
			AND (cs.construction_manager = %s OR cs.site_supervisor = %s)
			AND (
				cs.next_inspection_date <= %s
				OR DATEDIFF(CURDATE(), COALESCE(
					(SELECT MAX(inspection_date) 
					 FROM `tabSupplier Inspection` 
					 WHERE construction_site = cs.name 
					 AND docstatus = 1), 
					cs.start_date
				)) >= 7
			)
			ORDER BY days_since_last_inspection DESC
		""", (frappe.session.user, frappe.session.user, today()), as_dict=True)
		
		return sites
	
	return []

@frappe.whitelist()
def mark_reminder_acknowledged(site_name):
	"""Mark inspection reminder as acknowledged"""
	
	site_doc = frappe.get_doc("Construction Site", site_name)
	site_doc.db_set("next_inspection_date", add_days(today(), 7))
	
	return {"status": "success", "message": _("Reminder acknowledged. Next inspection scheduled for {0}").format(add_days(today(), 7))}