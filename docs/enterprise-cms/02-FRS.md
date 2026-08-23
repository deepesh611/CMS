# Functional Requirements Specification (FRS)

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 02 — Functional Requirements Specification |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline |
| **Related** | [00-INDEX](00-INDEX.md) · [01-BRS](01-BRS.md) · [03-USE-CASES](03-USE-CASES.md) · [05-USER-STORIES](05-USER-STORIES.md) |

**Priority legend:** M = Must (MVP) · S = Should (Phase 2) · C = Could (Phase 3)  
**Each FR:** ID | Statement | Priority | Notes

---

## Global rules (apply to all modules)

| ID | Requirement | P |
|---|---|---|
| FR-GLO-001 | Every record is scoped to `tenant_id`; optional `campus_id` where campus-scoped. | M |
| FR-GLO-002 | All mutating actions write an audit event (actor, action, entity, timestamp, correlation id). Never log PII/PHI field values. | M |
| FR-GLO-003 | Soft-delete with restore where legally allowed; hard-delete only via retention/erasure workflow. | M |
| FR-GLO-004 | Notifications respect channel preferences, consent, and quiet hours. | M |
| FR-GLO-005 | AI outputs are advisory; high-risk actions require human confirmation. | M |
| FR-GLO-006 | APIs are versioned; web and mobile use the same contracts. | M |

---

## Module 1 — Membership Management

### Registration & profile

| ID | Requirement | P |
|---|---|---|
| FR-MEM-001 | System shall create members with: Membership ID, Family ID, Full Name, Email, Mobile, DOB, Gender, Marital Status, Address, Profession, Care Cell, Ministries, Skills, Talents, Membership Status. | M |
| FR-MEM-002 | System shall generate unique Membership ID per tenant (configurable format). | M |
| FR-MEM-003 | System shall support Family Management: spouse link, unlimited children, shared Family ID. | M |
| FR-MEM-004 | System shall validate email/mobile uniqueness rules per tenant policy (warn vs block). | M |
| FR-MEM-005 | System shall store profile photo and documents via pluggable object storage. | M |
| FR-MEM-006 | Member self-registration via portal shall require campus selection and admin verification before Active status. | S |

### Lifecycle & status

| ID | Requirement | P |
|---|---|---|
| FR-MEM-010 | System shall support membership statuses: Prospect, In Class, Active, Inactive, Transferred Out, Transferred In, Suspended, Deceased (configurable labels). | M |
| FR-MEM-011 | Status transitions shall enforce allowed-state matrix and record reason + actor. | M |
| FR-MEM-012 | System shall track Baptism (date, campus, officiant, certificate). | M |
| FR-MEM-013 | System shall support Membership Transfer (in/out) with source/destination church/campus and effective date. | M |
| FR-MEM-014 | System shall manage Membership Classes (enrolment, attendance, completion → eligible for reception). | M |
| FR-MEM-015 | System shall link Marriage Records and Baby Dedications to member/family (see CER). | M |
| FR-MEM-016 | System shall support Member Classification tags (e.g., youth, senior, new believer) multi-select. | M |
| FR-MEM-017 | System shall record Church Functions participation history for the member. | S |

### Workflows

| ID | Requirement | P |
|---|---|---|
| FR-MEM-020 | New member workflow: Register → Verify → Assign Care Cell → Optional Class → Activate. | M |
| FR-MEM-021 | Transfer-out workflow: Request → Pastoral approve → Close local ministries/roster → Archive. | M |
| FR-MEM-022 | Deceased workflow: Mark status → Stop automated COM (except pastoral) → Retain per policy. | M |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-MEM-030 | AI shall provide Membership Growth Analysis by campus/period. | C |
| FR-MEM-031 | AI shall predict attendance risk / churn signals from engagement features. | C |
| FR-MEM-032 | AI shall recommend ministry suitability from skills/talents/history. | S |
| FR-MEM-033 | AI shall compute Engagement Score (explainable factors). | S |
| FR-MEM-040 | Notify Care Cell Leader on new member assignment (WhatsApp/Email/Push per prefs). | M |
| FR-MEM-041 | Birthday/anniversary greetings optional automation (COM). | S |

---

## Module 2 — Visitor Management

### Registration

| ID | Requirement | P |
|---|---|---|
| FR-VIS-001 | System shall register visitors with identity/contact fields and **Visitor Source** from exact enum: Friend, Church Member, Family Member, Care Cell Member, Pastor, Ministry Leader, Church Event, Outreach Program, Website, Facebook, Instagram, YouTube, WhatsApp, Google Search, Walk-In, Advertisement, Other. | M |
| FR-VIS-002 | When source requires a referrer (Friend, Church Member, Family Member, Care Cell Member, Pastor, Ministry Leader), system shall capture referrer link (member/user id). | M |
| FR-VIS-003 | System shall capture visit date, campus, service, interests, prayer needs flag (no note body in analytics). | M |
| FR-VIS-004 | Duplicate detection shall suggest merge candidates (mobile/email/name+DOB heuristics). | S |

### Lifecycle & pipeline

| ID | Requirement | P |
|---|---|---|
| FR-VIS-010 | Pipeline stages: New → Contacted → Engaged → Class Invited → Converted → Lost/Closed. | M |
| FR-VIS-011 | Convert Visitor → Member shall create/link member record and close visitor as Converted with audit. | M |
| FR-VIS-012 | Visitor Analytics shall report by source, campus, conversion rate, time-to-convert. | M |

### Follow-up workflow (mandatory schedule)

| ID | Requirement | P |
|---|---|---|
| FR-VIS-020 | On visitor create, system shall auto-create follow-up tasks for **Day 1, Day 3, Day 7, Day 14, Day 30** relative to first visit. | M |
| FR-VIS-021 | Each follow-up task shall assign owner (default Care Cell Leader or Visitor Team role) and due datetime. | M |
| FR-VIS-022 | Completing a task shall require outcome code + optional note; overdue tasks escalate per policy. | M |
| FR-VIS-023 | Follow-Up Plans shall be configurable templates but default days remain 1/3/7/14/30. | S |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-VIS-030 | AI Visitor Engagement Score. | S |
| FR-VIS-031 | AI Conversion Probability. | C |
| FR-VIS-032 | AI Follow-Up Recommendations (channel/message timing). | S |
| FR-VIS-033 | AI Pastoral Escalation when score/risk thresholds met. | S |
| FR-VIS-040 | Notify assignee on task create/due/overdue via Email/SMS/WhatsApp/Push. | M |

---

## Module 3 — Counselling Management

### Categories & risk

| ID | Requirement | P |
|---|---|---|
| FR-COUN-001 | Cases shall use categories: Marriage, Family, Youth, Addiction, Mental Health, Career, Grief, Trauma, Financial, Spiritual Care, Leadership Mentoring, Church Conflict. | M |
| FR-COUN-002 | Risk levels shall be exactly: **Low**, **Moderate**, **High**. | M |
| FR-COUN-003 | High risk shall trigger mandatory supervisor notification and tighter follow-up SLA. | M |

### Registration & case lifecycle

| ID | Requirement | P |
|---|---|---|
| FR-COUN-010 | Open case with counselee (member/visitor), category, risk, assigned counsellor, campus. | M |
| FR-COUN-011 | Session Management: schedule, attend, duration, session summary (confidential). | M |
| FR-COUN-012 | Follow-Up Scheduling linked to case with reminders. | M |
| FR-COUN-013 | Referral Management: internal (pastor/elder) or external agency flag + status (no clinical EHR). | S |
| FR-COUN-014 | Confidential Notes: encrypted at rest; readable only by assigned Counsellor and Senior Pastor (configurable). | M |
| FR-COUN-015 | Case statuses: Open, Active, On Hold, Referred, Closed. | M |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-COUN-030 | AI Risk Identification suggestions (counsellor confirms). | S |
| FR-COUN-031 | AI Referral Suggestions. | S |
| FR-COUN-032 | AI Follow-Up Predictions. | C |
| FR-COUN-040 | Notify counsellor/counselee (non-sensitive) for session reminders via preferred channels. | M |
| FR-COUN-041 | Never send confidential note content over SMS/WhatsApp. | M |

---

## Module 4 — Prayer Support Management

### Categories

| ID | Requirement | P |
|---|---|---|
| FR-PRAY-001 | Prayer categories shall be: Spiritual Growth, Healing, Family, Financial, Career, Education, Emotional Support, Church Growth, Ministry, Emergency, Special Needs. | M |

### Lifecycle & features

| ID | Requirement | P |
|---|---|---|
| FR-PRAY-010 | Submit prayer request (member/visitor/anonymous-to-team per policy) with category, confidentiality flag, urgency. | M |
| FR-PRAY-011 | Assign to Prayer Teams; track prayed status and follow-up. | M |
| FR-PRAY-012 | Support Testimonies linked to closed/answered requests. | S |
| FR-PRAY-013 | Escalation path: Team → Pastor → Senior Pastor for Emergency/High urgency. | M |
| FR-PRAY-014 | Confidential requests hidden from general prayer walls; team-only. | M |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-PRAY-030 | AI Prayer Generation (draft; human edit before share). | S |
| FR-PRAY-031 | AI Scripture Suggestions. | S |
| FR-PRAY-032 | AI Prayer Points extraction. | S |
| FR-PRAY-033 | AI Follow-Up Recommendations. | S |
| FR-PRAY-040 | Notify prayer team on assign; escalate Emergency immediately (Push/SMS/WhatsApp). | M |

---

## Module 5 — Welfare Management

### Requestors

| ID | Requirement | P |
|---|---|---|
| FR-WEL-001 | Only these requestor roles may create welfare requests: **Care Cell Leader**, **Associate Care Cell Leader**, **Counsellor**, **Ministry Leader**, **Pastor**. | M |

### Lifecycle

| ID | Requirement | P |
|---|---|---|
| FR-WEL-010 | Create Welfare Request linked to beneficiary (Member A), need type, amount/currency, narrative, supporting docs. | M |
| FR-WEL-011 | Approval Workflow: Submit → Case Assessment → Welfare Team Review → Pastoral/Finance approve (threshold matrix) → Disburse → Follow-Up Review. | M |
| FR-WEL-012 | Case Assessment captures household, income indicators, prior aid history (no raw bank passwords). | M |
| FR-WEL-013 | Welfare Assistance records disbursement method, fund source, voucher link (FIN). | M |
| FR-WEL-014 | Follow-Up Reviews at configurable intervals post-assistance. | S |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-WEL-030 | AI Eligibility Assessment score (explainable). | S |
| FR-WEL-031 | AI Risk Scoring (fraud/dependency signals). | S |
| FR-WEL-032 | AI Funding Impact Analysis. | C |
| FR-WEL-033 | AI Approval Recommendations (never auto-approve above threshold). | S |
| FR-WEL-040 | Notify requestor and approvers on state changes via Email/Push/WhatsApp. | M |

---

## Module 6 — Welfare Comparison Engine

### Comparison scope

| ID | Requirement | P |
|---|---|---|
| FR-WCE-001 | Users with permission shall compare **up to 5** welfare cases simultaneously. | S |
| FR-WCE-002 | Comparison categories shall be exactly: **A. Eligibility**, **B. Documentation**, **C. Financial Assessment**, **D. Risk Assessment**, **E. Impact Assessment**, **F. Operational Feasibility**, **G. Management Review**, **H. Budget Availability**, **I. Recommendation**. | S |

### Scoring & output

| ID | Requirement | P |
|---|---|---|
| FR-WCE-010 | Weighted scoring per category A–I; tenant-configurable weights summing to 100%. | S |
| FR-WCE-011 | Produce rankings and scorecards for selected cases. | S |
| FR-WCE-012 | Executive Dashboard widgets for comparison sessions. | S |
| FR-WCE-013 | Charts for category radar/bar comparisons. | S |
| FR-WCE-014 | Export comparison dataset to **Power BI** (no confidential free-text dumps by default). | S |
| FR-WCE-020 | Persist comparison session for audit (who compared which cases, weights, outcome decision). | S |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-WCE-030 | AI may suggest weight adjustments or highlight score outliers; human confirms. | C |
| FR-WCE-040 | Notify decision board when comparison finalized. | S |

---

## Module 7 — Church Ceremonies & Member Functions

### Ceremony catalogue

| ID | Requirement | P |
|---|---|---|
| FR-CER-001 | System shall support ceremonies: Baby Dedication, Baptism, Membership Reception, Thanksgiving, Wedding Anniversary, House Blessing, Marriage Banns, Wedding Service, Funeral Service, Memorial Service. | M |

### Baby Dedication

| ID | Requirement | P |
|---|---|---|
| FR-CER-010 | Capture: Child Name, Given Name, Date of Birth, Place of Birth, Father Name, Mother Name (placeholders in docs; live data access-controlled). | M |
| FR-CER-011 | Workflow: Care Cell Recommendation → Elder Review → Pastoral Approval → Scheduling → Certificate Generation. | M |
| FR-CER-012 | Scheduling may insert into Service Slot (SLOT). | M |

### Marriage Banns & weddings

| ID | Requirement | P |
|---|---|---|
| FR-CER-020 | Capture: Bride, Groom, Parents, Wedding Date, Venue, Counselling Status. | M |
| FR-CER-021 | Marriage Banns publication period with Objection Tracking. | S |
| FR-CER-022 | Wedding Scheduling + Certificate generation. | S |
| FR-CER-023 | Block wedding schedule if required counselling incomplete (configurable). | S |

### Other ceremonies & notifications

| ID | Requirement | P |
|---|---|---|
| FR-CER-030 | Baptism, Membership Reception, Thanksgiving, Anniversary, House Blessing, Funeral, Memorial: request → approve → schedule → certificate/record as applicable. | M/S |
| FR-CER-040 | Notify stakeholders on approval/schedule via Email/WhatsApp/Push. | M |

---

## Module 8 — Service Slot Management

### Services & slots

| ID | Requirement | P |
|---|---|---|
| FR-SLOT-001 | Supported services: **Friday Main Service**, **Sunday Main Service**, **Special Service**. | M |
| FR-SLOT-002 | Program slots: **Before Worship**, **After Worship**, **Before Sermon**, **After Sermon**, **During Announcements**, **Before Closing Prayer**. | M |
| FR-SLOT-003 | Users shall insert church functions/ceremonies into a service + program slot with duration and owner. | M |
| FR-SLOT-004 | System shall prevent double-booking conflicts for same service/slot/time. | M |
| FR-SLOT-005 | Publish agenda to COM channels / display screens feed. | S |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-SLOT-030 | AI Capacity Validation (time budget vs service length). | S |
| FR-SLOT-031 | AI Agenda Optimization suggestions. | C |
| FR-SLOT-032 | AI Conflict Detection across campuses/resources. | S |
| FR-SLOT-040 | Notify inserted function owners when agenda published or changed. | M |

---

## Module 9 — Church Activity Roster

### Coverage

| ID | Requirement | P |
|---|---|---|
| FR-ROST-001 | Roster shall support: Sermons, Counselling, Hospital Visits, Care Cell Meetings, Ministry Events, Worship Teams, Volunteers, Friday School. | M |
| FR-ROST-002 | Assign people/roles to dated activities with campus and location. | M |
| FR-ROST-003 | Capture availability and substitutions. | S |

### AI scheduler

| ID | Requirement | P |
|---|---|---|
| FR-ROST-030 | AI Rotation Engine for fair recurring assignments. | S |
| FR-ROST-031 | AI Conflict Detection (person double-booked). | M |
| FR-ROST-032 | AI Availability Matching. | S |
| FR-ROST-033 | AI Fair Assignment metrics (load balance). | S |

### Notifications

| ID | Requirement | P |
|---|---|---|
| FR-ROST-040 | On assign/change/remind: **Email**, **SMS**, **WhatsApp**, **Push Notification**. | M |

---

## Module 10 — Communication & Digital Engagement

### Channels & content

| ID | Requirement | P |
|---|---|---|
| FR-COM-001 | Channels: Email, WhatsApp, SMS, Mobile App (Push), Member Portal. | M |
| FR-COM-002 | Support content types: Flyers, Videos, Announcements, Events, Daily Devotions. | M |
| FR-COM-003 | File types allowed: PDF, JPG, JPEG, PNG, BMP, GIF, MP4. | M |
| FR-COM-004 | Maximum file size: **50 MB** per attachment. | M |
| FR-COM-005 | **Email special rule:** allow Images + PDF only; **disallow MP4**. | M |
| FR-COM-006 | Segment audiences by campus, care cell, ministry, status, custom lists. | M |
| FR-COM-007 | Store delivery logs (provider id, status) without message body PII where possible. | M |

### Daily Devotions

| ID | Requirement | P |
|---|---|---|
| FR-COM-010 | Generate/compose: Verse of the Day, Daily Prayer, Reflection, Devotional Article. | S |
| FR-COM-011 | Broadcast devotion to WhatsApp, Email, Mobile App, Member Portal. | S |

### Push notifications

| ID | Requirement | P |
|---|---|---|
| FR-COM-020 | Push types: Event Reminders, Daily Devotions, Emergency Alerts, Counselling Follow-Ups, Welfare Updates, Prayer Requests. | M |
| FR-COM-021 | Scheduling modes: Immediate, Scheduled, Recurring. | M |

### AI

| ID | Requirement | P |
|---|---|---|
| FR-COM-030 | AI assist for devotion drafts and announcement tone; human approve before send. | S |

---

## Module 11 — Finance Management

### Submodules

| ID | Requirement | P |
|---|---|---|
| FR-FIN-001 | Support: Donations, Tithes, Offerings, Welfare Funds, Mission Funds, Budgeting, Cash Management, Vendor Management, Recurring Expenses. | M |
| FR-FIN-002 | Recurring expense examples configurable: Friday Worship Hall Rental, Intercession Hall Rental, Friday School Rental, Women's Fellowship Rental, Men's Fellowship Rental, Utilities, Internet, Cleaning, Security. | M |
| FR-FIN-003 | Multi-currency: OMR, USD, EUR, GBP, AED, SAR, INR, QAR, KWD, BHD. | M |
| FR-FIN-004 | Currency conversion with rate date; exchange gain/loss posting. | S |
| FR-FIN-005 | Foreign Missions reporting by currency and project. | S |
| FR-FIN-006 | Segregation of duties: create vs approve payment above threshold. | M |

### Tally Prime

| ID | Requirement | P |
|---|---|---|
| FR-FIN-020 | Integrate with Tally Prime via XML/API: Ledger Synchronization, Receipt Vouchers, Payment Vouchers, Journal Entries, Bank Reconciliation. | S |
| FR-FIN-021 | Sync shall be idempotent with dead-letter/exception queue and manual resolve UI. | S |

### AI & notifications

| ID | Requirement | P |
|---|---|---|
| FR-FIN-030 | AI: Budget Forecasts, Cashflow Forecasts, Expense Analysis, Fund Utilization, Anomaly Detection. | C |
| FR-FIN-031 | Detect: Duplicate Payments, Overspending, Budget Overruns, Currency Risks, Vendor Risks. | S |
| FR-FIN-040 | Notify finance roles on anomalies, failed Tally sync, approval requests. | M |

---

## Module 12 — Analytics & Executive Dashboards

| ID | Requirement | P |
|---|---|---|
| FR-ANA-001 | Dashboards for: Membership, Visitors, Care Cells, Prayer, Counselling, Welfare, Finance, Communication, Events. | M |
| FR-ANA-002 | Filters: tenant (implicit), campus, date range, ministry. | M |
| FR-ANA-003 | Role-based widget visibility (e.g., finance widgets only for FIN roles). | M |
| FR-ANA-004 | Export aggregates to CSV/Excel/PDF; Power BI dataset export. | S |
| FR-ANA-010 | AI Insights Engine: Growth Trends, Attendance Trends, Giving Trends, Ministry Performance, Volunteer Participation, Welfare Demand, Counselling Trends. | C |
| FR-ANA-011 | Insights shall not expose confidential counselling note text. | M |
| FR-ANA-020 | Near-real-time KPI refresh via cache/events; heavy reports async. | S |

---

## Cross-cutting — Security (RBAC & compliance)

### Roles (system defaults)

| ID | Requirement | P |
|---|---|---|
| FR-SEC-001 | System roles shall include: Senior Pastor, Pastor, Elder, Counsellor, Care Cell Leader, Welfare Team, Ministry Leader, Finance Manager, Treasurer, Administrator, Auditor, Volunteer. | M |
| FR-SEC-002 | Implement RBAC: role → permission → module/action; IT Admin editable matrix. | M |
| FR-SEC-003 | MFA (TOTP or IdP) required for privileged roles; optional for others per policy. | M |
| FR-SEC-004 | Audit Logs for auth, RBAC changes, data mutations, exports. | M |
| FR-SEC-005 | Field-Level Security for counselling notes, welfare narratives, sensitive finance. | M |
| FR-SEC-006 | Confidential Data Controls: encryption, masking in UI lists, no SMS of secrets. | M |
| FR-SEC-007 | GDPR-style: consent, retention, access/erasure workflows, DPIA hooks. | M |
| FR-SEC-008 | Session timeout, lockout after failed attempts, CSRF/CSP for web. | M |
| FR-SEC-009 | Associate Care Cell Leader may be a distinct role or Care Cell Leader subtype with WEL request rights (align with FR-WEL-001). | M |

---

## Cross-cutting — Integrations

| ID | Requirement | P |
|---|---|---|
| FR-INT-001 | WhatsApp Business API integration for outbound templates and status webhooks. | M |
| FR-INT-002 | Email via SMTP/M365 Graph as configured. | M |
| FR-INT-003 | SMS provider abstraction (e.g., Twilio) with log mode for non-prod. | M |
| FR-INT-004 | Mobile Push (APNs/FCM) with topic/user targeting. | M |
| FR-INT-005 | Tally Prime XML/API connector (see FR-FIN-020). | S |
| FR-INT-006 | Microsoft 365: SSO (OIDC), calendar sync for events/roster, optional mail send. | S |
| FR-INT-007 | Power BI export/connector for ANA/WCE datasets. | S |
| FR-INT-008 | Integration health dashboard: latency, error rate, last success. | S |
| FR-INT-009 | All outbound integrations use secrets from secure store; circuit breakers + retries. | M |

---

## Cross-cutting — AI Copilot

| ID | Requirement | P |
|---|---|---|
| FR-AI-001 | Copilot entry points in MEM, VIS, COUN, PRAY, WEL/WCE, SLOT, ROST, COM, FIN, ANA. | S |
| FR-AI-002 | Recommendations include rationale and confidence; user can accept/edit/reject (logged). | S |
| FR-AI-003 | Prompt/context scrubbing: exclude unnecessary PII; never train on tenant data without contract. | M |
| FR-AI-004 | Feature flags per tenant for each AI capability. | M |
| FR-AI-005 | Safety: block auto-send of AI pastoral content without human approval. | M |
| FR-AI-006 | Evaluate quality metrics (acceptance rate, override rate) in ANA. | C |

---

## Traceability summary

| Module | FR ranges | Epic |
|---|---|---|
| Membership | FR-MEM-001… | EPIC-01 |
| Visitors | FR-VIS-001… | EPIC-02 |
| Counselling | FR-COUN-001… | EPIC-03 |
| Prayer | FR-PRAY-001… | EPIC-04 |
| Welfare | FR-WEL-001… | EPIC-05 |
| WCE | FR-WCE-001… | EPIC-06 |
| Ceremonies | FR-CER-001… | EPIC-07 |
| Service Slots | FR-SLOT-001… | EPIC-08 |
| Roster | FR-ROST-001… | EPIC-09 |
| Communication | FR-COM-001… | EPIC-10 |
| Finance | FR-FIN-001… | EPIC-11 |
| Analytics | FR-ANA-001… | EPIC-12 |
| Security | FR-SEC-* | Cross |
| Integrations | FR-INT-* | Cross |
| AI | FR-AI-* | Cross |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial FRS baseline |
