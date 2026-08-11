# Group update — Resolved items: check-in/out · attendance · approver (copy-paste ready)

_For the Pansen WhatsApp group. Plain English, from Stefan._

---

**Update — Check-in / Check-out (your top priority) ✅ FIXED**

Hi team, I've sorted out the check-in/check-out issue. Quick summary:

**What was wrong**
The scanner itself was working fine. The real problem was that the *automatic nightly check-out was not switched on*. So whenever a guard scanned someone **in** but forgot to scan them **out**, that person stayed "Checked In" forever. Over time this:
- made the **On-Site count too high** (people who had already left still counted as inside), and
- **blocked multi-day workers the next day** — the scanner said *"already checked in"* and wouldn't let them re-enter. This is what your team was seeing at the gate.

**What I did**
1. **Closed all the stuck records** — the On-Site count is now correct (it was showing 54 people who had actually already left).
2. **Switched on the nightly auto check-out** — from tonight it runs automatically every night, so this will not build up again.
3. **Tested the full cycle** (check-in → check-out) end-to-end — working correctly.

**What you'll notice now**
- The **On-Site number is accurate** (good for a fire drill / head-count).
- **Multi-day workers can re-enter** the next morning without being blocked.
- If a guard forgets to scan someone out, the system **auto-closes it at end of day** — no action needed from you.

**Also live — Work-hours attendance report ✅**
You asked for actual work time (time in / time out / hours per worker). It's now available: **Reports → Site Pass Attendance Report** — filter by date / contractor and **export to Excel**.
⚠️ **One honest note:** right now most exits are **not scanned**, so those hours show as **"Auto (est.)"** (estimated to end-of-day, which reads high). Hours are exact only where the report shows **"Scanned"**. So for accurate work-hours, the one thing needed from the gate is: **guards must scan workers OUT when they leave.** The report clearly marks which is which.

**Also live — "Who issued / approved each pass" ✅**
You asked to see who approved each gate pass. The **Site Pass Report** now has an **"Issued / Approved By"** column (exportable to Excel):
- a **person's name** → an admin created/approved that pass in the back office;
- **"Auto-issued (self-registration)"** → the visitor self-registered and the pass issued automatically after a verified Aadhaar (no manual step — this keeps the gate fast).
All existing passes were back-filled, so the history is complete.

I've updated the **Meeting Follow-up guide (v1.4)** — Sections 8 (check-in/out), 9 (attendance) and 10 (who issued/approved) now cover these, with screenshots. Sharing the file here.

Next: gate-crowd fast flow (no-OTP for a queue of workers) and contractor batch sign-up. Please keep dropping requirements in the group. 🙏

---

**Attach:** `PANSEN_VMS_Meeting_Followup_EN.pdf` (v1.4) — the picture guide with all resolved items (Aadhaar, Email OTP, exceptions, records, check-in/out fix, attendance report, and the approver record).
