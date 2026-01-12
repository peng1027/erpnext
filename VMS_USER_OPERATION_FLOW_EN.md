# VMS (Visitor Management System) - User Operation Flow

## Document Information
- **Version**: 1.0
- **Date**: 2025-11-26
- **System URL**: https://vendorqc.duckdns.org
- **Platform**: Frappe/ERPNext v15

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [User Roles](#2-user-roles)
3. [Reception Staff Operations](#3-reception-staff-operations)
4. [Security Guard Operations](#4-security-guard-operations)
5. [Host Employee Operations](#5-host-employee-operations)
6. [Administrator Operations](#6-administrator-operations)
7. [API Integration Guide](#7-api-integration-guide)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. System Overview

### 1.1 Key Features
| Feature | Description |
|---------|-------------|
| Visitor Pass Issuance | Create and issue visitor passes with QR codes |
| QR Code Scanning | Entry/exit tracking via QR code scanning |
| Multi-Entry Support | Long-term passes support multiple entries |
| Host Notifications | Email notifications when visitors arrive/depart |
| Security Dashboard | Real-time monitoring of visitor activity |
| Duplicate Scan Protection | 5-minute cooldown prevents accidental double scans |

### 1.2 Pass Status Flow
```
[Issued] --> [Active] --> [Used/Expired]
    |            |
    |            +--> [Active] (for multi-day passes after exit)
    |
    +--> [Cancelled]
```

| Status | Description |
|--------|-------------|
| Issued | Pass created but visitor has not entered yet |
| Active | Visitor has entered and is currently on premises |
| Used | Visitor has exited (single-day pass) |
| Expired | Pass validity period has ended |
| Cancelled | Pass manually cancelled by administrator |

---

## 2. User Roles

### 2.1 Reception Staff
- Create new visitor passes
- Print/send QR codes to visitors
- View visitor information

### 2.2 Security Guard
- Scan QR codes at entry/exit gates
- Verify visitor identity
- Monitor active visitors

### 2.3 Host Employee
- Receive arrival/departure notifications
- Pre-register expected visitors (optional)

### 2.4 System Administrator
- Manage visitor pass settings
- Access security dashboard
- Generate reports
- Cancel/modify passes

---

## 3. Reception Staff Operations

### 3.1 Creating a New Visitor Pass

**Step 1: Access the Visitor Pass Form**
1. Login to the system: https://vendorqc.duckdns.org
2. Navigate to: **Vendor Inspection** > **Visitor Pass** > **+ Add Visitor Pass**

**Step 2: Fill in Visitor Information**

| Field | Required | Description |
|-------|----------|-------------|
| Visitor Name | Yes | Full name of the visitor |
| Mobile Number | No | Contact phone number |
| Visitor From | No | Company/Organization visitor represents |
| ID Type | No | Type of identification (ID Card, Passport, etc.) |
| ID Number | No | Identification number |
| Visitor Photo | No | Upload visitor photo for verification |

**Step 3: Fill in Visit Details**

| Field | Required | Description |
|-------|----------|-------------|
| Visitor Type | Yes | Visitor / Contractor / VIP / Interview |
| To Meet | Yes | Name of host employee |
| Department | No | Department to visit |
| Purpose | No | Reason for visit |
| Meeting Location | No | Specific meeting room/area |

**Step 4: Set Validity Period**

| Field | Required | Description |
|-------|----------|-------------|
| Valid From | Yes | Start date/time of pass validity |
| Validity Days | Yes | Number of days pass is valid (1-365) |
| Valid Until | Auto | Automatically calculated end date |

**Step 5: Configure Notifications**

| Option | Default | Description |
|--------|---------|-------------|
| Notify Host on Arrival | Yes | Send email when visitor enters |
| Notify Host on Departure | No | Send email when visitor exits |
| Send Pass to Visitor | No | Send QR code to visitor's email |

**Step 6: Save and Issue Pass**
1. Click **Save** button
2. System auto-generates:
   - Pass Number (format: VP-YYYYMMDD-####)
   - QR Code containing pass data
3. Print or email the QR code to the visitor

### 3.2 Printing a Visitor Pass

1. Open the saved Visitor Pass document
2. Click **Print** > **Visitor Pass Print**
3. The printout includes:
   - Visitor name and photo
   - Pass number
   - QR code
   - Validity period
   - Host information

### 3.3 Sending Pass via Email

1. Open the Visitor Pass document
2. Click **Menu** > **Send Pass to Visitor**
3. Visitor receives email with:
   - QR code image
   - Pass details
   - Entry instructions

---

## 4. Security Guard Operations

### 4.1 QR Code Scanning (Entry)

**Using Web Interface:**
1. Open scanner page: https://vendorqc.duckdns.org/visitor-scan
2. Point camera at visitor's QR code
3. System displays:
   - Visitor name and photo
   - Pass validity status
   - Host information
4. If valid: **"Entry granted. Welcome [Name]!"**
5. System automatically:
   - Records entry time
   - Logs entry gate
   - Updates status to "Active"
   - Sends notification to host (if enabled)

**Using API (for integrated devices):**
```bash
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.verify_visitor_pass
{
    "qr_data": "{\"type\":\"VISITOR_PASS\",\"pass_number\":\"VP-20251126-0001\"...}",
    "gate_id": "Main Gate"
}
```

### 4.2 QR Code Scanning (Exit)

1. Scan the same QR code when visitor leaves
2. System automatically detects this is an exit
3. System displays:
   - **"Exit recorded. Thank you [Name]! Duration: X.X hours"**
4. System automatically:
   - Records exit time
   - Calculates visit duration
   - Sends departure notification (if enabled)
   - Updates status appropriately

### 4.3 Handling Scan Errors

| Error Message | Cause | Action |
|---------------|-------|--------|
| "Pass not yet valid" | Visitor arrived before valid_from | Ask visitor to wait or contact host |
| "Pass expired" | Pass validity has ended | Contact reception for new pass |
| "Pass has been cancelled" | Pass was cancelled | Contact administrator |
| "Please wait X seconds" | Duplicate scan protection | Wait for cooldown period |

### 4.4 Viewing Active Visitors

1. Access Security Dashboard: **Vendor Inspection** > **Security Dashboard**
2. Or use API:
```bash
GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors
```
3. Dashboard shows:
   - List of all visitors currently on-site
   - Entry time and gate
   - Host and department information

---

## 5. Host Employee Operations

### 5.1 Receiving Arrival Notifications

When a visitor arrives, hosts receive an email containing:
- Visitor name and company
- Pass number
- Entry time and gate
- Visit purpose
- Meeting location
- Action prompt: "Please proceed to receive your visitor"

### 5.2 Receiving Departure Notifications

When a visitor departs (if enabled), hosts receive:
- Visitor name
- Exit time
- Total visit duration

### 5.3 Pre-Registering Visitors (Optional)

Hosts can pre-register expected visitors:
1. Navigate to: **Vendor Inspection** > **Visitor Pass** > **+ Add Visitor Pass**
2. Fill in visitor and meeting details
3. Set appropriate validity period
4. Save - pass is ready for visitor arrival
5. Optionally send QR code to visitor in advance

---

## 6. Administrator Operations

### 6.1 Accessing Security Dashboard

**Via Web:**
1. Login as administrator
2. Navigate to: **Vendor Inspection** > **Security Dashboard**

**Via API:**
```bash
GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_security_dashboard
```

**Dashboard Shows:**
| Metric | Description |
|--------|-------------|
| Active Visitors | Currently on-site visitors |
| Today's Entries | Total entries today |
| Today's Exits | Total exits today |
| Total Passes | All-time pass count |
| Status Breakdown | Passes by status (Issued, Active, Used, etc.) |
| Recent Activity | Latest 10 entry/exit events |

### 6.2 Cancelling a Visitor Pass

**Via Web:**
1. Open the Visitor Pass document
2. Click **Menu** > **Cancel Pass**
3. Confirm cancellation

**Via API:**
```bash
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.cancel_visitor_pass
{
    "pass_name": "VP-20251126-0001",
    "reason": "Visitor meeting cancelled"
}
```

### 6.3 Viewing Visitor History

**For a Specific Visitor:**
```bash
GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_visitor_history
?visitor_name=John Smith
&from_date=2025-01-01
&to_date=2025-12-31
```

**Response includes:**
- All passes for the visitor
- Entry/exit logs with timestamps
- Total visits and duration

### 6.4 Managing Entry/Exit Logs

Each Visitor Pass has a Child Table "Entry Exit Logs" containing:

| Field | Description |
|-------|-------------|
| Entry Datetime | When visitor entered |
| Exit Datetime | When visitor exited |
| Device ID | Which gate/scanner was used |
| Entry Method | QR Code / Fingerprint / Face Recognition |
| Duration Hours | Calculated time spent |
| Notes | Any additional notes |

---

## 7. API Integration Guide

### 7.1 Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verify_visitor_pass` | POST | Verify QR code and record entry/exit |
| `/attendance_webhook` | POST | Webhook for external devices |
| `/get_active_visitors` | GET | List current on-site visitors |
| `/get_security_dashboard` | GET | Dashboard statistics |
| `/cancel_visitor_pass` | POST | Cancel a pass |
| `/get_visitor_history` | GET | Visitor visit history |

### 7.2 Device Integration (Attendance Webhook)

For integrating external devices (biometric, turnstiles, etc.):

```bash
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.attendance_webhook

Parameters:
- device_id: "GATE-01" (device identifier)
- event_type: "entry" or "exit"
- identifier: pass_number or QR data
- identifier_type: "qr", "pass_number", "fingerprint", "face"
- timestamp: optional (defaults to now)

Example Request:
{
    "device_id": "TURNSTILE-MAIN",
    "event_type": "entry",
    "identifier": "VP-20251126-0001",
    "identifier_type": "pass_number"
}

Example Response:
{
    "success": true,
    "message": "Entry recorded for John Smith",
    "event_type": "entry",
    "device_id": "TURNSTILE-MAIN",
    "visitor_data": {
        "pass_number": "VP-20251126-0001",
        "visitor_name": "John Smith",
        "visitor_type": "Visitor",
        "department": "Engineering",
        "to_meet": "Jane Doe",
        "entry_time": "2025-11-26 14:30:00",
        "status": "Active"
    }
}
```

### 7.3 Duplicate Scan Protection

- **Cooldown Period**: 5 minutes (300 seconds)
- Same pass scanned within cooldown returns:
```json
{
    "success": false,
    "message": "Please wait 291 seconds before scanning again",
    "cooldown_remaining": 291
}
```

---

## 8. Troubleshooting

### 8.1 Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| QR code won't scan | Poor print quality | Reprint at higher resolution |
| "Pass not found" error | Wrong pass number | Verify pass exists in system |
| No notification sent | Email not configured | Check SMTP settings |
| Host not receiving emails | Employee email not set | Update employee record |

### 8.2 Status Not Updating

If pass status doesn't update after scan:
1. Check browser console for errors
2. Verify network connectivity
3. Check server logs: `bench --site vendorqc.localhost show-logs`

### 8.3 Duplicate Scan Blocked

If legitimate scan is blocked:
1. Wait for cooldown period (5 minutes max)
2. Or use a different gate/device
3. Administrator can manually update pass if needed

### 8.4 Contact Support

For technical issues:
- Email: support@example.com
- System Admin: Check Error Logs in Frappe

---

## Appendix A: Pass Number Format

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | VP- | VP- |
| Date | YYYYMMDD | 20251126 |
| Separator | - | - |
| Sequence | 0001-9999 | 0001 |
| **Full Format** | VP-YYYYMMDD-#### | VP-20251126-0001 |

## Appendix B: QR Code Data Structure

```json
{
    "type": "VISITOR_PASS",
    "pass_number": "VP-20251126-0001",
    "name": "VP-20251126-0001",
    "visitor_name": "John Smith",
    "visitor_from": "ABC Company",
    "to_meet": "Jane Doe",
    "department": "Engineering",
    "meeting_location": "Meeting Room A",
    "visitor_type": "Visitor",
    "purpose": "Business Meeting",
    "mobile": "+1234567890",
    "valid_from": "2025-11-26 09:00:00",
    "valid_until": "2025-11-26 18:00:00",
    "status": "Issued",
    "generated_at": "2025-11-26T08:30:00.000000"
}
```

---

**Document End**
