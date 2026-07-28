# VMS Silent-Outage Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make VMS detect a registration outage within hours instead of never, by fixing the corrupted liveness signal and escalating errors nobody reads.

**Architecture:** The tenant liveness metric currently derives from `Site Pass.modified`, which nightly background jobs refresh — so the system monitors itself and always reports healthy. We add a `last_pass_created` field sourced from `MAX(creation)`, switch health classification to it, then add two hourly checks: a same-day stall detector and an Error Log burst escalator. All alerts go to email via the existing sender.

**Tech Stack:** Frappe Framework (Python 3.10), MariaDB, Redis (`frappe.cache()`), pymysql for cross-site reads, AWS SES for mail.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-28-vms-silent-outage-monitoring-design.md`
- Target repo: `peng1027/vms`. Work on branch `feat/outage-monitoring` off `master`.
- **Production is a live client system. NOTHING deploys without explicit user approval.** Local commits only.
- Frappe uses **tab indentation** in `vms/vms/*.py` (match surrounding file style exactly).
- `last_activity` keeps its current meaning and population. Never change it.
- Checks are **read-only** against business data. Never write a `Site Pass`.
- Every default is overridable per-site via `site_config.json`; a missing or malformed key falls back to the default rather than throwing.
- Suppression must always expire. No permanent mute.
- Alert-path exceptions must be logged via `frappe.log_error`, never swallowed.

---

### Task 1: Collector captures `last_pass_created`

**Files:**
- Modify: `vms/vms/doctype/tenant/tenant.json` (add field)
- Modify: `vms/vms/tenant_usage_collector.py:110-120`
- Test: `vms/tests/test_outage_monitor.py` (create)

**Interfaces:**
- Consumes: nothing
- Produces: `Tenant.last_pass_created` (Datetime, nullable); `stats["last_pass_created"]` key in the dict returned by the per-site collector

- [ ] **Step 1: Read the current collector block**

Open `vms/vms/tenant_usage_collector.py` and read lines 105–145. Confirm the
existing shape — you must add alongside, not replace:

```python
cursor.execute("SELECT MAX(modified) as last_mod FROM `tabSite Pass`")
row = cursor.fetchone()
stats["last_activity"] = row["last_mod"] if row and row["last_mod"] else None
```

- [ ] **Step 2: Add the field to the Tenant DocType**

In `vms/vms/doctype/tenant/tenant.json`, add `"last_pass_created"` to the
`field_order` array immediately after `"last_activity"`, and add this object to
the `fields` array:

```json
{
  "fieldname": "last_pass_created",
  "fieldtype": "Datetime",
  "label": "Last Pass Created",
  "read_only": 1,
  "description": "MAX(creation) of Site Pass on the tenant site. Real user activity only - never touched by background jobs."
}
```

- [ ] **Step 3: Write the failing test**

Create `vms/tests/test_outage_monitor.py`:

```python
import unittest
from frappe.utils import add_to_date, now_datetime
from vms.vms.tenant_usage_collector import _calculate_health_status


class TestHealthStatus(unittest.TestCase):
	def test_none_is_unknown_not_inactive(self):
		# A newly provisioned tenant has no passes yet. It must not alert.
		self.assertEqual(_calculate_health_status(None), "Unknown")

	def test_recent_is_active(self):
		self.assertEqual(
			_calculate_health_status(add_to_date(now_datetime(), hours=-2)), "Active"
		)

	def test_ten_days_is_low_activity(self):
		# Boundaries are 7d/30d in _calculate_health_status. Do NOT retune them:
		# same-day detection is Task 5's job, and shifting these would change
		# health status for every tenant.
		self.assertEqual(
			_calculate_health_status(add_to_date(now_datetime(), days=-10)), "Low Activity"
		)

	def test_six_weeks_is_inactive(self):
		# Regression anchor: the exact pansen incident.
		self.assertEqual(
			_calculate_health_status(add_to_date(now_datetime(), days=-42)), "Inactive"
		)
```

- [ ] **Step 4: Run the test to see the current behaviour**

Run: `cd /path/to/frappe-bench && bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`

Expected: `test_none_is_unknown_not_inactive` FAILS if the current function
returns something other than `"Unknown"` for `None`. Record what it actually
returns — you need to preserve any existing caller expectations.

- [ ] **Step 5: Add the `MAX(creation)` query**

In `vms/vms/tenant_usage_collector.py`, directly after the existing
`last_activity` block, add:

```python
		# last_activity above is MAX(modified), which nightly jobs
		# (expire_overdue_passes, auto_checkout_stale_passes) refresh even when no
		# human has registered anyone. Only MAX(creation) reflects real user
		# activity, so health is classified on this field.
		try:
			cursor.execute("SELECT MAX(creation) as last_created FROM `tabSite Pass`")
			row = cursor.fetchone()
			stats["last_pass_created"] = row["last_created"] if row and row["last_created"] else None
		except Exception:
			stats["last_pass_created"] = None
```

- [ ] **Step 6: Persist the new field**

Find where the collector writes stats onto the Tenant doc (search for
`last_activity` around line 182). Add the sibling write immediately after it,
matching the existing style:

```python
	if stats.get("last_pass_created"):
		tenant_doc.last_pass_created = stats["last_pass_created"]
```

- [ ] **Step 7: Run the tests**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: the three non-`None` tests PASS. `test_none_is_unknown_not_inactive`
may still fail — Task 2 fixes it.

- [ ] **Step 8: Commit**

```bash
git add vms/vms/doctype/tenant/tenant.json vms/vms/tenant_usage_collector.py vms/tests/test_outage_monitor.py
git commit -m "feat(monitoring): collect last_pass_created from MAX(creation)

last_activity derives from MAX(modified), which nightly jobs refresh, so a
tenant appears active while registration is dead. Add the creation-based
signal alongside it; last_activity is unchanged."
```

---

### Task 2: Classify health on `last_pass_created`

**Files:**
- Modify: `vms/vms/tenant_usage_collector.py:142,147-160`
- Modify: `vms/vms/tenant_usage_alerts.py` (`_process_tenant_alert`)
- Test: `vms/tests/test_outage_monitor.py`

**Interfaces:**
- Consumes: `stats["last_pass_created"]` from Task 1
- Produces: `_calculate_health_status(value)` returning one of
  `"Active" | "Low Activity" | "Inactive" | "Unknown"`; `_health_from_stats(stats)`

- [ ] **Step 1: Write the failing regression test**

Append to `vms/tests/test_outage_monitor.py`:

```python
class TestHealthUsesCreationNotModified(unittest.TestCase):
	def test_modified_recently_but_created_long_ago_is_inactive(self):
		"""The exact pansen bug: nightly jobs touched passes for 6 weeks while
		nobody registered anyone. Classification must follow creation."""
		from vms.vms.tenant_usage_collector import _health_from_stats

		stats = {
			"last_activity": add_to_date(now_datetime(), days=-2),       # background jobs
			"last_pass_created": add_to_date(now_datetime(), days=-42),  # real users
		}
		self.assertEqual(_health_from_stats(stats), "Inactive")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: FAIL — `cannot import name '_health_from_stats'`

- [ ] **Step 3: Make `_calculate_health_status` handle None**

In `vms/vms/tenant_usage_collector.py`, change the signature and guard at line
~147 so a missing value is explicitly unknown rather than implicitly stale:

```python
def _calculate_health_status(last_pass_created):
	"""Classify tenant health from REAL user activity (Site Pass creation).

	Never pass last_activity here: it derives from MAX(modified), which nightly
	jobs refresh, and would report a dead tenant as Active.
	"""
	if not last_pass_created:
		return "Unknown"
```

Leave the rest of the function body unchanged, renaming the local variable
references from `last_activity` to `last_pass_created` throughout.

- [ ] **Step 4: Add the stats-level helper**

Add directly below `_calculate_health_status`:

```python
def _health_from_stats(stats):
	"""Single place that decides which signal drives health."""
	return _calculate_health_status(stats.get("last_pass_created"))
```

- [ ] **Step 5: Switch the call site**

At line ~142, replace:

```python
	stats["health_status"] = _calculate_health_status(stats.get("last_activity"))
```

with:

```python
	stats["health_status"] = _health_from_stats(stats)
```

- [ ] **Step 6: Switch the alert classifier**

In `vms/vms/tenant_usage_alerts.py`, in `check_tenant_health_alerts`, add
`"last_pass_created"` to the `fields` list of the `frappe.get_all("Tenant", ...)`
call. Then in `_process_tenant_alert`, replace the first four lines:

```python
def _process_tenant_alert(tenant, today):
	"""Evaluate one tenant for health transition. Returns True if alert created."""
	# Uses last_pass_created, not last_activity: the latter is refreshed by
	# nightly jobs and would never go stale.
	if not tenant.get("last_pass_created"):
		return False

	last_dt = get_datetime(tenant.last_pass_created)
```

Leave everything below unchanged, except the alert record field near the end:

```python
	alert.last_activity = tenant.last_pass_created
```

- [ ] **Step 7: Run the tests**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: ALL PASS, including `test_none_is_unknown_not_inactive`.

- [ ] **Step 8: Commit**

```bash
git add vms/vms/tenant_usage_collector.py vms/vms/tenant_usage_alerts.py vms/tests/test_outage_monitor.py
git commit -m "fix(monitoring): classify tenant health on creation, not modified

Regression test reproduces the pansen incident: passes modified 2 days ago,
created 42 days ago, must classify Inactive."
```

---

### Task 3: Backfill patch for existing tenants

**Files:**
- Create: `vms/patches/v1_0/backfill_last_pass_created.py`
- Modify: `vms/patches.txt`

**Interfaces:**
- Consumes: `Tenant.last_pass_created` from Task 1
- Produces: populated values for all existing tenants

- [ ] **Step 1: Check the patches.txt format**

Run: `tail -5 vms/patches.txt` and note the exact module-path style used, plus
whether a `[post_model_sync]` section exists. Match it. Also confirm the
directory `vms/patches/v1_0/` exists and contains `__init__.py`; create the
`__init__.py` if missing.

- [ ] **Step 2: Write the patch**

Create `vms/patches/v1_0/backfill_last_pass_created.py`:

```python
import frappe


def execute():
	"""Populate Tenant.last_pass_created for existing rows.

	Admin site only - Tenant records live there. Leaves the value NULL when the
	tenant site cannot be read; the next scheduled collector run fills it in.
	NULL classifies as Unknown, never Inactive, so this cannot cause a false alert.
	"""
	if "admin" not in frappe.local.site:
		return
	if not frappe.db.exists("DocType", "Tenant"):
		return
	if not frappe.db.has_column("Tenant", "last_pass_created"):
		return

	from vms.vms.tenant_usage_collector import collect_tenant_usage_manual

	try:
		collect_tenant_usage_manual()
	except Exception as e:
		frappe.log_error(
			f"backfill_last_pass_created failed: {str(e)[:200]}", "VMS Patch"
		)
```

- [ ] **Step 3: Register the patch**

Append to `vms/patches.txt` (under `[post_model_sync]` if that section exists):

```
vms.patches.v1_0.backfill_last_pass_created
```

- [ ] **Step 4: Verify it is importable**

Run: `python3 -m py_compile vms/patches/v1_0/backfill_last_pass_created.py`
Expected: no output (success).

- [ ] **Step 5: Commit**

```bash
git add vms/patches/v1_0/backfill_last_pass_created.py vms/patches.txt
git commit -m "feat(monitoring): backfill last_pass_created for existing tenants"
```

---

### Task 4: Alert suppression helper

**Files:**
- Create: `vms/vms/outage_monitor.py`
- Test: `vms/tests/test_outage_monitor.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `_config(key, default)` → value from `site_config.json`, falling back to `default` on missing/malformed
  - `_should_alert(key: str, silence_hours: int) -> bool` — True when not suppressed; sets suppression as a side effect
  - `_clear_alert(key: str) -> bool` — True if a suppression existed (i.e. this is a recovery)
  - `_send_alert(subject: str, body: str) -> None`
  - `DEFAULT_SILENCE_HOURS = 12`

- [ ] **Step 1: Write the failing test**

Append to `vms/tests/test_outage_monitor.py`:

```python
class TestSuppression(unittest.TestCase):
	def setUp(self):
		import frappe

		self.key = "test:rule:sig"
		frappe.cache().delete_value("vms_alert_silence:" + self.key)

	def test_first_call_alerts_second_is_suppressed(self):
		from vms.vms.outage_monitor import _should_alert

		self.assertTrue(_should_alert(self.key, silence_hours=12))
		self.assertFalse(_should_alert(self.key, silence_hours=12))

	def test_clear_reports_whether_it_was_suppressed(self):
		from vms.vms.outage_monitor import _clear_alert, _should_alert

		self.assertFalse(_clear_alert(self.key))   # nothing to clear
		_should_alert(self.key, silence_hours=12)
		self.assertTrue(_clear_alert(self.key))    # was suppressed -> recovery
		self.assertFalse(_clear_alert(self.key))   # already cleared

	def test_config_falls_back_on_missing_key(self):
		from vms.vms.outage_monitor import _config

		self.assertEqual(_config("definitely_not_a_real_key_xyz", 6), 6)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: FAIL — `No module named 'vms.vms.outage_monitor'`

- [ ] **Step 3: Create the module**

Create `vms/vms/outage_monitor.py`:

```python
"""Business-outcome monitoring for VMS tenants.

Separate from system_health.py, which watches infrastructure liveness. This
module watches whether the product is actually being used, because a site can be
perfectly healthy while its core function is entirely broken - which is exactly
what happened to pansen for six weeks in June-July 2026.
"""

import frappe

SILENCE_KEY_PREFIX = "vms_alert_silence:"
DEFAULT_SILENCE_HOURS = 12


def _config(key, default):
	"""Read a per-site setting, falling back to default.

	A typo in site_config.json must never disable monitoring silently, so any
	failure to read or coerce returns the default rather than raising.
	"""
	try:
		value = frappe.get_site_config().get(key)
		if value is None:
			return default
		if isinstance(default, int) and not isinstance(default, bool):
			return int(value)
		return value
	except Exception:
		return default


def _should_alert(key, silence_hours=DEFAULT_SILENCE_HOURS):
	"""True if this alert is not currently suppressed. Sets suppression if so.

	Suppression always carries a TTL, so it expires on its own. There is no
	permanent mute by design - an alert that can be switched off forever is an
	alert that will be.
	"""
	cache_key = SILENCE_KEY_PREFIX + key
	if frappe.cache().get_value(cache_key):
		return False
	frappe.cache().set_value(cache_key, "1", expires_in_sec=silence_hours * 3600)
	return True


def _clear_alert(key):
	"""Clear suppression. Returns True if one existed (i.e. this is a recovery)."""
	cache_key = SILENCE_KEY_PREFIX + key
	if frappe.cache().get_value(cache_key):
		frappe.cache().delete_value(cache_key)
		return True
	return False


def _send_alert(subject, body):
	"""Email the alert. Never raises - a failure here is itself logged so the
	error-burst rule can escalate it."""
	try:
		recipient = _config("outage_alert_email", "developer@tarode.com")
		frappe.sendmail(recipients=[recipient], subject=subject, message=body)
	except Exception as e:
		frappe.log_error(f"outage alert send failed: {str(e)[:200]}", "VMS Outage Monitor")
```

- [ ] **Step 4: Run the tests**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add vms/vms/outage_monitor.py vms/tests/test_outage_monitor.py
git commit -m "feat(monitoring): alert suppression with mandatory expiry"
```

---

### Task 5: Same-day stall check (Fix 3)

**Files:**
- Modify: `vms/vms/outage_monitor.py`
- Test: `vms/tests/test_outage_monitor.py`

**Interfaces:**
- Consumes: `_config`, `_should_alert`, `_clear_alert`, `_send_alert`,
  `DEFAULT_SILENCE_HOURS` from Task 4
- Produces: `check_stall()` — hourly scheduler entry point;
  `_within_business_hours(now, hours_str, days_str) -> bool`

- [ ] **Step 1: Write the failing test**

Append to `vms/tests/test_outage_monitor.py`:

```python
from datetime import datetime


class TestBusinessHours(unittest.TestCase):
	def _check(self, dt):
		from vms.vms.outage_monitor import _within_business_hours

		return _within_business_hours(dt, "08:00-20:00", "1-6")

	def test_midday_monday_is_inside(self):
		self.assertTrue(self._check(datetime(2026, 7, 27, 12, 0)))   # Monday

	def test_early_morning_is_outside(self):
		# Prevents 03:00 false alarms, which train people to ignore alerts.
		self.assertFalse(self._check(datetime(2026, 7, 27, 3, 0)))

	def test_sunday_is_outside(self):
		self.assertFalse(self._check(datetime(2026, 7, 26, 12, 0)))  # Sunday

	def test_boundaries_inclusive_start_exclusive_end(self):
		self.assertTrue(self._check(datetime(2026, 7, 27, 8, 0)))
		self.assertFalse(self._check(datetime(2026, 7, 27, 20, 0)))

	def test_malformed_config_fails_open(self):
		from vms.vms.outage_monitor import _within_business_hours

		# Never fail closed: a bad config must not silently disable monitoring.
		self.assertTrue(
			_within_business_hours(datetime(2026, 7, 27, 3, 0), "garbage", "1-6")
		)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: FAIL — `cannot import name '_within_business_hours'`

- [ ] **Step 3: Implement the pure helper**

Append to `vms/vms/outage_monitor.py`:

```python
def _within_business_hours(now, hours_str, days_str):
	"""True if `now` falls inside the configured gate operating window.

	Outside the window the stall rule does not evaluate, because a quiet night is
	not an outage and nightly false alarms are how monitoring gets ignored.

	Fails OPEN: malformed config returns True, so a typo produces noise (which
	gets noticed and fixed) rather than silence (which does not).
	"""
	try:
		start_s, end_s = hours_str.split("-")
		start_h, start_m = [int(x) for x in start_s.split(":")]
		end_h, end_m = [int(x) for x in end_s.split(":")]
		day_from, day_to = [int(x) for x in days_str.split("-")]
	except Exception:
		return True

	if not (day_from <= now.isoweekday() <= day_to):
		return False

	minutes = now.hour * 60 + now.minute
	return (start_h * 60 + start_m) <= minutes < (end_h * 60 + end_m)
```

- [ ] **Step 4: Implement the check**

Append to `vms/vms/outage_monitor.py`:

```python
@frappe.whitelist()
def check_stall():
	"""Hourly: alert when no Site Pass has been created for N hours during
	business hours. Detects an outage the same working day."""
	try:
		if not _config("outage_alert_enabled", True):
			return
		if not frappe.db.exists("DocType", "Site Pass"):
			return

		from frappe.utils import add_to_date, now_datetime

		now = now_datetime()
		if not _within_business_hours(
			now,
			_config("outage_business_hours", "08:00-20:00"),
			_config("outage_business_days", "1-6"),
		):
			return

		hours = _config("outage_stall_hours", 6)
		since = add_to_date(now, hours=-hours)
		count = frappe.db.count("Site Pass", {"creation": [">=", since]})

		site = frappe.local.site
		key = f"{site}:stall"
		silence = _config("outage_alert_silence_hours", DEFAULT_SILENCE_HOURS)

		if count == 0:
			if _should_alert(key, silence):
				_send_alert(
					f"[VMS] No visitor passes created on {site} for {hours}h",
					f"No Site Pass has been created on {site} since {since} "
					f"({hours}h), during configured business hours.\n\n"
					f"Registration may be broken. Check /register end to end.",
				)
		elif _clear_alert(key):
			# Report recovery, otherwise silence is ambiguous: "fixed" looks
			# identical to "still broken but muted".
			_send_alert(
				f"[VMS] Recovered: passes are being created again on {site}",
				f"{count} pass(es) created in the last {hours}h on {site}.",
			)
	except Exception as e:
		frappe.log_error(f"check_stall failed: {str(e)[:200]}", "VMS Outage Monitor")
```

- [ ] **Step 5: Run the tests**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add vms/vms/outage_monitor.py vms/tests/test_outage_monitor.py
git commit -m "feat(monitoring): same-day stall check with business hours guard"
```

---

### Task 6: Error-burst escalation (Fix 2)

**Files:**
- Modify: `vms/vms/outage_monitor.py`
- Test: `vms/tests/test_outage_monitor.py`

**Interfaces:**
- Consumes: `_config`, `_should_alert`, `_send_alert`, `DEFAULT_SILENCE_HOURS` from Task 4
- Produces: `check_error_bursts()` — hourly scheduler entry point;
  `_normalise_signature(method, error) -> str`

- [ ] **Step 1: Write the failing test**

Append to `vms/tests/test_outage_monitor.py`:

```python
class TestErrorSignature(unittest.TestCase):
	def test_ids_and_digits_collapse(self):
		from vms.vms.outage_monitor import _normalise_signature

		a = _normalise_signature("tasks.foo", "Unknown column 'contact_pho' in row 12345")
		b = _normalise_signature("tasks.foo", "Unknown column 'contact_pho' in row 98765")
		self.assertEqual(a, b)

	def test_distinct_errors_stay_distinct(self):
		from vms.vms.outage_monitor import _normalise_signature

		a = _normalise_signature("tasks.foo", "Unknown column 'contact_pho'")
		b = _normalise_signature("tasks.bar", "Connection refused")
		self.assertNotEqual(a, b)

	def test_only_first_line_used(self):
		from vms.vms.outage_monitor import _normalise_signature

		a = _normalise_signature("tasks.foo", "Boom\n  File x\n  File y")
		b = _normalise_signature("tasks.foo", "Boom\n  totally different trace")
		self.assertEqual(a, b)
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: FAIL — `cannot import name '_normalise_signature'`

- [ ] **Step 3: Implement signature normalisation**

Add `import re` to the top of `vms/vms/outage_monitor.py` (below `import frappe`),
then append:

```python
_DIGITS = re.compile(r"\d+")


def _normalise_signature(method, error):
	"""Collapse near-identical errors into one signature.

	Only the first line is used - tracebacks vary per occurrence while the
	message does not. Digits are stripped so row IDs and timestamps do not
	fragment one recurring fault into hundreds of unique ones.
	"""
	first_line = (error or "").strip().split("\n")[0]
	return f"{method or 'unknown'}|{_DIGITS.sub('#', first_line)}"[:180]
```

- [ ] **Step 4: Implement the check**

Append to `vms/vms/outage_monitor.py`:

```python
@frappe.whitelist()
def check_error_bursts():
	"""Hourly: alert when the same error repeats. Errors that only land in a
	table nobody reads are not monitoring - check_pass_expiry_alerts failed
	~12x/hour for weeks without anyone being told."""
	try:
		if not _config("outage_alert_enabled", True):
			return

		from frappe.utils import add_to_date, now_datetime

		threshold = _config("outage_error_burst_threshold", 10)
		since = add_to_date(now_datetime(), hours=-1)

		rows = frappe.get_all(
			"Error Log",
			filters={"creation": [">=", since]},
			fields=["method", "error"],
			limit_page_length=2000,
		)

		buckets = {}
		for r in rows:
			sig = _normalise_signature(r.get("method"), r.get("error"))
			buckets.setdefault(sig, []).append(r)

		site = frappe.local.site
		silence = _config("outage_alert_silence_hours", DEFAULT_SILENCE_HOURS)

		for sig, items in buckets.items():
			if len(items) < threshold:
				continue
			if _should_alert(f"{site}:errorburst:{sig}", silence):
				_send_alert(
					f"[VMS] Repeating error on {site} ({len(items)}x/hour)",
					f"Signature: {sig}\nOccurrences in the last hour: {len(items)}\n\n"
					f"Most recent:\n{(items[-1].get('error') or '')[:2000]}",
				)
	except Exception as e:
		frappe.log_error(f"check_error_bursts failed: {str(e)[:200]}", "VMS Outage Monitor")
```

- [ ] **Step 5: Run the tests**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add vms/vms/outage_monitor.py vms/tests/test_outage_monitor.py
git commit -m "feat(monitoring): escalate repeating errors from Error Log"
```

---

### Task 7: Register hourly jobs

**Files:**
- Modify: `vms/hooks.py` (`scheduler_events["hourly"]`)

**Interfaces:**
- Consumes: `check_stall`, `check_error_bursts` from Tasks 5 and 6
- Produces: both running hourly on every site

- [ ] **Step 1: Read the current hourly block**

Run: `sed -n '/^scheduler_events/,/^}/p' vms/hooks.py`

Note the existing entries and **check every line ends with a comma** — this file
has previously been broken by a missing trailing comma before an appended item.

- [ ] **Step 2: Add the two jobs**

In `vms/hooks.py`, extend the `"hourly"` list:

```python
	"hourly": [
		"vms.tasks.check_pass_expiry_alerts",
		"vms.tasks.expire_overdue_passes",
		"vms.tasks.process_anomaly_alerts",
		"vms.tasks.sync_offline_queue",
		"vms.vms.outage_monitor.check_stall",
		"vms.vms.outage_monitor.check_error_bursts",
	],
```

- [ ] **Step 3: Verify the file still parses**

Run: `python3 -m py_compile vms/hooks.py`
Expected: no output (success).

- [ ] **Step 4: Confirm the monitor module parses**

Run: `python3 -m py_compile vms/vms/outage_monitor.py`
Expected: no output (success).

- [ ] **Step 5: Run the full test module**

Run: `bench --site <test-site> run-tests --module vms.tests.test_outage_monitor`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add vms/hooks.py
git commit -m "feat(monitoring): register stall and error-burst checks hourly"
```

---

## Deployment (requires explicit user approval — do NOT run unprompted)

Deployment is **not** part of this plan's tasks. When the user approves:

1. Push the branch; merge to `master` on the server via `git fetch` + `git merge`
   (never hand-edit files on the server — an hourly cron auto-commits there).
2. Clear bytecode, or stale `.pyc` will serve the old code:
   `find /home/ubuntu/frappe-bench/apps/vms -name '*.pyc' -delete && find /home/ubuntu/frappe-bench/apps/vms -name '__pycache__' -type d -exec rm -rf {} +`
3. `bench --site admin.vmsys.co migrate` (runs the backfill patch)
4. `sudo supervisorctl restart all`
5. **Verify the fix:** Pansen's `last_pass_created` must read `2026-06-16` and
   `health_status` must flip `Active → Inactive`. That flip is the proof.
6. **Prove alerts fire:** temporarily set `outage_stall_hours` to `1` on pansen,
   wait for the hourly run, confirm the email arrives, then restore to `6`. An
   alerting system never observed to fire is not known to work.

**Rollback:** `git reset --hard <pre-merge-sha>` + clear `.pyc` + restart.

---

## Self-Review

**Spec coverage:**
- §3 Fix 1 (`last_pass_created`, collector, classification, Unknown-on-NULL) → Tasks 1, 2
- §3 backfill → Task 3
- §4 Fix 2 error bursts → Task 6
- §5 Fix 3 stall check + business hours + config → Task 5
- §6 suppression, expiry, recovery → Tasks 4, 5
- §8 components/module layout → Tasks 4–6
- §9 invariants 1–5 → Task 4 (`_send_alert` never raises; TTL always set),
  read-only queries throughout, per-check try/except, Task 2 (creation-only signal)
- §10 testing → tests in Tasks 1, 2, 4, 5, 6, including both regression anchors
- §11 rollout → Deployment section

**Deviation from spec, accepted:** §8 lists `_pass_count_since(dt)` as a separate
helper. Task 5 calls `frappe.db.count` inline instead — a one-line query does not
earn its own function, and the spec's intent (read-only counting) is preserved.

**Gap accepted:** §5's per-site loop is not implemented. Frappe's scheduler
already invokes hourly jobs once per site, so invariant 4 (per-site isolation) is
satisfied by the scheduler rather than by an in-process loop. No separate task.

**Placeholder scan:** none — every step carries runnable code or an exact command.

**Type consistency:** `_config`, `_should_alert`, `_clear_alert`, `_send_alert`,
`_within_business_hours`, `_normalise_signature`, `_health_from_stats`,
`_calculate_health_status`, `DEFAULT_SILENCE_HOURS` are each defined once and
referenced with matching names and arities across Tasks 2, 4, 5, 6.
