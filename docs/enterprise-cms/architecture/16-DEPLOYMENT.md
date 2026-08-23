# 16 — Deployment Architecture (Azure)

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 16 — Deployment Architecture |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related** | [00-INDEX](../00-INDEX.md) · [14-MULTI-TENANT](14-MULTI-TENANT.md) · [15-SCALABILITY](15-SCALABILITY.md) · [17-INTEGRATIONS](17-INTEGRATIONS.md) · [11-SECURITY-MODEL](../11-SECURITY-MODEL.md) |

**Conventions:** Resource names are illustrative (`aks-cms-prod-01`). No real subscription IDs, secrets, or connection strings.

---

## 1. Purpose

Define Azure deployment topology: AKS, data stores, messaging, secrets, edge HTTPS, CI/CD, environments, blue-green, observability, DR, and microservice boundaries.

---

## 2. Logical topology

```
Clients (Web / iOS / Android)
        │
        ▼
Azure Front Door / Application Gateway
  • HTTPS only • HTTP → HTTPS redirect • WAF
        │
        ▼
AKS cluster (private nodes preferred)
  ┌─────────┬─────────┬─────────┬─────────┐
  │ Identity│Membership│ Pastoral│ Finance │ …
  └─────────┴─────────┴─────────┴─────────┘
        │         │          │
        ▼         ▼          ▼
 PostgreSQL    Redis      Service Bus / Event Hubs
 Flexible      Cache
        │
        ▼
 Blob Storage ← Key Vault (CMK / secrets)
```

Outbound integrations (WhatsApp, SMS, Graph, Tally bridge) use managed identity + Key Vault secrets; private endpoints where supported.

---

## 3. Azure building blocks

| Component | Azure service | Notes |
|---|---|---|
| Compute | **AKS** | Microservices + workers; HPA/VPA as needed |
| Packaging | **Docker** images in Azure Container Registry (ACR) |
| OLTP | **Azure Database for PostgreSQL – Flexible Server** | CMK; read replicas; private link |
| Cache | **Azure Cache for Redis** | TLS; tenant key prefix |
| Messaging | **Service Bus** and/or **Event Hubs** | Commands vs high-volume events |
| Media / exports | **Blob Storage** | Private; lifecycle; CMK |
| Secrets / keys | **Key Vault** | Secrets, certs, CMK; access via managed identity |
| Edge | **Application Gateway** and/or **Front Door** | Global entry; WAF |
| Observability | App Insights + Grafana + OpenTelemetry | See §8 |
| Identity edge | Entra ID app registrations | SSO OIDC |

### 3.1 HTTPS enforcement (mandatory)

| Rule | Implementation |
|---|---|
| HTTPS only for application content | Front Door / App Gateway listeners on 443 |
| HTTP → HTTPS redirect | Explicit redirect rule; **do not** serve app content on port 80 |
| TLS | 1.2+; managed certificates |
| HSTS | Enabled at edge |

---

## 4. Microservice boundary map

| Service | Responsibility | Data affinity |
|---|---|---|
| **Identity** | AuthN, sessions, MFA, device trust, RBAC queries | Identity schema; talks to Entra |
| **Membership** | MEM profiles, families, status, cells assignment | Membership DB schema |
| **Pastoral** | COUN, PRAY, WEL, WCE, CER (care domain) | Pastoral schema; elevated encryption |
| **Finance** | FIN ledgers, budgets, receipts, dual control | Finance schema |
| **Comm** | Templates, preference center, send orchestration | COM + notification status |
| **Roster** | SLOT, ROST, volunteer assignments | Roster schema |
| **AI** | Inference gateway, redaction, recommendation store | Feature store; no raw PHI logs |
| **Integration** | WhatsApp, SMS, Push, **Tally**, **M365**, Power BI export adapters | Connector configs (secrets in KV) |
| **Analytics** | Projections, dashboard APIs, report jobs | Read models |
| **Admin / Tenant** | Tenant catalog, branding, feature flags, metering | Control plane |

**Boundaries:** Sync calls for user-facing reads; async events for cross-domain side effects. No shared mutable DB schemas across services without an owned integration contract. API gateway / ingress routes by path (`/api/v1/membership/…`).

---

## 5. Environments

| Env | Purpose | Data |
|---|---|---|
| **dev** | Feature branches / local integration | Synthetic only |
| **test** | Automated QA | Synthetic / anonymized |
| **stage** | Pre-prod, perf, UAT | Anonymized; prod-like SKUs optional |
| **prod** | Live tenants | Real; strict change control |

Promotion: build once → promote image digest; config via env-specific Key Vault / dual-slot settings. **No prod secrets in non-prod.**

---

## 6. CI/CD

| Option | Use |
|---|---|
| **GitHub Actions** | Build, test, scan, push ACR, deploy Helm/GitOps |
| **Azure DevOps** | Alternate enterprise pipelines |

**Pipeline stages (typical)**

1. Lint / unit / contract tests  
2. Container build + SCA / image scan  
3. Push to ACR (immutable tag = git SHA)  
4. Deploy to dev/test  
5. Integration / isolation tests  
6. Manual approval → stage  
7. Manual approval → prod (blue-green)  

Infrastructure via Terraform/Bicep; secrets never in repo. Conventional commits; small MRs.

---

## 7. Blue-green deployment

| Step | Detail |
|---|---|
| Green deploy | New ReplicaSet / slot with target image |
| Smoke | Health + synthetic tenant checks |
| Shift traffic | Ingress weight 100% → green |
| Monitor | Error rate, latency, queue lag |
| Rollback | Instant weight back to blue |

DB migrations: backward-compatible expand/contract; never break blue during green warmup.

---

## 8. Observability

| Pillar | Stack |
|---|---|
| Tracing / metrics / logs | **OpenTelemetry** SDKs → OTLP collector |
| APM | **Application Insights** |
| Dashboards / alerts | **Grafana** (+ Azure Monitor) |
| SLIs | Availability, latency p95/p99, queue age, sync success |

**Log format (apps):** structured; recommended pattern aligned with platform logging standards — timestamp, level, logger name, message. **Never** log PHI/PII, tokens, or note bodies.

Correlation: `trace_id` / `correlation_id` across API → bus → worker.

---

## 9. Disaster recovery

| Item | Target class (illustrative; confirm per contract) |
|---|---|
| Topology | Geo-paired Azure regions |
| RPO | ≤ 15 minutes (DB geo-backup / async replica policy) |
| RTO | ≤ 4 hours for core pastoral + identity (tiered) |
| DB | Flexible Server geo-redundant backup; dedicated tenants may have warmer standby |
| Blob | GRS/GZRS |
| Key Vault | Soft-delete + purge protection; replica strategy |
| Runbooks | Failover drill quarterly; break-glass admin in secondary |

DR drills use synthetic tenants only in documentation evidence.

---

## 10. Security deployment notes

- Private link for PostgreSQL, Redis, Blob, Key Vault.
- AKS azure AD RBAC; least-privilege workload identities.
- WAF rulesets at Front Door/App Gateway.
- Image signing / admission policy optional enterprise control.
- Align with [11-SECURITY-MODEL](../11-SECURITY-MODEL.md).

---

## 11. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial Azure deployment architecture |

**Related:** [15-SCALABILITY](15-SCALABILITY.md) · [17-INTEGRATIONS](17-INTEGRATIONS.md) · [14-MULTI-TENANT](14-MULTI-TENANT.md)
