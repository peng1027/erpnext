# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, getdate, get_files_path
import os
from datetime import datetime, timedelta

def generate_weekly_reports():
	"""Generate weekly inspection reports for all active construction sites"""
	
	week_start = add_days(today(), -7)
	week_end = today()
	
	# Get all active construction sites
	active_sites = frappe.get_all("Construction Site",
		filters={"status": ["in", ["Active", "In Progress"]]},
		fields=["name", "site_name", "supplier", "project", "construction_manager"]
	)
	
	for site in active_sites:
		try:
			generate_site_weekly_report(site, week_start, week_end)
		except Exception as e:
			frappe.log_error(f"Error generating weekly report for site {site.name}: {str(e)}")

def generate_site_weekly_report(site, week_start, week_end):
	"""Generate weekly report for a specific construction site"""
	
	# Get inspections for the week
	inspections = frappe.get_all("Supplier Inspection",
		filters={
			"construction_site": site.name,
			"inspection_date": ["between", [week_start, week_end]],
			"docstatus": 1
		},
		fields=["name", "inspection_date", "inspector", "overall_rating", 
				"safety_rating", "quality_rating", "progress_rating", 
				"issues_found", "corrective_actions"]
	)
	
	if not inspections:
		return  # No inspections this week
	
	# Calculate weekly statistics
	total_inspections = len(inspections)
	avg_overall_rating = sum([insp.overall_rating or 0 for insp in inspections]) / total_inspections
	avg_safety_rating = sum([insp.safety_rating or 0 for insp in inspections]) / total_inspections
	avg_quality_rating = sum([insp.quality_rating or 0 for insp in inspections]) / total_inspections
	avg_progress_rating = sum([insp.progress_rating or 0 for insp in inspections]) / total_inspections
	
	total_issues = sum([insp.issues_found or 0 for insp in inspections])
	
	# Create weekly report document
	weekly_report = frappe.get_doc({
		"doctype": "Weekly Inspection Report",
		"construction_site": site.name,
		"site_name": site.site_name,
		"supplier": site.supplier,
		"project": site.project,
		"week_start_date": week_start,
		"week_end_date": week_end,
		"total_inspections": total_inspections,
		"average_overall_rating": avg_overall_rating,
		"average_safety_rating": avg_safety_rating,
		"average_quality_rating": avg_quality_rating,
		"average_progress_rating": avg_progress_rating,
		"total_issues_found": total_issues,
		"report_generated_on": today(),
		"generated_by": "System"
	})
	
	# Add inspection details
	for inspection in inspections:
		weekly_report.append("inspection_details", {
			"inspection": inspection.name,
			"inspection_date": inspection.inspection_date,
			"inspector": inspection.inspector,
			"overall_rating": inspection.overall_rating,
			"safety_rating": inspection.safety_rating,
			"quality_rating": inspection.quality_rating,
			"progress_rating": inspection.progress_rating,
			"issues_found": inspection.issues_found,
			"corrective_actions": inspection.corrective_actions
		})
	
	weekly_report.insert(ignore_permissions=True)
	
	# Send report to construction manager
	if site.construction_manager:
		send_weekly_report_email(site, weekly_report)

def send_weekly_report_email(site, weekly_report):
	"""Send weekly report email to construction manager"""
	
	manager_email = frappe.db.get_value("User", site.construction_manager, "email")
	if not manager_email:
		return
	
	subject = _("Weekly Inspection Report - {0}").format(site.site_name)
	
	# Generate report content
	report_content = generate_weekly_report_html(weekly_report)
	
	frappe.sendmail(
		recipients=[manager_email],
		subject=subject,
		message=report_content,
		delayed=False
	)

def generate_weekly_report_html(report):
	"""Generate HTML content for weekly report"""
	
	html_content = f"""
	<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
		<h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
			週間巡檢報告 - {report.site_name}
		</h2>
		
		<div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
			<h3 style="color: #2c3e50; margin-top: 0;">基本信息</h3>
			<table style="width: 100%; border-collapse: collapse;">
				<tr>
					<td style="padding: 8px; font-weight: bold;">施工現場:</td>
					<td style="padding: 8px;">{report.site_name}</td>
				</tr>
				<tr>
					<td style="padding: 8px; font-weight: bold;">供應商:</td>
					<td style="padding: 8px;">{report.supplier or 'N/A'}</td>
				</tr>
				<tr>
					<td style="padding: 8px; font-weight: bold;">項目:</td>
					<td style="padding: 8px;">{report.project or 'N/A'}</td>
				</tr>
				<tr>
					<td style="padding: 8px; font-weight: bold;">報告週期:</td>
					<td style="padding: 8px;">{report.week_start_date} 至 {report.week_end_date}</td>
				</tr>
			</table>
		</div>
		
		<div style="background-color: #e8f5e8; padding: 20px; border-radius: 5px; margin: 20px 0;">
			<h3 style="color: #2c3e50; margin-top: 0;">週間統計</h3>
			<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
				<div>
					<p><strong>總巡檢次數:</strong> {report.total_inspections}</p>
					<p><strong>平均整體評分:</strong> {report.average_overall_rating:.1f}/5</p>
					<p><strong>平均安全評分:</strong> {report.average_safety_rating:.1f}/5</p>
				</div>
				<div>
					<p><strong>平均品質評分:</strong> {report.average_quality_rating:.1f}/5</p>
					<p><strong>平均進度評分:</strong> {report.average_progress_rating:.1f}/5</p>
					<p><strong>發現問題總數:</strong> {report.total_issues_found}</p>
				</div>
			</div>
		</div>
		
		<div style="margin: 20px 0;">
			<h3 style="color: #2c3e50;">巡檢詳情</h3>
			<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
				<thead>
					<tr style="background-color: #3498db; color: white;">
						<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">日期</th>
						<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">巡檢員</th>
						<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">整體評分</th>
						<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">安全評分</th>
						<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">品質評分</th>
						<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">進度評分</th>
						<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">問題數</th>
					</tr>
				</thead>
				<tbody>
	"""
	
	for detail in report.inspection_details:
		html_content += f"""
					<tr>
						<td style="padding: 8px; border: 1px solid #ddd;">{detail.inspection_date}</td>
						<td style="padding: 8px; border: 1px solid #ddd;">{detail.inspector}</td>
						<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{detail.overall_rating or 'N/A'}</td>
						<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{detail.safety_rating or 'N/A'}</td>
						<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{detail.quality_rating or 'N/A'}</td>
						<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{detail.progress_rating or 'N/A'}</td>
						<td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{detail.issues_found or 0}</td>
					</tr>
		"""
	
	html_content += """
				</tbody>
			</table>
		</div>
		
		<div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
			<p style="margin: 0; color: #856404;">
				<strong>注意:</strong> 此報告由系統自動生成。如有疑問，請聯繫系統管理員。
			</p>
		</div>
	</div>
	"""
	
	return html_content

def cleanup_old_inspection_photos():
	"""Clean up old inspection photos to save storage space"""
	
	# Get photos older than 6 months
	six_months_ago = add_days(today(), -180)
	
	old_inspections = frappe.get_all("Supplier Inspection",
		filters={
			"inspection_date": ["<", six_months_ago],
			"docstatus": 1
		},
		fields=["name"]
	)
	
	cleaned_count = 0
	
	for inspection in old_inspections:
		try:
			# Get inspection document
			inspection_doc = frappe.get_doc("Supplier Inspection", inspection.name)
			
			# Clean up photos from checklist items
			for item in inspection_doc.checklist_items:
				if item.photo:
					file_path = frappe.get_site_path() + item.photo
					if os.path.exists(file_path):
						os.remove(file_path)
						cleaned_count += 1
					
					# Clear photo field
					item.db_set("photo", None)
			
			# Clean up attachments
			attachments = frappe.get_all("File",
				filters={
					"attached_to_doctype": "Supplier Inspection",
					"attached_to_name": inspection.name
				}
			)
			
			for attachment in attachments:
				try:
					frappe.delete_doc("File", attachment.name)
					cleaned_count += 1
				except:
					pass
					
		except Exception as e:
			frappe.log_error(f"Error cleaning up photos for inspection {inspection.name}: {str(e)}")
	
	if cleaned_count > 0:
		frappe.log_error(f"Cleaned up {cleaned_count} old inspection photos")

@frappe.whitelist()
def get_weekly_report_data(site_name, week_start=None):
	"""Get weekly report data for a specific site"""
	
	if not week_start:
		week_start = add_days(today(), -7)
	
	week_end = add_days(week_start, 6)
	
	# Get inspections for the week
	inspections = frappe.get_all("Supplier Inspection",
		filters={
			"construction_site": site_name,
			"inspection_date": ["between", [week_start, week_end]],
			"docstatus": 1
		},
		fields=["name", "inspection_date", "inspector", "overall_rating", 
				"safety_rating", "quality_rating", "progress_rating", 
				"issues_found", "corrective_actions"]
	)
	
	if not inspections:
		return {"message": _("No inspections found for the specified week")}
	
	# Calculate statistics
	total_inspections = len(inspections)
	avg_overall_rating = sum([insp.overall_rating or 0 for insp in inspections]) / total_inspections
	avg_safety_rating = sum([insp.safety_rating or 0 for insp in inspections]) / total_inspections
	avg_quality_rating = sum([insp.quality_rating or 0 for insp in inspections]) / total_inspections
	avg_progress_rating = sum([insp.progress_rating or 0 for insp in inspections]) / total_inspections
	total_issues = sum([insp.issues_found or 0 for insp in inspections])
	
	return {
		"week_start": week_start,
		"week_end": week_end,
		"total_inspections": total_inspections,
		"average_overall_rating": round(avg_overall_rating, 1),
		"average_safety_rating": round(avg_safety_rating, 1),
		"average_quality_rating": round(avg_quality_rating, 1),
		"average_progress_rating": round(avg_progress_rating, 1),
		"total_issues_found": total_issues,
		"inspections": inspections
	}