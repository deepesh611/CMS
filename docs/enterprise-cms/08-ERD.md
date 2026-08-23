# Entity Relationship Diagram (ERD)

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 08 — ERD |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Design baseline |
| **Related** | [07-DATABASE-SCHEMA](07-DATABASE-SCHEMA.md) · [schemas/](schemas/) · [api/09-API-SPEC](api/09-API-SPEC.md) |

> Placeholders only (`Member A`, `Visitor B`). No real PII.

---

## 1. Identity & tenancy

```mermaid
erDiagram
  TENANTS ||--o{ CAMPUSES : has
  TENANTS ||--o{ USERS : has
  TENANTS ||--o{ ROLES : has
  USERS ||--o{ USER_ROLES : assigned
  ROLES ||--o{ USER_ROLES : grants
  ROLES ||--o{ ROLE_PERMISSIONS : includes
  PERMISSIONS ||--o{ ROLE_PERMISSIONS : mapped
  CAMPUSES ||--o{ USER_ROLES : "optional scope"
  USERS }o--o| MEMBERS : "portal link"

  TENANTS {
    uuid id PK
    text code UK
    text name
    char primary_currency
  }
  CAMPUSES {
    uuid id PK
    uuid tenant_id FK
    text code
    text name
  }
  USERS {
    uuid id PK
    uuid tenant_id FK
    citext email
    uuid member_id FK
  }
  ROLES {
    uuid id PK
    uuid tenant_id FK
    text code
  }
  PERMISSIONS {
    uuid id PK
    text code UK
    text module
  }
  USER_ROLES {
    uuid id PK
    uuid user_id FK
    uuid role_id FK
    uuid campus_id FK
  }
  ROLE_PERMISSIONS {
    uuid id PK
    uuid role_id FK
    uuid permission_id FK
  }
  MEMBERS {
    uuid id PK
    uuid tenant_id FK
  }
```

**Cardinality**

| Relationship | Card. | Notes |
|---|---|---|
| Tenant → Campus | 1:N | ≥1 campus per tenant |
| Tenant → User | 1:N | Email unique per tenant |
| User → Role | N:M | Optional campus scope on assignment |
| Role → Permission | N:M | System + custom roles |
| User ↔ Member | 0..1:0..1 | Portal users may link one member |

---

## 2. Member / family / care cell

```mermaid
erDiagram
  TENANTS ||--o{ MEMBERS : owns
  CAMPUSES ||--o{ MEMBERS : "home campus"
  MEMBER_STATUSES ||--o{ MEMBERS : status
  FAMILIES ||--o{ MEMBERS : "optional family"
  FAMILIES ||--o{ FAMILY_MEMBERS : contains
  MEMBERS ||--o{ FAMILY_MEMBERS : participates
  CARE_CELLS ||--o{ MEMBERS : "primary cell"
  CARE_CELLS ||--o{ CARE_CELL_MEMBERS : roster
  MEMBERS ||--o{ CARE_CELL_MEMBERS : belongs
  MEMBERS ||--o{ BAPTISMS : has
  MEMBERS ||--o{ TRANSFERS : has
  MEMBERSHIP_CLASSES ||--o{ CLASS_ENROLLMENTS : enrolls
  MEMBERS ||--o{ CLASS_ENROLLMENTS : enrolled
  MEMBERS ||--o{ MEMBER_SKILLS : has
  MEMBERS ||--o{ MEMBER_MINISTRIES : serves
  MEMBERS ||--o| MARRIAGES : "bride/groom"
  FAMILIES ||--o{ BABY_DEDICATIONS : requests

  MEMBERS {
    uuid id PK
    uuid tenant_id FK
    uuid campus_id FK
    text membership_number UK
    uuid family_id FK
    uuid care_cell_id FK
    uuid status_id FK
    text legal_name
  }
  FAMILIES {
    uuid id PK
    uuid tenant_id FK
    text family_code UK
    uuid primary_member_id FK
  }
  FAMILY_MEMBERS {
    uuid id PK
    uuid family_id FK
    uuid member_id FK
    enum relationship
  }
  CARE_CELLS {
    uuid id PK
    uuid campus_id FK
    uuid leader_member_id FK
  }
  CARE_CELL_MEMBERS {
    uuid id PK
    uuid care_cell_id FK
    uuid member_id FK
  }
  BAPTISMS {
    uuid id PK
    uuid member_id FK
    date baptism_date
  }
  TRANSFERS {
    uuid id PK
    uuid member_id FK
    enum direction
  }
  CLASS_ENROLLMENTS {
    uuid id PK
    uuid class_id FK
    uuid member_id FK
  }
```

**Cardinality**

| Relationship | Card. | Notes |
|---|---|---|
| Family → Member | 1:N | Member may be family-less |
| Family ↔ Member (junction) | N:M | Relationship typed |
| Care Cell → Member (primary) | 1:N | `members.care_cell_id` |
| Care Cell ↔ Member (history) | N:M | `care_cell_members` |
| Member → Baptism | 1:N | Multiple historical rare |
| Class → Enrollment | 1:N | Unique (class, member) |

---

## 3. Visitor domain

```mermaid
erDiagram
  VISITOR_SOURCES ||--o{ VISITORS : attributes
  CAMPUSES ||--o{ VISITORS : hosts
  MEMBERS ||--o{ VISITORS : "referrer"
  MEMBERS ||--o| VISITORS : "converted_to"
  VISITORS ||--|{ VISITOR_FOLLOWUPS : schedules
  USERS ||--o{ VISITOR_FOLLOWUPS : assigned

  VISITORS {
    uuid id PK
    uuid tenant_id FK
    text visitor_number UK
    uuid source_id FK
    uuid referrer_member_id FK
    enum pipeline_stage
    uuid converted_member_id FK
    timestamptz first_visit_at
  }
  VISITOR_FOLLOWUPS {
    uuid id PK
    uuid visitor_id FK
    smallint day_offset
    timestamptz due_at
    uuid assignee_user_id FK
    enum status
  }
  VISITOR_SOURCES {
    uuid id PK
    text code
    boolean requires_referrer
  }
```

**Cardinality**

| Relationship | Card. | Notes |
|---|---|---|
| Source → Visitor | 1:N | Referrer required when flagged |
| Visitor → Follow-up | 1:5 | Day offsets 1/3/7/14/30 unique |
| Visitor → Member (convert) | 0..1:0..1 | Sets stage `converted` |

---

## 4. Counselling

```mermaid
erDiagram
  MEMBERS ||--o{ COUNSELLING_CASES : "counselee"
  VISITORS ||--o{ COUNSELLING_CASES : "counselee"
  COUNSELLING_CATEGORIES ||--o{ COUNSELLING_CASES : categorizes
  USERS ||--o{ COUNSELLING_CASES : "counsellor"
  COUNSELLING_CASES ||--o{ COUNSELLING_SESSIONS : has
  COUNSELLING_CASES ||--o{ COUNSELLING_REFERRALS : refers

  COUNSELLING_CASES {
    uuid id PK
    text case_number UK
    enum risk_level
    enum status
    uuid assigned_counsellor_user_id FK
  }
  COUNSELLING_SESSIONS {
    uuid id PK
    uuid case_id FK
    bytea summary_ciphertext
    timestamptz next_followup_at
  }
  COUNSELLING_REFERRALS {
    uuid id PK
    uuid case_id FK
    text referral_type
  }
```

**Cardinality:** Case has 0..N sessions and 0..N referrals. Exactly one of member/visitor counselee required. High risk triggers supervisor notification (app rule).

---

## 5. Welfare

```mermaid
erDiagram
  MEMBERS ||--o{ WELFARE_REQUESTS : beneficiary
  USERS ||--o{ WELFARE_REQUESTS : requestor
  WELFARE_NEED_TYPES ||--o{ WELFARE_REQUESTS : type
  WELFARE_REQUESTS ||--o| WELFARE_ASSESSMENTS : assessed
  WELFARE_REQUESTS ||--o{ WELFARE_APPROVALS : approvals
  WELFARE_REQUESTS ||--o{ WELFARE_ASSISTANCES : disbursed
  WELFARE_REQUESTS ||--o{ WELFARE_FOLLOWUP_REVIEWS : reviews
  FUNDS ||--o{ WELFARE_ASSISTANCES : funded
  WELFARE_COMPARISONS ||--o{ WELFARE_COMPARISON_ITEMS : includes
  WELFARE_REQUESTS ||--o{ WELFARE_COMPARISON_ITEMS : compared
  WELFARE_COMPARISON_ITEMS ||--o{ WELFARE_COMPARISON_SCORES : scored

  WELFARE_REQUESTS {
    uuid id PK
    text request_number UK
    numeric amount_requested
    char currency_code
    enum status
  }
  WELFARE_COMPARISONS {
    uuid id PK
    text session_number UK
    jsonb weights
  }
  WELFARE_COMPARISON_ITEMS {
    uuid id PK
    uuid comparison_id FK
    uuid welfare_request_id FK
    smallint display_order
  }
```

**Cardinality:** Comparison includes **1–5** items. Each item has up to **9** scores (A–I). Assistance 0..N per request after approval.

---

## 6. Finance (core giving)

```mermaid
erDiagram
  FUNDS ||--o{ DONATIONS : receives
  FUNDS ||--o{ TITHES : receives
  FUNDS ||--o{ OFFERINGS : receives
  MEMBERS ||--o{ DONATIONS : gives
  MEMBERS ||--o{ TITHES : tithes
  MEMBERS ||--o{ OFFERINGS : offers
  VENDORS ||--o{ EXPENSE_PAYMENTS : paid
  FUNDS ||--o{ EXPENSE_PAYMENTS : charged
  RECURRING_EXPENSES ||--o{ EXPENSE_PAYMENTS : generates
  BUDGETS ||--o{ BUDGET_LINES : contains
  FUNDS ||--o{ BUDGET_LINES : plans

  FUNDS {
    uuid id PK
    text code UK
    enum fund_type
    char currency_code
  }
  DONATIONS {
    uuid id PK
    numeric amount
    text idempotency_key UK
    timestamptz received_at
  }
  TITHES {
    uuid id PK
    uuid member_id FK
    int period_year
  }
  EXPENSE_PAYMENTS {
    uuid id PK
    enum status
    uuid requested_by FK
    uuid approved_by FK
  }
```

**Cardinality:** Giving rows optionally link member (offerings may be anonymous). Expense approver ≠ requester (SoD check).

---

## 7. Textual cardinality notes (summary)

1. **Hard tenant boundary:** every domain entity hangs off `tenants` (1:N). No cross-tenant FKs.
2. **Campus:** most operational entities are N per campus; executive queries omit campus filter.
3. **Soft delete:** relationships remain for audit; default reads exclude `deleted_at IS NOT NULL`.
4. **Conversion:** Visitor → Member is a lifecycle transition, not a subtype inheritance.
5. **Confidentiality:** Counselling session ciphertext is owned by case; access is role-filtered, not modeled as separate “note user” table.
6. **Partitioned tables** (`attendance_events`, `notifications`, `audit_log`, deliveries, snapshots, tally events) are **append-oriented**; ERD treats them as 1:N from tenant/user/entity without reverse navigation requirements.

---

## 8. Cross-module relationship matrix

| From \ To | MEM | VIS | COUN | PRAY | WEL | CER | SLOT | ROST | COM | FIN | ANA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **MEM** | — | referrer / convert | counselee | requester | beneficiary | subject | — | assignee | audience | giver | metrics |
| **VIS** | convert | — | counselee | — | — | — | — | — | audience | — | funnel |
| **COUN** | case link | case link | — | escalate* | — | counselling gate | — | duty type | reminders | — | trends |
| **PRAY** | requester | — | — | — | — | — | — | — | notify | — | volume |
| **WEL** | beneficiary | — | — | — | WCE | — | — | — | status push | fund/voucher | demand |
| **CER** | dedication/marriage | — | status block | — | — | — | slot insert | — | announce | — | counts |
| **SLOT** | — | — | — | — | — | hosts | — | — | publish | — | — |
| **ROST** | assignee | — | activity | — | — | — | — | — | assign notify | — | load |
| **COM** | segment | segment | non-sensitive | team | updates | ceremony | agenda | reminders | — | — | delivery KPIs |
| **FIN** | giving | — | — | — | assistance | — | — | — | anomaly alert | Tally | cashflow |
| **ANA / AI** | scores | conversion | risk hint* | draft* | eligibility* | — | optimize* | fair assign* | draft* | forecast* | store |

\*AI advisory only; human confirmation required for high-risk actions.

---

## 9. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial Mermaid ERD + matrix |
