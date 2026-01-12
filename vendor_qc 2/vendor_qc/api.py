import frappe, base64
from frappe.utils import nowdate

@frappe.whitelist()
def dashboard():
    # Simple counters
    open_ncr = frappe.db.count("NCR", {"status": ["in", ["Open","Under Review"]]})
    overdue = frappe.db.count("NCR", {"status": ["in", ["Open","Under Review"]], "due_date": ["<", nowdate()]})
    visits = frappe.db.count("Vendor Site Visit", {"creation": [">", nowdate() + " 00:00:00"]})
    return {"open_ncr": open_ncr, "overdue": overdue, "visits_today": visits}

@frappe.whitelist()
def list_sites():
    sites = frappe.get_all("Contractor Site", fields=["name","site_name","geofence_radius","project","supplier"])
    return sites

@frappe.whitelist()
def list_ncrs(supplier=None):
    filters = {}
    if supplier:
        filters["supplier"] = supplier
    ncrs = frappe.get_all("NCR", filters=filters, fields=["name","title","supplier","severity","due_date","status","site","project"])
    return ncrs

@frappe.whitelist()
def upload_image(content_base64:str, filename:str="photo.jpg"):
    data = base64.b64decode(content_base64.split(",")[-1])
    file = frappe.get_doc({
        "doctype":"File",
        "file_name": filename,
        "attached_to_doctype": None,
        "is_private": 1
    })
    file.insert(ignore_permissions=True)
    with open(file.get_full_path(), "wb") as f:
        f.write(data)
    return {"file_url": file.file_url, "file_name": file.file_name}

@frappe.whitelist()
def create_inspection(site:str, supplier:str, template:str=None, checklist:dict=None, remarks:str="", photos:list=None):
    """Create a Quality Inspection + link to our Contractor Site/Task as needed."""
    qi = frappe.get_doc({
        "doctype":"Quality Inspection",
        "inspection_type":"In Process",
        "reference_type":"Contractor Site",
        "reference_name": site,
        "supplier": supplier,
        "description": remarks or "Vendor QC mobile submission",
        "status":"Draft"
    }).insert()
    # attach photos
    if photos:
        for p in photos:
            try:
                upload = upload_image(p["content"], p.get("filename","photo.jpg"))
                qi.add_comment("Comment", text=f"Photo: {upload['file_url']}")
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Vendor QC upload photo failed")
    return {"quality_inspection": qi.name}

@frappe.whitelist()
def create_ncr(title:str, site:str, supplier:str, severity:str="Medium", due_date:str=None, description:str="", photos:list=None, project:str=None):
    doc = frappe.get_doc({
        "doctype":"NCR",
        "title": title,
        "site": site,
        "supplier": supplier,
        "severity": severity,
        "due_date": due_date or nowdate(),
        "status": "Open",
        "project": project,
        "description": description
    }).insert()
    # attach photos via child table
    if photos:
        for p in photos:
            try:
                upload = upload_image(p["content"], p.get("filename","ncr.jpg"))
                child = frappe.get_doc({"doctype":"NCR Photo","parenttype":"NCR","parent":doc.name,"parentfield":"photos","image":upload["file_url"]})
                child.insert()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "Vendor QC NCR photo failed")
    # create Issue for SLA tracking
    issue = frappe.get_doc({
        "doctype":"Issue",
        "subject": f"NCR {doc.name}: {doc.title}",
        "priority":"Medium",
        "ncr": doc.name
    }).insert()
    return {"ncr": doc.name, "issue": issue.name}

@frappe.whitelist()
def supplier_reply(ncr:str, message:str):
    doc = frappe.get_doc("NCR", ncr)
    doc.add_comment("Comment", text=f"Supplier CAPA: {message}")
    doc.status = "Under Review"
    doc.save()
    return {"ok": True}
