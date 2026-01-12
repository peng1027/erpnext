# Vendor QC (Frappe/ERPNext App)

A **complete, high-fidelity** Vendor Inspection (Contractor QC) system built on **Frappe/ERPNext**.

## Modules
- Custom DocTypes: Contractor Site, Vendor Site Visit, NCR, NCR Photo (child)
- Uses ERPNext built-ins: Project/Task, Supplier, Issue, Quality Inspection (+ Template)
- Portal/PWA: Mobile-first bilingual UI (EN ⇄ zh-Hant) with geofenced check-in, checklist, photo uploads
- API endpoints: create inspection, create NCR, supplier reply, dashboard, uploads
- Scheduler: Overdue NCR escalation to Issue with SLA

## Quickstart
```bash
# In your bench environment (ERPNext v15+ recommended)
cd ~/frappe-bench
bench get-app vendor_qc /path/to/vendor_qc  # or: bench get-app https://YOUR_REPO_URL.git
bench --site your.site.name install-app vendor_qc
bench restart
```

### Roles to create (or reuse existing):
- System Manager
- Inspector
- Supplier Supervisor
- PM
- ISM
- GA

(Assign in Role Permission Manager. Minimal permissions are included inside the DocType JSON.)

### Portal / App URL
After installation and login, open:
- **/app** (this app's PWA-like page): `/app/app`
- You can also add Desk shortcuts or Portal routes as needed.

### REST Endpoints (Session-authenticated)
- `POST /api/method/vendor_qc.api.create_inspection`
- `POST /api/method/vendor_qc.api.create_ncr`
- `POST /api/method/vendor_qc.api.supplier_reply`
- `POST /api/method/vendor_qc.api.dashboard`
- `POST /api/method/vendor_qc.api.list_sites`
- `POST /api/method/vendor_qc.api.list_ncrs`
- `POST /api/method/vendor_qc.api.upload_image` (base64)

A Postman collection is included at `postman/Vendor_QC.postman_collection.json`.
