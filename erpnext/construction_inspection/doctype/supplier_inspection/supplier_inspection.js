// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Inspection', {
    refresh: function(frm) {
        // 添加自定義按鈕
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('從模板創建'), function() {
                create_from_template(frm);
            });
            
            frm.add_custom_button(__('快速巡檢'), function() {
                open_mobile_inspection(frm);
            });
        }
        
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('生成報告'), function() {
                generate_inspection_report(frm);
            });
            
            frm.add_custom_button(__('創建跟進任務'), function() {
                create_follow_up_task(frm);
            });
        }
        
        // 設置字段樣式
        setup_field_styling(frm);
        
        // 計算評分
        calculate_ratings(frm);
    },
    
    construction_site: function(frm) {
        if (frm.doc.construction_site) {
            // 自動填充供應商信息
            frappe.db.get_value('Construction Site', frm.doc.construction_site, 'supplier')
                .then(r => {
                    if (r.message.supplier) {
                        frm.set_value('supplier', r.message.supplier);
                    }
                });
        }
    },
    
    safety_compliance: function(frm) {
        calculate_overall_rating(frm);
    },
    
    quality_rating: function(frm) {
        calculate_overall_rating(frm);
    },
    
    progress_rating: function(frm) {
        calculate_overall_rating(frm);
    }
});

function setup_field_styling(frm) {
    // 為移動端優化字段顯示
    if (frappe.utils.is_mobile()) {
        frm.toggle_display(['column_break_3', 'column_break_9', 'column_break_15', 
                           'column_break_23', 'column_break_29', 'column_break_35'], false);
    }
    
    // 設置評分字段的顏色
    setTimeout(() => {
        const rating_fields = ['safety_compliance', 'quality_rating', 'progress_rating', 'overall_rating'];
        rating_fields.forEach(field => {
            const field_wrapper = frm.get_field(field).$wrapper;
            if (field_wrapper) {
                const rating_value = frm.doc[field];
                if (rating_value >= 4) {
                    field_wrapper.addClass('rating-good');
                } else if (rating_value >= 3) {
                    field_wrapper.addClass('rating-medium');
                } else if (rating_value > 0) {
                    field_wrapper.addClass('rating-poor');
                }
            }
        });
    }, 500);
}

function calculate_overall_rating(frm) {
    const ratings = [];
    
    if (frm.doc.safety_compliance) ratings.push(frm.doc.safety_compliance);
    if (frm.doc.quality_rating) ratings.push(frm.doc.quality_rating);
    if (frm.doc.progress_rating) ratings.push(frm.doc.progress_rating);
    
    if (ratings.length > 0) {
        const overall = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        frm.set_value('overall_rating', Math.round(overall * 10) / 10);
    }
}

function calculate_ratings(frm) {
    if (frm.doc.checklist_items && frm.doc.checklist_items.length > 0) {
        let total_weight = 0;
        let weighted_score = 0;
        
        frm.doc.checklist_items.forEach(item => {
            if (item.rating && item.weight) {
                total_weight += item.weight;
                weighted_score += item.rating * item.weight;
            }
        });
        
        if (total_weight > 0) {
            const calculated_rating = weighted_score / total_weight;
            frm.set_value('overall_rating', Math.round(calculated_rating * 10) / 10);
        }
    }
}

function create_from_template(frm) {
    const d = new frappe.ui.Dialog({
        title: __('選擇巡檢模板'),
        fields: [
            {
                fieldtype: 'Link',
                fieldname: 'template',
                label: __('巡檢模板'),
                options: 'Inspection Template',
                reqd: 1
            }
        ],
        primary_action: function() {
            const values = d.get_values();
            if (values.template) {
                frappe.call({
                    method: 'erpnext.construction_inspection.doctype.supplier_inspection.supplier_inspection.create_inspection_from_template',
                    args: {
                        construction_site: frm.doc.construction_site,
                        template_name: values.template
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.clear_table('checklist_items');
                            r.message.checklist_items.forEach(item => {
                                const row = frm.add_child('checklist_items');
                                Object.assign(row, item);
                            });
                            frm.refresh_field('checklist_items');
                            d.hide();
                        }
                    }
                });
            }
        },
        primary_action_label: __('創建')
    });
    d.show();
}

function open_mobile_inspection(frm) {
    // 打開移動端巡檢界面
    const mobile_url = `/app/mobile-inspection/${frm.doc.name}`;
    if (frappe.utils.is_mobile()) {
        window.location.href = mobile_url;
    } else {
        window.open(mobile_url, '_blank', 'width=400,height=800');
    }
}

function generate_inspection_report(frm) {
    frappe.call({
        method: 'frappe.utils.print_format.download_pdf',
        args: {
            doctype: frm.doc.doctype,
            name: frm.doc.name,
            format: 'Inspection Report',
            letterhead: 1
        },
        callback: function(r) {
            if (r.message) {
                window.open(r.message.file_url);
            }
        }
    });
}

function create_follow_up_task(frm) {
    frappe.new_doc('Task', {
        subject: `巡檢跟進 - ${frm.doc.inspection_title}`,
        description: frm.doc.corrective_actions,
        project: frm.doc.project,
        priority: frm.doc.inspection_status === '不通過' ? 'High' : 'Medium'
    });
}

// 檢查清單項目表格事件
frappe.ui.form.on('Inspection Checklist Item', {
    status: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.status === '通過') {
            frappe.model.set_value(cdt, cdn, 'rating', 5);
        } else if (row.status === '不通過') {
            frappe.model.set_value(cdt, cdn, 'rating', 1);
        }
        calculate_ratings(frm);
    },
    
    rating: function(frm, cdt, cdn) {
        calculate_ratings(frm);
    }
});

// 添加CSS樣式
frappe.ready(() => {
    const style = `
        <style>
        .rating-good .rating-wrapper {
            color: #28a745 !important;
        }
        .rating-medium .rating-wrapper {
            color: #ffc107 !important;
        }
        .rating-poor .rating-wrapper {
            color: #dc3545 !important;
        }
        
        @media (max-width: 768px) {
            .form-column {
                width: 100% !important;
            }
            .form-section {
                margin-bottom: 15px;
            }
            .btn-group {
                display: flex;
                flex-wrap: wrap;
            }
            .btn-group .btn {
                margin: 2px;
                flex: 1;
                min-width: 120px;
            }
        }
        </style>
    `;
    $('head').append(style);
});