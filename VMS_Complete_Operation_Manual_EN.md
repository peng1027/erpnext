# VMS - Visitor Management System
## Complete Operation Manual

**Version:** 1.0
**Last Updated:** November 2025
**System URL:** https://vendorqc.duckdns.org

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Login & Home Page](#2-login--home-page)
3. [Visitor Pass Management](#3-visitor-pass-management)
4. [QR Code Scanning](#4-qr-code-scanning)
5. [Gate Pass Management](#5-gate-pass-management)
6. [Work Order Management](#6-work-order-management)
7. [Inspection Management](#7-inspection-management)
8. [Security Dashboard](#8-security-dashboard)
9. [Master Data Setup](#9-master-data-setup)
10. [Reports & Analytics](#10-reports--analytics)
11. [API Integration Guide](#11-api-integration-guide)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. System Overview

### 1.1 About VMS

The Visitor Management System (VMS) is a comprehensive solution for managing visitors, contractors, and vendors at your facility. It provides:

- **Visitor Pass Management** - Issue and track visitor passes with QR codes
- **Gate Pass Control** - Manage material entry/exit
- **Work Order Tracking** - Schedule and monitor work orders
- **Inspection Management** - Conduct and record inspections
- **Security Dashboard** - Real-time monitoring of all activities

### 1.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VMS SYSTEM                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Visitor   │  │    Gate     │  │    Work     │         │
│  │    Pass     │  │    Pass     │  │    Order    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          ▼                                   │
│              ┌─────────────────────┐                        │
│              │   QR Code Scanner   │                        │
│              │   (Mobile/Desktop)  │                        │
│              └─────────────────────┘                        │
│                          │                                   │
│                          ▼                                   │
│              ┌─────────────────────┐                        │
│              │  Security Dashboard │                        │
│              │   (Real-time View)  │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 User Roles

| Role | Permissions |
|------|-------------|
| Administrator | Full access to all modules |
| Security Officer | Visitor pass, gate pass, scanning |
| Quality Manager | Inspections, NCR, CAPA |
| Receptionist | Create visitor passes only |
| Gate Operator | Gate pass management only |

---

## 2. Login & Home Page

### 2.1 Login Screen

**URL:** `https://vendorqc.duckdns.org/login`

```
┌─────────────────────────────────────────┐
│                                         │
│            VENDOR QC                    │
│                                         │
│    ┌─────────────────────────────┐     │
│    │ Email                       │     │
│    └─────────────────────────────┘     │
│                                         │
│    ┌─────────────────────────────┐     │
│    │ Password                    │     │
│    └─────────────────────────────┘     │
│                                         │
│         [      Login      ]             │
│                                         │
│         Forgot Password?                │
│                                         │
└─────────────────────────────────────────┘
```

**Steps:**
1. Enter your registered email address
2. Enter your password
3. Click **Login** button
4. You will be redirected to the home page

### 2.2 Home Page / Workspace

**URL:** `https://vendorqc.duckdns.org/app/vendor-inspection`

```
┌─────────────────────────────────────────────────────────────────┐
│  ☰  Vendor Inspection                    🔍 Search    👤 User  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  QUICK ACTIONS                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐│
│  │ New Visitor  │ │ New Gate     │ │ New Work     │ │ New     ││
│  │ Pass  ↗      │ │ Pass  ↗      │ │ Order  ↗     │ │Inspect ↗││
│  └──────────────┘ └──────────────┘ └──────────────┘ └─────────┘│
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  VISITOR & GATE PASS          WORK & INSPECTION                 │
│  • Visitor Pass               • Work Order                      │
│  • Gate Pass                  • Inspection Visit                │
│  • Vendor Visit               • NCR                             │
│  • Vendor Staff               • CAPA                            │
│                                                                  │
│  MASTER DATA                                                     │
│  • Supplier                                                      │
│  • Project Site                                                  │
│  • Inspection Checklist                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Navigation:**
- Click **Quick Actions** buttons to create new records quickly
- Click items under each section to view the list
- Use the **Search** bar (⌘+G) to find any document

---

## 3. Visitor Pass Management

### 3.1 Create New Visitor Pass

**Path:** Quick Actions → New Visitor Pass
**URL:** `https://vendorqc.duckdns.org/app/visitor-pass/new`

```
┌─────────────────────────────────────────────────────────────────┐
│  New Visitor Pass                              [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  VISITOR INFORMATION                                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Visitor Name *         [John Smith                        ] ││
│  │ Company/From *         [ABC Corporation Ltd               ] ││
│  │ Mobile Number          [+91-9876543210                    ] ││
│  │ Email                  [john.smith@abc.com                ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ID VERIFICATION                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ID Type               [Aadhar Card           ▼]            ││
│  │ ID Number             [1234-5678-9012                     ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  VISIT DETAILS                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ To Meet *              [Mr. Rajesh Kumar                  ] ││
│  │ Department             [Quality Assurance      ▼]          ││
│  │ Meeting Location       [Conference Room A                 ] ││
│  │ Visitor Type           [Vendor                 ▼]          ││
│  │ Purpose                [Quality Audit Meeting             ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  VALIDITY                                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Valid From *           [2025-11-27 09:00      📅]          ││
│  │ Validity Days          [1                                 ] ││
│  │ Valid Until            [2025-11-28 09:00      ] (Auto)     ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  PHOTO                                                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  [📷 Attach Photo]                                         ││
│  │                                                             ││
│  │  Drag and drop or click to upload visitor photo            ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Field Descriptions:**

| Field | Required | Description |
|-------|----------|-------------|
| Visitor Name | Yes | Full name of the visitor |
| Company/From | Yes | Visitor's company or organization |
| Mobile Number | No | Contact number with country code |
| Email | No | Email address for notifications |
| ID Type | No | Type of ID (Aadhar, PAN, Passport, etc.) |
| ID Number | No | Government ID number |
| To Meet | Yes | Name of the host employee |
| Department | No | Department being visited |
| Meeting Location | No | Specific location within facility |
| Visitor Type | No | Vendor, Contractor, Client, Guest, etc. |
| Purpose | No | Reason for the visit |
| Valid From | Yes | Start date and time of validity |
| Validity Days | No | Number of days pass is valid (default: 1) |
| Photo | No | Visitor's photograph |

**Steps to Create:**
1. Click **New Visitor Pass** from Quick Actions
2. Fill in visitor information (name, company, mobile)
3. Enter ID details if required
4. Specify who the visitor is meeting
5. Set validity period
6. Upload visitor photo (optional but recommended)
7. Click **Save**
8. Pass number and QR code are auto-generated

### 3.2 View Visitor Pass List

**Path:** Visitor & Gate Pass → Visitor Pass
**URL:** `https://vendorqc.duckdns.org/app/visitor-pass`

```
┌─────────────────────────────────────────────────────────────────┐
│  Visitor Pass                    [+ Add Visitor Pass] [Refresh] │
├─────────────────────────────────────────────────────────────────┤
│  🔍 Filter by Status: [All ▼]    Date: [Today ▼]    [Search...] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  □ Pass Number      Visitor Name       Status    Valid Until    │
│  ─────────────────────────────────────────────────────────────  │
│  □ VP-20251127-0001 John Smith         🟢 Active  28-Nov-2025   │
│  □ VP-20251127-0002 Sarah Johnson      🟡 Issued  28-Nov-2025   │
│  □ VP-20251126-0001 Mike Chen          🔴 Expired 27-Nov-2025   │
│  □ VP-20251126-0002 Priya Sharma       ⚫ Used    27-Nov-2025   │
│  □ VP-20251125-0001 David Lee          🔴 Expired 26-Nov-2025   │
│                                                                  │
│  Showing 1-5 of 14                              [< 1 2 3 >]     │
└─────────────────────────────────────────────────────────────────┘
```

**Status Indicators:**
- 🟡 **Issued** - Pass created but visitor hasn't entered yet
- 🟢 **Active** - Visitor is currently inside the facility
- ⚫ **Used** - Visitor has completed the visit
- 🔴 **Expired** - Pass validity period has ended
- ⛔ **Cancelled** - Pass manually cancelled

### 3.3 Print Visitor Pass Card

**Path:** Open Visitor Pass → Menu → Print

```
┌─────────────────────────────────────────────────────────────────┐
│  VP-20251127-0001                              [🖨️ Print] [PDF] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    Print Format: [Visitor Pass Card ▼]                          │
│    Language: [en ▼]                                              │
│                                                                  │
│    ┌─────────────────────────────────────┐                      │
│    │ ┌─────────────────────────────────┐ │                      │
│    │ │      VENDOR QC                  │ │                      │
│    │ │    VISITOR PASS                 │ │                      │
│    │ ├─────────────────────────────────┤ │                      │
│    │ │ NAME                    ┌─────┐ │ │                      │
│    │ │ John Smith              │Photo│ │ │                      │
│    │ │ FROM                    └─────┘ │ │                      │
│    │ │ ABC Corporation         ┌─────┐ │ │                      │
│    │ │ TO MEET                 │ QR  │ │ │                      │
│    │ │ Mr. Rajesh Kumar        │Code │ │ │                      │
│    │ │ DEPARTMENT              └─────┘ │ │                      │
│    │ │ Quality Assurance     VP-xxx    │ │                      │
│    │ │ MOBILE                          │ │                      │
│    │ │ +91-9876543210                  │ │                      │
│    │ ├─────────────────────────────────┤ │                      │
│    │ │      Entry Time: 09:30          │ │                      │
│    │ ├─────────────────────────────────┤ │                      │
│    │ │ Safety Instructions...          │ │                      │
│    │ ├─────────────────────────────────┤ │                      │
│    │ │ Valid: 27-11-2025 to 28-11-2025 │ │                      │
│    │ ├─────────────────────────────────┤ │                      │
│    │ │ John Smith  Rajesh Kumar        │ │                      │
│    │ │ ─────────── ─────────── ─────── │ │                      │
│    │ │  Visitor      Host     Security │ │                      │
│    │ └─────────────────────────────────┘ │                      │
│    └─────────────────────────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Print Steps:**
1. Open the Visitor Pass document
2. Click **Print** icon or press `Ctrl+P`
3. Select **Visitor Pass Card** as Print Format
4. Click **Print** for direct printing
5. Click **PDF** to download as PDF file

---

## 4. QR Code Scanning

### 4.1 Entry Scan Process

When a visitor arrives at the gate:

```
┌─────────────────────────────────────────┐
│          QR CODE SCANNER                │
├─────────────────────────────────────────┤
│                                         │
│         ┌─────────────────┐             │
│         │                 │             │
│         │   📷 SCAN QR    │             │
│         │                 │             │
│         │   Point camera  │             │
│         │   at QR code    │             │
│         │                 │             │
│         └─────────────────┘             │
│                                         │
│  Or enter Pass Number manually:         │
│  ┌─────────────────────────────────┐   │
│  │ VP-20251127-0001                │   │
│  └─────────────────────────────────┘   │
│                                         │
│         [    VERIFY    ]                │
│                                         │
└─────────────────────────────────────────┘
```

**Successful Entry Response:**

```
┌─────────────────────────────────────────┐
│              ✅ ENTRY GRANTED           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐                            │
│  │  Photo  │  John Smith                │
│  │         │  ABC Corporation           │
│  └─────────┘                            │
│                                         │
│  To Meet: Mr. Rajesh Kumar              │
│  Department: Quality Assurance          │
│                                         │
│  Entry Time: 09:30                      │
│  Gate: Main Entrance                    │
│                                         │
│  Pass Valid Until: 28-Nov-2025 09:00    │
│                                         │
│         [     OK     ]                  │
│                                         │
└─────────────────────────────────────────┘
```

**Error Responses:**

| Scenario | Message |
|----------|---------|
| Expired Pass | "Pass expired on: 2025-11-27 00:00" |
| Cancelled Pass | "Pass has been cancelled" |
| Not Yet Valid | "Pass not yet valid. Valid from: 2025-11-28 09:00" |
| Duplicate Scan | "Please wait 299 seconds before scanning again" |
| Invalid QR | "Invalid QR code data format" |

### 4.2 Exit Scan Process

```
┌─────────────────────────────────────────┐
│              ✅ EXIT RECORDED           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐                            │
│  │  Photo  │  John Smith                │
│  │         │  ABC Corporation           │
│  └─────────┘                            │
│                                         │
│  Exit Time: 17:45                       │
│  Gate: Exit Gate B                      │
│                                         │
│  Duration: 8.25 hours                   │
│                                         │
│  Thank you for visiting!                │
│                                         │
│         [     OK     ]                  │
│                                         │
└─────────────────────────────────────────┘
```

### 4.3 Duplicate Scan Protection

The system has a 5-minute cooldown period to prevent accidental duplicate scans:

```
┌─────────────────────────────────────────┐
│              ⚠️ PLEASE WAIT             │
├─────────────────────────────────────────┤
│                                         │
│  This pass was recently scanned.        │
│                                         │
│  Please wait 299 seconds before         │
│  scanning again.                        │
│                                         │
│  Time remaining: 4:59                   │
│                                         │
│         [     OK     ]                  │
│                                         │
└─────────────────────────────────────────┘
```

---

## 5. Gate Pass Management

### 5.1 Create New Gate Pass

**Path:** Quick Actions → New Gate Pass
**URL:** `https://vendorqc.duckdns.org/app/gate-pass/new`

```
┌─────────────────────────────────────────────────────────────────┐
│  New Gate Pass                                 [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MATERIAL DETAILS                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Material Description * [Laptop and Testing Equipment      ] ││
│  │ Quantity *             [2                                 ] ││
│  │ Unit                   [Nos                    ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  PASS DETAILS                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Purpose *              [Outward                 ▼]          ││
│  │ Carrier Name           [DHL Express                       ] ││
│  │ Vehicle Number         [MH-12-AB-1234                     ] ││
│  │ Expected Return Date   [2025-12-04             📅]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  AUTHORIZATION                                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Authorized By          [Select Employee        ▼]          ││
│  │ Remarks                [For client demo                   ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Purpose Types:**
- **Outward** - Material going out of facility
- **Inward** - Material coming into facility
- **Returnable** - Material going out but expected to return
- **Non-Returnable** - Material going out permanently

---

## 6. Work Order Management

### 6.1 Create New Work Order

**Path:** Quick Actions → New Work Order
**URL:** `https://vendorqc.duckdns.org/app/work-order/new`

```
┌─────────────────────────────────────────────────────────────────┐
│  New Work Order                                [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WORK ORDER DETAILS                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Title *                [Electrical System Inspection      ] ││
│  │ Description            [Complete inspection of building A ] ││
│  │                        [electrical systems                ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  SCHEDULE                                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Planned Start *        [2025-11-28 09:00      📅]          ││
│  │ Planned End *          [2025-11-28 17:00      📅]          ││
│  │ Priority               [High                   ▼]          ││
│  │ Status                 [Open                   ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ASSIGNMENT                                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Vendor *               [Select Vendor          ▼]          ││
│  │ Supervisor *           [Select Supervisor      ▼]          ││
│  │ Zone                   [Building A             ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Work Order Status Flow:**
```
Open → In Progress → Completed → Closed
         ↓
      On Hold → In Progress
```

---

## 7. Inspection Management

### 7.1 Create Inspection Visit

**Path:** Quick Actions → New Inspection
**URL:** `https://vendorqc.duckdns.org/app/inspection-visit/new`

```
┌─────────────────────────────────────────────────────────────────┐
│  New Inspection Visit                          [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INSPECTION DETAILS                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Work Order             [Select Work Order      ▼]          ││
│  │ Inspector              [Select Inspector       ▼]          ││
│  │ Inspection Date *      [2025-11-28             📅]          ││
│  │ Inspection Type        [Routine                ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  CHECKLIST                                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ □ Safety equipment check                          [Pass ▼] ││
│  │ □ Documentation review                            [Pass ▼] ││
│  │ □ Quality standards compliance                    [Fail ▼] ││
│  │ □ Environmental compliance                        [Pass ▼] ││
│  │                                        [+ Add Item]        ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  FINDINGS                                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Finding 1: [Missing safety labels on equipment           ] ││
│  │ Severity: [Major ▼]                     [+ Add Finding]   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  PHOTO EVIDENCE                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  [📷 Attach Photos]                                        ││
│  │  ┌─────┐ ┌─────┐ ┌─────┐                                  ││
│  │  │ IMG │ │ IMG │ │ IMG │                                  ││
│  │  │  1  │ │  2  │ │  3  │                                  ││
│  │  └─────┘ └─────┘ └─────┘                                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 NCR (Non-Conformance Report)

When an inspection finds issues, create an NCR:

```
┌─────────────────────────────────────────────────────────────────┐
│  New NCR                                       [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  NCR DETAILS                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Source Inspection      [INS-2025-00041         ▼]          ││
│  │ NCR Type               [Major                  ▼]          ││
│  │ Category               [Safety                 ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  DESCRIPTION                                                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Non-Conformance:                                            ││
│  │ [Missing safety labels on electrical equipment. This       ]││
│  │ [violates safety standard ISO 45001 section 6.2.           ]││
│  │                                                             ││
│  │ Immediate Containment Action:                               ││
│  │ [Stop work on affected equipment until labels installed.   ]││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  CORRECTIVE ACTION                                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Assigned To            [Select Person          ▼]          ││
│  │ Due Date               [2025-12-01             📅]          ││
│  │ Action Required:                                            ││
│  │ [Install safety labels on all equipment. Conduct training  ]││
│  │ [for workers on safety labeling requirements.              ]││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Security Dashboard

### 8.1 Real-Time Monitoring

**API Endpoint:** `GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_security_dashboard`

```
┌─────────────────────────────────────────────────────────────────┐
│  SECURITY DASHBOARD                              🔄 Refresh     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TODAY'S SUMMARY                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │     3      │ │    12      │ │     9      │ │    14      │   │
│  │  Active    │ │  Entries   │ │   Exits    │ │   Total    │   │
│  │  Visitors  │ │   Today    │ │   Today    │ │   Passes   │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  CURRENT VISITORS                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Name            Company           Entry    To Meet          ││
│  │ ───────────────────────────────────────────────────────────││
│  │ John Smith      ABC Corp          09:30    Rajesh Kumar     ││
│  │ Sarah Johnson   XYZ Ltd           10:15    Priya Sharma     ││
│  │ Mike Chen       Tech Solutions    11:00    Amit Patel       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  RECENT ACTIVITY                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Time   Pass Number      Name           Action    Gate       ││
│  │ ──────────────────────────────────────────────────────────  ││
│  │ 11:00  VP-20251127-0003 Mike Chen      Entry     Gate A     ││
│  │ 10:45  VP-20251127-0002 Sarah Johnson  Entry     Main       ││
│  │ 10:30  VP-20251126-0005 David Lee      Exit      Gate B     ││
│  │ 09:30  VP-20251127-0001 John Smith     Entry     Main       ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  GATE STATISTICS                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Gate          Total Scans    Entries    Exits               ││
│  │ ───────────────────────────────────────────────────────────││
│  │ Main Gate     15             10         5                   ││
│  │ Gate A        8              5          3                   ││
│  │ Gate B        6              2          4                   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Dashboard API Response

```json
{
  "success": true,
  "timestamp": "2025-11-27T17:46:53",
  "summary": {
    "active_visitors": 3,
    "today_entries": 12,
    "today_exits": 9,
    "total_passes": 14
  },
  "status_breakdown": {
    "Issued": 2,
    "Active": 3,
    "Used": 5,
    "Expired": 4
  },
  "recent_activity": [
    {
      "pass_number": "VP-20251127-0003",
      "visitor_name": "Mike Chen",
      "action_type": "entry",
      "entry_datetime": "2025-11-27 11:00:00",
      "device_id": "Gate A"
    }
  ],
  "gate_statistics": [
    {
      "gate": "Main Gate",
      "total_scans": 15,
      "entries": 10,
      "exits": 5
    }
  ]
}
```

---

## 9. Master Data Setup

### 9.1 Suppliers

**Path:** Master Data → Supplier

Create suppliers/vendors who will be working at your facility:

```
┌─────────────────────────────────────────────────────────────────┐
│  New Supplier                                  [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SUPPLIER INFORMATION                                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Supplier Name *        [ABC Services Pvt Ltd              ] ││
│  │ Supplier Type          [Contractor            ▼]          ││
│  │ Contact Person         [Mr. Rajesh Kumar                  ] ││
│  │ Phone                  [+91-9876543210                    ] ││
│  │ Email                  [contact@abcservices.com           ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ADDRESS                                                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Address Line 1         [123 Industrial Area               ] ││
│  │ City                   [Mumbai                            ] ││
│  │ State                  [Maharashtra                       ] ││
│  │ PIN Code               [400001                            ] ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Project Sites

**Path:** Master Data → Project Site

Define locations/zones within your facility:

```
┌─────────────────────────────────────────────────────────────────┐
│  New Project Site                              [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SITE DETAILS                                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Site Name *            [Building A - Production           ] ││
│  │ Site Code              [BLDG-A                            ] ││
│  │ Location               [Ground Floor, East Wing           ] ││
│  │ Site Manager           [Select Manager         ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Inspection Checklist Templates

**Path:** Master Data → Inspection Checklist

Create reusable checklists for inspections:

```
┌─────────────────────────────────────────────────────────────────┐
│  New Inspection Checklist Template             [Save] [Cancel]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TEMPLATE DETAILS                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Template Name *        [Safety Inspection Checklist       ] ││
│  │ Category               [Safety                 ▼]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  CHECKLIST ITEMS                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ # Item                                          Required    ││
│  │ ───────────────────────────────────────────────────────────││
│  │ 1 PPE worn correctly                            ☑          ││
│  │ 2 Safety signage visible                        ☑          ││
│  │ 3 Fire extinguishers accessible                 ☑          ││
│  │ 4 Emergency exits clear                         ☑          ││
│  │ 5 First aid kit available                       ☐          ││
│  │                                      [+ Add Item]          ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Reports & Analytics

### 10.1 Visitor History Report

**API Endpoint:** `GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_visitor_history`

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| pass_name | Filter by specific pass |
| visitor_name | Search by visitor name |
| from_date | Start date filter |
| to_date | End date filter |
| limit | Number of records (default: 50) |

**Example Response:**
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "pass_number": "VP-20251127-0001",
      "visitor_name": "John Smith",
      "visitor_from": "ABC Corporation",
      "entry_datetime": "2025-11-27 09:30:00",
      "exit_datetime": "2025-11-27 17:45:00",
      "duration_hours": 8.25,
      "device_id": "Main Gate"
    }
  ]
}
```

### 10.2 Active Visitors List

**API Endpoint:** `GET /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.get_active_visitors`

Returns list of all visitors currently inside the facility.

---

## 11. API Integration Guide

### 11.1 Authentication

All API calls require authentication. Include the API key in the header:

```http
Authorization: token api_key:api_secret
```

### 11.2 Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/method/verify_visitor_pass` | POST | Verify QR code and record entry/exit |
| `/api/method/attendance_webhook` | POST | Webhook for attendance devices |
| `/api/method/get_security_dashboard` | GET | Get real-time dashboard data |
| `/api/method/get_active_visitors` | GET | Get list of current visitors |
| `/api/method/cancel_visitor_pass` | POST | Cancel a visitor pass |
| `/api/method/get_visitor_history` | GET | Get visitor history with filters |

### 11.3 Verify Visitor Pass API

**Request:**
```json
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.verify_visitor_pass

{
  "qr_data": "{\"type\":\"VISITOR_PASS\",\"pass_number\":\"VP-20251127-0001\",...}",
  "gate_id": "Main Gate"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Entry granted. Welcome John Smith!",
  "action": "entry",
  "visitor_name": "John Smith",
  "pass_number": "VP-20251127-0001",
  "visitor_photo": "/files/john_smith.jpg",
  "to_meet": "Mr. Rajesh Kumar",
  "department": "Quality Assurance"
}
```

### 11.4 Attendance Webhook API

For integration with biometric/RFID devices:

**Request:**
```json
POST /api/method/vendor_inspection.vendor_inspection.doctype.visitor_pass.visitor_pass.attendance_webhook

{
  "device_id": "Gate-A-Scanner",
  "event_type": "entry",
  "identifier": "VP-20251127-0001",
  "identifier_type": "pass_number",
  "timestamp": "2025-11-27T09:30:00"
}
```

**Supported identifier_type:**
- `qr` - QR code data (JSON string)
- `pass_number` - Visitor pass number
- `fingerprint` - Fingerprint ID
- `face` - Face recognition ID

---

## 12. Troubleshooting

### 12.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| QR code not scanning | Poor image quality | Ensure good lighting, clean camera lens |
| Pass expired immediately | Incorrect valid_from date | Check date/time settings |
| Photo not showing in print | Private file | Re-upload photo or save the pass again |
| Duplicate scan error | Within 5-min cooldown | Wait for cooldown period |
| Links not showing in workspace | Cache issue | Clear browser cache (Ctrl+Shift+R) |

### 12.2 System Status Check

1. **Check if system is running:**
   - Open `https://vendorqc.duckdns.org`
   - Login page should appear

2. **Check API status:**
   - Try accessing dashboard API
   - Should return valid JSON response

3. **Clear cache:**
   - Browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Server: Run `bench clear-cache` (admin only)

### 12.3 Contact Support

For technical support:
- Email: support@vendorqc.com
- Phone: +91-XXXXXXXXXX
- Hours: 9:00 AM - 6:00 PM IST, Monday-Friday

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S / Cmd+S | Save document |
| Ctrl+P / Cmd+P | Print |
| Ctrl+G / Cmd+G | Global search |
| Ctrl+B / Cmd+B | Back to list |
| Ctrl+E / Cmd+E | Edit mode |
| Escape | Cancel / Close |

---

## Appendix B: Status Codes Reference

### Visitor Pass Status
| Status | Code | Description |
|--------|------|-------------|
| Issued | 1 | Pass created, visitor not yet arrived |
| Active | 2 | Visitor currently inside facility |
| Used | 3 | Visit completed (entry + exit) |
| Expired | 4 | Pass validity period ended |
| Cancelled | 5 | Pass manually cancelled |

### API Response Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Contact support |

---

**Document Version:** 1.0
**Created:** November 2025
**Last Updated:** November 27, 2025

© 2025 Vendor QC. All rights reserved.
