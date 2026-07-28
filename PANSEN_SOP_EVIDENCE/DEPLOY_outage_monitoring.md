# Deploy runbook — VMS outage monitoring

Branch `feat/outage-monitoring` @ `2dec125` (13 commits off production `bd1e0c1`).
**NOT pushed, NOT deployed.** 22 tests pass.

## 1. Set config BEFORE enabling alerts

`sites/pansen.vmsys.co/site_config.json` — calibrated from 1,451 real passes:

    "outage_alert_enabled": false,
    "outage_stall_hours": 36,
    "outage_business_hours": "06:00-23:00",
    "outage_business_days": "1-7",
    "outage_error_burst_threshold": 10,
    "outage_alert_email": "developer@tarode.com"

`sites/admin.vmsys.co/site_config.json` — the stall check self-guards on admin,
but set this anyway so the burst check is explicit:

    "outage_alert_enabled": true

Leave tarode/bluesen untouched (not in use).

## 2. Deploy

    cd /home/ubuntu/frappe-bench/apps/vms
    git fetch origin feat/outage-monitoring && git merge --no-edit FETCH_HEAD

Then clear stale bytecode — this app has been bitten by it before. Delete every
`*.pyc` file and every `__pycache__` directory under `apps/vms`, then:

    cd /home/ubuntu/frappe-bench
    bench --site admin.vmsys.co migrate      # runs the backfill patch
    sudo supervisorctl restart all

**Rollback:** `git reset --hard bd1e0c1`, clear bytecode again, restart.

## 3. Verify the fix actually worked

Pansen's `last_pass_created` must read **2026-06-16**, and `health_status` must
flip **Active → Inactive**. That flip is the proof — it is the first true
reading in six weeks.

## 4. Watch the first two hours

`check_pass_expiry_alerts` fails ~12×/hour, above the burst threshold, so expect
that email almost immediately. It is the intended catch, not a malfunction.
Several unrelated buckets may also cross 10/hour on day one, because existing
code logs long text into `Error Log.method`.

## 5. Enable the stall check only after step 4 settles

Set `"outage_alert_enabled": true` on pansen.

Then **prove it fires**: temporarily set `"outage_stall_hours": 1`, wait for the
hourly run, confirm the email arrives, and restore it to `36`. An alerting
system that has never been observed to fire is not known to work — which is how
this whole incident began.

## 6. Confirm with Pansen on site (30 July)

- Is the gate genuinely active ~24h, or is late-night traffic after-hours data entry?
- Was Sunday really a working day?
- Were the five long gaps (527h, 351h, 313h, 190h, 165h) planned shutdowns?

Any of these may move `outage_stall_hours` off 36.

## Known and accepted

- **Email only.** A dead-man's-switch is a documented future addition; email
  cannot alert you when the whole server is down.
- **36h is not same-day detection**, and that is honest. It catches a six-week
  outage in a day and a half instead of the 30 days the old classifier needed.
  True same-day detection needs the deferred synthetic canary.
- **Pansen will start emailing its own `admin_email`** on the Inactive
  transition. Warn the client before deploying, or they will receive it cold.
