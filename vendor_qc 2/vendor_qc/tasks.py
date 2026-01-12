import frappe
from frappe.utils import nowdate

def escalate_overdue_ncrs():
    """Find overdue NCRs and escalate by creating/updating a linked Issue."""
    ncrs = frappe.get_all("NCR",
        filters={"status": ["in", ["Open", "Under Review"]], "due_date": ["<", nowdate()]},
        fields=["name","title","supplier","owner"])
    for n in ncrs:
        issue = frappe.get_value("Issue", {"ncr": n["name"]}, "name")
        subject = f"NCR Overdue: {n['name']} · {n['title']}"
        if not issue:
            issue = frappe.get_doc({
                "doctype": "Issue",
                "subject": subject,
                "priority": "High",
                "ncr": n["name"],
                "raised_by": frappe.get_value("User", n["owner"], "email")
            }).insert(ignore_permissions=True)
        else:
            iss = frappe.get_doc("Issue", issue)
            iss.priority = "High"
            iss.save(ignore_permissions=True)
        # optional: send email/notification here
