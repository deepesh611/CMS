# 11 — Security Model

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 11 — Security Model |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline / Design-ready |
| **Related FRs** | FR-SEC-001…009, FR-GLO-001…003, FR-COUN-014, FR-PRAY-*, FR-FIN-* |
| **Related** | [00-INDEX](00-INDEX.md) · [01-BRS](01-BRS.md) · [02-FRS](02-FRS.md) · [architecture/14-MULTI-TENANT](architecture/14-MULTI-TENANT.md) · [architecture/16-DEPLOYMENT](architecture/16-DEPLOYMENT.md) |

**Conventions:** Persons referenced as Member A, Visitor B, Case C-1001. No real PII/PHI, credentials, or secrets in this document.

---

## 1. Purpose & principles

This document defines authentication, authorization, confidential-data controls, audit, privacy workflows, encryption, secrets, sessions, and break-glass pastoral access for the multi-tenant CMS.

| Principle | Application |
|---|---|
| Least privilege | Roles grant only required module actions; field-level denies override module grants |
| Defence in depth | Tenant RLS + API authZ + field ACL + encryption + audit |
| Pastoral confidentiality | Counselling notes and confidential prayer bodies never appear in SMS, list UIs, or AI logs |
| Separation of duties | Finance create ≠ approve ≠ export for high-value actions; Auditor is read/export-audit only |
| Zero trust for secrets | KMS-backed Key Vault; no plaintext secrets in code, Helm values, or CI logs |
| Human accountability | Every privileged and break-glass action is dual-controlled or immutably audited |

---

## 2. System roles (exact set)

Per **FR-SEC-001**, the platform defines exactly these twelve roles:

| Code | Role | Typical scope |
|---|---|---|
| `SP` | Senior Pastor | Tenant-wide pastoral oversight; confidential access; high-risk approvals |
| `PA` | Pastor | Campus/ministry pastoral ops; ceremony & welfare approvals |
| `EL` | Elder | Elder review gates (ceremonies, discipline pathways) |
| `CO` | Counsellor | Assigned counselling cases; confidential notes |
| `CCL` | Care Cell Leader | Cell members/visitors; welfare request initiation; cell attendance |
| `WT` | Welfare Team | Welfare assess/approve/assist; WCE comparison |
| `ML` | Ministry Leader | Rosters, ministry volunteers, ministry events |
| `FM` | Finance Manager | Ledgers, budgets, vouchers, Tally sync, reports |
| `TR` | Treasurer | Receipts, bank rec, disbursement confirmation; dual-control with FM |
| `AD` | Administrator | Users, campuses, RBAC matrix, integrations, feature flags |
| `AU` | Auditor | Read-only + audit export; no business mutations |
| `VO` | Volunteer | Self-service roster; limited COM; no confidential modules |

**Notes**

- A user may hold multiple roles; effective permission = union, subject to field-level deny and campus scope.
- Associate Care Cell Leader may be implemented as `CCL` subtype or tag with WEL request rights (FR-SEC-009)—not a thirteenth system role.
- Member portal users are not a system role; they use self-service scopes (own profile, own giving summary per policy, own prayer/events).

---

## 3. Permission vocabulary

| Symbol | Meaning |
|---|---|
| **C** | Create |
| **R** | Read (list + detail within scope) |
| **U** | Update |
| **D** | Delete / soft-delete |
| **A** | Approve / reject workflow step |
| **E** | Export (PDF/Excel/Power BI / bulk download) |
| **—** | No access |
| **\*** | Scoped: own campus / assigned care cell / assigned case only |
| **‡** | Field-restricted: module R allowed but confidential fields masked/denied |

Campus and care-cell scope filters always apply unless role is tenant-global (`SP`, `AD`, `AU`, `FM`/`TR` for finance per tenant policy).

---

## 4. RBAC matrix (module × role)

Modules: **MEM** Membership · **VIS** Visitors · **COUN** Counselling · **PRAY** Prayer · **WEL** Welfare · **WCE** Comparison · **CER** Ceremonies · **SLOT** Service slots · **ROST** Roster · **COM** Communication · **FIN** Finance · **ANA** Analytics · **SEC** Admin/security config · **AUD** Audit trail

### 4.1 Core people & pastoral modules

| Module | SP | PA | EL | CO | CCL | WT | ML | FM | TR | AD | AU | VO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **MEM** | CRUD A E | CRUD\* A\* | R\* | R\* | CRU\* | R\* | R\* | R | R | CRUD E | R E | R\* own |
| **VIS** | CRUD A E | CRUD\* A | R\* | R\* | CRUD\* | R\* | R\* | — | — | CRUD E | R E | CRU\* (visitor team) |
| **COUN** | R‡ A E‡ | R\*‡ A\* | — | CRUD\*‡ A\* | — | — | — | — | — | C (case shell only) R shell | R shell E meta | — |
| **PRAY** | CRUD A E‡ | CRUD\* A | R\* | R\*‡ | CRU\* | R\* | R\* | — | — | CRUD E‡ | R E‡ | C\* (own request) R public |
| **WEL** | R A E | R\* A\* | R\* | C R\* | C R\* U\* | CRUD A E | C R\* | R A (fund) | R A (disburse) | R E | R E | — |
| **WCE** | R A E | R\* A\* | R\* | — | — | CRUD A E | — | R E | R | R E | R E | — |

### 4.2 Operations, finance & platform

| Module | SP | PA | EL | CO | CCL | WT | ML | FM | TR | AD | AU | VO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CER** | R A E | CRUD\* A | R A (elder review) | — | C R\* (recommend) | — | R\* | — | — | CRUD E | R E | — |
| **SLOT** | R A | CRUD\* A | R\* | — | R\* | — | R\* | — | — | CRUD E | R E | R\* |
| **ROST** | R A E | R\* A\* | R\* | — | R\* U\* | — | CRUD\* A\* E\* | — | — | CRUD E | R E | R\* U\* (self assign) |
| **COM** | CRUD A E | CRUD\* A | R\* | R\* | CRU\* | CRU\* | CRU\* | R (finance notices) | R | CRUD E | R E | R\* (receive + limited send) |
| **FIN** | R‡ A E‡ | R\*‡ | — | — | — | R welfare fund‡ | — | CRUD A E | CRU A E (dual) | R config | R E | — (self giving portal only) |
| **ANA** | R E | R\* E\* | R\* | R\* (COUN KPIs meta) | R\* | R\* WEL | R\* ROST/COM | R E FIN | R E FIN | R E | R E | — |
| **SEC** | R A (break-glass) | — | — | — | — | — | — | — | — | CRUD A E | R E | — |
| **AUD** | R E | R\* | — | R\* own cases | — | R\* WEL | — | R FIN | R FIN | R E | R E | — |

### 4.2 Matrix legend clarifications

| Pattern | Rule |
|---|---|
| COUN for `AD` | May create case shell and assign counsellor; **cannot** read Confidential Notes |
| COUN for `AU` | Metadata only (status, dates, category, risk band)—**not** note bodies |
| PRAY ‡ | Confidential prayer body readable by SP / assigned Pastor / assigned prayer team leads per policy |
| FIN ‡ | Giving **amounts** and donor detail: FM, TR, SP (policy), AU (audit export); others see aggregates or masked |
| Dual control | Welfare disbursement > threshold and FIN journals require FM **and** TR (or SP) approval sequence |
| Volunteer VIS | Only if tagged Visitor Team; otherwise no VIS create |

Administrators edit the live matrix in SEC UI; changes require MFA step-up and write to AUD (FR-SEC-002).

---

## 5. Authentication & MFA

### 5.1 Identity

| Method | Use |
|---|---|
| Local credentials + MFA | Small tenants; emergency break-glass admin |
| OIDC SSO (Microsoft 365 / Entra ID) | Enterprise tenants (recommended) |
| Mobile device trust | See §10 |

### 5.2 MFA policy (FR-SEC-003)

| Role class | MFA |
|---|---|
| Senior Pastor, Finance Manager, Treasurer, Administrator, Auditor | **Mandatory** (TOTP or IdP MFA) |
| Pastor, Elder, Counsellor, Welfare Team | **Mandatory** |
| Care Cell Leader, Ministry Leader | Mandatory if tenant policy = elevated; else recommended |
| Volunteer | Optional / risk-based (sensitive actions step-up) |

**Controls**

- Step-up MFA for: RBAC changes, break-glass, finance export, counselling note open, erasure approval, Tally credential rotate.
- Lockout after N failed attempts (tenant policy; default 5); progressive delay; Administrator unlock with audit.
- Password / passkey policy via IdP where SSO enabled.

---

## 6. Field-level security (FLS)

Field ACL is evaluated **after** module RBAC. Deny wins.

### 6.1 Counselling notes (`COUN`)

| Field group | Allowed readers | Rules |
|---|---|---|
| Case shell (id, category, status, risk band, dates, assignees) | CO (assigned), SP, PA (if policy), AD (shell only), AU (meta) | Lists never show note preview |
| **Confidential Notes** | Assigned Counsellor + Senior Pastor (configurable FR-COUN-014) | Encrypted at rest; separate key material; open action audited |
| Session attachments | Same as notes | Virus scan; no public URLs |
| Reminder SMS/Push | Time + “session reminder” only | **Never** note text |

### 6.2 Prayer confidential (`PRAY`)

| Classification | Visibility |
|---|---|
| Public / congregation | Members with PRAY R; may appear in moderated feeds |
| Team | Prayer team + Pastor + SP |
| **Confidential** | Submitter, assigned intercessors, Pastor/SP per policy | Body masked in lists; export redacts body unless E‡ granted |

### 6.3 Giving amounts (`FIN`)

| Data | Visibility |
|---|---|
| Individual gift amount / donor line | FM, TR, SP (tenant policy), AU (controlled export) |
| Member self-view | Own gifts only (portal) |
| Care Cell / ministry leaders | Aggregates only (no donor drill-down) unless SP grants temporary view |
| UI lists / ANA widgets for non-finance | Masked (`••••`) or bucketed totals |

### 6.4 Welfare narratives

Sensitive free-text and supporting documents: WT, SP, PA (approvers), assigned CCL requestor (own request), AU (meta/redacted export). Not sent on SMS.

---

## 7. Audit logs

### 7.1 What is logged (FR-SEC-004, FR-GLO-002)

| Category | Events |
|---|---|
| AuthN | Login success/fail, MFA challenge, logout, lockout, SSO assertion |
| AuthZ | Permission deny, role grant/revoke, matrix change |
| Data | Create/update/soft-delete/restore; status transitions |
| Sensitive open | Confidential note view, giving line view, break-glass |
| Export | Who, report id, filters, row count, destination |
| Privacy | Consent change, access request, erasure request/decision |
| Integration | Connector config change (no secret values), sync job result codes |

### 7.2 Log payload rules

- Store: `tenant_id`, `actor_id`, `role_snapshot`, `action`, `entity_type`, `entity_id`, `campus_id`, `correlation_id`, `ip`/`device_trust_id`, `timestamp`, `before_hash`/`after_hash` (optional).
- **Never** store raw note bodies, prayer confidential text, full addresses, or gift amounts in log messages.
- Logs are append-only (WORM / immutability tier); retention ≥ legal minimum (default 7 years for finance-adjacent; tenant policy).

### 7.3 Access to audit

| Role | Access |
|---|---|
| Auditor | Full tenant audit read + export |
| Administrator | Operational audit; cannot purge |
| Senior Pastor | Pastoral-sensitive event subset |
| Others | Own actions only (optional) |

---

## 8. GDPR-style privacy controls (FR-SEC-007)

Applies as **privacy-by-design** baseline; map to local law (GDPR/PDPL/etc.) per tenant jurisdiction.

### 8.1 Consent

| Consent type | Examples | Enforcement |
|---|---|---|
| Channel | Email, WhatsApp, SMS, Push | COM + notification preference center |
| Purpose | Pastoral care, marketing events, analytics | Purpose tags on processing |
| Photo / directory | Member directory visibility | MEM profile flags |

Consent version, timestamp, channel, and actor stored; withdrawal stops non-essential processing.

### 8.2 Data subject export

- Self-service or AD-assisted export package (JSON/PDF): profile, attendance summary, own giving summary, own prayer (non-third-party), communication prefs.
- Counselling notes: **not** auto-exported to subject without counsellor/SP legal review workflow.
- Export jobs audited; files expire in Blob after TTL.

### 8.3 Erasure & retention exceptions

| Data class | Default erasure | Retention exception |
|---|---|---|
| Marketing COM prefs / non-essential profile extras | Erase on approved request | — |
| Membership operational history | Anonymize identifiers | Statistical aggregates retained |
| Counselling notes | Legal hold / pastoral policy review | May retain under legitimate interest / legal obligation with sealed access |
| Finance transactions, receipts, Tally sync | **No full erasure** | Statutory retention (tenant-configured; often 7–10 years) |
| Welfare disbursements linked to funds | Anonymize narrative; keep ledger integrity | Finance/legal hold |
| Audit logs | No subject-driven purge of integrity trail | Pseudonymize actor/subject refs where law allows |

Erasure workflow: Request → verify identity → impact assessment → dual approval (AD + SP or DPO role) → execute anonymize/delete → certificate of completion → AUD entry.

---

## 9. Encryption & secrets

### 9.1 In transit

- TLS 1.2+ end-to-end for all client ↔ App Gateway/Front Door ↔ services.
- HTTP → HTTPS redirect only; no application content on port 80 ([architecture/16-DEPLOYMENT](architecture/16-DEPLOYMENT.md)).
- mTLS optional between mesh services in AKS.

### 9.2 At rest

| Store | Encryption |
|---|---|
| PostgreSQL Flexible Server | Azure storage encryption + customer-managed key (CMK) via Key Vault |
| Redis | TLS + encryption at rest |
| Blob (media, exports) | SSE with CMK; private endpoints |
| Confidential note columns | Application-level envelope encryption (data key in Key Vault) in addition to DB TDE |

### 9.3 Secrets (KMS / Key Vault)

- All secrets (DB, WhatsApp tokens, SMS keys, Tally credentials, Graph app secrets, JWT signing keys) in **Azure Key Vault** with **KMS CMK**.
- Runtime injection via CSI / managed identity; never commit secrets; never log secret values.
- Rotation playbooks; dual control for production secret write.
- Terraform: `aws_secretsmanager`-equivalent Azure resources must use explicit key_id; recovery windows per platform standard (destroyable non-prod = 0 where applicable).

---

## 10. Session & device trust (mobile)

### 10.1 Session

| Control | Default |
|---|---|
| Access token TTL | Short-lived (e.g., 15–60 min) |
| Refresh token | Rotating; revoke on password/SSO change |
| Idle timeout | Role-based (privileged shorter) |
| Absolute session max | 8–12 h web; mobile refresh with biometric re-auth option |
| Concurrent sessions | Tenant policy; force logout on risk |

CSRF tokens + CSP for web (FR-SEC-008).

### 10.2 Device trust

| Signal | Use |
|---|---|
| Device attestation (iOS/Android) | Register device_trust_id bound to user |
| Biometric unlock | Local gate to refresh token |
| Jailbreak/root heuristics | Block or step-up MFA |
| Remote wipe / revoke | AD or user can revoke device |
| Untrusted device | Limit confidential module download; watermark exports |

---

## 11. Confidential data controls (FR-SEC-006)

| Control | Behaviour |
|---|---|
| Masking | Lists/search show initials or membership id—not full confidential fields |
| Copy/print | Optional disable for COUN notes on web |
| Screenshots | Mobile flag + watermark on sensitive screens |
| Search indexing | Confidential bodies excluded from OpenSearch or encrypted index with ACL |
| Backups | Same classification; restore access audited |
| Support access | No standing access; break-glass only (§12) |
| AI / analytics | Feature vectors only; redaction pipeline ([13-AI-AND-NOTIFICATIONS](13-AI-AND-NOTIFICATIONS.md)) |
| Notifications | Channel templates strip confidential fields |

---

## 12. Break-glass pastoral access (dual control)

Used when urgent pastoral duty requires access beyond normal assignment (e.g., counsellor unavailable, emergency welfare).

### 12.1 Flow

1. **Requester** (typically Senior Pastor or Pastor) opens Break-Glass on Case C-1001 / Member A sealed record.
2. States **business justification** (structured reason codes + free text; free text retained in AUD, not in COM).
3. **Approver** (second privileged actor: SP if requester is PA; AD or second SP/Elder policy) must approve within TTL (e.g., 15 minutes).
4. Both complete **step-up MFA**.
5. System grants **time-boxed** elevated read (e.g., 30–120 minutes) on specified entity only.
6. All field opens during window emit high-severity AUD events; SIEM alert optional.
7. Auto-revoke at expiry; optional post-incident review task.

### 12.2 Rules

| Rule | Detail |
|---|---|
| Dual control | Requester ≠ Approver |
| No standing break-glass role | Elevation is entitlement ticket, not permanent role |
| Auditor visibility | AU receives immutable event; cannot approve own glass |
| Finance | Break-glass does **not** bypass dual-control payment approval |
| Logging | Justification stored; note contents still not written into log body |

---

## 13. Threat & control summary

| Threat | Primary controls |
|---|---|
| Cross-tenant data leak | `tenant_id` RLS + app filters + separate encryption keys per tenant (enterprise option) |
| Insider counselling disclosure | FLS + encryption + AUD + break-glass dual control |
| Privilege escalation | MFA step-up + matrix change audit + Auditor review |
| Credential theft | MFA, device trust, short sessions, Key Vault |
| Bulk exfiltration | Export permission + rate limits + watermark + AUD |
| Integration abuse | Circuit breakers, least-privilege app registrations, secret rotation |

---

## 14. Implementation checklist

- [ ] Seed twelve roles; load default matrix §4
- [ ] Enforce MFA for privileged classes
- [ ] Column encryption + FLS for COUN notes, PRAY confidential, FIN amounts
- [ ] Immutable audit store + export for AU
- [ ] Consent, export, erasure workflows with finance retention exceptions
- [ ] Key Vault CMK wiring for DB, Blob, app secrets
- [ ] Session/device trust for mobile apps
- [ ] Break-glass dual-control API + UI
- [ ] Security review before production PHI/pastoral data load

---

## 15. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial enterprise security model |

**Related:** [12-DASHBOARDS-AND-REPORTS](12-DASHBOARDS-AND-REPORTS.md) · [13-AI-AND-NOTIFICATIONS](13-AI-AND-NOTIFICATIONS.md) · [architecture/14-MULTI-TENANT](architecture/14-MULTI-TENANT.md) · [architecture/16-DEPLOYMENT](architecture/16-DEPLOYMENT.md)
