# 14 — Multi-Tenant Architecture

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 14 — Multi-Tenant Architecture |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related FRs** | FR-GLO-001, FR-SEC-*, FR-AI-004 |
| **Related** | [00-INDEX](../00-INDEX.md) · [11-SECURITY-MODEL](../11-SECURITY-MODEL.md) · [15-SCALABILITY](15-SCALABILITY.md) · [16-DEPLOYMENT](16-DEPLOYMENT.md) |

**Conventions:** Tenant codes as `TEN-DEMO-01`. No real org names, domains, or secrets.

---

## 1. Purpose

Define tenancy models, campus and denomination hierarchies, data isolation, branding, feature flags, and metering for a multi-tenant, multi-campus SaaS CMS targeting 100k+ members on large tenants.

---

## 2. Tenant models

### 2.1 Preferred: Shared database + `tenant_id` RLS

| Aspect | Design |
|---|---|
| Database | Single Azure PostgreSQL Flexible Server (or pooled cluster) per environment |
| Isolation | Every table includes `tenant_id` (UUID); **Row-Level Security (RLS)** enforced |
| Application | Middleware sets `SET app.tenant_id = …` / session GUC; repositories never omit tenant predicate |
| Pros | Cost-efficient, simpler ops, uniform migrations |
| Cons | Noisy neighbour risk—mitigate via pooling, quotas, partitioning ([15-SCALABILITY](15-SCALABILITY.md)) |

**Mandatory:** Defence in depth—RLS **and** application filters. Integration jobs and admin scripts must set tenant context or fail closed.

### 2.2 Optional: Dedicated database (enterprise)

| Aspect | Design |
|---|---|
| Trigger | Contractual isolation, extreme scale, residency, or regulated tenants |
| Pattern | Dedicated PostgreSQL Flexible Server (or dedicated DB on shared server) per tenant |
| Routing | Tenant catalog maps `tenant_id` → connection secret in Key Vault |
| Migrations | Same schema version; fleet migration tooling |
| Pros | Stronger blast-radius isolation; independent restore |
| Cons | Higher cost; more ops |

Hybrid allowed: most tenants shared; flagged enterprise tenants dedicated.

### 2.3 Tenant catalog (control plane)

| Field (logical) | Purpose |
|---|---|
| `tenant_id` | Primary key |
| `slug` / display name | Branding & URLs |
| `tier` | Standard / Enterprise |
| `db_mode` | `shared` \| `dedicated` |
| `residency_region` | Azure region constraint |
| `status` | Trial / Active / Suspended / Offboarded |
| `feature_flags` | JSON / flag service ref |
| `branding` | Logo, colours, email from-name |
| `metering_plan` | Quotas & SKU |

Control plane DB is separate from tenant data plane where feasible.

---

## 3. Hierarchy

### 3.1 Campus hierarchy (within tenant)

```
Tenant (Church / Org)
 └── Campus (1..N)
      ├── Care Cells
      ├── Ministries
      ├── Service slots / events
      └── Local finance cost centres (optional)
```

| Rule | Detail |
|---|---|
| FR-GLO-001 | Records scoped by `tenant_id`; optional `campus_id` |
| Users | Role assignments may be tenant-global or campus-scoped |
| Cross-campus | SP/AD/FM (policy) see all campuses; CCL limited to assigned cells/campuses |
| Transfer | Membership transfer updates campus + audit |

### 3.2 Denomination / organization hierarchy (optional)

```
Denomination / Network (optional umbrella)
 └── Region / District (optional)
      └── Tenant (legal church entity — billing & data boundary)
           └── Campuses …
```

| Layer | Data boundary |
|---|---|
| Umbrella | Aggregate analytics **only** if tenants opt in; never raw member rows cross-tenant |
| Tenant | **Hard isolation** boundary for PII/pastoral/finance |
| Campus | Operational boundary inside tenant |

Umbrella admins do **not** bypass tenant RLS without explicit delegated read models and contracts.

---

## 4. Data isolation

| Layer | Control |
|---|---|
| Network | Private endpoints; no public DB |
| AuthN | Tokens include `tenant_id`; reject mismatch |
| AuthZ | RBAC within tenant ([11-SECURITY-MODEL](../11-SECURITY-MODEL.md)) |
| RLS | PostgreSQL policies on all tenant tables |
| Blob | Container prefix or container-per-tenant; SAS scoped |
| Redis | Key prefix `t:{tenant_id}:…` |
| Search | Index-per-tenant or routing key filter mandatory |
| AI | Tenant-partitioned inference; no cross-tenant training by default |
| Backups | Shared backups logically restorable per tenant; dedicated DB = independent restore |
| Support | Break-glass dual control; time-boxed |

**Testing:** Automated tenant isolation tests (attempt cross-tenant read → deny) in CI.

---

## 5. Branding

| Element | Tenant-configurable |
|---|---|
| Logo / favicon | Yes (Blob) |
| Primary/secondary colours | Yes (CSS variables) |
| Portal title | Yes |
| Email from name / reply domain | Yes (DNS/DKIM per tenant or shared relay with display name) |
| WhatsApp profile | Mapped to WABA assets |
| Login background | Optional |
| Certificate templates | CER module |

Branding never alters security headers or CSP trust in unsafe ways.

---

## 6. Feature flags

| Scope | Examples |
|---|---|
| Module enable | WCE, AI Copilot, Tally, M365 calendar |
| AI capability | Per FR-AI-004 (conversion score, roster fairness, etc.) |
| Channel | WhatsApp / SMS region availability |
| Beta UX | New dashboard widgets |
| Compliance | Erasure workflow strictness |

Flags evaluated server-side; client hints are non-authoritative. Changes audited.

---

## 7. Metering & quotas

| Meter | Example quota (plan-based) |
|---|---|
| Active members | Soft/hard caps; alert at 80/100% |
| Campuses | Per plan |
| Monthly COM messages | Per channel |
| Storage (Blob) | GB included |
| AI inference calls | Monthly units |
| Power BI exports | Count / rows |
| Dedicated DB | Enterprise SKU only |

**Enforcement:** Soft warn → hard block non-critical creates → never block emergency pastoral alerts without SP override.

Billing export is aggregate (counts)—no PII.

---

## 8. Tenant lifecycle

| Stage | Actions |
|---|---|
| Provision | Create catalog row, schema seed / RLS role, admin user, default campuses, default RBAC matrix |
| Configure | Branding, SSO, integrations, currencies, feature flags |
| Operate | Metering, support under isolation rules |
| Suspend | Block logins except AD break-glass; retain data |
| Offboard | Export package → retention clock → anonymize/delete per policy |

---

## 9. Decision guide

| Requirement | Choose |
|---|---|
| Default SaaS cost efficiency | Shared DB + RLS |
| Contractual dedicated isolation | Dedicated DB |
| Multi-campus single legal entity | One tenant, many campuses |
| Network of churches with separate legal entities | One tenant each; optional umbrella analytics opt-in |

---

## 10. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial multi-tenant architecture |

**Related:** [15-SCALABILITY](15-SCALABILITY.md) · [16-DEPLOYMENT](16-DEPLOYMENT.md) · [11-SECURITY-MODEL](../11-SECURITY-MODEL.md)
