from frappe import _

def get_data():
    return [
        {
            "module_name": "Vendor QC",
            "category": "Modules",
            "label": _("Vendor QC"),
            "color": "purple",
            "icon": "octicon octicon-checklist",
            "type": "module",
            "description": _("Vendor QC module")
        }
    ]
