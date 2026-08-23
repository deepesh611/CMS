# 15 — Scalability Strategy

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 15 — Scalability Strategy |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related** | [00-INDEX](../00-INDEX.md) · [14-MULTI-TENANT](14-MULTI-TENANT.md) · [16-DEPLOYMENT](16-DEPLOYMENT.md) · [12-DASHBOARDS-AND-REPORTS](../12-DASHBOARDS-AND-REPORTS.md) |

**Scale target:** Multi-tenant SaaS; **100,000+ members per large tenant**; 99.9% availability class.

---

## 1. Goals & load assumptions

| Dimension | Target class (large tenant) |
|---|---|
| Members | ≥ 100,000 |
| Concurrent web/mobile users | Thousands at peak (Sunday services, events) |
| Notification bursts | Tens of thousands / hour (devotions, emergency) |
| Dashboard freshness | Seconds–minutes via read models |
| Search | Sub-second typical membership/visitor lookup |

Design for horizontal scale-out; avoid single-pod vertical-only limits.

---

## 2. Strategy catalogue

### 2.1 Read replicas (PostgreSQL)

| Use | Pattern |
|---|---|
| ANA dashboards, reports, search hydration | Read replica / flexible server read endpoints |
| Writes | Primary only |
| Lag | Monitor replication lag; critical finance reads may pin primary |

### 2.2 Redis cache

| Cache | TTL guidance |
|---|---|
| Session / token metadata | Short |
| RBAC permission snapshot | Invalidate on role change |
| Feature flags / branding | Minutes |
| Hot member cards | Short; tenant-prefixed keys |
| Rate-limit counters | Sliding window |
| Idempotency keys | Hours |

**Rules:** `t:{tenant_id}:…` prefix; stampede protection; never cache confidential note bodies.

### 2.3 CQRS for dashboards

| Side | Store |
|---|---|
| Command | Normalized OLTP schema |
| Query | Materialized views / projection tables / Redis aggregates updated by domain events |
| Rebuild | Replay from events or nightly reconcile job |

DASH-* and Power BI prefer projections—not heavy OLTP joins at request time ([12-DASHBOARDS-AND-REPORTS](../12-DASHBOARDS-AND-REPORTS.md)).

### 2.4 Partitioning

| Candidate | Key |
|---|---|
| Attendance / check-in facts | Range by month + tenant |
| Audit / notification status | Time-based |
| COM message metadata | Time-based |
| Finance postings | Fiscal period |

Avoid over-partitioning small reference tables. Prefer Delta-style incremental mindset for analytics exports.

### 2.5 Async workers

| Queue | Workloads |
|---|---|
| Azure Service Bus / Event Hubs | Notifications, Tally sync, exports, AI inference, projection builders |
| Priority | Critical alerts > transactional COM > bulk digests |
| Back-pressure | Prefetch limits; poison message DLQ |

Synchronous API path stays thin: validate → persist → enqueue.

### 2.6 CDN for media

| Asset | CDN |
|---|---|
| Public branding, devotion images | Azure Front Door / CDN |
| Private member docs | Origin Blob private; short-lived SAS; no open CDN without auth |

Cache-Control tuned; virus scan on upload.

### 2.7 Search (OpenSearch)

| Index | Content |
|---|---|
| Members / visitors | Searchable fields only; confidential bodies excluded |
| Events / COM templates | Operational search |
| Security | Tenant filter mandatory on every query |

Sync via change events; bulk reindex per tenant job.

### 2.8 Connection pooling

| Layer | Tooling |
|---|---|
| App → DB | PgBouncer / Azure built-in pooling; sized per pod |
| Avoid | Connection-per-request storms on HPA scale-out |
| Dedicated tenants | Separate pools |

### 2.9 Rate limiting

| Scope | Example |
|---|---|
| Per user / token | API RPS |
| Per tenant | Fair-share to prevent noisy neighbour |
| Per IP | Auth endpoints |
| Export / AI | Stricter quotas |

Return `429` with retry-after; meter for plan enforcement ([14-MULTI-TENANT](14-MULTI-TENANT.md)).

### 2.10 Horizontal pod autoscaling (HPA)

| Signal | Use |
|---|---|
| CPU / memory | Baseline |
| Queue depth | Worker deployments |
| RPS / latency SLI | API gateways |
| Custom metrics | Notification backlog |

Separate HPA for API, workers, AI workers, projection consumers.

### 2.11 Cost controls

| Lever | Practice |
|---|---|
| Spot / scale-to-zero | Non-prod workers |
| Cache hit ratio | Reduce DB RU/CPU |
| Async batching | COM & exports |
| Lifecycle policies | Blob tiering / export TTL |
| Right-size SKUs | Autoscale bounds + budget alerts |
| AI | Token budgets per tenant; degrade to rules-based when exhausted |

---

## 3. Hot-path scenarios

| Scenario | Mitigations |
|---|---|
| Sunday check-in surge | Edge cache config; write batching; SLOT/ROST read replicas; queue non-critical COM |
| Emergency alert blast | Pre-warmed workers; SMS/Push priority lane; template cache |
| Month-end finance + Tally | Dedicated worker pool; rate-limit interactive reports |
| Large Excel export | Async only; stream from projection; row cap |

---

## 4. Data & Spark-style guidance (analytics jobs)

When building warehouse/ETL jobs aligned with platform compliance rules:

- Prefer columnar transforms; avoid driver-heavy `collect()` on large sets.
- Filter and reduce columns early; justify expensive counts/distincts.
- Incremental loads over full rewrites; idempotent merges.
- No PHI/PII in job logs.

---

## 5. Capacity planning checklist

- [ ] Load test 100k-member tenant (read + check-in + notify)
- [ ] Chaos: kill API pods; verify queue drain
- [ ] Replica lag alerts
- [ ] Redis eviction policy validated (no silent confidential bleed)
- [ ] OpenSearch tenant isolation tests
- [ ] HPA cool-down tuned to avoid flap
- [ ] Cost dashboards + budget alerts per env

---

## 6. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial scalability strategy |

**Related:** [14-MULTI-TENANT](14-MULTI-TENANT.md) · [16-DEPLOYMENT](16-DEPLOYMENT.md) · [13-AI-AND-NOTIFICATIONS](../13-AI-AND-NOTIFICATIONS.md)
