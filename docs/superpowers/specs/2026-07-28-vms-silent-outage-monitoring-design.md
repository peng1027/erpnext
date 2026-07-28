# VMS Silent-Outage Monitoring — Design

**Date:** 2026-07-28
**Status:** Approved for planning
**Scope:** tenant *business* health. Infra/liveness health is covered by
`VMS_HEALTH_MONITORING_DESIGN.md` (2026-06-25) and is explicitly out of scope here.

---

## 1. Problem

Visitor registration on `pansen.vmsys.co` was **completely broken for six weeks**
and nothing reported it.

The monitoring was not missing and was not down. It ran every day of the outage
and concluded the tenant was healthy:

| Signal | Value on 2026-07-28 |
|---|---|
| Last Site Pass **created** | `2026-06-16` — 42 days ago |
| Last Site Pass **modified** | `2026-07-26` — 2 days ago |
| `Tenant TENANT-0036.health_status` | **"Active"** |
| `Tenant TENANT-0036.last_activity` | `2026-07-26 00:30:27` (= last *modified*) |
| `Tenant Alert Log` rows | 301, newest today |

**Root cause: the liveness metric is derived from `modified`, not `creation`.**
The daily jobs `expire_overdue_passes` and `auto_checkout_stale_passes` update
old passes every night. The system therefore refreshes its own heartbeat — it is
monitoring its own background jobs rather than user activity.

A correctly-functioning alerting pipeline on a corrupted signal is worse than no
alerting, because the green light is trusted. The admin dashboard also showed
Pansen healthy throughout, so the signal misled the vendor as well as the client.

**Secondary gap:** `check_pass_expiry_alerts` has been failing ~12×/hour, writing
to `Error Log` continuously. Nothing escalates it. Errors that only land in a
table nobody reads are not monitoring.

**Goal:** never again lose weeks to a silent outage.

## 2. Non-goals

- **Synthetic transaction / canary.** Deferred by decision. Faster detection, but
  needs OTP bypass and test-data cleanup. Revisit after this ships.
- **Unit-test coverage.** Tracked separately. (Today: 14 test files, but 10 are
  empty Frappe stubs with 0 asserts; real coverage is 3 files / 30 tests.)
- **New alert channels.** Email only. See §7 for the accepted limitation.
- **Changing the meaning of `last_activity`.** Explicitly preserved — see §3.

---

## 3. Fix 1 — correct the signal (additive)

Add a new field rather than redefining `last_activity`. Redefining it would flip
health status across all tenants on deploy and silently change the meaning of
301 historical `Tenant Alert Log` rows. Additive keeps history interpretable and
makes the two signals independently visible.

**New field on `Tenant`:**

| Field | Type | Meaning |
|---|---|---|
| `last_pass_created` | `Datetime` | `MAX(creation)` of `Site Pass` on that tenant's site |

Format `YYYY-MM-DD HH:MM:SS.ffffff` (synthetic example `2026-01-01 09:00:00.000000`).
Nullable — a tenant with no passes yet has `NULL`, which must be treated as
"no data", never as "stale" (a newly-provisioned tenant must not alert).

`last_activity` keeps its current definition and population. Unchanged.

**Populated by** the existing `collect_tenant_usage` daily collector, which
already reads tenant databases over pymysql. It gains one query:
`SELECT MAX(creation) FROM \`tabSite Pass\``.

**Health classification switches to `last_pass_created`:**

| Status | Condition |
|---|---|
| Active | `last_pass_created` within 7d |
| Low Activity | within 30d |
| Inactive | 30d or older |
| Unknown | `last_pass_created IS NULL` |

**Corrected 2026-07-28 after reading the code.** An earlier draft of this table
said 24h/7d, taken from a stale note rather than from
`_calculate_health_status`, whose real boundaries are 7d/30d. Ruling: keep the
existing boundaries and change only the *source column*. Rationale: classifying
30 days late would be useless on its own, but same-day detection is Fix 3's job
(§5), not this classifier's — and re-tuning these boundaries would shift health
status for every tenant and risk weekend/holiday noise for no added benefit.
**Only the `modified` → `creation` change and the NULL → `Unknown` change are in
scope here.**

**Expected immediate effect on deploy:** Pansen flips `Active → Inactive`. This
is correct, and is the first true reading in six weeks.

**Dashboard** shows both fields side by side. A large gap between them is itself
diagnostic — it means background jobs are running while users are absent.

---

## 4. Fix 2 — error-burst escalation

Runs **hourly**, per site.

Group `Error Log` rows from the last hour by a normalised signature: the `method`
field plus the first line of `error`, with digits and IDs stripped so
near-identical errors collapse into one. If any signature occurs
`>= outage_error_burst_threshold` times (default **10**), email the signature,
the count, and the most recent full traceback.

This would have surfaced `check_pass_expiry_alerts` on day one.

---

## 5. Fix 3 — same-day stall check

Fix 1 alone detects an outage at the 7-day mark. This shortens it to same-day.

Runs **hourly**, per site. During business hours, if
`COUNT(Site Pass created in the last outage_stall_hours) == 0` → alert.
Default **6 hours**, per decision.

**Business hours** default 08:00–20:00 site-local, Mon–Sat. Outside that window
the rule does not evaluate. This is what prevents the night and Sunday false
alarms that would otherwise train recipients to ignore the alert — the failure
mode that kills most monitoring.

### Calibrated against real data — 2026-07-28

The 6h / 08:00–20:00 / Mon–Sat figures in an earlier draft were **assumptions and
all three were wrong**. Measured against Pansen's 1,451 passes over its active
window (2026-01-28 → 2026-06-16):

| Setting | Assumed | **Calibrated** | Evidence |
|---|---|---|---|
| `outage_business_days` | `"1-6"` | **`"1-7"`** | Sunday had 173 passes over 12 Sundays — a normal working day. Busiest days are Fri/Sat. |
| `outage_business_hours` | `"08:00-20:00"` | **`"06:00-23:00"`** | 18% of passes fell outside the assumed window (21:00 = 55, 23:00 = 23, 05:00–07:00 = 139). |
| `outage_stall_hours` | `6` | **`36`** | See gap analysis below. |

**Gap analysis (1,450 consecutive-pass intervals):** mean gap 2.1h. Gaps over
6h: 88. Over 12h: 51. Over 24h: 7. Over 48h: 5.

The decisive feature is a **cliff**. The five largest gaps are 527h, 351h, 313h,
190h and 165h — genuine multi-day site closures. The sixth largest is **30h**.
Normal operation therefore never exceeds ~30 hours without a pass.

`36` sits above the 30h normal ceiling and below the 165h shortest real closure.
It would have fired 5 times in 4.5 months, each a genuine extended shutdown.

For contrast, `6` would have fired **88 times** — roughly every 1.5 days. That is
the alert-fatigue path that recreates the original incident in a new form.

**36h is not a same-day rule, and that is honest.** It detects a six-week outage
in a day and a half instead of the 30 days the old classifier needed — a large
improvement without false alarms. Genuine same-day detection needs the synthetic
canary (§2 non-goals); this data is precisely why: real traffic here is too
sparse and bursty to distinguish "quiet" from "broken" within a single day.

> **Still to confirm with Pansen on site:** whether the near-24h activity profile
> reflects real gate operation or after-hours data entry, and whether the five
> long gaps were planned shutdowns. Both affect whether 36h should move.

### Configuration

Per-site in `site_config.json`, all optional, defaults as above:

| Key | Default |
|---|---|
| `outage_alert_enabled` | `true` |
| `outage_stall_hours` | `6` |
| `outage_business_hours` | `"08:00-20:00"` |
| `outage_business_days` | `"1-6"` (ISO, Mon=1) |
| `outage_error_burst_threshold` | `10` |
| `outage_alert_email` | `developer@tarode.com` |

Config rather than constants: gate hours are a client-operational detail and must
not require a code change and redeploy.

---

## 6. Alert suppression

Without suppression, a six-week outage sends ~1,000 emails and gets filtered to
trash — reproducing the original failure in a new form.

- After firing, a rule+site (+signature for Fix 2) is suppressed for
  `ALERT_SILENCE_HOURS`, default **12**.
- State in Redis: `vms_alert_silence:<site>:<rule>:<signature>`, TTL = window.
- **Suppression always expires.** There is no permanent mute. An alert that can
  be switched off forever is an alert that will be.
- **Recovery is reported.** When a suppressed rule evaluates healthy again, send
  one "recovered" email and clear the key. Without this, silence is ambiguous —
  "fixed" is indistinguishable from "still broken, still muted".

---

## 7. Accepted limitation

Email has two blind spots: it can be ignored, and a fully-down server sends
nothing. A dead-man's-switch (healthchecks.io, already used by the infra layer)
covers both and should be added later. Recorded here so this is a known decision,
not an oversight.

---

## 8. Components

New module `vms/vms/outage_monitor.py`, separate from `tasks.py` (already a large
grab-bag) and `system_health.py` (infra liveness, a different concern):

| Function | Responsibility |
|---|---|
| `check_stall()` | Fix 3 entry point; hourly |
| `check_error_bursts()` | Fix 2 entry point; hourly |
| `_within_business_hours(cfg, now)` | Pure; window/day logic |
| `_pass_count_since(dt)` | Read-only count |
| `_error_signatures(since)` | Group + normalise |
| `_should_alert(key, hours)` | Suppression check + set |
| `_send_alert(subject, body, cfg)` | Email via existing sender |

Changes to existing files:
- `Tenant` DocType JSON — add `last_pass_created`
- `collect_tenant_usage` — populate it
- `tenant_usage_alerts.py` — classify on the new field
- `hooks.py` — register two hourly jobs
- Patch — backfill `last_pass_created` for existing tenants

The pure helpers hold the tricky logic and are unit-testable without a site or DB.

---

## 9. Invariants

1. **The alerter must never fail silently.** Exceptions are caught, logged, and
   are themselves Fix-2 candidates. Monitoring that dies quietly manufactures
   false confidence — the exact failure this spec exists to end.
2. **Suppression always expires.** By construction.
3. **Checks never write business data.** Read-only against `Site Pass` and
   `Error Log`.
4. **Per-site isolation.** One site throwing must not stop others being
   evaluated; loop bodies individually wrapped.
5. **Background jobs must never refresh a liveness metric.** The rule this
   incident taught. Any future health signal must derive from user-originated
   events only.

---

## 10. Testing

Untested paths break — that is the lesson of this incident. The monitor gets
tests, or we add a component whose failure mode is again silence.

**Unit (pure, no DB):**
- inside/outside business hours; weekday boundaries; malformed config → defaults
- signature normalisation collapses near-identical errors, keeps distinct ones apart
- `last_pass_created IS NULL` → "Unknown", never "Inactive"

**Integration (test site, seeded, rolled back):**
- 0 passes in window during business hours → alerts
- normal volume → does **not** alert
- 0 passes outside business hours → does **not** alert
- re-run inside silence window → does **not** re-alert; after expiry → alerts
- recovery after suppression → exactly one "recovered" email
- ≥10 identical errors/hour → alerts; 9 → does not
- one site raising does not prevent the next being evaluated

**Regression anchors — both reproduce the actual incident:**
- A tenant whose passes are only *modified* (never created) for 7+ days must be
  classified **Inactive**, not Active. This is the exact bug.
- A site whose last creation is 6 weeks old must alert on the first run.

---

## 11. Rollout

1. Add field + backfill patch; verify Pansen's `last_pass_created` reads
   `2026-06-16` and status flips to **Inactive**. That flip is the proof the fix
   works.
2. Enable Fix 2 and Fix 3 on pansen only (`outage_alert_enabled`).
3. Observe one week; tune `outage_stall_hours` against real gate hours.
4. Enable for other tenants as they go live.

**Prove it fires.** Temporarily set `outage_stall_hours` to a value guaranteed to
trip, confirm the email arrives, then restore. An alerting system that has never
been observed to fire is not known to work — which is how this incident began.
