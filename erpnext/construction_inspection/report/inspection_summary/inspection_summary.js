// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Inspection Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "construction_site",
			"label": __("Construction Site"),
			"fieldtype": "Link",
			"options": "Construction Site"
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname": "inspector",
			"label": __("Inspector"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "min_rating",
			"label": __("Minimum Rating"),
			"fieldtype": "Float",
			"precision": 1
		},
		{
			"fieldname": "max_rating",
			"label": __("Maximum Rating"),
			"fieldtype": "Float",
			"precision": 1
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nSubmitted\nApproved\nRejected"
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// 評分欄位的顏色格式化
		if (["safety_rating", "quality_rating", "progress_rating", "overall_rating"].includes(column.fieldname)) {
			const rating = parseFloat(data[column.fieldname]);
			if (rating >= 4.5) {
				value = `<span style="color: #28a745; font-weight: bold;">${value}</span>`;
			} else if (rating >= 3.5) {
				value = `<span style="color: #17a2b8; font-weight: bold;">${value}</span>`;
			} else if (rating >= 2.5) {
				value = `<span style="color: #ffc107; font-weight: bold;">${value}</span>`;
			} else if (rating > 0) {
				value = `<span style="color: #dc3545; font-weight: bold;">${value}</span>`;
			}
		}
		
		// 狀態欄位的格式化
		if (column.fieldname === "status") {
			const status = data.status;
			let color = "#6c757d";
			if (status === "Approved") color = "#28a745";
			else if (status === "Submitted") color = "#17a2b8";
			else if (status === "Rejected") color = "#dc3545";
			
			value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
		}
		
		// 問題數量的格式化
		if (column.fieldname === "issues_count") {
			const count = parseInt(data.issues_count);
			if (count > 0) {
				value = `<span style="color: #dc3545; font-weight: bold;">${count}</span>`;
			}
		}
		
		return value;
	},
	
	"onload": function(report) {
		// 添加自定義按鈕
		report.page.add_inner_button(__("Export to Excel"), function() {
			frappe.query_report.export_report();
		});
		
		report.page.add_inner_button(__("Analytics Dashboard"), function() {
			frappe.set_route("query-report", "Inspection Analytics");
		});
		
		report.page.add_inner_button(__("Create Inspection"), function() {
			frappe.new_doc("Supplier Inspection");
		});
		
		// 添加刷新按鈕
		report.page.add_action_icon("fa fa-refresh", function() {
			report.refresh();
		});
	},
	
	"after_datatable_render": function(datatable_obj) {
		// 添加行點擊事件
		$(datatable_obj.wrapper).find('.dt-row').on('click', function() {
			const data = datatable_obj.datamanager.getRow($(this).index());
			if (data && data[0].content) {
				frappe.set_route("Form", "Supplier Inspection", data[0].content);
			}
		});
		
		// 添加工具提示
		$(datatable_obj.wrapper).find('[data-original-title]').tooltip();
	}
};

// 自定義函數：獲取巡檢分析數據
function get_inspection_analytics() {
	const filters = frappe.query_report.get_filter_values();
	
	frappe.call({
		method: "erpnext.construction_inspection.report.inspection_summary.inspection_summary.get_inspection_analytics",
		args: {
			filters: filters
		},
		callback: function(r) {
			if (r.message) {
				show_analytics_dialog(r.message);
			}
		}
	});
}

// 顯示分析對話框
function show_analytics_dialog(data) {
	const dialog = new frappe.ui.Dialog({
		title: __("Inspection Analytics"),
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "analytics_html"
			}
		]
	});
	
	const stats = data.stats;
	const monthly_trend = data.monthly_trend;
	const supplier_ranking = data.supplier_ranking;
	
	const html = `
		<div class="analytics-container">
			<div class="row">
				<div class="col-md-6">
					<div class="card">
						<div class="card-header">
							<h5>基本統計</h5>
						</div>
						<div class="card-body">
							<table class="table table-borderless">
								<tr>
									<td>總巡檢次數:</td>
									<td><strong>${stats.total_inspections}</strong></td>
								</tr>
								<tr>
									<td>平均評分:</td>
									<td><strong>${(stats.avg_rating || 0).toFixed(1)}</strong></td>
								</tr>
								<tr>
									<td>優秀評分數:</td>
									<td><strong>${stats.excellent_count}</strong></td>
								</tr>
								<tr>
									<td>待改進數:</td>
									<td><strong>${stats.poor_count}</strong></td>
								</tr>
								<tr>
									<td>涉及現場數:</td>
									<td><strong>${stats.sites_inspected}</strong></td>
								</tr>
								<tr>
									<td>涉及供應商數:</td>
									<td><strong>${stats.suppliers_involved}</strong></td>
								</tr>
							</table>
						</div>
					</div>
				</div>
				<div class="col-md-6">
					<div class="card">
						<div class="card-header">
							<h5>供應商排名 (前10名)</h5>
						</div>
						<div class="card-body">
							<table class="table table-sm">
								<thead>
									<tr>
										<th>供應商</th>
										<th>平均評分</th>
										<th>巡檢次數</th>
									</tr>
								</thead>
								<tbody>
									${supplier_ranking.map((supplier, index) => `
										<tr>
											<td>${supplier.supplier}</td>
											<td><span class="badge badge-${supplier.avg_rating >= 4.5 ? 'success' : supplier.avg_rating >= 3.5 ? 'info' : 'warning'}">${supplier.avg_rating.toFixed(1)}</span></td>
											<td>${supplier.inspection_count}</td>
										</tr>
									`).join('')}
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</div>
		</div>
	`;
	
	dialog.fields_dict.analytics_html.$wrapper.html(html);
	dialog.show();
}

// 添加CSS樣式
frappe.provide("frappe.query_reports");
$(`
<style>
	.analytics-container .card {
		margin-bottom: 20px;
		border: 1px solid #dee2e6;
		border-radius: 8px;
	}
	
	.analytics-container .card-header {
		background-color: #f8f9fa;
		border-bottom: 1px solid #dee2e6;
		padding: 12px 20px;
	}
	
	.analytics-container .card-header h5 {
		margin: 0;
		font-size: 16px;
		font-weight: 600;
	}
	
	.analytics-container .card-body {
		padding: 20px;
	}
	
	.analytics-container .table td {
		padding: 8px 0;
		border: none;
	}
	
	.analytics-container .table th {
		border-bottom: 2px solid #dee2e6;
		font-weight: 600;
	}
	
	.analytics-container .badge {
		font-size: 12px;
		padding: 4px 8px;
	}
</style>
`).appendTo("head");