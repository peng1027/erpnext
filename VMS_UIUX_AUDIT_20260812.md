# VMS UI/UX Audit — 2026-08-12

Scope: the four user journeys of the VMS front end, judged against four
standards at once. Written for internal use; the client-facing extract is the
section marked **Client-safe findings**.

---

## 1. Method

### The four standards, and how they combine

They are not averaged. Averaging produces numbers that no decision can be made
from. They are layered, and a lower layer overrides a higher one.

| Layer | Standard | How a failure is written |
|---|---|---|
| 1 | DPDP notice/consent; WCAG 2.2 AA blockers | **"Does not comply."** A defect, not a suggestion. |
| 2 | Indian construction-site field conditions | **Veto.** Any recommendation that fails here is deleted, not demoted. |
| 3 | Nielsen's heuristics | Severity 0–4 (frequency × obstruction × recurrence). |
| 4 | Commercial VMS products (Envoy, Eptura, Sine) | Positioning context only. **Never a source of recommendations.** |

Layer 2's five conditions: low-literacy migrant workers; screens in direct
sunlight; cheap Android handsets; a queue at the gate; intermittent network.
A recommendation that is correct under WCAG but adds three screens of reading
for a worker in a queue does not survive.

### Evidence tiers

Every finding carries one. This codebase has repeatedly shipped code that looked
complete and had never run, so "the source says so" is not the same as "it does
so."

| Tier | Meaning | Permitted wording |
|---|---|---|
| **E1** | Observed in a screenshot or a live render | May be stated as fact |
| **E2** | Read in source; behaviour inferred | Must say "the source shows…" |
| **E3** | Inferred from context, no direct evidence | Must say "unverified"; **excluded from any client-facing version** |

---

## 2. Verdict

The registration flow is competently built and gets several things right that
commercial products get wrong. It fails on two counts that are objective and
one that is decisive in the field.

- **Two Layer-1 compliance failures.** One is now fixed (below); one is fixed in
  code but not deployed.
- **One Layer-2 veto-level gap: the product has no multi-language support at
  all.** This outweighs every other finding in this document.

---

## 3. Journey 1 — Self-registration (`vms/www/register.html`)

Evidence: `PANSEN_SOP_EVIDENCE/01-registration-form.png`,
`02-mobile-view.png` (E1) plus source (E2).

### Layer 1 — does not comply

**L1-1 · Pinch-zoom disabled — WCAG 2.2 SC 1.4.4 (AA)** · E2 · **FIXED
2026-08-12**
The viewport meta carried `maximum-scale=1.0, user-scalable=no`. AA requires
text to be resizable to 200%. iOS has ignored this since iOS 10; Android Chrome
honours it, and Android is what these users carry.
Affected six pages, all of them input-taking: `register`, `login`,
`tenant-register`, `apply`, `forgot-password`, `update-password`. Read-only
pages were unaffected — the distribution shows the cause was the old habit of
suppressing iOS zoom-on-focus for small inputs, a workaround that is now
unnecessary (iOS does not zoom for inputs ≥16px).
Fixed in `fix/a11y-viewport-zoom` (`d9524db`), removing only the two offending
parameters. **Deployed 2026-08-14** as `ab58550`; between the fix and that
date this section read "Fixed" while production still blocked zoom - the
commit existed and had never been cherry-picked onto the deployed branch.

**L1-2 · No DPDP notice or consent at the point of collection** · E1 + E2
`consent` appears **0 times** in `register.html`, and 0 times across all public
pages. The only privacy statement on screen is Aadhaar-specific ("your Aadhaar
number is never stored") while the form collects name, mobile, email, company,
host, purpose, ID type and number, photograph and site location.
DPDP §5 requires notice at or before collection.
Fixed in code on `feat/dpdp-consent` (`5bfb27b`) — **not deployed**.

### Layer 2 — field viability

**L2-1 · No internationalisation anywhere in the product** · E2 · **highest
impact finding in this audit**
`language_switcher|data-i18n|hindi|हिन` matches **0 times across all public
pages**. `language_switcher.js` exists in the repo and is precached by `sw.js`,
but no page loads it — the file ships, is cached, and never executes.
A migrant worker at Bhilwara must complete an English form containing "Purpose
of Visit" and "Organization". Every accessibility refinement below is moot for
someone who cannot read the field labels.

**L2-2 · Single-page form roughly 4–5 phone screens tall** · E1
The main throughput constraint at a gate queue. Note that the machinery for
progressive disclosure already exists (see R-1) and is simply not used to
shorten a single sitting.

### Layer 3 — Nielsen severity

| # | Finding | Sev | Tier |
|---|---|---|---|
| N-1 | Aadhaar instruction ("photo of the QR on the BACK") is text-only, no diagram — precisely where low-literacy users need a picture | 3 | E1 |
| N-2 | "Find your pass" occupies the top of the first screen with the heaviest visual weight, competing with "register new"; first-time users may search before registering | 2 | E1 |
| N-3 | Required-field marking inconsistent: Purpose of Visit, ID Type, ID Number carry no asterisk | 2 | E1 |
| N-4 | Date renders `2026/07/28`; India conventionally uses DD/MM/YYYY, and a native date input follows browser locale | 1 | E1 |

### Hypotheses the evidence refuted

Recorded because they are the kind of thing a source-only review asserts
confidently and wrongly.

| Hypothesis | Reality |
|---|---|
| **R-1** Choosing "Worker" only swaps a label; the form still asks visitor questions | **False.** `.visitor-fields/.worker-fields` toggle correctly (`register.html:1064`, CSS `:374`) |
| **R-2** The mobile view overflows horizontally (screenshot is clipped at the right edge) | **False.** All four width rules are `max-width`, which cannot cause overflow. The clipping is a capture artefact |

### Done well — do not change

Real `<label>` elements above every field rather than placeholder-as-label;
separated `+91` country prefix; explicit "Photo * (Required)"; the Aadhaar
privacy statement surfaced inline instead of hidden behind a link.

---

## 4. Findings that span all four journeys

Established by source sweep across `vms/www/*.html`, no rendering required.

| Finding | register | guard | my-pass | dashboard | login | tenant-reg |
|---|---|---|---|---|---|---|
| Blocks pinch-zoom (**now fixed**) | was YES | no | no | no | was YES | was YES |
| Any i18n | 0 | 0 | 0 | 0 | 0 | 0 |
| Any consent | 0 | 0 | 0 | 0 | 0 | 0 |

Two of the three are therefore product-level, not page-level: **no page in the
product supports a second language, and no page obtains consent.**

---

## 4b. What is actually deployed

Committed is not deployed. This document said "Fixed" for two days about a
change that was only ever on a branch, so the distinction is recorded here.

| Change | Branch | On production? |
|---|---|---|
| Pinch-zoom unblocked | `fix/a11y-viewport-zoom` | **Yes** — `ab58550`, 2026-08-14 |
| Right-to-Access report | `fix/dpdp-retention-purge` | **Yes** — 2026-08-14 |
| Aadhaar retention clock + cleanup gate | `fix/dpdp-retention-purge` | **Yes** — 2026-08-14 |
| DPDP consent at collection | `feat/dpdp-consent` | **No** — needs a schema migration on all three tenants, and turns consent into a hard requirement on Pansen and Bluesen the moment it lands |
| Site Pass retention purge (`579030f`) | `fix/dpdp-retention-purge` | **No, deliberately** — it would irreversibly anonymise 376 of Pansen's 1453 passes and all 3 of Bluesen's. Held pending written confirmation that those records are not needed for CLRA/BOCW labour compliance |

## 5. Open — requires E1 evidence

`guard.html`, `my-pass.html` and the admin back office have **no visual
evidence**. Their entries above are E2 and are labelled as such; no visual
judgement about them appears in this document.

Obtaining E1 requires rendering them, and the only environment where they can be
rendered is the client's production site. Deliberately not done unilaterally.
Agreed approach: capture screenshots during the client walkthrough, then
complete the visual layer of the audit from those.

Needed: `guard.html` mid-scan; `my-pass.html` showing an issued pass; the admin
approval list.

---

## 6. Recommendations, ranked

1. **Multi-language support (Hindi first).** Nothing else in this document
   changes outcomes as much. `language_switcher.js` already exists — establish
   why it was never wired up before treating this as greenfield.
2. **Deploy the DPDP consent work** (`feat/dpdp-consent`). Note it makes consent
   mandatory on Pansen, since `require_consent_for_entry` is already `1`; the
   notice text is the client's and they should read it first.
3. **Illustrate the Aadhaar QR instruction.** Cheapest large gain for
   low-literacy users.
4. **Split the form by role using the toggle that already exists.**
5. Normalise required-field marking; reconsider the prominence of "Find your
   pass".

Not recommended, though commercial products do it: multi-step wizards with
progress indicators, and richer inline help text. Both add taps and reading for
a user standing in a queue. Layer 2 vetoes them.

---

## 7. Client-safe findings

E1 and E2 only; no E3, no unverified inference.

- Pinch-zoom was disabled on six input pages, failing WCAG 2.2 AA (SC 1.4.4).
  **Fixed.**
- The product currently ships no multi-language support; the registration flow
  is English-only.
- The registration form presents no privacy notice covering the personal data it
  collects. Implemented, pending deployment.
- Form labelling, country-code handling and the Aadhaar privacy statement follow
  good practice and need no change.
