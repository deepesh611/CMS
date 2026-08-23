# Database Schema — PostgreSQL Logical Design

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 07 — Database Schema |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Design baseline |
| **RDBMS** | PostgreSQL 16+ |
| **Scale** | Multi-tenant, multi-campus, 100,000+ members / large tenant |
| **DDL** | [schemas/postgresql-core.sql](schemas/postgresql-core.sql) · [schemas/postgresql-pastoral-ops.sql](schemas/postgresql-pastoral-ops.sql) · [schemas/postgresql-finance-analytics.sql](schemas/postgresql-finance-analytics.sql) |
| **Related** | [08-ERD](08-ERD.md) · [api/09-API-SPEC](api/09-API-SPEC.md) · [02-FRS](02-FRS.md) |

> **Compliance:** No real PII/PHI in examples. Use placeholders (`Member A`, `Visitor B`, `Case C-1001`). Sensitive pastoral fields are encrypted at rest and excluded from analytics extracts.

---

## 1. Design principles

| Principle | Rule |
|---|---|
| Multi-tenant isolation | Every tenant-scoped table includes `tenant_id UUID NOT NULL`. Application + RLS enforce isolation. |
| Multi-campus | Optional `campus_id` where campus-scoped; org-wide rollups ignore campus filter for executives. |
| Surrogate keys | Primary keys are `UUID` (`gen_random_uuid()`). No sequential PKs exposed externally. |
| Soft delete | `deleted_at TIMESTAMPTZ NULL`; queries default to `deleted_at IS NULL`. Hard delete only via retention/erasure jobs. |
| Audit columns | `created_at`, `created_by`, `updated_at`, `updated_by` on all mutable tables. |
| Idempotency | External money/sync tables carry `idempotency_key` / provider refs with unique constraints. |
| No secrets in DB config | Connection strings and API keys live in KMS-backed secret stores, not table defaults. |
| PHI/PII minimization | Counselling note bodies and welfare narratives: column-level encryption + field-level ACL. Never log values. |

---

## 2. Naming conventions

| Object | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural nouns | `members`, `visitor_followups` |
| Columns | `snake_case` | `membership_number`, `care_cell_id` |
| Primary key | `{table_singular}_id` or `id` | `id` (UUID) preferred for consistency |
| Foreign keys | `{referenced_table_singular}_id` | `member_id`, `tenant_id` |
| Unique indexes | `uq_{table}_{cols}` | `uq_members_tenant_membership_number` |
| Indexes | `ix_{table}_{cols}` | `ix_members_tenant_campus_status` |
| Check constraints | `ck_{table}_{rule}` | `ck_donations_amount_positive` |
| Enums (PG types) | `{domain}_{name}` | `membership_status_code`, `visitor_source_code` |
| Lookup tables | `{domain}_{name}s` or `*_lookup` | `visitor_sources`, `member_statuses` |
| Partition parents | same name as logical table | `attendance_events`, `notifications`, `audit_log` |
| Partition children | `{parent}_y{YYYY}m{MM}` | `audit_log_y2026m08` |
| Schemas | logical modules as PG schemas | `core`, `identity`, `membership`, `pastoral`, `finance`, `analytics` |

**Boolean columns:** prefix `is_` / `has_` (`is_active`, `has_consent`).  
**Timestamps:** always `TIMESTAMPTZ`.  
**Money:** `NUMERIC(18,4)` amount + `CHAR(3)` ISO currency.  
**JSON:** `JSONB` for extensible attributes only (never replace core columns).

---

## 3. Standard column sets

### 3.1 Tenant entity base

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `UUID` | NO | PK, default `gen_random_uuid()` |
| `tenant_id` | `UUID` | NO | FK → `tenants.id` |
| `created_at` | `TIMESTAMPTZ` | NO | default `now()` |
| `created_by` | `UUID` | YES | FK → `users.id` (system null) |
| `updated_at` | `TIMESTAMPTZ` | NO | default `now()` |
| `updated_by` | `UUID` | YES | FK → `users.id` |
| `deleted_at` | `TIMESTAMPTZ` | YES | soft delete |
| `row_version` | `INT` | NO | optimistic concurrency, default 1 |

### 3.2 Campus-scoped entity

Adds `campus_id UUID NULL` (FK → `campuses.id`, same `tenant_id`).

### 3.3 Audit event payload (immutable)

| Column | Type | Notes |
|---|---|---|
| `actor_user_id` | `UUID` | may be null for system |
| `action` | `TEXT` | `CREATE` / `UPDATE` / `DELETE` / `EXPORT` / `LOGIN` … |
| `entity_type` | `TEXT` | e.g. `member` |
| `entity_id` | `UUID` | |
| `correlation_id` | `UUID` | request/trace id |
| `ip_hash` | `BYTEA` | hashed; never store raw IP with PII join |
| `before_hash` / `after_hash` | `BYTEA` | optional integrity hashes; **no field values** |

---

## 4. Partitioning strategy

High-write / high-volume tables are **RANGE-partitioned by month** on event/created timestamp.

| Table | Partition key | Retention (default) | Notes |
|---|---|---|---|
| `attendance_events` | `RANGE (occurred_at)` | 36 months hot + archive | Member/visitor check-in |
| `notifications` | `RANGE (created_at)` | 12 months hot | Delivery attempts |
| `audit_log` | `RANGE (occurred_at)` | 84 months (7y) or tenant policy | Immutable; no UPDATE/DELETE grants |
| `communication_deliveries` | `RANGE (created_at)` | 24 months | Provider status |
| `tally_sync_events` | `RANGE (created_at)` | 36 months | Finance sync trail |
| `analytics_snapshots` | `RANGE (snapshot_at)` | 60 months | KPI cubes |

### 4.1 Partition management

- Create next **3 months** of partitions via scheduled job (`pg_partman` or app migrator).
- Detach + move cold partitions to cheaper storage / export after retention.
- All partition children inherit parent indexes (local indexes on `(tenant_id, …)`).
- Application **must** include partition key in queries where possible for pruning.

### 4.2 Example (attendance)

```sql
CREATE TABLE attendance_events (
  id UUID NOT NULL,
  tenant_id UUID NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  -- …
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

CREATE TABLE attendance_events_y2026m08
  PARTITION OF attendance_events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
```

---

## 5. Indexing strategy

### 5.1 Rules

1. **Always** lead composite indexes with `tenant_id` on tenant tables.
2. Soft-delete filters: prefer partial indexes `WHERE deleted_at IS NULL`.
3. FK columns used in joins get dedicated indexes.
4. Status/pipeline list screens: `(tenant_id, campus_id, status, created_at DESC)`.
5. Unique business keys: `(tenant_id, natural_key)` with partial active filter when needed.
6. Avoid low-cardinality alone indexes (`is_active`); combine with tenant + date.
7. GIN indexes on `JSONB` attributes and `TEXT[]` tags only where query patterns require.
8. Partitioned tables: indexes defined on parent; verify prune-friendly predicates.

### 5.2 Critical indexes (summary)

| Area | Index | Purpose |
|---|---|---|
| Members | `uq_members_tenant_membership_number` | Natural ID |
| Members | `ix_members_tenant_campus_status` | Directory |
| Members | `ix_members_tenant_care_cell` | Cell roster |
| Members | `ix_members_tenant_email_active` (partial unique optional) | Dup policy |
| Visitors | `ix_visitors_tenant_stage_visit` | Pipeline |
| Visitors | `ix_visitor_followups_assignee_due` | SLA worklist |
| Counselling | `ix_counselling_cases_counsellor_status` | Caseload |
| Welfare | `ix_welfare_requests_tenant_status` | Approvals queue |
| Finance | `ix_donations_tenant_received_at` | Giving reports |
| Finance | `uq_donations_tenant_idempotency` | Idempotent posts |
| Notifications | `ix_notifications_tenant_user_created` | Inbox |
| Audit | `ix_audit_log_tenant_entity` | Forensics |
| Roster | `ix_roster_assignments_member_date` | Conflict detection |

---

## 6. Enumerations & lookup tables

Prefer **lookup tables** for tenant-configurable labels; use **PostgreSQL ENUM** only for closed, code-stable sets shipped with the product.

### 6.1 Product ENUMs (stable)

| Type | Values |
|---|---|
| `gender_code` | `male`, `female`, `unspecified`, `prefer_not_to_say` |
| `marital_status_code` | `single`, `married`, `widowed`, `divorced`, `separated`, `other` |
| `risk_level_code` | `low`, `moderate`, `high` |
| `urgency_code` | `normal`, `high`, `emergency` |
| `notification_channel` | `email`, `sms`, `whatsapp`, `push`, `portal` |
| `notification_status` | `queued`, `sent`, `delivered`, `failed`, `suppressed` |
| `giving_instrument` | `cash`, `card`, `bank_transfer`, `cheque`, `online`, `other` |
| `tally_sync_status` | `pending`, `in_progress`, `succeeded`, `failed`, `dead_letter` |
| `ceremony_type_code` | `baby_dedication`, `baptism`, `membership_reception`, `thanksgiving`, `wedding_anniversary`, `house_blessing`, `marriage_banns`, `wedding_service`, `funeral_service`, `memorial_service` |
| `service_type_code` | `friday_main`, `sunday_main`, `special` |
| `program_slot_code` | `before_worship`, `after_worship`, `before_sermon`, `after_sermon`, `during_announcements`, `before_closing_prayer` |
| `wce_category_code` | `A`…`I` (Eligibility … Recommendation) |

### 6.2 Lookup tables (seeded + configurable labels)

| Table | Purpose | Seed highlights |
|---|---|---|
| `member_statuses` | Membership lifecycle | Prospect, In Class, Active, Inactive, Transferred Out, Transferred In, Suspended, Deceased |
| `visitor_sources` | Attribution | Friend, Church Member, Family Member, Care Cell Member, Pastor, Ministry Leader, Church Event, Outreach Program, Website, Facebook, Instagram, YouTube, WhatsApp, Google Search, Walk-In, Advertisement, Other |
| `visitor_pipeline_stages` | Pipeline | New, Contacted, Engaged, Class Invited, Converted, Lost/Closed |
| `counselling_categories` | Case category | Marriage, Family, Youth, Addiction, Mental Health, Career, Grief, Trauma, Financial, Spiritual Care, Leadership Mentoring, Church Conflict |
| `prayer_categories` | Prayer taxonomy | Spiritual Growth, Healing, Family, Financial, Career, Education, Emotional Support, Church Growth, Ministry, Emergency, Special Needs |
| `welfare_need_types` | Aid taxonomy | Food, Housing, Medical, Education, Utilities, Emergency Relief, Other |
| `followup_outcome_codes` | Visit outcomes | Contacted, No Answer, Rescheduled, Declined, Converted, Escalated |
| `currencies` | ISO currencies | OMR, USD, EUR, GBP, AED, SAR, INR, QAR, KWD, BHD |
| `permissions` | RBAC catalogue | `members.read`, `welfare.approve`, … |
| `roles` | System + custom roles | Senior Pastor, Pastor, Elder, Counsellor, Care Cell Leader, … |

---

## 7. Full table catalogue (by module)

Legend: **PK** primary key · **FK** foreign key · **UQ** unique · **N** nullable · **NN** not null · Soft = has `deleted_at` + audit columns unless noted.

### 7.1 CORE — tenancy & campus

#### `tenants`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `code` | TEXT | NN | UQ |
| `name` | TEXT | NN | |
| `primary_currency` | CHAR(3) | NN | FK → currencies |
| `timezone` | TEXT | NN | IANA |
| `status` | TEXT | NN | `active`/`suspended` |
| `settings` | JSONB | NN | default `{}` |
| audit + soft | | | |

#### `campuses`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` | UUID | NN | FK tenants |
| `code` | TEXT | NN | UQ `(tenant_id, code)` |
| `name` | TEXT | NN | |
| `timezone` | TEXT | NN | |
| `address_line1`…`country_code` | TEXT | N | |
| `is_primary` | BOOLEAN | NN | |
| audit + soft | | | |

#### `care_cells`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` | UUID | NN | FK |
| `campus_id` | UUID | NN | FK campuses |
| `code` | TEXT | NN | UQ `(tenant_id, code)` |
| `name` | TEXT | NN | |
| `leader_member_id` | UUID | N | FK members |
| `associate_leader_member_id` | UUID | N | FK members |
| `is_active` | BOOLEAN | NN | |
| audit + soft | | | |

#### `care_cell_members`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` | UUID | NN | |
| `care_cell_id` | UUID | NN | FK care_cells |
| `member_id` | UUID | NN | FK members |
| `role_in_cell` | TEXT | NN | `member`/`leader`/`associate` |
| `joined_at` | DATE | NN | |
| | | | UQ `(tenant_id, care_cell_id, member_id)` WHERE deleted_at IS NULL |

---

### 7.2 IDENTITY — users & RBAC

#### `users`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` | UUID | NN | FK |
| `email` | CITEXT | NN | UQ `(tenant_id, email)` active |
| `display_name` | TEXT | NN | |
| `member_id` | UUID | N | FK members (portal link) |
| `idp_subject` | TEXT | N | OIDC sub |
| `mfa_required` | BOOLEAN | NN | |
| `is_active` | BOOLEAN | NN | |
| `last_login_at` | TIMESTAMPTZ | N | |
| audit + soft | | | |

#### `roles` / `permissions` / `role_permissions` / `user_roles`

| Table | Key columns | Uniques |
|---|---|---|
| `roles` | `tenant_id`, `code`, `name`, `is_system` | UQ `(tenant_id, code)` |
| `permissions` | `code`, `module`, `description` | UQ `code` (global catalogue) |
| `role_permissions` | `role_id`, `permission_id` | UQ `(role_id, permission_id)` |
| `user_roles` | `user_id`, `role_id`, `campus_id` N | UQ `(tenant_id, user_id, role_id, COALESCE(campus_id, …))` |

---

### 7.3 MEMBERSHIP

#### `member_statuses` (lookup)

`id`, `tenant_id` (null = system seed), `code`, `label`, `sort_order`, `is_terminal`

#### `members`

| Column | Type | Null | Constraints |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` | UUID | NN | FK |
| `campus_id` | UUID | NN | FK |
| `membership_number` | TEXT | NN | UQ `(tenant_id, membership_number)` |
| `family_id` | UUID | N | FK families |
| `care_cell_id` | UUID | N | FK care_cells |
| `status_id` | UUID | NN | FK member_statuses |
| `legal_name` | TEXT | NN | |
| `preferred_name` | TEXT | N | |
| `email` | CITEXT | N | |
| `mobile_e164` | TEXT | N | |
| `date_of_birth` | DATE | N | |
| `gender` | gender_code | N | |
| `marital_status` | marital_status_code | N | |
| `address_*` | TEXT | N | |
| `profession` | TEXT | N | |
| `photo_object_key` | TEXT | N | object storage key |
| `classification_tags` | TEXT[] | NN | default `{}` |
| `engagement_score` | NUMERIC(5,2) | N | AI-derived |
| `consent_comms_at` | TIMESTAMPTZ | N | |
| audit + soft | | | |

#### `families` / `family_members`

| Table | Columns | Constraints |
|---|---|---|
| `families` | `id`, `tenant_id`, `family_code`, `campus_id`, `primary_member_id` | UQ `(tenant_id, family_code)` |
| `family_members` | `family_id`, `member_id`, `relationship` (`spouse`,`child`,`parent`,`other`) | UQ `(tenant_id, family_id, member_id)` |

#### `baptisms`

`member_id`, `baptism_date`, `campus_id`, `officiant_user_id`, `certificate_object_key`, notes (non-PHI)

#### `transfers`

`member_id`, `direction` (`in`/`out`), `effective_date`, `source_church`, `destination_church`, `source_campus_id`, `destination_campus_id`, `status`, `approved_by`

#### `membership_classes` / `class_enrollments`

| Table | Notes |
|---|---|
| `membership_classes` | `name`, `campus_id`, `starts_on`, `ends_on`, `capacity` |
| `class_enrollments` | `class_id`, `member_id`, `status` (`enrolled`/`completed`/`withdrawn`), `completed_at` · UQ `(class_id, member_id)` |

#### `marriages` (membership-linked record)

`bride_member_id`, `groom_member_id`, `marriage_date`, `venue`, `certificate_object_key`, `counselling_case_id` N

#### `baby_dedications`

`child_given_name`, `date_of_birth`, `place_of_birth`, `father_member_id`, `mother_member_id`, `family_id`, `status`, `ceremony_id` N, certificate key

#### `member_skills` / `member_ministries`

| Table | Columns | UQ |
|---|---|---|
| `member_skills` | `member_id`, `skill_code`, `proficiency` | `(tenant_id, member_id, skill_code)` |
| `member_ministries` | `member_id`, `ministry_code`, `role_title`, `started_on`, `ended_on` | active unique optional |

#### `attendance_events` (partitioned)

`member_id` N, `visitor_id` N, `campus_id`, `service_type`, `occurred_at`, `checkin_method`

---

### 7.4 VISITOR

#### `visitor_sources` (lookup)

`code`, `label`, `requires_referrer` BOOLEAN

#### `visitors`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | UUID | NN | PK |
| `tenant_id` / `campus_id` | UUID | NN | |
| `visitor_number` | TEXT | NN | UQ per tenant |
| `display_name` | TEXT | NN | |
| `email` / `mobile_e164` | | N | |
| `first_visit_at` | TIMESTAMPTZ | NN | |
| `source_id` | UUID | NN | FK visitor_sources |
| `referrer_member_id` | UUID | N | required when source.requires_referrer |
| `pipeline_stage` | TEXT | NN | |
| `converted_member_id` | UUID | N | set on convert |
| `interests` | TEXT[] | NN | |
| `has_prayer_need` | BOOLEAN | NN | flag only; no note body |
| audit + soft | | | |

#### `visitor_followups`

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | UUID | NN | |
| `visitor_id` | UUID | NN | FK |
| `day_offset` | SMALLINT | NN | 1,3,7,14,30 |
| `due_at` | TIMESTAMPTZ | NN | |
| `assignee_user_id` | UUID | NN | |
| `status` | TEXT | NN | `pending`/`completed`/`cancelled`/`escalated` |
| `outcome_code` | TEXT | N | |
| `completed_at` | TIMESTAMPTZ | N | |
| | | | UQ `(visitor_id, day_offset)` |

---

### 7.5 PASTORAL — counselling

#### `counselling_cases`

`counselee_member_id` N, `counselee_visitor_id` N, `category_id`, `risk_level`, `status` (`open`/`active`/`on_hold`/`referred`/`closed`), `assigned_counsellor_user_id`, `campus_id`, `opened_at`, `closed_at`

#### `counselling_sessions`

`case_id`, `scheduled_at`, `attended_at`, `duration_minutes`, `summary_ciphertext` (encrypted), `next_followup_at`

#### `counselling_referrals`

`case_id`, `referral_type` (`internal`/`external`), `target_label`, `status`, `referred_at`

---

### 7.6 PASTORAL — prayer

#### `prayer_requests`

`requester_member_id` N, `category_id`, `urgency`, `is_confidential`, `status`, `body_ciphertext`, `escalated_at`, `escalated_to_user_id`

#### `prayer_teams` / `prayer_team_members` / `prayer_assignments`

Team membership and request assignment with `prayed_at`, `followup_at`

#### `prayer_testimonies`

`prayer_request_id`, `body_ciphertext`, `published_at`, `is_public`

---

### 7.7 WELFARE + WCE

#### `welfare_requests`

`beneficiary_member_id`, `requestor_user_id`, `need_type_id`, `amount_requested`, `currency_code`, `narrative_ciphertext`, `status` (`submitted`/`assessment`/`review`/`approved`/`rejected`/`disbursed`/`closed`), `campus_id`

#### `welfare_assessments` / `welfare_approvals` / `welfare_assistances` / `welfare_followup_reviews`

Lifecycle artifacts; `welfare_assistances` links `fund_id`, `voucher_id` N, `disbursed_at`, `amount`

#### `welfare_comparisons` / `welfare_comparison_items` / `welfare_comparison_scores`

Session of ≤5 cases; scores A–I with weights; `decision_notes` (non-raw narrative)

---

### 7.8 CEREMONIES / SLOTS / ROSTER

#### `ceremonies`

`ceremony_type`, `status`, `member_ids` via junction, `scheduled_at`, `campus_id`, `service_slot_item_id` N, certificate keys

#### `ceremony_approvals` / `ceremony_objections` (banns)

Approval chain; objections with `raised_at`, `resolved_at`, `outcome`

#### `service_occurrences` / `service_slot_items`

Occurrence of Friday/Sunday/Special; items in program slots with duration, owner, conflict checks

#### `activity_rosters` / `roster_assignments` / `roster_availability`

Activity types: sermons, counselling, hospital visits, care cells, ministry events, worship, volunteers, Friday School

---

### 7.9 COMMUNICATIONS

#### `communications`

`channel_mix`, `content_type`, `subject`, `body_ref`, `audience_filter` JSONB, `scheduled_at`, `status`, `created_by`

#### `communication_attachments`

`object_key`, `content_type`, `byte_size` (≤ 50MB), channel eligibility flags

#### `communication_deliveries` (partitioned)

Per-recipient provider status; **no message body PII** in logs

#### `notifications` (partitioned)

In-app/push queue: `user_id`, `channel`, `template_code`, `payload_ref`, `status`, `created_at`

---

### 7.10 FINANCE

#### `funds`

`code`, `name`, `fund_type` (`general`/`welfare`/`mission`/`other`), `currency_code`, `is_active`

#### `donations` / `tithes` / `offerings`

Shared pattern: `member_id` N, `fund_id`, `amount`, `currency_code`, `fx_rate`, `amount_base`, `received_at`, `instrument`, `idempotency_key`, `campus_id`

#### `budgets` / `budget_lines`

Period budgets by fund/campus/category

#### `vendors` / `recurring_expenses` / `expense_payments`

Vendor master; recurring templates (hall rentals, utilities, …); payment runs with SoD

#### `exchange_rates`

`base_currency`, `quote_currency`, `rate_date`, `rate` · UQ `(base, quote, rate_date)`

#### `tally_sync_events` (partitioned)

`entity_type`, `entity_id`, `operation`, `status`, `request_hash`, `response_code`, `error_code` (no secrets)

---

### 7.11 ANALYTICS & AI

#### `analytics_snapshots` (partitioned)

`snapshot_at`, `campus_id` N, `metric_domain`, `metric_code`, `dimensions` JSONB, `value_num`, `value_json`

#### `ai_recommendations`

`domain`, `entity_type`, `entity_id`, `recommendation_type`, `rationale`, `confidence`, `status` (`pending`/`accepted`/`edited`/`rejected`), `model_version`, **no raw counselling note text**

#### `audit_log` (partitioned, immutable)

See §3.3

---

## 8. Row-level security (RLS)

### 8.1 Session context

Application sets per-connection:

```sql
SELECT set_config('app.tenant_id', '<uuid>', true);
SELECT set_config('app.user_id', '<uuid>', true);
SELECT set_config('app.roles', 'pastor,counsellor', true);
```

### 8.2 Baseline policy (tenant tables)

```sql
CREATE POLICY tenant_isolation ON members
  USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
```

Enable `FORCE ROW LEVEL SECURITY` on all tenant tables. Migrations run as owner bypass only in controlled jobs.

### 8.3 Field-level / role policies

| Domain | Extra RLS / grants |
|---|---|
| Counselling notes | SELECT on `summary_ciphertext` only if user is assigned counsellor OR Senior Pastor (break-glass audited) |
| Welfare narratives | Welfare Team + approvers + requestor |
| Finance journals | Finance Manager / Treasurer / Auditor (read) |
| Audit log | Auditor + Admin; INSERT-only for app role |
| Cross-campus | Campus-scoped roles filter `campus_id IN (user campuses)` |

### 8.4 Soft delete

Default policies add `AND deleted_at IS NULL` for non-admin roles. Restore requires `members.restore` permission.

---

## 9. Capacity notes (100k+ members)

| Object | Order-of-magnitude (large tenant) | Design response |
|---|---|---|
| `members` | 1e5–3e5 rows | B-tree on tenant+status; archive soft-deleted |
| `attendance_events` | 1e7+/yr | Monthly partitions + prune |
| `notifications` | 1e7+/yr | Partitions; TTL detach |
| `audit_log` | high write | Partitions; append-only tablespace |
| Hot path lists | p95 &lt; 2s | Covering indexes + Redis cache for directories |

Connection pooling (PgBouncer), read replicas for ANA, and async exports for large CSV/Power BI.

---

## 10. Migration & versioning

- DDL shipped as ordered SQL files under `schemas/`; apply via migrator (one version at a time, idempotent guards).
- Never skip intermediate versions.
- Seed lookups in separate `seeds/` (system rows `tenant_id IS NULL`).
- Schema compare utilities live in shared runtime libraries (per platform standards).

---

## 11. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial PostgreSQL logical design + catalogue |

**Next:** [08-ERD.md](08-ERD.md) · DDL in [schemas/](schemas/) · APIs in [api/09-API-SPEC.md](api/09-API-SPEC.md)
