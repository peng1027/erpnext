# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, add_days, add_months, getdate
from datetime import datetime, timedelta
import json

def generate_monthly_analytics():
	"""Generate monthly analytics for construction inspection performance"""
	
	month_start = add_months(today(), -1).replace(day=1)
	month_end = add_days(add_months(month_start, 1), -1)
	
	# Generate analytics for each active construction site
	active_sites = frappe.get_all("Construction Site",
		filters={"status": ["in", ["Active", "In Progress", "Completed"]]},
		fields=["name", "site_name", "supplier", "project", "construction_manager"]
	)
	
	overall_analytics = {
		"month_start": month_start,
		"month_end": month_end,
		"total_sites": len(active_sites),
		"total_inspections": 0,
		"average_rating": 0,
		"total_issues": 0,
		"supplier_performance": {},
		"inspector_performance": {},
		"site_analytics": []
	}
	
	for site in active_sites:
		try:
			site_analytics = generate_site_monthly_analytics(site, month_start, month_end)
			overall_analytics["site_analytics"].append(site_analytics)
			
			# Aggregate data
			overall_analytics["total_inspections"] += site_analytics["total_inspections"]
			overall_analytics["total_issues"] += site_analytics["total_issues"]
			
			# Supplier performance aggregation
			supplier = site.supplier
			if supplier:
				if supplier not in overall_analytics["supplier_performance"]:
					overall_analytics["supplier_performance"][supplier] = {
						"total_inspections": 0,
						"average_rating": 0,
						"total_issues": 0,
						"sites": []
					}
				
				overall_analytics["supplier_performance"][supplier]["total_inspections"] += site_analytics["total_inspections"]
				overall_analytics["supplier_performance"][supplier]["total_issues"] += site_analytics["total_issues"]
				overall_analytics["supplier_performance"][supplier]["sites"].append(site.name)
				
				if site_analytics["average_rating"] > 0:
					current_avg = overall_analytics["supplier_performance"][supplier]["average_rating"]
					total_sites = len(overall_analytics["supplier_performance"][supplier]["sites"])
					overall_analytics["supplier_performance"][supplier]["average_rating"] = (
						(current_avg * (total_sites - 1) + site_analytics["average_rating"]) / total_sites
					)
			
		except Exception as e:
			frappe.log_error(f"Error generating monthly analytics for site {site.name}: {str(e)}")
	
	# Calculate overall average rating
	if overall_analytics["site_analytics"]:
		total_rating = sum([s["average_rating"] for s in overall_analytics["site_analytics"] if s["average_rating"] > 0])
		sites_with_rating = len([s for s in overall_analytics["site_analytics"] if s["average_rating"] > 0])
		if sites_with_rating > 0:
			overall_analytics["average_rating"] = total_rating / sites_with_rating
	
	# Save monthly analytics
	save_monthly_analytics(overall_analytics)
	
	# Send monthly report to management
	send_monthly_analytics_report(overall_analytics)

def generate_site_monthly_analytics(site, month_start, month_end):
	"""Generate monthly analytics for a specific construction site"""
	
	# Get inspections for the month
	inspections = frappe.get_all("Supplier Inspection",
		filters={
			"construction_site": site.name,
			"inspection_date": ["between", [month_start, month_end]],
			"docstatus": 1
		},
		fields=["name", "inspection_date", "inspector", "overall_rating", 
				"safety_rating", "quality_rating", "progress_rating", 
				"issues_found", "corrective_actions", "approval_status"]
	)
	
	total_inspections = len(inspections)
	
	if total_inspections == 0:
		return {
			"site_name": site.site_name,
			"site_code": site.name,
			"supplier": site.supplier,
			"total_inspections": 0,
			"average_rating": 0,
			"average_safety_rating": 0,
			"average_quality_rating": 0,
			"average_progress_rating": 0,
			"total_issues": 0,
			"approval_rate": 0,
			"inspector_distribution": {},
			"rating_trend": []
		}
	
	# Calculate averages
	avg_overall_rating = sum([insp.overall_rating or 0 for insp in inspections]) / total_inspections
	avg_safety_rating = sum([insp.safety_rating or 0 for insp in inspections]) / total_inspections
	avg_quality_rating = sum([insp.quality_rating or 0 for insp in inspections]) / total_inspections
	avg_progress_rating = sum([insp.progress_rating or 0 for insp in inspections]) / total_inspections
	
	total_issues = sum([insp.issues_found or 0 for insp in inspections])
	
	# Calculate approval rate
	approved_inspections = len([insp for insp in inspections if insp.approval_status == "Approved"])
	approval_rate = (approved_inspections / total_inspections) * 100 if total_inspections > 0 else 0
	
	# Inspector distribution
	inspector_distribution = {}
	for inspection in inspections:
		inspector = inspection.inspector
		if inspector:
			if inspector not in inspector_distribution:
				inspector_distribution[inspector] = 0
			inspector_distribution[inspector] += 1
	
	# Rating trend (weekly averages)
	rating_trend = []
	current_date = month_start
	while current_date <= month_end:
		week_end = min(add_days(current_date, 6), month_end)
		week_inspections = [insp for insp in inspections 
						   if current_date <= getdate(insp.inspection_date) <= week_end]
		
		if week_inspections:
			week_avg = sum([insp.overall_rating or 0 for insp in week_inspections]) / len(week_inspections)
			rating_trend.append({
				"week_start": current_date,
				"week_end": week_end,
				"average_rating": round(week_avg, 1),
				"inspection_count": len(week_inspections)
			})
		
		current_date = add_days(current_date, 7)
	
	return {
		"site_name": site.site_name,
		"site_code": site.name,
		"supplier": site.supplier,
		"total_inspections": total_inspections,
		"average_rating": round(avg_overall_rating, 1),
		"average_safety_rating": round(avg_safety_rating, 1),
		"average_quality_rating": round(avg_quality_rating, 1),
		"average_progress_rating": round(avg_progress_rating, 1),
		"total_issues": total_issues,
		"approval_rate": round(approval_rate, 1),
		"inspector_distribution": inspector_distribution,
		"rating_trend": rating_trend
	}

def save_monthly_analytics(analytics_data):
	"""Save monthly analytics to database"""
	
	# Create monthly analytics document
	monthly_analytics = frappe.get_doc({
		"doctype": "Monthly Inspection Analytics",
		"month_start": analytics_data["month_start"],
		"month_end": analytics_data["month_end"],
		"total_sites": analytics_data["total_sites"],
		"total_inspections": analytics_data["total_inspections"],
		"average_rating": analytics_data["average_rating"],
		"total_issues": analytics_data["total_issues"],
		"analytics_data": json.dumps(analytics_data),
		"generated_on": today(),
		"generated_by": "System"
	})
	
	# Add site analytics details
	for site_data in analytics_data["site_analytics"]:
		monthly_analytics.append("site_analytics", {
			"site_name": site_data["site_name"],
			"site_code": site_data["site_code"],
			"supplier": site_data["supplier"],
			"total_inspections": site_data["total_inspections"],
			"average_rating": site_data["average_rating"],
			"total_issues": site_data["total_issues"],
			"approval_rate": site_data["approval_rate"]
		})
	
	# Add supplier performance details
	for supplier, perf_data in analytics_data["supplier_performance"].items():
		monthly_analytics.append("supplier_performance", {
			"supplier": supplier,
			"total_inspections": perf_data["total_inspections"],
			"average_rating": perf_data["average_rating"],
			"total_issues": perf_data["total_issues"],
			"total_sites": len(perf_data["sites"])
		})
	
	monthly_analytics.insert(ignore_permissions=True)

def send_monthly_analytics_report(analytics_data):
	"""Send monthly analytics report to management"""
	
	# Get management users
	management_users = frappe.get_all("User",
		filters={
			"enabled": 1,
			"name": ["in", frappe.get_all("Has Role", 
				filters={"role": ["in", ["System Manager", "Construction Manager"]]},
				pluck="parent"
			)]
		},
		fields=["name", "email", "full_name"]
	)
	
	if not management_users:
		return
	
	subject = _("Monthly Construction Inspection Analytics - {0}").format(
		analytics_data["month_start"].strftime("%Y年%m月")
	)
	
	# Generate report content
	report_content = generate_monthly_analytics_html(analytics_data)
	
	# Send email to management
	for user in management_users:
		if user.email:
			frappe.sendmail(
				recipients=[user.email],
				subject=subject,
				message=report_content,
				delayed=False
			)

def generate_monthly_analytics_html(analytics):
	"""Generate HTML content for monthly analytics report"""
	
	html_content = f"""
	<div style="font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto;">
		<h1 style="color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 15px;">
			月度施工現場巡檢分析報告
		</h1>
		<p style="text-align: center; color: #7f8c8d; font-size: 16px;">
			報告期間: {analytics["month_start"].strftime("%Y年%m月%d日")} - {analytics["month_end"].strftime("%Y年%m月%d日")}
		</p>
		
		<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0;">
			<div style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 20px; border-radius: 10px; text-align: center;">
				<h3 style="margin: 0; font-size: 24px;">{analytics["total_sites"]}</h3>
				<p style="margin: 5px 0 0 0;">總施工現場</p>
			</div>
			<div style="background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; padding: 20px; border-radius: 10px; text-align: center;">
				<h3 style="margin: 0; font-size: 24px;">{analytics["total_inspections"]}</h3>
				<p style="margin: 5px 0 0 0;">總巡檢次數</p>
			</div>
			<div style="background: linear-gradient(135deg, #f39c12, #e67e22); color: white; padding: 20px; border-radius: 10px; text-align: center;">
				<h3 style="margin: 0; font-size: 24px;">{analytics["average_rating"]:.1f}</h3>
				<p style="margin: 5px 0 0 0;">平均評分</p>
			</div>
			<div style="background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 20px; border-radius: 10px; text-align: center;">
				<h3 style="margin: 0; font-size: 24px;">{analytics["total_issues"]}</h3>
				<p style="margin: 5px 0 0 0;">發現問題總數</p>
			</div>
		</div>
		
		<div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; margin: 30px 0;">
			<h2 style="color: #2c3e50; margin-top: 0;">供應商績效排名</h2>
			<table style="width: 100%; border-collapse: collapse; background: white; border-radius: 5px; overflow: hidden;">
				<thead>
					<tr style="background-color: #34495e; color: white;">
						<th style="padding: 15px; text-align: left;">供應商</th>
						<th style="padding: 15px; text-align: center;">巡檢次數</th>
						<th style="padding: 15px; text-align: center;">平均評分</th>
						<th style="padding: 15px; text-align: center;">問題數量</th>
						<th style="padding: 15px; text-align: center;">管理現場數</th>
					</tr>
				</thead>
				<tbody>
	"""
	
	# Sort suppliers by average rating
	sorted_suppliers = sorted(analytics["supplier_performance"].items(), 
							 key=lambda x: x[1]["average_rating"], reverse=True)
	
	for i, (supplier, perf) in enumerate(sorted_suppliers):
		row_color = "#f8f9fa" if i % 2 == 0 else "white"
		html_content += f"""
					<tr style="background-color: {row_color};">
						<td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{supplier}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{perf["total_inspections"]}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{perf["average_rating"]:.1f}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{perf["total_issues"]}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{len(perf["sites"])}</td>
					</tr>
		"""
	
	html_content += """
				</tbody>
			</table>
		</div>
		
		<div style="background-color: #f8f9fa; padding: 25px; border-radius: 10px; margin: 30px 0;">
			<h2 style="color: #2c3e50; margin-top: 0;">現場績效詳情</h2>
			<table style="width: 100%; border-collapse: collapse; background: white; border-radius: 5px; overflow: hidden;">
				<thead>
					<tr style="background-color: #34495e; color: white;">
						<th style="padding: 15px; text-align: left;">現場名稱</th>
						<th style="padding: 15px; text-align: left;">供應商</th>
						<th style="padding: 15px; text-align: center;">巡檢次數</th>
						<th style="padding: 15px; text-align: center;">平均評分</th>
						<th style="padding: 15px; text-align: center;">問題數量</th>
						<th style="padding: 15px; text-align: center;">通過率</th>
					</tr>
				</thead>
				<tbody>
	"""
	
	# Sort sites by average rating
	sorted_sites = sorted(analytics["site_analytics"], 
						 key=lambda x: x["average_rating"], reverse=True)
	
	for i, site in enumerate(sorted_sites):
		row_color = "#f8f9fa" if i % 2 == 0 else "white"
		html_content += f"""
					<tr style="background-color: {row_color};">
						<td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{site["site_name"]}</td>
						<td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{site["supplier"] or 'N/A'}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{site["total_inspections"]}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{site["average_rating"]:.1f}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{site["total_issues"]}</td>
						<td style="padding: 12px; text-align: center; border-bottom: 1px solid #dee2e6;">{site["approval_rate"]:.1f}%</td>
					</tr>
		"""
	
	html_content += """
				</tbody>
			</table>
		</div>
		
		<div style="background-color: #e8f5e8; padding: 20px; border-radius: 10px; margin: 30px 0;">
			<h3 style="color: #2c3e50; margin-top: 0;">關鍵洞察</h3>
			<ul style="color: #2c3e50; line-height: 1.6;">
	"""
	
	if analytics["average_rating"] >= 4:
		html_content += "<li>✅ 整體巡檢評分表現優秀，品質控制良好</li>"
	elif analytics["average_rating"] >= 3:
		html_content += "<li>⚠️ 整體巡檢評分中等，仍有改善空間</li>"
	else:
		html_content += "<li>❌ 整體巡檢評分偏低，需要重點關注品質改善</li>"
	
	if analytics["total_issues"] > 0:
		avg_issues_per_inspection = analytics["total_issues"] / analytics["total_inspections"] if analytics["total_inspections"] > 0 else 0
		html_content += f"<li>📊 平均每次巡檢發現 {avg_issues_per_inspection:.1f} 個問題</li>"
	
	if sorted_suppliers:
		best_supplier = sorted_suppliers[0]
		html_content += f"<li>🏆 表現最佳供應商: {best_supplier[0]} (評分: {best_supplier[1]['average_rating']:.1f})</li>"
	
	html_content += """
			</ul>
		</div>
		
		<div style="text-align: center; margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
			<p style="color: #7f8c8d; margin: 0;">
				此報告由施工現場巡檢系統自動生成 | 生成時間: """ + today() + """
			</p>
		</div>
	</div>
	"""
	
	return html_content

def archive_completed_inspections():
	"""Archive completed inspections older than 1 year"""
	
	one_year_ago = add_days(today(), -365)
	
	# Get completed inspections older than 1 year
	old_inspections = frappe.get_all("Supplier Inspection",
		filters={
			"inspection_date": ["<", one_year_ago],
			"docstatus": 1,
			"approval_status": "Approved"
		},
		fields=["name"]
	)
	
	archived_count = 0
	
	for inspection in old_inspections:
		try:
			# Move to archive table (if exists) or mark as archived
			inspection_doc = frappe.get_doc("Supplier Inspection", inspection.name)
			inspection_doc.db_set("is_archived", 1)
			archived_count += 1
			
		except Exception as e:
			frappe.log_error(f"Error archiving inspection {inspection.name}: {str(e)}")
	
	if archived_count > 0:
		frappe.log_error(f"Archived {archived_count} old inspections")

@frappe.whitelist()
def get_monthly_analytics_data(month_start=None):
	"""Get monthly analytics data for API access"""
	
	if not month_start:
		month_start = add_months(today(), -1).replace(day=1)
	else:
		month_start = getdate(month_start)
	
	month_end = add_days(add_months(month_start, 1), -1)
	
	# Check if analytics already exist
	existing_analytics = frappe.get_value("Monthly Inspection Analytics",
		filters={
			"month_start": month_start,
			"month_end": month_end
		},
		fieldname="analytics_data"
	)
	
	if existing_analytics:
		return json.loads(existing_analytics)
	
	# Generate new analytics
	generate_monthly_analytics()
	
	# Return newly generated analytics
	new_analytics = frappe.get_value("Monthly Inspection Analytics",
		filters={
			"month_start": month_start,
			"month_end": month_end
		},
		fieldname="analytics_data"
	)
	
	return json.loads(new_analytics) if new_analytics else {}