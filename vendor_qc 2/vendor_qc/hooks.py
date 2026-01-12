from . import __version__ as app_version

app_name = "vendor_qc"
app_title = "Vendor QC"
app_publisher = "APP Dev"
app_description = "Vendor inspection (Contractor QC) app on Frappe/ERPNext"
app_email = "dev@example.com"
app_license = "MIT"

# Scheduler
scheduler_events = {
    "cron": {
        "*/15 * * * *": ["vendor_qc.tasks.escalate_overdue_ncrs"]
    }
}
