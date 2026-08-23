# 13 — AI and Notifications

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 13 — AI Recommendation Framework & Notification Framework |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related FRs** | FR-AI-001…006, FR-GLO-004…005, FR-WCE-030, FR-COM-*, FR-INT-001…004 |
| **Related** | [00-INDEX](00-INDEX.md) · [02-FRS](02-FRS.md) · [11-SECURITY-MODEL](11-SECURITY-MODEL.md) · [12-DASHBOARDS-AND-REPORTS](12-DASHBOARDS-AND-REPORTS.md) · [architecture/17-INTEGRATIONS](architecture/17-INTEGRATIONS.md) |

**Conventions:** No raw PHI/PII in AI logs or examples. Use feature names and synthetic ids (Member A, Case C-1001).

---

# Part A — AI Recommendation Framework

## A1. Principles

| Principle | Rule |
|---|---|
| Advisory only | AI never auto-executes high-risk pastoral, welfare, or finance actions (FR-GLO-005, FR-AI-005) |
| Human-in-the-loop | Accept / Edit / Reject with rationale logged (FR-AI-002) |
| Explainability | Every recommendation shows top drivers + confidence |
| Privacy-first | Feature vectors & redacted text only; no raw notes in logs (FR-AI-003) |
| Tenant isolation | No cross-tenant training by default; per-tenant feature flags (FR-AI-004) |
| Measurable | Track acceptance/override rates in ANA (FR-AI-006) |

---

## A2. Features by module

| Module | Feature | Description |
|---|---|---|
| **MEM** | Growth analysis | Trend of joins/exits/status transitions; campus/cell hotspots |
| **MEM** | Ministry suitability | Suggest ministries from skills/talents/availability (non-binding) |
| **MEM** | Engagement score | Composite 0–100 from attendance, giving participation flag (not amounts to non-finance models), COM response, roster fulfilment |
| **VIS** | Attendance prediction | Likelihood Visitor B attends next N services |
| **VIS** | Visitor conversion probability | Score + stage-appropriate next action |
| **COUN** | Counselling risk assist | Risk band suggestion from structured fields only—not from note free text unless explicitly redacted & consented policy |
| **PRAY** | Prayer generation + scripture | Draft prayer text + scripture refs; **must** be approved before send |
| **WEL / WCE** | Welfare eligibility assist | Flag missing docs / eligibility gaps; WCE weight/outlier hints |
| **ROST / SLOT** | Roster fairness | Balance load, avoid burnout, respect skills & blackouts |
| **FIN** | Anomaly detection | Unusual posting patterns, duplicate receipts, FX outliers |
| **FIN** | Forecast | Tithes/offerings trajectory under base/optimistic/pessimistic scenarios |
| **COM / ANA** | Content & insight assist | Subject lines, devotion outlines, dashboard narrative (no confidential dumps) |

---

## A3. Model I/O contract

### A3.1 Inputs (features only — examples)

| Domain | Allowed feature examples | Forbidden in logs / default prompts |
|---|---|---|
| Membership | tenure_days, status_code, campus_id, cell_size_bucket, skills_embedding_id | Full name, phone, email, address, photo bytes |
| Visitor | visits_count, days_since_first, source_channel, sla_breach_count | Free-text counsellor notes |
| Counselling | category_code, risk_band_current, session_count, days_open | Confidential note body, attachments |
| Prayer | urgency_code, category_code, escalation_level | Confidential prayer body (unless redacted draft mode with ACL) |
| Welfare | need_category, amount_bucket, doc_completeness_%, prior_aid_count | Narrative free text in training logs |
| Finance | fund_id, amount_zscore, weekday, campus_id, currency | Raw donor identity in shared model traces |
| Roster | hours_served_30d, skill_tags, decline_rate | Private contact channels |

All inference requests carry `tenant_id`, `correlation_id`, `model_version`, `feature_schema_version`.

### A3.2 Outputs

| Field | Description |
|---|---|
| `recommendation_id` | Stable id for audit |
| `type` | Enum per feature |
| `payload` | Structured suggestion (scores, ids, draft text ref) |
| `confidence` | 0.0–1.0 |
| `explanations[]` | Human-readable drivers (feature names + direction) |
| `safety_flags[]` | e.g., `REQUIRES_HUMAN_APPROVAL`, `LOW_CONFIDENCE` |
| `model_version` | Traceability |

### A3.3 Confidence policy

| Band | UI | Default behaviour |
|---|---|---|
| ≥ 0.80 | Green | Suggest accept with review |
| 0.50–0.79 | Amber | Edit recommended |
| < 0.50 | Grey | Show as weak signal; no one-click apply |

---

## A4. Human-in-the-loop & explainability

```
Suggest → Review (rationale + confidence) → Accept | Edit | Reject → Persist decision → ANA metrics
```

| Action | Audit |
|---|---|
| Accept | Store recommendation_id + actor |
| Edit | Store diff hash (not full confidential text in AUD message) |
| Reject | Optional reason code |

**Explainability UX:** “Why this score?” panel lists top 3–5 drivers (e.g., `sla_breach_count ↑`, `visits_count ↑`). No raw feature dump of PII.

**Safety:** Auto-send of AI pastoral/prayer/COM content is **blocked** until human approval (FR-AI-005).

---

## A5. Copilot UX patterns

| Pattern | Where | Behaviour |
|---|---|---|
| Side panel Copilot | MEM, VIS, WEL, FIN, ANA | Context-aware chips; insert into form fields |
| Inline suggest | Roster builder, visitor next-action | Ghost text / “Apply suggestion” |
| Draft & approve | Prayer, devotion, WhatsApp template | Diff view; Approve & Send |
| Risk ribbon | COUN case header | Suggested risk band; counsellor confirms |
| Anomaly toast | FIN | Link to voucher; FM investigates |
| Comparison assist | WCE | Highlight score outliers; weight tweak proposal |
| Empty-state coach | New campus setup | Checklist—not generative overreach |

Copilot entry points per FR-AI-001; disabled when tenant feature flag off.

---

## A6. Data privacy for AI

| Control | Requirement |
|---|---|
| Redaction | PII detectors strip names, phones, emails, addresses before LLM prompts; structured ids retained |
| Tenant isolation | Inference keyed by tenant; caches partitioned; no shared prompt logs across tenants |
| Training | **No cross-tenant training by default**; opt-in contract + DPIA for any fine-tune |
| Retention | Prompt/response stores minimized TTL; exclude COUN note bodies by default |
| Access | Model ops cannot read tenant prompts without break-glass dual control |
| Evaluation | Offline eval sets use synthetic or heavily anonymized data |
| Grounding | Scripture/prayer assist uses approved corpus + citation; no invention unmarked |

---

# Part B — Notification Framework

## B1. Channels

| Channel | Provider abstraction | Typical use |
|---|---|---|
| **Email** | M365 Graph / SMTP | Receipts, digests, exports, formal notices |
| **WhatsApp** | WhatsApp Business API | Templates, reminders, devotion snippets |
| **SMS** | SMS gateway | Time-critical short alerts (**no confidential bodies**) |
| **Push** | APNs / FCM | Mobile reminders, roster changes |
| **In-app / Portal** | CMS inbox | Persistent history, deep links |

All channels respect consent + preference center (FR-GLO-004).

---

## B2. Notification types

| Type | Channels (typical) | Priority |
|---|---|---|
| Event reminders | Push, WhatsApp, Email, SMS | Normal |
| Daily Devotions | WhatsApp, Email, Push, In-app | Normal |
| Emergency Alerts | SMS, Push, WhatsApp, In-app (Email secondary) | Critical |
| Counselling Follow-Ups | Push, Email, In-app (SMS: time only) | High |
| Welfare Updates | Email, In-app, WhatsApp template | High |
| Prayer Requests | In-app, Email, WhatsApp (respect confidential) | Normal/High |
| Roster assignments | Push, Email, WhatsApp, In-app | Normal |

---

## B3. Delivery modes

| Mode | Behaviour |
|---|---|
| **Immediate** | Queue → send as soon as policy allows (bypass quiet hours only if Critical + policy) |
| **Scheduled** | Send at `scheduled_at` tenant timezone |
| **Recurring** | Cron-like (e.g., daily devotion 06:00); skip on unsubscribe |

Idempotency keys prevent duplicate sends on worker retry.

---

## B4. Templates

| Attribute | Rule |
|---|---|
| Template id | Per channel + locale + tenant override |
| Variables | Whitelisted tokens (`{{first_name}}`, `{{event_time}}`, `{{campus_name}}`) |
| Forbidden tokens | Confidential note fields, full giving amounts on SMS/WhatsApp unless FIN policy + channel allows Email |
| Approval | New WhatsApp templates follow Meta approval; COM content may need Pastor approve |
| Versioning | Immutable published versions; AUD on publish |

---

## B5. Preference center

| Setting | Options |
|---|---|
| Per-channel opt-in/out | Email, WhatsApp, SMS, Push |
| Per-type | Devotions, Events, Welfare, Prayer digests, Marketing |
| Quiet hours | e.g., 21:00–07:00 local; Critical may override per tenant policy |
| Digest vs instant | Daily/weekly digest bundling |
| Language / campus | Locale pack |

Member A manages own prefs in portal; AD can view compliance snapshot (RPT-COM-002)—not impersonate send without audit.

---

## B6. Quiet hours, failover, receipts

### Quiet hours

- Non-critical scheduled into next open window.
- Emergency Alerts: allowed if `priority=Critical` and role authorized.

### Failover channel

```
Primary fail (hard bounce / WhatsApp undeliverable)
  → Secondary per type matrix (e.g., WhatsApp → SMS → Email → In-app)
  → Stop when delivered or channels exhausted
  → Record failover_used on DASH-COM
```

### Delivery receipts

| Signal | Store |
|---|---|
| Accepted by provider | `accepted` |
| Delivered / read (if offered) | `delivered` / `read` |
| Failed | `failed` + provider code (no PII in error detail logs) |

DASH-COM KPIs consume these aggregates.

---

## B7. Media rules (50 MB)

| Rule | Detail |
|---|---|
| Max attachment / media size | **50 MB** per message payload (platform cap) |
| **Email** | **Images and PDF only**; **no MP4** (or other video containers) |
| WhatsApp / SMS | Provider limits apply (often much lower); reject oversize at compose |
| Push | No large binaries; deep link to portal/Blob |
| Virus scan | All uploads scanned before send |
| Confidential | Attachments follow FLS; no counselling note exports via blast COM |

---

## B8. Pipeline architecture (logical)

```
Domain event → Notification policy engine (consent, quiet hours, role)
  → Template render (redaction)
  → Channel router (+ failover)
  → Provider adapter (secrets from Key Vault)
  → Receipt webhook → status store → optional analytics
```

Workers are async ([architecture/15-SCALABILITY](architecture/15-SCALABILITY.md)); Circuit breakers per FR-INT-009.

---

## B9. Security & compliance hooks

- No confidential COUN/PRAY bodies on SMS.
- Emergency blast requires privileged role + optional dual approval.
- Retention of message content minimized; metadata retained for AUD.
- Integration credentials only via Key Vault ([11-SECURITY-MODEL](11-SECURITY-MODEL.md)).

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial AI + Notification frameworks |

**Related:** [11-SECURITY-MODEL](11-SECURITY-MODEL.md) · [12-DASHBOARDS-AND-REPORTS](12-DASHBOARDS-AND-REPORTS.md) · [architecture/16-DEPLOYMENT](architecture/16-DEPLOYMENT.md) · [architecture/17-INTEGRATIONS](architecture/17-INTEGRATIONS.md)
