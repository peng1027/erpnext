# VMS (Visitor Management System) - Standard Operating Procedures

## System Access
**Portal URL**: https://vendorqc.duckdns.org/app/vendor-inspection

**Document Version**: 1.0
**Last Updated**: November 25, 2025
**Status**: Phase 1A Complete - Production Ready

---

## Table of Contents
1. [Scenario 1: Vendor Visit for Product Inspection](#scenario-1-vendor-visit-for-product-inspection)
2. [Scenario 2: Long-term Contractor Access (7-Day Pass)](#scenario-2-long-term-contractor-access-7-day-pass)
3. [Scenario 3: Query Current Visitors On-Site](#scenario-3-query-current-visitors-on-site)
4. [System Architecture](#system-architecture)
5. [API Documentation](#api-documentation)
6. [Quick Action Buttons](#quick-action-buttons)

---

## Scenario 1: Vendor Visit for Product Inspection

### Use Case
- Vendor representatives visiting for quality audits
- Short-term visitors (same day or within a few days)

### Personnel Required
- Reception/Security Staff: Pass creation and gate scanning
- QA Inspector: Inspection record creation

---

### Step 1: Create Visitor Pass

**Operator**: Reception/Security Staff

**Actions**:
1. Access VMS System
2. Click **"New Visitor Pass"** quick action button
3. Fill in visitor information:

| Field | Example Value |
|-------|---------------|
| Visitor Name | John Smith |
| Visitor From | ABC Supplier Company |
| Mobile Number | +1-555-0123 |
| To Meet | QA Manager - David Lee |
| Department | Quality Management |
| Meeting Location | Inspection Lab A |
| Visitor Type | Vendor |
| Purpose | Product quality inspection and audit |
| Validity | 30 days (system default, adjustable to 1 day) |

4. Save - System automatically generates:
   - **Pass Number**: VP-20251125-0002
   - **QR Code**: For entry/exit scanning
5. Print or display QR Code to visitor

**Expected Results**:
- ✅ Visitor Pass created successfully
- ✅ QR Code auto-generated
- ✅ Validity period auto-calculated
- ✅ Pass Status: "Issued"

**System Behavior**:
```
Auto-generate: VP-YYYYMMDD-####
  ├─ Pass Number Format
  ├─ QR Code JSON Data
  └─ Validity: valid_from + validity_days = valid_until
```

---

### Step 2: Visitor Arrival - Scan QR Code for Entry

**Operator**: Gate Security Staff

**Actions**:
1. Visitor arrives at gate
2. Use scanner or mobile device to scan visitor's QR Code
3. System automatically calls API: `verify_visitor_pass`
4. System validates:
   - ✅ Pass is valid
   - ✅ Within validity period
   - ✅ Status is "Issued" or "Active"
5. System automatically records:
   - Entry Time: 2025-11-25 17:28:06
   - Entry Gate: Main Gate
   - Status Update: "Active"
   - Log entry in Child Table (entry_exit_logs)

**Expected Results**:
- ✅ System displays: **"Entry granted. Welcome John Smith!"**
- ✅ Entry record created
- ✅ Pass status changed to "Active"
- ✅ Child Table entry_exit_logs updated:
  ```json
  {
    "entry_datetime": "2025-11-25 17:28:06",
    "exit_datetime": null,
    "device_id": "Main Gate",
    "entry_method": "QR Code"
  }
  ```

**Security Check Points**:
- [ ] Valid pass number
- [ ] Pass not expired
- [ ] Pass not cancelled
- [ ] Visitor photo matches (if applicable)

---

### Step 3: Create Inspection Visit Record

**Operator**: QA Inspector

**Actions**:
1. Navigate to Visitor Pass detail page
2. Click **"Create"** > **"Create Inspection Visit"** button
3. System auto-populates:
   - Linked Pass: VP-20251125-0002
   - Visitor Name: John Smith (auto-fetch)
   - Visitor From: ABC Supplier Company (auto-fetch)
   - Visitor Mobile: +1-555-0123 (auto-fetch)
4. Fill in inspection details:
   - Inspection Site: SITE-0002
   - Supplier: Quanta Computer
   - Inspection Template: Safety Inspection
   - Inspector: Administrator
5. Save record

**Expected Results**:
- ✅ Inspection Visit record created (VI-0034)
- ✅ Auto-linked to Visitor Pass
- ✅ Visitor data auto-populated
- ✅ Ready for inspection checklist

**Data Flow**:
```
Visitor Pass → Inspection Visit
     ↓              ↓
  QR Code      Auto-fetch visitor data
  Entry Log    Inspection checklist
```

---

### Step 4: Visitor Departure - Scan QR Code for Exit

**Operator**: Gate Security Staff

**Actions**:
1. Visitor prepares to leave
2. Scan visitor's QR Code again
3. System logic:
   - Check Child Table for incomplete entry
   - Find entry without exit_datetime
   - Determine action: "exit"
4. System automatically records:
   - Update Child Table: set exit_datetime
   - Calculate duration: 0.0 hours
   - Exit Gate: Main Gate
   - Status Update: "Used"

**Expected Results**:
- ✅ System displays: **"Exit recorded. Thank you John Smith! Duration: 0.0 hours"**
- ✅ Exit record created
- ✅ Duration auto-calculated
- ✅ Pass status changed to "Used"
- ✅ Child Table entry_exit_logs updated:
  ```json
  {
    "entry_datetime": "2025-11-25 17:28:06",
    "exit_datetime": "2025-11-25 18:30:00",
    "device_id": "Main Gate",
    "entry_method": "QR Code",
    "duration_hours": 1.03
  }
  ```

**Completion Checklist**:
- [ ] Exit time recorded
- [ ] Duration calculated
- [ ] Pass status updated
- [ ] Visitor departed safely

---

## Scenario 2: Long-term Contractor Access (30-Day Pass)

### Use Case
- Engineering contractors
- Long-term maintenance personnel
- Visitors requiring multiple entries/exits

---

### Step 1: Create Long-term Visitor Pass

**Operator**: Reception/Security Staff

**Actions**:
1. Access VMS System
2. Click **"New Visitor Pass"**
3. Fill in visitor information:

| Field | Example Value |
|-------|---------------|
| Visitor Name | Tom Chen |
| Visitor From | XYZ Engineering Co. |
| Mobile Number | +1-555-0456 |
| To Meet | Engineering Manager - Peter Zhang |
| Department | Engineering |
| Meeting Location | Construction Site B |
| Visitor Type | Contractor |
| Purpose | Equipment installation and maintenance |
| **Validity** | **30 days** ← System Default |

4. Save to generate long-term pass

**Expected Results**:
- ✅ Pass Number: VP-20251125-0003
- ✅ Validity: 30 days (2025-11-25 to 2025-12-25)
- ✅ QR Code generated
- ✅ Multiple entry/exit enabled

**Long-term Pass Features**:
- Valid for multiple days
- Supports multiple entry/exit cycles
- All history preserved in Child Table
- No data overwrite issue

---

### Step 2: Day 1 Entry/Exit

**Operator**: Gate Security Staff

**Morning Arrival**:
1. Scan QR Code
2. System records entry (Side Gate)
3. Status: "Active"

**Evening Departure**:
1. Scan QR Code again
2. System records exit (Side Gate)
3. Calculate today's duration
4. Status: "Active" (still valid for next 6 days)

**Expected Results**:
- ✅ Entry Record: 2025-11-25 08:00:00
- ✅ Exit Record: 2025-11-25 17:00:00
- ✅ Duration: 9.0 hours
- ✅ Child Table records: 1
- ✅ Pass remains "Active"

**Child Table Structure**:
```
entry_exit_logs (Table)
├─ Record 1
│  ├─ entry_datetime: 2025-11-25 08:00:00
│  ├─ exit_datetime: 2025-11-25 17:00:00
│  ├─ device_id: Side Gate
│  ├─ entry_method: QR Code
│  └─ duration_hours: 9.0
```

---

### Step 3: Days 2-30 Repeated Entry/Exit

**Daily Process**:
Each day when visitor enters/exits:
1. System auto-determines: entry or exit
2. Creates new record in Child Table
3. **Does NOT overwrite** previous records
4. Each record has complete entry/exit timestamps

**Advantages**:
- ✅ Complete historical records preserved
- ✅ Track daily working hours
- ✅ No data overwrite issues
- ✅ Audit trail maintained

**Example: 7-Day History**
```
Day 1: Entry 08:00 → Exit 17:00 (9h)
Day 2: Entry 08:15 → Exit 16:45 (8.5h)
Day 3: Entry 08:30 → Exit 17:15 (8.75h)
Day 4: Entry 08:00 → Exit 12:00 (4h - Half day)
Day 5: Entry 08:10 → Exit 17:20 (9.17h)
Day 6: Entry 08:00 → Exit 17:00 (9h)
Day 7: Entry 08:05 → Exit 16:55 (8.83h)
---
Total: 57.25 hours over 7 days
```

**Child Table Final State**:
- ✅ 7 complete records
- ✅ All timestamps preserved
- ✅ Duration calculated for each day
- ✅ Easy to generate timesheet report

---

## Scenario 3: Query Current Visitors On-Site

### Use Case
- Security personnel monitoring
- Emergency evacuation
- Visitor management statistics

---

### Method 1: API Query

**Endpoint**:
```bash
GET https://vendorqc.duckdns.org/api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors
```

**Response Example**:
```json
[
  {
    "visitor_name": "John Smith",
    "pass_number": "VP-20251125-0002",
    "visitor_from": "ABC Supplier Company",
    "entry_time": "2025-11-25 17:28:06",
    "pass_status": "Active"
  },
  {
    "visitor_name": "Tom Chen",
    "pass_number": "VP-20251125-0003",
    "visitor_from": "XYZ Engineering Co.",
    "entry_time": "2025-11-25 08:00:00",
    "pass_status": "Active"
  }
]
```

---

### Method 2: System Report

**Actions**:
1. Navigate to Visitor Pass List
2. Apply filter: Status = "Active"
3. View all current on-site visitors

**Expected Results**:
- ✅ Display current on-site visitor count: 3
- ✅ Each visitor information:
  - Visitor Name
  - Pass Number
  - Visitor Company
  - Entry Time
  - Current Status

**Use Cases**:
- **Emergency Evacuation**: Know exactly who's on-site
- **Security Monitoring**: Real-time visitor tracking
- **Capacity Management**: Monitor visitor count
- **Reporting**: Daily/weekly visitor statistics

---

## System Architecture

### Data Relationship
```
Work Order (Job Order)
    ↓ [Link: work_order]
Visitor Pass (Visitor Pass)
    ├─ entry_exit_logs (Child Table) → All entry/exit records
    ├─ qr_code_data (JSON)
    ├─ Custom Fields:
    │  ├─ work_order (Link)
    │  └─ vendor (Link, fetch_from work_order)
    └─ [Quick Action: Create Inspection Visit]
         ↓ [Link: visitor_pass]
    Inspection Visit (Inspection Visit)
         ├─ Custom Fields:
         │  ├─ visitor_pass (Link)
         │  ├─ visitor_name (fetch_from)
         │  ├─ visitor_from (fetch_from)
         │  └─ visitor_mobile (fetch_from)
         └─ Inspection checklist
```

---

### Child Table Structure: entry_exit_logs

| Field | Type | Description |
|-------|------|-------------|
| entry_datetime | Datetime | Entry timestamp |
| exit_datetime | Datetime | Exit timestamp (null if not yet departed) |
| device_id | Data | Gate/door ID (e.g., "Main Gate") |
| entry_method | Select | Entry method (QR Code/Fingerprint/Face Recognition/Manual) |
| duration_hours | Float | Stay duration in hours (auto-calculated) |
| notes | Small Text | Additional notes |

**Why Child Table?**
- Supports multiple entry/exit cycles
- No data overwrite issue
- Complete historical records
- Easy to generate reports

---

### State Machine: Pass Status

```
Issued → Active → Used
  ↓       ↓        ↓
  (Created) (Entered) (Exited)

Special States:
├─ Cancelled: Pass invalidated
└─ Expired: Past validity period
```

**Status Transitions**:
1. **Issued**: Pass created, not yet used
2. **Active**: Visitor entered, currently on-site
3. **Used**: Visitor exited (for single-day pass)
4. **Cancelled**: Pass manually cancelled
5. **Expired**: Past valid_until date

---

## API Documentation

### API 1: Verify Visitor Pass (Entry/Exit Recording)

**Endpoint**:
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.verify_visitor_pass
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| qr_data | String (JSON) | Yes | QR Code JSON data |
| gate_id | String | No | Gate/door ID (default: "Main Gate") |

**Request Example**:
```json
{
  "qr_data": "{\"type\":\"VISITOR_PASS\",\"pass_number\":\"VP-20251125-0002\",\"name\":\"VP-20251125-0002\",\"visitor_name\":\"John Smith\"}",
  "gate_id": "Main Gate"
}
```

**Response Success (Entry)**:
```json
{
  "valid": true,
  "message": "Entry granted. Welcome John Smith!",
  "visitor_name": "John Smith",
  "action": "entry",
  "pass_number": "VP-20251125-0002",
  "visitor_photo": "/files/photo.jpg",
  "to_meet": "QA Manager - David Lee",
  "department": "Quality Management",
  "details": {
    "entry_time": "2025-11-25 17:28:06.633176",
    "exit_time": null
  }
}
```

**Response Success (Exit)**:
```json
{
  "valid": true,
  "message": "Exit recorded. Thank you John Smith! Duration: 1.5 hours",
  "visitor_name": "John Smith",
  "action": "exit",
  "pass_number": "VP-20251125-0002",
  "details": {
    "entry_time": "2025-11-25 17:28:06.633176",
    "exit_time": "2025-11-25 19:00:00.000000"
  }
}
```

**Response Error**:
```json
{
  "valid": false,
  "message": "Pass expired on: 2025-11-24 18:00"
}
```

**Error Cases**:
- Pass not found
- Pass expired
- Pass cancelled
- Invalid QR code format

---

### API 2: Generate QR Code Image

**Endpoint**:
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_qr_image
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| qr_data | String (JSON) | Yes | QR Code JSON data |

**Response**:
```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
```
Returns base64 encoded PNG image

---

### API 3: Get Active Visitors

**Endpoint**:
```
GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors
```

**Parameters**: None

**Response**:
```json
[
  {
    "name": "VP-20251125-0002",
    "visitor_name": "John Smith",
    "pass_number": "VP-20251125-0002",
    "visitor_from": "ABC Supplier Company",
    "entry_time": "2025-11-25 17:28:06",
    "pass_status": "Active",
    "to_meet": "QA Manager - David Lee",
    "department": "Quality Management"
  }
]
```

---

### API 4: Biometric Device Webhook

**Endpoint**:
```
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.attendance_webhook
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| device_id | String | Yes | Device ID |
| event_type | String | Yes | "entry" or "exit" |
| identifier | String | Yes | QR code/fingerprint/face ID |
| identifier_type | String | No | "qr"/"fingerprint"/"face" (default: "qr") |
| timestamp | String | No | ISO timestamp (default: now) |

**Request Example**:
```json
{
  "device_id": "Biometric-Gate-001",
  "event_type": "entry",
  "identifier": "FP-12345",
  "identifier_type": "fingerprint",
  "timestamp": "2025-11-25T08:00:00"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Entry recorded successfully",
  "visitor_name": "John Smith",
  "pass_number": "VP-20251125-0002"
}
```

**Supported Identifier Types**:
- **qr**: QR Code data (JSON string)
- **pass_number**: Pass number (e.g., "VP-20251125-0002")
- **fingerprint**: Fingerprint template ID
- **face**: Face recognition ID

---

## Quick Action Buttons (Client Scripts)

### Visitor Pass Form

**Button**: "Create Inspection Visit"
- **Location**: Create dropdown menu
- **Action**: Auto-create Inspection Visit record
- **Auto-populated fields**:
  - visitor_pass: Current Visitor Pass
  - visitor_name: From Visitor Pass
  - visitor_from: From Visitor Pass
  - visitor_mobile: From Visitor Pass
  - supplier_name: From linked vendor

**Usage**:
1. Open Visitor Pass record
2. Click "Create" > "Create Inspection Visit"
3. System pre-fills visitor data
4. Complete inspection details and save

---

### Work Order Form

**Button 1**: "Create Visitor Pass"
- **Location**: Create dropdown menu
- **Action**: Quick create Visitor Pass
- **Auto-populated fields**:
  - work_order: Current Work Order
  - vendor: From Work Order

**Button 2**: "View Visitor Passes"
- **Location**: View dropdown menu
- **Action**: Filter Visitor Pass list by current Work Order
- **Result**: Show all passes linked to this Work Order

**Usage**:
1. Open Work Order record
2. Click "Create" > "Create Visitor Pass" to add visitor
3. Click "View" > "View Visitor Passes" to see all visitors

---

## Validation & Testing Results

### ✅ Scenario 1: Vendor Visit for Inspection
- [x] Create Visitor Pass ✓
- [x] QR Code auto-generated ✓
- [x] Entry record (QR Code scan) ✓
- [x] Create Inspection Visit record ✓
- [x] Auto-link to Visitor Pass ✓
- [x] Exit record (QR Code scan) ✓

### ✅ Scenario 2: Long-term Contractor
- [x] Create 7-day long-term pass ✓
- [x] Multiple entry/exit records (Child Table) ✓
- [x] Historical records preserved ✓
- [x] No data overwrite ✓

### ✅ Scenario 3: Query Active Visitors
- [x] API functioning correctly ✓
- [x] Return current on-site visitors ✓

---

## System Advantages

### 1. No Data Overwrite Issue
- Uses Child Table to record all entry/exit events
- Long-term passes support multiple entry/exit cycles
- Complete historical records preserved

### 2. Automation
- QR Code auto-generated
- Entry/exit time auto-recorded
- Duration auto-calculated
- Status auto-updated

### 3. Complete Data Linking
- Work Order → Visitor Pass → Inspection Visit
- Visitor data auto-populated (fetch_from)
- Reduces duplicate data entry

### 4. Multiple Identification Methods
- QR Code scanning
- Fingerprint recognition
- Face recognition
- Manual entry

---

## Troubleshooting Guide

### Issue 1: QR Code Not Scanning

**Symptoms**:
- Scanner cannot read QR code
- "Invalid QR code" error

**Solutions**:
1. Check QR code image quality
2. Verify qr_code_data field is not empty
3. Test with different scanner/camera
4. Re-generate QR code if corrupted

**Prevention**:
- Regular QR code validation
- Use high-quality QR code generation
- Test with multiple devices

---

### Issue 2: Pass Expired Error

**Symptoms**:
- "Pass expired on: YYYY-MM-DD" message
- Cannot enter with valid pass

**Solutions**:
1. Check valid_until date
2. Extend validity period if needed
3. Create new pass if expired

**Prevention**:
- Set appropriate validity days
- Monitor pass expiration
- Send expiration notifications

---

### Issue 3: Entry/Exit Record Missing

**Symptoms**:
- Visitor entered but no record
- Cannot exit (no incomplete entry found)

**Solutions**:
1. Check Child Table entry_exit_logs
2. Verify API call succeeded
3. Check network connectivity
4. Manual entry if needed

**Prevention**:
- Regular API monitoring
- Database backup
- Error logging enabled

---

## Security & Compliance

### Data Privacy
- Visitor photos encrypted
- Personal data protected per GDPR
- Access logs maintained

### Access Control
- Role-based permissions
- Security staff: Entry/exit recording
- QA staff: Inspection visit creation
- Admin: Full access

### Audit Trail
- All entry/exit events logged
- Timestamp and gate ID recorded
- Complete history in Child Table
- Cannot be modified after recording

---

## Next Phase Planning (Phase 1B)

### 1. Print Format Optimization
- [ ] Visitor Pass Card design
- [ ] ID badge template
- [ ] QR code positioning

### 2. Reporting Features
- [ ] Visitor statistics report
- [ ] Duration analysis report
- [ ] Supplier visit frequency report

### 3. Notification System
- [ ] Visitor arrival notification
- [ ] Visitor departure notification
- [ ] Email/SMS integration

### 4. Advanced Search
- [ ] Search by company
- [ ] Search by date range
- [ ] Search by visitor type

---

## Support & Contact

**System Administrator**: Administrator
**System URL**: https://vendorqc.duckdns.org
**Documentation**: VMS_USER_OPERATION_FLOW.md

**Emergency Contacts**:
- Security: [Contact Info]
- IT Support: [Contact Info]
- System Admin: [Contact Info]

---

**Document Control**:
- Version: 1.0
- Date: November 25, 2025
- Status: Production Ready
- Phase: 1A Complete

**Approval**:
- [ ] Security Manager
- [ ] QA Manager
- [ ] IT Manager
- [ ] Operations Manager

---

**End of SOP Document**
