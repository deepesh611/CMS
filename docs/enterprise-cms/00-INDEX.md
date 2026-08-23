# Enterprise Church Management System — Documentation Index

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | Master Index |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Development-ready |
| **Audience** | Product Owners, Engineers, Architects, QA, Security, Church Ops |
| **Scale target** | Multi-tenant, multi-campus, 100,000+ members |
| **Pack size** | ~12,000 lines across 33 files |

---

## 1. Purpose

Single entry point for the Enterprise CMS documentation pack: **20 deliverables**, **12 modules**, and cross-cutting architecture (security, integrations, AI, multi-tenancy, Azure deployment).

---

## 2. Quick start (by role)

| Role | Start here | Then read |
|---|---|---|
| Product Owner / BA | [01-BRS](01-BRS.md) → [05-USER-STORIES](05-USER-STORIES.md) | [02-FRS](02-FRS.md), [03-USE-CASES](03-USE-CASES.md) |
| Backend Engineer | [02-FRS](02-FRS.md) → [schemas/](schemas/) → [api/09-API-SPEC](api/09-API-SPEC.md) | [10-WORKFLOWS](10-WORKFLOWS-AND-AUTOMATION.md), [11-SECURITY](11-SECURITY-MODEL.md) |
| Frontend / Mobile | [ux/06-SCREENS-AND-NAV](ux/06-SCREENS-AND-NAV.md) → [modules/](modules/) | [13-AI-AND-NOTIFICATIONS](13-AI-AND-NOTIFICATIONS.md) |
| Data / Analytics | [12-DASHBOARDS-AND-REPORTS](12-DASHBOARDS-AND-REPORTS.md) | [08-ERD](08-ERD.md), Power BI section in integrations |
| Security / Compliance | [11-SECURITY-MODEL](11-SECURITY-MODEL.md) | BRS constraints, counselling/welfare FLS |
| DevOps / Platform | [16-DEPLOYMENT](architecture/16-DEPLOYMENT.md) | [15-SCALABILITY](architecture/15-SCALABILITY.md), [14-MULTI-TENANT](architecture/14-MULTI-TENANT.md) |
| Finance Ops | [M11-finance](modules/M11-finance.md) | Tally / multi-currency / [17-INTEGRATIONS](architecture/17-INTEGRATIONS.md) |

---

## 3. Twelve functional modules

| # | Module | Code | Spec |
|---|---|---|---|
| 1 | Membership Management | `MEM` | [M01-membership.md](modules/M01-membership.md) |
| 2 | Visitor Management | `VIS` | [M02-visitor.md](modules/M02-visitor.md) |
| 3 | Counselling Management | `COUN` | [M03-counselling.md](modules/M03-counselling.md) |
| 4 | Prayer Support Management | `PRAY` | [M04-prayer.md](modules/M04-prayer.md) |
| 5 | Welfare Management | `WEL` | [M05-welfare.md](modules/M05-welfare.md) |
| 6 | Welfare Comparison Engine | `WCE` | [M06-welfare-comparison.md](modules/M06-welfare-comparison.md) |
| 7 | Church Ceremonies & Member Functions | `CER` | [M07-ceremonies.md](modules/M07-ceremonies.md) |
| 8 | Service Slot Management | `SLOT` | [M08-service-slots.md](modules/M08-service-slots.md) |
| 9 | Church Activity Roster | `ROST` | [M09-activity-roster.md](modules/M09-activity-roster.md) |
| 10 | Communication & Digital Engagement | `COM` | [M10-communication.md](modules/M10-communication.md) |
| 11 | Finance Management | `FIN` | [M11-finance.md](modules/M11-finance.md) |
| 12 | Analytics & Executive Dashboards | `ANA` | [M12-analytics.md](modules/M12-analytics.md) |

Cross-cutting: [FRS SEC/INT/AI](02-FRS.md) · [Module Design Overview](04-MODULE-DESIGN.md)

---

## 4. Twenty deliverables (master catalogue)

| # | Deliverable | File | Status |
|---|---|---|---|
| 1 | Functional Requirements Specification (FRS) | [02-FRS.md](02-FRS.md) | v1.0 |
| 2 | Business Requirements Specification (BRS) | [01-BRS.md](01-BRS.md) | v1.0 |
| 3 | Use Cases | [03-USE-CASES.md](03-USE-CASES.md) | v1.0 |
| 4 | Module Design | [04-MODULE-DESIGN.md](04-MODULE-DESIGN.md) + [modules/](modules/) | v1.0 |
| 5 | User Stories | [05-USER-STORIES.md](05-USER-STORIES.md) | v1.0 |
| 6 | Screen Designs | [ux/06-SCREENS-AND-NAV.md](ux/06-SCREENS-AND-NAV.md) | v1.0 |
| 7 | Navigation Structure | [ux/06-SCREENS-AND-NAV.md](ux/06-SCREENS-AND-NAV.md) | v1.0 |
| 8 | Database Schema | [07-DATABASE-SCHEMA.md](07-DATABASE-SCHEMA.md) · [schemas/](schemas/) | v1.0 |
| 9 | Entity Relationship Diagram (ERD) | [08-ERD.md](08-ERD.md) | v1.0 |
| 10 | API Specifications | [api/09-API-SPEC.md](api/09-API-SPEC.md) | v1.0 |
| 11 | Workflow Diagrams | [10-WORKFLOWS-AND-AUTOMATION.md](10-WORKFLOWS-AND-AUTOMATION.md) | v1.0 |
| 12 | Automation Rules | [10-WORKFLOWS-AND-AUTOMATION.md](10-WORKFLOWS-AND-AUTOMATION.md) | v1.0 |
| 13 | Security Model | [11-SECURITY-MODEL.md](11-SECURITY-MODEL.md) | v1.0 |
| 14 | Dashboard Design | [12-DASHBOARDS-AND-REPORTS.md](12-DASHBOARDS-AND-REPORTS.md) | v1.0 |
| 15 | Report Catalogue | [12-DASHBOARDS-AND-REPORTS.md](12-DASHBOARDS-AND-REPORTS.md) | v1.0 |
| 16 | AI Recommendation Framework | [13-AI-AND-NOTIFICATIONS.md](13-AI-AND-NOTIFICATIONS.md) | v1.0 |
| 17 | Notification Framework | [13-AI-AND-NOTIFICATIONS.md](13-AI-AND-NOTIFICATIONS.md) | v1.0 |
| 18 | Multi-Tenant Architecture | [architecture/14-MULTI-TENANT.md](architecture/14-MULTI-TENANT.md) | v1.0 |
| 19 | Scalability Strategy | [architecture/15-SCALABILITY.md](architecture/15-SCALABILITY.md) | v1.0 |
| 20 | Deployment Architecture | [architecture/16-DEPLOYMENT.md](architecture/16-DEPLOYMENT.md) | v1.0 |

**Related:** [17-INTEGRATIONS.md](architecture/17-INTEGRATIONS.md) (WhatsApp, Email, SMS, Push, Tally Prime, M365, Power BI)

---

## 5. PostgreSQL DDL

| Script | Scope |
|---|---|
| [postgresql-core.sql](schemas/postgresql-core.sql) | Tenants, campuses, identity, members, families, visitors, care cells |
| [postgresql-pastoral-ops.sql](schemas/postgresql-pastoral-ops.sql) | Counselling, prayer, welfare, WCE, ceremonies, slots, roster, comms, notifications |
| [postgresql-finance-analytics.sql](schemas/postgresql-finance-analytics.sql) | Multi-currency finance, Tally sync, analytics, AI recommendations |

---

## 6. Implementation roadmap (summary)

| Phase | Focus |
|---|---|
| **MVP** | Membership, Visitors (+ Day 1/3/7/14/30), Care Cells, basic Comm (Email), RBAC + MFA, Finance core (tithes/offerings), Web app |
| **Phase 2** | Counselling, Prayer, Welfare + WCE, Ceremonies, Roster, WhatsApp/SMS/Push, Mobile apps, Tally Prime |
| **Phase 3** | AI Copilot suite, GraphQL, advanced analytics/Power BI, M365 deep sync, denomination multi-tenant scale |

---

## 7. Compliance note

Pastoral counselling notes, confidential prayer requests, welfare assessments, and giving records are **sensitive**. Treat as confidential with field-level security, audit logging, and no PHI/PII in application logs. Prefer encryption at rest (KMS), TLS in transit, and GDPR-style consent/export/erasure with finance/legal retention exceptions — see [11-SECURITY-MODEL](11-SECURITY-MODEL.md).

---

## 8. Document control

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-08-23 | Full baseline pack authored (BRS/FRS/UC/Stories/Modules/UX/Schema/ERD/API/Workflows/Security/Dashboards/AI/Tenant/Scale/Deploy/Integrations) |
