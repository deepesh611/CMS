# 17 — Integrations

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 17 — Integrations Architecture |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related FRs** | FR-INT-001…009, FR-FIN-020, FR-COM-*, FR-WCE-014 |
| **Related** | [00-INDEX](../00-INDEX.md) · [02-FRS](../02-FRS.md) · [13-AI-AND-NOTIFICATIONS](../13-AI-AND-NOTIFICATIONS.md) · [16-DEPLOYMENT](16-DEPLOYMENT.md) · [11-SECURITY-MODEL](../11-SECURITY-MODEL.md) |

**Conventions:** Endpoint and credential examples are placeholders (`{{KV_SECRET_REF}}`). No real API keys, phone numbers, or member data.

---

## 1. Purpose

Specify external system connectors: messaging (WhatsApp, Email, SMS, Push), **Tally Prime**, **Microsoft 365**, and **Power BI**, including data flows, security, failure handling, and health monitoring.

**Cross-cutting (FR-INT-008, FR-INT-009)**

| Control | Requirement |
|---|---|
| Secrets | Key Vault only; managed identity; rotation |
| Resilience | Retries with jitter, circuit breakers, DLQ |
| Health | Integration dashboard: latency, error rate, last success |
| Tenancy | Credentials and WABA/SMS accounts mapped per tenant |
| Privacy | No PHI/PII in connector logs; redact payloads in traces |

---

## 2. WhatsApp Business API (FR-INT-001)

| Item | Specification |
|---|---|
| **Capability** | Outbound template messages; optional session messages within window; status webhooks |
| **Auth** | Permanent token / OAuth app secret in Key Vault |
| **Mapping** | Tenant → WABA / phone number id |
| **Templates** | Pre-approved; CMS template id ↔ Meta template name; locale variants |
| **Webhooks** | Delivery, read, failures → notification status store |
| **Content rules** | Respect preference center; no counselling note bodies; media within provider limits (platform cap 50 MB; WhatsApp typically lower) |
| **Failover** | On hard failure → SMS/Email per [13-AI-AND-NOTIFICATIONS](../13-AI-AND-NOTIFICATIONS.md) |

**Flows:** Domain event → Comm service → WhatsApp adapter → provider → webhook → receipt.

---

## 3. Email — Microsoft 365 Graph / SMTP (FR-INT-002)

| Mode | When | Notes |
|---|---|---|
| **Microsoft Graph** | Enterprise tenants with M365 | `Mail.Send` application or delegated per design; sender mailbox per tenant policy |
| **SMTP** | Lightweight / fallback | TLS SMTP; credentials in Key Vault |

| Rule | Detail |
|---|---|
| Attachments | **Images + PDF only**; **no MP4**; max **50 MB** total per message |
| DKIM/SPF | Tenant custom domain or shared relay with correct From display |
| Bounce handling | Ingest NDRs / Graph events → suppress / failover |
| Bulk | Throttle to Graph/SMTP limits; digests preferred over storms |

---

## 4. SMS gateway (FR-INT-003)

| Item | Specification |
|---|---|
| **Abstraction** | Provider interface (e.g., commercial SMS API); **log mode** in non-prod (no real send) |
| **Use** | OTP (if used), emergency alerts, short reminders |
| **Body policy** | Time + generic text only for counselling; never confidential prayer/notes/amounts |
| **Encoding** | GSM-7 / UCS-2 length awareness; segment billing metrics |
| **Opt-out** | STOP handling → preference center |

---

## 5. Push — APNs / FCM (FR-INT-004)

| Platform | Service |
|---|---|
| iOS | **APNs** (token auth key in Key Vault) |
| Android | **FCM** (service account JSON in Key Vault) |

| Topic | Behaviour |
|---|---|
| Targeting | Device trust ids / user topics; campus topics optional |
| Payload | Title, body, deep link; no sensitive note text |
| Invalid tokens | Prune on provider error codes |
| Quiet hours | Honoured unless Critical |

---

## 6. Tally Prime (FR-INT-005)

Bridge church FIN module with Tally Prime via **XML / API** connector (on-prem gateway or approved hosted bridge). Databricks/air-gapped patterns N/A here; use Integration service + secure tunnel as deployed.

### 6.1 Objects synced

| CMS concept | Tally direction | Notes |
|---|---|---|
| **Ledgers** | Bi-directional or CMS→Tally master sync | Funds, banks, income/expense ledgers |
| **Receipts** | CMS → Tally | Tithes, offerings, donations |
| **Payments** | CMS → Tally | Welfare disbursements, expenses |
| **Journals** | CMS → Tally | Adjustments, FX reval (policy) |
| **Bank reconciliation** | Status exchange | Unreconciled items surfaced on DASH-FIN |

### 6.2 Technical pattern

```
FIN posting approved
  → Outbox event
  → Tally worker
  → XML/API payload (ids, amounts, ledger codes — minimal PII)
  → Ack / voucher number stored on CMS voucher
  → On failure: retry → DLQ → RPT-FIN-004 exception queue
```

| Control | Rule |
|---|---|
| Idempotency | External ref = CMS voucher id |
| Multi-currency | Map to Tally currency masters; store rate used |
| Secrets | Tally company path / API keys in Key Vault |
| Dual control | Connector does not bypass FM/TR approvals |
| PII | Prefer Membership ID over full name where Tally config allows |

---

## 7. Microsoft 365 (FR-INT-006)

| Graph area | Use |
|---|---|
| **SSO (OIDC)** | Entra ID login for staff |
| **Calendar** | Sync events, ceremonies, roster blocks to organizer calendars |
| **Mail** | Optional send via Graph (§3) |
| **Teams** | Optional notifications / meeting links for counselling slots (metadata only) |
| **Files** | Optional SharePoint/OneDrive for non-PHI ministry docs—not counselling notes store of record |

| Security | Detail |
|---|---|
| App registration | Least-privilege Graph scopes |
| Admin consent | Per tenant |
| Calendar content | Event title/time/location; no confidential case notes in body |

---

## 8. Power BI export (FR-INT-007)

| Dataset | Source | Sensitivity |
|---|---|---|
| Membership growth | ANA projections | Internal |
| Visitor funnel | ANA | Internal |
| Welfare / **WCE** scores | WCE session measures | Confidential — **no confidential free-text by default** |
| Finance summary | FIN aggregates | Restricted |
| COM delivery | Comm receipts | Internal |
| Executive pack | Combined | Confidential |

| Delivery | Pattern |
|---|---|
| Push dataset | Service principal → tenant workspace |
| Pull | Export API → Blob → Power BI dataflow |
| RLS | Campus/role mirrored where published |
| Audit | Export actor, report id, row count |

---

## 9. Connector matrix (summary)

| Integration | Direction | Sync | Criticality |
|---|---|---|---|
| WhatsApp | Out + webhooks in | Near real-time | High |
| Email Graph/SMTP | Out (+ bounce in) | Near real-time | High |
| SMS | Out (+ opt-out in) | Near real-time | High |
| Push APNs/FCM | Out | Near real-time | High |
| Tally Prime | Primarily out; ack in | Async batch / near real-time | High (finance) |
| M365 Calendar | Bi-directional light | Scheduled / event-driven | Medium |
| M365 Mail | Out | Near real-time | Medium |
| Teams (optional) | Out | Event-driven | Low |
| Power BI | Out | Scheduled / on-demand | Medium |

---

## 10. Failure handling & observability

| Pattern | Behaviour |
|---|---|
| Retry | Exponential backoff + jitter; max N |
| Circuit breaker | Open on sustained provider errors |
| DLQ | Manual replay UI for FM/AD |
| Idempotency | Required for Tally & COM |
| Health UI | Last success, p95 latency, error % per connector (FR-INT-008) |
| Alerts | Page on Critical channel or Tally backlog age |

---

## 11. Onboarding checklist (per tenant)

- [ ] Key Vault secrets created (CMK); Integration identity granted get/list
- [ ] WhatsApp templates approved & mapped
- [ ] Email mode (Graph vs SMTP) + domain auth
- [ ] SMS provider + log mode verified in test
- [ ] APNs/FCM apps configured
- [ ] Tally ledger map UAT with synthetic vouchers
- [ ] Entra app consent + calendar test user
- [ ] Power BI workspace + RLS test
- [ ] Isolation test: tenant A credentials cannot send as tenant B

---

## 12. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial integrations architecture |

**Related:** [16-DEPLOYMENT](16-DEPLOYMENT.md) · [13-AI-AND-NOTIFICATIONS](../13-AI-AND-NOTIFICATIONS.md) · [12-DASHBOARDS-AND-REPORTS](../12-DASHBOARDS-AND-REPORTS.md) · [11-SECURITY-MODEL](../11-SECURITY-MODEL.md)
