# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, now_datetime
from frappe.desk.doctype.notification.notification import get_context

def get_notification_config():
	"""Get notification configuration for construction inspection module"""
	
	return {
		"for_doctype": {
			"Supplier Inspection": {
				"status": "inspection_status_notification"
			},
			"Construction Site": {
				"status": "site_status_notification"
			}
		}
	}

def inspection_status_notification(doc, method=None):
	"""Handle inspection status change notifications"""
	
	if method == "on_submit":
		send_inspection_submitted_notification(doc)
	elif method == "on_cancel":
		send_inspection_cancelled_notification(doc)
	elif hasattr(doc, "approval_status") and doc.approval_status:
		send_inspection_approval_notification(doc)

def site_status_notification(doc, method=None):
	"""Handle construction site status change notifications"""
	
	if method == "on_update":
		send_site_update_notification(doc)

def send_inspection_submitted_notification(inspection_doc):
	"""Send notification when inspection is submitted"""
	
	# Get construction site details
	site_doc = frappe.get_doc("Construction Site", inspection_doc.construction_site)
	
	# Prepare notification data
	notification_data = {
		"inspection_name": inspection_doc.name,
		"site_name": site_doc.site_name,
		"inspector": inspection_doc.inspector,
		"inspection_date": inspection_doc.inspection_date,
		"overall_rating": inspection_doc.overall_rating,
		"issues_found": inspection_doc.issues_found or 0
	}
	
	# Send to construction manager
	if site_doc.construction_manager:
		create_notification(
			user=site_doc.construction_manager,
			subject=_("New Inspection Submitted: {0}").format(site_doc.site_name),
			message=_("Inspector {0} has submitted an inspection for {1} with overall rating {2}/5").format(
				inspection_doc.inspector, site_doc.site_name, inspection_doc.overall_rating or "N/A"
			),
			doctype="Supplier Inspection",
			docname=inspection_doc.name,
			notification_type="Alert"
		)
		
		send_inspection_email_notification(
			recipient=site_doc.construction_manager,
			template="inspection_submitted",
			data=notification_data
		)
	
	# Send to site supervisor if different from construction manager
	if site_doc.site_supervisor and site_doc.site_supervisor != site_doc.construction_manager:
		create_notification(
			user=site_doc.site_supervisor,
			subject=_("New Inspection Submitted: {0}").format(site_doc.site_name),
			message=_("Inspector {0} has submitted an inspection for {1}").format(
				inspection_doc.inspector, site_doc.site_name
			),
			doctype="Supplier Inspection",
			docname=inspection_doc.name,
			notification_type="Alert"
		)
	
	# Send to supplier if issues found
	if inspection_doc.issues_found and inspection_doc.issues_found > 0:
		supplier_users = get_supplier_users(site_doc.supplier)
		for user in supplier_users:
			create_notification(
				user=user,
				subject=_("Inspection Issues Found: {0}").format(site_doc.site_name),
				message=_("{0} issues found during inspection. Please review and take corrective action.").format(
					inspection_doc.issues_found
				),
				doctype="Supplier Inspection",
				docname=inspection_doc.name,
				notification_type="Alert"
			)

def send_inspection_approval_notification(inspection_doc):
	"""Send notification when inspection is approved/rejected"""
	
	site_doc = frappe.get_doc("Construction Site", inspection_doc.construction_site)
	
	# Prepare notification data
	notification_data = {
		"inspection_name": inspection_doc.name,
		"site_name": site_doc.site_name,
		"inspector": inspection_doc.inspector,
		"approval_status": inspection_doc.approval_status,
		"approved_by": inspection_doc.approved_by,
		"approval_date": inspection_doc.approval_date
	}
	
	# Send to inspector
	if inspection_doc.inspector:
		status_text = _("approved") if inspection_doc.approval_status == "Approved" else _("rejected")
		create_notification(
			user=inspection_doc.inspector,
			subject=_("Inspection {0}: {1}").format(status_text, site_doc.site_name),
			message=_("Your inspection for {0} has been {1} by {2}").format(
				site_doc.site_name, status_text, inspection_doc.approved_by or "management"
			),
			doctype="Supplier Inspection",
			docname=inspection_doc.name,
			notification_type="Alert" if inspection_doc.approval_status == "Approved" else "Warning"
		)
		
		send_inspection_email_notification(
			recipient=inspection_doc.inspector,
			template="inspection_approval",
			data=notification_data
		)
	
	# Send to supplier if approved
	if inspection_doc.approval_status == "Approved":
		supplier_users = get_supplier_users(site_doc.supplier)
		for user in supplier_users:
			create_notification(
				user=user,
				subject=_("Inspection Approved: {0}").format(site_doc.site_name),
				message=_("The inspection for {0} has been approved. Good work!").format(site_doc.site_name),
				doctype="Supplier Inspection",
				docname=inspection_doc.name,
				notification_type="Success"
			)

def send_inspection_cancelled_notification(inspection_doc):
	"""Send notification when inspection is cancelled"""
	
	site_doc = frappe.get_doc("Construction Site", inspection_doc.construction_site)
	
	# Send to relevant users
	users_to_notify = []
	if site_doc.construction_manager:
		users_to_notify.append(site_doc.construction_manager)
	if site_doc.site_supervisor and site_doc.site_supervisor not in users_to_notify:
		users_to_notify.append(site_doc.site_supervisor)
	if inspection_doc.inspector and inspection_doc.inspector not in users_to_notify:
		users_to_notify.append(inspection_doc.inspector)
	
	for user in users_to_notify:
		create_notification(
			user=user,
			subject=_("Inspection Cancelled: {0}").format(site_doc.site_name),
			message=_("The inspection for {0} on {1} has been cancelled").format(
				site_doc.site_name, inspection_doc.inspection_date
			),
			doctype="Supplier Inspection",
			docname=inspection_doc.name,
			notification_type="Warning"
		)

def send_site_update_notification(site_doc):
	"""Send notification when construction site is updated"""
	
	# Check if status changed
	if site_doc.has_value_changed("status"):
		old_status = site_doc.get_db_value("status")
		new_status = site_doc.status
		
		# Send to relevant users
		users_to_notify = []
		if site_doc.construction_manager:
			users_to_notify.append(site_doc.construction_manager)
		if site_doc.site_supervisor and site_doc.site_supervisor not in users_to_notify:
			users_to_notify.append(site_doc.site_supervisor)
		
		# Add supplier users
		supplier_users = get_supplier_users(site_doc.supplier)
		for user in supplier_users:
			if user not in users_to_notify:
				users_to_notify.append(user)
		
		for user in users_to_notify:
			create_notification(
				user=user,
				subject=_("Site Status Updated: {0}").format(site_doc.site_name),
				message=_("Construction site {0} status changed from {1} to {2}").format(
					site_doc.site_name, old_status or "N/A", new_status
				),
				doctype="Construction Site",
				docname=site_doc.name,
				notification_type="Info"
			)

def create_notification(user, subject, message, doctype, docname, notification_type="Alert"):
	"""Create a notification log entry"""
	
	try:
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"subject": subject,
			"email_content": message,
			"for_user": user,
			"type": notification_type,
			"document_type": doctype,
			"document_name": docname,
			"from_user": frappe.session.user
		})
		notification.insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error creating notification: {str(e)}")

def send_inspection_email_notification(recipient, template, data):
	"""Send email notification for inspection events"""
	
	try:
		# Get recipient email
		recipient_email = frappe.db.get_value("User", recipient, "email")
		if not recipient_email:
			return
		
		# Get email template
		email_content = get_email_template(template, data)
		
		frappe.sendmail(
			recipients=[recipient_email],
			subject=email_content["subject"],
			message=email_content["message"],
			delayed=False
		)
		
	except Exception as e:
		frappe.log_error(f"Error sending email notification: {str(e)}")

def get_email_template(template_name, data):
	"""Get email template content"""
	
	templates = {
		"inspection_submitted": {
			"subject": _("New Inspection Submitted - {site_name}").format(**data),
			"message": _("""
			<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
				<h2 style="color: #2c3e50;">新巡檢報告已提交</h2>
				
				<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
					<h3 style="color: #2c3e50; margin-top: 0;">巡檢詳情</h3>
					<table style="width: 100%;">
						<tr>
							<td style="padding: 8px; font-weight: bold;">施工現場:</td>
							<td style="padding: 8px;">{site_name}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">巡檢員:</td>
							<td style="padding: 8px;">{inspector}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">巡檢日期:</td>
							<td style="padding: 8px;">{inspection_date}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">整體評分:</td>
							<td style="padding: 8px;">{overall_rating}/5</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">發現問題:</td>
							<td style="padding: 8px;">{issues_found} 個</td>
						</tr>
					</table>
				</div>
				
				<p>請登入系統查看詳細巡檢報告。</p>
				
				<div style="text-align: center; margin: 30px 0;">
					<a href="/app/supplier-inspection/{inspection_name}" 
					   style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
						查看巡檢報告
					</a>
				</div>
			</div>
			""").format(**data)
		},
		
		"inspection_approval": {
			"subject": _("Inspection {approval_status} - {site_name}").format(**data),
			"message": _("""
			<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
				<h2 style="color: #2c3e50;">巡檢報告審核結果</h2>
				
				<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
					<h3 style="color: #2c3e50; margin-top: 0;">審核詳情</h3>
					<table style="width: 100%;">
						<tr>
							<td style="padding: 8px; font-weight: bold;">施工現場:</td>
							<td style="padding: 8px;">{site_name}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">巡檢員:</td>
							<td style="padding: 8px;">{inspector}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">審核狀態:</td>
							<td style="padding: 8px;">{approval_status}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">審核人:</td>
							<td style="padding: 8px;">{approved_by}</td>
						</tr>
						<tr>
							<td style="padding: 8px; font-weight: bold;">審核日期:</td>
							<td style="padding: 8px;">{approval_date}</td>
						</tr>
					</table>
				</div>
				
				<div style="text-align: center; margin: 30px 0;">
					<a href="/app/supplier-inspection/{inspection_name}" 
					   style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">
						查看詳細內容
					</a>
				</div>
			</div>
			""").format(**data)
		}
	}
	
	return templates.get(template_name, {
		"subject": _("Construction Inspection Notification"),
		"message": _("You have a new notification from the construction inspection system.")
	})

def get_supplier_users(supplier_name):
	"""Get users associated with a supplier"""
	
	if not supplier_name:
		return []
	
	# Get supplier document
	try:
		supplier_doc = frappe.get_doc("Supplier", supplier_name)
		users = []
		
		# Add primary contact
		if hasattr(supplier_doc, "supplier_primary_contact") and supplier_doc.supplier_primary_contact:
			contact_doc = frappe.get_doc("Contact", supplier_doc.supplier_primary_contact)
			if hasattr(contact_doc, "user") and contact_doc.user:
				users.append(contact_doc.user)
		
		# Add users with Supplier role linked to this supplier
		supplier_users = frappe.get_all("User",
			filters={
				"enabled": 1,
				"name": ["in", frappe.get_all("Has Role", 
					filters={"role": "Supplier"},
					pluck="parent"
				)]
			},
			fields=["name"]
		)
		
		# Filter users who have access to this supplier
		for user in supplier_users:
			# Check if user has permission to this supplier
			if frappe.has_permission("Supplier", "read", supplier_name, user.name):
				if user.name not in users:
					users.append(user.name)
		
		return users
		
	except Exception as e:
		frappe.log_error(f"Error getting supplier users for {supplier_name}: {str(e)}")
		return []

@frappe.whitelist()
def get_user_notifications():
	"""Get notifications for current user"""
	
	notifications = frappe.get_all("Notification Log",
		filters={
			"for_user": frappe.session.user,
			"read": 0
		},
		fields=["name", "subject", "email_content", "creation", "document_type", "document_name", "type"],
		order_by="creation desc",
		limit=20
	)
	
	return notifications

@frappe.whitelist()
def mark_notification_read(notification_name):
	"""Mark notification as read"""
	
	try:
		notification = frappe.get_doc("Notification Log", notification_name)
		if notification.for_user == frappe.session.user:
			notification.db_set("read", 1)
			return {"status": "success"}
		else:
			return {"status": "error", "message": "Unauthorized"}
	except Exception as e:
		return {"status": "error", "message": str(e)}

@frappe.whitelist()
def send_test_notification(user, message):
	"""Send test notification (for testing purposes)"""
	
	if not frappe.has_permission("System Manager"):
		frappe.throw(_("Only System Manager can send test notifications"))
	
	create_notification(
		user=user,
		subject=_("Test Notification"),
		message=message,
		doctype="Construction Site",
		docname="TEST",
		notification_type="Info"
	)
	
	return {"status": "success", "message": _("Test notification sent to {0}").format(user)}