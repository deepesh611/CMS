# Business Requirements Specification (BRS)

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 01 — Business Requirements Specification |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Approved for design baseline |
| **Owner** | Product / Church Operations Leadership |
| **Related** | [00-INDEX](00-INDEX.md) · [02-FRS](02-FRS.md) · [03-USE-CASES](03-USE-CASES.md) · [05-USER-STORIES](05-USER-STORIES.md) |

---

## 1. Vision

Enable multi-campus, multi-tenant faith organizations to run membership, pastoral care, welfare, ceremonies, scheduling, communications, and finance on one secure, API-first platform—with WhatsApp/Email/SMS/Push reach, Tally Prime and Microsoft 365 connectivity, multi-currency accounting, and an AI Copilot that assists (never replaces) pastoral judgment.

**North star:** Every member, visitor, and ministry volunteer is known, cared for, and engaged—while leadership has trustworthy data, auditability, and operational control at 100k+ member scale.

---

## 2. Goals

### 2.1 Business goals

| ID | Goal | Measurable outcome |
|---|---|---|
| BG-01 | Unify church operations | Single system of record per tenant for people, care, money, and ministry activity |
| BG-02 | Accelerate visitor → member conversion | Structured Day 1/3/7/14/30 follow-up; pipeline visibility |
| BG-03 | Protect pastoral confidentiality | Role- and field-level access; immutable audit for sensitive modules |
| BG-04 | Fair, transparent welfare decisions | Request → assess → approve → assist; compare up to 5 cases (A–I) |
| BG-05 | Reliable multi-currency finance | Tithes/offerings/donations/funds with FX; Tally Prime sync |
| BG-06 | Omnichannel engagement | Devotions, alerts, events via Email/WhatsApp/SMS/Push/Portal |
| BG-07 | Executive insight | Real-time dashboards + Power BI export; AI trend/anomaly assist |
| BG-08 | Scale without fork | Multi-campus + multi-tenant isolation; 99.9% availability |

### 2.2 Product goals

- Web + iOS/Android clients on shared APIs (REST + GraphQL).
- Workflow automation for follow-ups, approvals, rostering, and finance vouchers.
- AI Copilot for recommendations, forecasts, scripture/prayer assist, roster optimization—human-in-the-loop.
- Azure-ready: containers, Kubernetes, Redis, PostgreSQL, CI/CD.

---

## 3. Stakeholders

| Stakeholder | Interest | Primary modules |
|---|---|---|
| Senior Pastor / Lead Pastor | Vision, confidentiality, pastoral escalation | COUN, PRAY, WEL, ANA, CER |
| Pastors / Elders | Approvals, ceremonies, care oversight | CER, SLOT, WEL, VIS |
| Counsellors | Case/session management; confidential notes | COUN |
| Care Cell Leaders / Associates | Visitors, welfare requests, cell health | VIS, WEL, MEM, ROST |
| Ministry Leaders | Rosters, volunteers, events | ROST, COM, MEM |
| Welfare Team | Assessment, assistance, comparison | WEL, WCE, FIN |
| Finance Manager / Treasurer | Ledgers, budgets, Tally, multi-currency | FIN, ANA |
| Administrator | Users, campuses, config, M365 | SEC, INT, all |
| Auditor | Immutable trails, segregation of duties | SEC, FIN, WEL |
| Volunteers | Self-service roster, limited COM | ROST, COM |
| Members (portal/app) | Profile, giving, prayer, events, devotion | MEM, COM, FIN, PRAY |
| IT / Platform | Tenancy, integrations, uptime | INT, SEC, deploy |
| Product Owner / BA | Roadmap, acceptance | All |

---

## 4. Success metrics (KPIs)

| KPI | Target (steady-state) | Notes |
|---|---|---|
| Member records under management | ≥ 100,000 / large tenant | Soft ceiling with horizontal scale plan |
| Availability (platform) | ≥ 99.9% monthly | Excludes planned windows |
| Visitor follow-up SLA adherence | ≥ 90% on Day 1/3/7/14/30 tasks | Auto-created + notified |
| Visitor → member conversion (tracked) | Baseline + uplift vs year-1 | Funnel in ANA |
| Counselling confidentiality incidents | 0 unauthorized disclosures | Audit + access reviews |
| Welfare decision cycle time | −30% vs manual process | Request → decision |
| Finance postings synced to Tally | ≥ 99% success within SLA | Retry + exception queue |
| Communication delivery success | ≥ 98% accepted by provider | Channel failover rules |
| MFA adoption (privileged roles) | 100% | Senior Pastor, Finance, Admin, Auditor |
| Audit completeness | 100% of mutating actions | Immutable store |
| AI recommendation acceptance rate | Tracked; advisory only | No auto-approve high-risk |

---

## 5. Business capabilities → modules 1–12

| Capability | Module | Business value |
|---|---|---|
| Member lifecycle, families, baptism, transfer, classes, classification | **1 Membership** | Single person/family registry; ministry fit |
| Visitor capture, sources, pipeline, automated follow-up | **2 Visitors** | Growth engine; conversion analytics |
| Christian counselling cases, sessions, risk, referrals | **3 Counselling** | Care quality + confidentiality |
| Prayer requests, teams, testimonies, escalations | **4 Prayer** | Pastoral prayer coverage |
| Welfare request → approve → assist → review | **5 Welfare** | Stewardship of aid |
| Side-by-side compare ≤5 cases (A–I scoring) | **6 Welfare Comparison** | Fair executive decisions |
| Baby dedication, baptism, banns, weddings, funerals, etc. | **7 Ceremonies** | Sacramental/admin lifecycle |
| Insert functions into Friday/Sunday/Special services | **8 Service Slots** | Orderly worship agendas |
| Sermons, visits, cells, worship, Friday School rostering | **9 Roster** | Fair scheduling + notify |
| Flyers, video, announcements, daily devotion, push | **10 Communication** | Omnichannel engagement |
| Donations, tithes, offerings, funds, vendors, FX, Tally | **11 Finance** | Trustworthy accounting |
| Membership/visitor/care/finance/exec dashboards + AI insights | **12 Analytics** | Decision support |

Cross-cutting capabilities: **RBAC/MFA/Audit**, **Integrations** (WhatsApp, Email, SMS, Push, Tally Prime, M365, Power BI), **AI Copilot**.

---

## 6. Non-functional requirements (business view)

| Area | Requirement |
|---|---|
| **Scale** | Support 100,000+ members per large tenant; multi-campus hierarchies; burst attendance/comms loads |
| **Multi-campus** | Campus-scoped data where appropriate; org-wide rollups for executives |
| **Multi-tenant** | Hard isolation of data, config, secrets, and jobs; no cross-tenant leakage |
| **Availability** | 99.9% monthly for core APIs and web; RPO/RTO defined in deployment architecture |
| **Performance** | Interactive list/search p95 &lt; 2s under design load; exports async when large |
| **Security** | RBAC, MFA, encryption in transit/at rest, field-level controls for counselling/welfare |
| **Auditability** | Who/what/when/where for creates, updates, deletes, exports, privilege changes |
| **Localization** | Multi-currency (see §7); date/time per campus TZ; content language extensible |
| **Accessibility** | WCAG 2.1 AA target for web portal |
| **Observability** | Structured logs (no PII/PHI), metrics, traces; integration health dashboards |

---

## 7. Constraints & compliance

### 7.1 Pastoral confidentiality

- Counselling notes and high-sensitivity prayer/welfare fields visible only to assigned roles (e.g., Counsellor + Senior Pastor policy).
- Break-glass access must be dual-controlled or fully audited with justification.
- Exports of confidential modules require elevated permission + watermark/audit.

### 7.2 GDPR-style privacy

- Lawful basis / consent capture for communications and data processing.
- Purpose limitation; retention schedules per data class.
- Data subject access, correction, and erasure/pseudonymization workflows (with legal hold exceptions).
- Privacy by design: minimize identifiers in analytics extracts.

### 7.3 Audit & segregation of duties

- Finance: initiator ≠ approver for thresholds; Auditor read-only on journals.
- All admin/RBAC changes audited.
- Immutable audit store; retention per tenant policy.

### 7.4 Multi-currency

Supported currencies (ISO):

| Code | Name |
|---|---|
| OMR | Omani Rial |
| USD | US Dollar |
| EUR | Euro |
| GBP | British Pound |
| AED | UAE Dirham |
| SAR | Saudi Riyal |
| INR | Indian Rupee |
| QAR | Qatari Riyal |
| KWD | Kuwaiti Dinar |
| BHD | Bahraini Dinar |

Features required: conversion rates, exchange gain/loss, foreign missions reporting, base currency per tenant/campus policy.

### 7.5 Other constraints

- No PHI/PII in application logs, support tickets, or documentation examples.
- Secrets via managed secret store / KMS; never hardcoded.
- Air-gapped / bridge patterns apply where organizational network policy requires (see platform standards).

---

## 8. Integrations (business requirements)

| Integration | Business need | Success criteria |
|---|---|---|
| **WhatsApp** | Devotions, follow-ups, roster, alerts | Opt-in; delivery receipts; template compliance |
| **Email** | Same + attachments (images/PDF only; no MP4) | Bounce handling; 50MB max attachment policy |
| **SMS** | Short alerts / MFA / reminders | Cost controls; quiet hours |
| **Push** | App: events, devotion, emergency, care updates | Immediate / scheduled / recurring |
| **Tally Prime** | Ledger sync; receipt/payment/journal vouchers; bank recon | Idempotent sync; exception queue |
| **Microsoft 365** | Mail/calendar/identity/files as configured | SSO optional; calendar sync for roster/events |
| **Power BI** | Executive analytics export | Secure dataset; no confidential note bodies |

Channel file rules (COM): max **50 MB**; types PDF/JPG/JPEG/PNG/BMP/GIF/MP4; **Email: images + PDF only (no MP4)**.

---

## 9. Out of scope (v1.0 baseline)

Explicitly out of scope for MVP / Phase 1 unless later chartered:

- Full EHR / clinical medical records systems.
- Denominational payroll HRIS replacement (basic volunteer tracking only).
- Cryptocurrency wallets / DeFi.
- Unattended fully autonomous AI pastoral decisions (AI is advisory).
- Public open registration without tenant admin controls.
- Real-time video streaming CDN product (MP4 attach/link only in COM).
- Custom hardware POS (online/manual giving capture first).

---

## 10. Phased roadmap

### MVP (Phase 1) — Core operations

- Tenancy + campuses + RBAC + MFA + audit baseline  
- Membership + Family + status lifecycle  
- Visitors + sources + Day 1/3/7/14/30 follow-up  
- Basic Prayer + Welfare request/approve  
- Ceremonies: Baby Dedication + Baptism + Membership Reception  
- Service slots (Friday/Sunday/Special)  
- Communication: Email + SMS + WhatsApp templates; Push skeleton  
- Finance: tithes/offerings/donations; single base currency + multi-currency capture  
- Analytics: membership, visitors, giving KPIs  
- REST APIs for mobile shell  

**Exit criteria:** Pilot campus live; SLA follow-up ≥80%; zero critical security findings open.

### Phase 2 — Care depth & finance enterprise

- Full Counselling (categories, risk, confidential notes, referrals)  
- Prayer teams, testimonies, escalations  
- Welfare Comparison Engine (≤5 cases, A–I)  
- Marriage Banns / Wedding / Funeral / Memorial workflows  
- Full Roster + AI conflict/fairness assist  
- Daily Devotions generator + multi-channel broadcast  
- Tally Prime vouchers + bank recon  
- M365 calendar/SSO (as licensed)  
- Power BI export  
- GraphQL + event bus  

### Phase 3 — Intelligence & scale

- Full AI Copilot suite (growth, conversion, risk, forecasts, anomalies)  
- Advanced multi-currency FX + foreign missions packs  
- Multi-region HA; advanced scalability (read replicas, sharding strategy)  
- Expanded automation rules library  
- Member portal self-service maturity  
- Cross-campus executive AI insights  

---

## 11. Assumptions & dependencies

| Assumption / dependency | Impact if wrong |
|---|---|
| Tenant provides WhatsApp Business / SMS provider accounts | Channels degrade to Email/Push only |
| Tally Prime company masters aligned with CMS chart of accounts | Sync exceptions rise |
| M365 tenant available for SSO/calendar | Fall back to local accounts |
| Leadership adopts Day 1–30 visitor discipline | Conversion KPIs miss |
| Legal counsel defines retention & consent texts per jurisdiction | Delay go-live |
| Azure subscription + K8s platform ready | Deploy path changes |

---

## 12. Risks (business)

| Risk | Mitigation |
|---|---|
| Confidential data misuse | Field-level ACL, MFA, audit, training |
| Channel spam / opt-out noncompliance | Consent registry; quiet hours; preference center |
| Finance/Tally mismatch | Reconciliation reports; dual review |
| AI hallucination in pastoral context | Human approve; no auto-send without review for sensitive |
| Over-customization per campus | Config over code; feature flags |
| Scale underestimation | Load tests; scalability strategy deliverable |

---

## 13. Acceptance (BRS-level)

BRS is accepted when:

1. Stakeholders confirm module map and phased roadmap.  
2. NFR targets (100k, multi-tenant/campus, 99.9%) endorsed.  
3. Integration list and currency list confirmed.  
4. Out-of-scope list agreed.  
5. Traceability established to [02-FRS](02-FRS.md) and [05-USER-STORIES](05-USER-STORIES.md).

---

## 14. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial BRS baseline |
