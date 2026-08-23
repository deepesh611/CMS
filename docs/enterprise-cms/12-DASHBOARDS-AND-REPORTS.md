# 12 — Dashboards and Reports

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 12 — Dashboards and Reports |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related FRs** | FR-ANA-*, FR-WCE-001…014, FR-WCE-020, FR-SEC-005 |
| **Related** | [00-INDEX](00-INDEX.md) · [02-FRS](02-FRS.md) · [11-SECURITY-MODEL](11-SECURITY-MODEL.md) · [architecture/15-SCALABILITY](architecture/15-SCALABILITY.md) · [architecture/17-INTEGRATIONS](architecture/17-INTEGRATIONS.md) |

**Conventions:** Example figures are synthetic. Persons as Member A, Visitor B, Case C-1001. No real PII.

---

## 1. Purpose

Define executive and operational dashboard layouts (KPI cards, charts, filters, drill-downs) and the report catalogue (id, audience, parameters, format, frequency, sensitivity), including the **Welfare Comparison Engine** executive view.

**Global filters (all dashboards unless noted)**

| Filter | Values |
|---|---|
| Campus | All / Campus-01…N (scoped by role) |
| Date range | Presets: Today, 7d, 30d, Quarter, YTD, Custom |
| Care cell | All / cell list (MEM/VIS/WEL/PRAY scoped) |
| Ministry | Optional where relevant |
| Currency | FIN/WEL amounts (tenant base + display FX) |

**Access:** Widget visibility follows [11-SECURITY-MODEL](11-SECURITY-MODEL.md). Sensitive cards (giving amounts, counselling risk detail) respect FLS.

**Performance:** Dashboards read from CQRS read models / materialized views ([architecture/15-SCALABILITY](architecture/15-SCALABILITY.md)); exports async above row thresholds.

---

## 2. Dashboard designs

### 2.1 Membership (`DASH-MEM`)

| Element | Specification |
|---|---|
| **Audience** | Senior Pastor, Pastor, Care Cell Leader, Administrator |
| **KPI cards** | Total active members · New this period · Inactive/suspended · Families · Baptisms YTD · Avg attendance rate (linked) |
| **Charts** | Membership status stack (Prospect→Active…) · Growth line (net adds) · Age/gender pyramid (aggregated) · Care cell size bar · Campus comparison |
| **Tables** | Recent registrations · Pending verifications · Transfers in/out |
| **Drill-downs** | KPI → filtered member list → Member A profile (no bulk PII export without E) |
| **Actions** | Export RPT-MEM-001/002 · Assign care cell bulk (if permitted) |

### 2.2 Visitors (`DASH-VIS`)

| Element | Specification |
|---|---|
| **Audience** | Care Cell Leader, Pastor, Visitor Team Volunteer, Senior Pastor |
| **KPI cards** | New visitors · Follow-up SLA % (Day 1/3/7/14/30) · Overdue tasks · Conversion rate · Pipeline by stage |
| **Charts** | Funnel (First visit → Contacted → Returning → Converted) · Source channel pie · Campus heatmap by week · SLA burndown |
| **Tables** | Overdue follow-ups · Upcoming Day-N tasks · Conversion candidates (AI score optional) |
| **Drill-downs** | Stage bar → visitor list → Visitor B timeline |
| **Actions** | Create follow-up · Convert to member · Export RPT-VIS-001 |

### 2.3 Care Cells (`DASH-CELL`)

| Element | Specification |
|---|---|
| **Audience** | Care Cell Leader, Pastor, Senior Pastor |
| **KPI cards** | Active cells · Avg cell size · Weekly attendance % · Members without cell · Welfare requests from cells |
| **Charts** | Attendance trend per cell · Health score distribution · Leader span-of-care · Geographic/campus map (aggregated) |
| **Tables** | Cells below attendance threshold · Unassigned members · Leader vacancies |
| **Drill-downs** | Cell row → roster + recent attendance · Member A card |
| **Actions** | Export RPT-CELL-001 · Open roster |

### 2.4 Prayer (`DASH-PRAY`)

| Element | Specification |
|---|---|
| **Audience** | Pastor, Senior Pastor, Prayer team leads |
| **KPI cards** | Open requests · Confidential count (count only) · Escalated · Avg resolution days · Answered/closed this period |
| **Charts** | Volume by category · Urgency mix · Escalation path funnel · Campus load |
| **Tables** | High urgency queue · Escalations awaiting Pastor/SP · Aging > N days |
| **Drill-downs** | Queue → request detail (**confidential body only if FLS allows**) |
| **Actions** | Assign intercessor · Escalate · Export RPT-PRAY-001 (redacted default) |

### 2.5 Counselling (`DASH-COUN`)

| Element | Specification |
|---|---|
| **Audience** | Counsellor (own caseload), Senior Pastor, Pastor (policy) |
| **KPI cards** | Open cases · High risk count · Sessions this period · Avg case age · Follow-ups due |
| **Charts** | Cases by category · Risk band trend · Counsellor caseload (anonymized labels for SP) · Closure rate |
| **Tables** | High-risk cases · Sessions due today · Unassigned cases |
| **Drill-downs** | Case C-1001 shell → notes only if authorized |
| **Actions** | Schedule session · Export RPT-COUN-001 (**metadata only** for AU; no note bodies) |
| **Hard rule** | No note text, attachment names with PHI, or free-text snippets on dashboard tiles |

### 2.6 Welfare (`DASH-WEL`)

| Element | Specification |
|---|---|
| **Audience** | Welfare Team, Pastor, Senior Pastor, Finance Manager |
| **KPI cards** | Open requests · Pending approval · Approved amount (period) · Disbursed · Avg cycle time · Budget remaining (Welfare Fund) |
| **Charts** | Request→Assess→Approve→Assist funnel · Amount by need category · Campus comparison · Aging buckets |
| **Tables** | Awaiting assessment · Dual-control disbursements · Follow-up reviews due |
| **Drill-downs** | Request → case file → linked FIN voucher (if any) |
| **Actions** | Open WCE · Approve · Export RPT-WEL-001/002 |

### 2.7 Finance (`DASH-FIN`)

| Element | Specification |
|---|---|
| **Audience** | Finance Manager, Treasurer, Senior Pastor, Auditor |
| **KPI cards** | Tithes/offerings (period) · Donations · Welfare fund balance · Budget vs actual % · Unreconciled bank items · Tally sync success % |
| **Charts** | Income by fund · Multi-currency stacked (base currency) · Trend vs prior year · Expense by ministry · Anomaly flags (AI optional) |
| **Tables** | Recent receipts · Failed Tally posts · Pending approvals |
| **Drill-downs** | Fund → ledger lines (**amounts FLS**) · Voucher detail |
| **Actions** | Export RPT-FIN-* · Trigger Tally retry · Power BI |

### 2.8 Communication (`DASH-COM`)

| Element | Specification |
|---|---|
| **Audience** | Ministry Leader, Administrator, Pastor, Care Cell Leader |
| **KPI cards** | Messages sent · Delivery success % · Open/read rate (where available) · Quiet-hour suppressed · Failover used · Unsubscribed |
| **Charts** | Channel mix (Email/WhatsApp/SMS/Push/In-app) · Template performance · Bounce/failure reasons · Campaign timeline |
| **Tables** | Failed deliveries · Pending approvals (AI content) · Preference opt-outs |
| **Drill-downs** | Campaign → recipient cohorts (aggregated) → message status (no body dump for confidential) |
| **Actions** | Export RPT-COM-001 · Retry failed · Open preference analytics |

### 2.9 Events (`DASH-EVT`)

| Element | Specification |
|---|---|
| **Audience** | Ministry Leader, Pastor, Administrator, Elder |
| **KPI cards** | Upcoming events · Registrations · Capacity % · Check-in rate · No-shows · Linked ceremonies/slots |
| **Charts** | Registration vs capacity · Attendance by campus · Series trend · Roster coverage for event roles |
| **Tables** | Events this week · Waitlists · Slot conflicts |
| **Drill-downs** | Event → attendees (scoped) → Member A check-in |
| **Actions** | Export RPT-EVT-001 · Sync M365 calendar · Notify registrants |

---

## 3. Shared UX patterns

| Pattern | Rule |
|---|---|
| KPI card | Value, delta vs prior period, sparkline optional, click → drill list |
| Empty state | Clear CTA; never fabricate sample PII |
| Refresh | Auto 5–15 min for ops; manual refresh; “as of” timestamp |
| Export | Respect E permission; async email/portal link; AUD entry |
| Mobile | KPI strip + one primary chart; tables as cards |
| Accessibility | Colour + pattern; not colour-only risk indicators |

---

## 4. Report catalogue

**Sensitivity:** `Public` · `Internal` · `Confidential` · `Restricted` (counselling/finance line-level)

| Report ID | Name | Audience | Parameters | Format | Frequency | Sensitivity |
|---|---|---|---|---|---|---|
| RPT-MEM-001 | Membership register | AD, SP, PA, CCL\* | Campus, status, care cell, date | Excel, PDF | On-demand / Monthly | Internal |
| RPT-MEM-002 | Membership growth summary | SP, PA, AD | Campus, date range | PDF, Power BI | Weekly | Internal |
| RPT-MEM-003 | Baptism & transfer log | PA, SP, AD, EL | Campus, date | Excel, PDF | Monthly | Internal |
| RPT-VIS-001 | Visitor pipeline & SLA | CCL, PA, SP, VO\* | Campus, cell, date, stage | Excel, PDF | Daily / Weekly | Internal |
| RPT-VIS-002 | Conversion cohort | SP, PA, AD | Campus, cohort month | Excel, Power BI | Monthly | Internal |
| RPT-CELL-001 | Care cell health | CCL, PA, SP | Campus, cell | PDF, Excel | Weekly | Internal |
| RPT-CELL-002 | Unassigned members | AD, PA, CCL | Campus | Excel | Weekly | Internal |
| RPT-PRAY-001 | Prayer activity (redacted) | PA, SP, prayer leads | Campus, urgency, date | PDF, Excel | Weekly | Confidential |
| RPT-PRAY-002 | Escalation audit | SP, AU | Date | Excel | Monthly | Restricted |
| RPT-COUN-001 | Caseload metadata | CO\*, SP, AU | Counsellor, risk, date | Excel, PDF | Weekly | Restricted |
| RPT-COUN-002 | Session attendance (no notes) | CO\*, SP | Date, counsellor | PDF | Monthly | Confidential |
| RPT-WEL-001 | Welfare request register | WT, PA, SP, FM | Campus, status, date | Excel, PDF | Weekly | Confidential |
| RPT-WEL-002 | Disbursement & fund usage | WT, FM, TR, SP, AU | Fund, currency, date | Excel, PDF, Power BI | Monthly | Restricted |
| RPT-WCE-001 | Comparison session pack | WT, SP, FM | Session id | PDF, Power BI | On-demand | Confidential |
| RPT-CER-001 | Ceremony pipeline | EL, PA, SP, AD | Type, status, date | Excel, PDF | Monthly | Internal |
| RPT-SLOT-001 | Service slot utilisation | PA, AD, ML | Campus, date | Excel, Power BI | Weekly | Internal |
| RPT-ROST-001 | Roster coverage & fairness | ML, PA, CCL | Ministry, date | Excel, PDF | Weekly | Internal |
| RPT-COM-001 | Channel delivery summary | AD, ML, PA | Channel, campaign, date | Excel, Power BI | Weekly | Internal |
| RPT-COM-002 | Consent & preference snapshot | AD, AU | Campus | Excel | Monthly | Internal |
| RPT-FIN-001 | Receipts & offerings | FM, TR, SP, AU | Fund, currency, date, campus | Excel, PDF | Daily / Monthly | Restricted |
| RPT-FIN-002 | Budget vs actual | FM, TR, SP | Cost centre, date | Excel, Power BI | Monthly | Confidential |
| RPT-FIN-003 | Bank reconciliation | FM, TR, AU | Account, date | Excel, PDF | Monthly | Restricted |
| RPT-FIN-004 | Tally sync exception | FM, AD | Date, status | Excel | Daily | Internal |
| RPT-EVT-001 | Event attendance | ML, PA, AD | Event, campus | Excel, PDF | Per event | Internal |
| RPT-ANA-001 | Executive pack | SP, PA, FM | Campus, date | PDF, Power BI | Weekly | Confidential |
| RPT-AUD-001 | Security & access audit | AU, AD, SP | Date, actor, action | Excel | On-demand / Monthly | Restricted |
| RPT-GDPR-001 | Erasure / access request log | AD, AU | Date, status | Excel, PDF | On-demand | Restricted |

\* Scoped to assignment/campus.

---

## 5. Welfare Comparison Engine — executive view (`DASH-WCE`)

Aligns with **FR-WCE-001…014, FR-WCE-020**.

### 5.1 Purpose

Enable Welfare Team / Senior Pastor / Finance Manager to compare **up to five** welfare cases side-by-side with transparent weighted scoring and an auditable decision.

### 5.2 Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Filters: Campus | Date | Fund | Session status                    │
├──────────────┬──────────────┬──────────────┬──────────────┬─────┤
│ Case C-1001  │ Case C-1002  │ Case C-1003  │ Case C-1004  │ …   │
│ (select ≤5)  │              │              │              │     │
├──────────────┴──────────────┴──────────────┴──────────────┴─────┤
│ KPI strip: Cases in session | Avg score | Budget headroom | SLA │
├─────────────────────────────┬───────────────────────────────────┤
│ Category score matrix A–I   │ Ranking board (weighted total)    │
│ (heatmap / table)           │ 1…5 with delta vs mean            │
├─────────────────────────────┼───────────────────────────────────┤
│ Radar / spider (≤5 series)  │ Grouped bar by category           │
├─────────────────────────────┴───────────────────────────────────┤
│ Weight editor (sum=100%) · Decision panel · Audit trail snippet │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Categories A–I (exact)

| Code | Category |
|---|---|
| **A** | Eligibility |
| **B** | Documentation |
| **C** | Financial Assessment |
| **D** | Risk Assessment |
| **E** | Impact Assessment |
| **F** | Operational Feasibility |
| **G** | Management Review |
| **H** | Budget Availability |
| **I** | Recommendation |

Each category scored on a tenant scale (e.g., 0–10). **Weights** are tenant-configurable and **must sum to 100%**.

### 5.4 Scoring & ranking

| Step | Behaviour |
|---|---|
| Input | Assessors enter/adjust category scores per case |
| Compute | `weighted_total = Σ (score_c × weight_c)` |
| Rank | Descending weighted_total; ties broken by policy (e.g., urgency, then case age) |
| Persist | Session id, case set, weights, scores, actors, final decision → AUD (FR-WCE-020) |
| AI assist | Optional outlier/weight hints; human confirms ([13-AI-AND-NOTIFICATIONS](13-AI-AND-NOTIFICATIONS.md)) |

### 5.5 Charts

| Chart | Use |
|---|---|
| Radar/spider | Shape of strengths/gaps across A–I per case |
| Grouped bar | Category-by-category comparison |
| Ranking bar | Weighted totals 1…5 |
| Budget gauge | Fund availability vs requested amounts (aggregated) |

### 5.6 Export

| Output | Content rules |
|---|---|
| PDF session pack (RPT-WCE-001) | Scores, weights, ranks, decision rationale; narratives redacted by default |
| Power BI dataset | Structured measures + category scores; **no confidential free-text dumps by default** (FR-WCE-014) |
| Excel | Same as Power BI tabular; Restricted sensitivity |

### 5.7 Permissions

| Action | Roles |
|---|---|
| Create/edit session | Welfare Team |
| View executive widgets | WT, SP, FM, AU (read) |
| Finalize decision | WT + Pastor/SP approval per policy |
| Export | Roles with E on WCE |

---

## 6. Power BI & async export

| Topic | Standard |
|---|---|
| Datasets | Membership growth, Visitor funnel, Welfare/WCE, Finance summary, COM delivery, Executive pack |
| Gateway | Service principal; tenant-isolated workspaces |
| Refresh | Scheduled + on-demand; respect quiet hours for push notifications of completion |
| Row-level | Power BI RLS mirrors campus/role where published |
| Large exports | Queue → Blob SAS (short TTL) → notify actor; AUD with row count only |

---

## 7. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial dashboards + report catalogue + WCE executive view |

**Related:** [11-SECURITY-MODEL](11-SECURITY-MODEL.md) · [13-AI-AND-NOTIFICATIONS](13-AI-AND-NOTIFICATIONS.md) · [architecture/17-INTEGRATIONS](architecture/17-INTEGRATIONS.md)
