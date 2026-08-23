# API Specification

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 09 — API Specification |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Design baseline |
| **Base URL** | `https://{tenant-host}/api/v1` |
| **Related** | [07-DATABASE-SCHEMA](../07-DATABASE-SCHEMA.md) · [10-WORKFLOWS](../10-WORKFLOWS-AND-AUTOMATION.md) · [02-FRS](../02-FRS.md) |

> API-first: Web, iOS, and Android share these contracts. No real PII in examples.

---

## 1. REST conventions

### 1.1 Versioning

- URI versioning: `/api/v1/...`
- Breaking changes → `/api/v2`; additive fields allowed in v1 with compatibility notes.
- `Accept: application/json` required unless documented otherwise (file upload).

### 1.2 Resource naming

- Plural nouns, kebab or camel avoided in paths: `/members`, `/visitor-followups`
- Nested only for strong ownership: `/visitors/{id}/followups`
- Prefer filter query for cross-cutting lists: `/followups?assigneeUserId=&status=pending`

### 1.3 Error envelope

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "One or more fields are invalid.",
    "correlationId": "00000000-0000-4000-8000-000000000001",
    "details": [
      { "field": "campusId", "code": "REQUIRED", "message": "campusId is required." }
    ]
  }
}
```

| HTTP | When |
|---|---|
| 400 | Validation / bad request |
| 401 | Missing/invalid token |
| 403 | Authenticated but scope/tenant denied |
| 404 | Not found **in tenant** (no cross-tenant leak) |
| 409 | Conflict (unique, state machine) |
| 422 | Semantic business rule failure |
| 429 | Rate limited |
| 500 | Unexpected (no stack/PII) |

### 1.4 Pagination

Query: `page` (1-based), `pageSize` (default 25, max 100), optional `cursor` for large sets.

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 25,
    "totalItems": 1204,
    "totalPages": 49,
    "nextCursor": null
  }
}
```

### 1.5 Filtering, sorting, sparse fields

- Filter: `?campusId=&status=&q=` (q = non-PII safe search tokens / membership number)
- Sort: `?sort=-createdAt,legalName` (`-` = DESC)
- Fields: `?fields=id,membershipNumber,status` (allow-list per resource)

### 1.6 Idempotency

- Header `Idempotency-Key: <uuid>` required on POST for finance posts, visitor create (optional but recommended), welfare approve, communications send.
- Server stores key per tenant for ≥24h; replay returns original response.

### 1.7 Concurrency

- `If-Match: "<rowVersion>"` on PATCH/PUT; 412 on mismatch.

### 1.8 Tenancy

- Tenant resolved from JWT claim `tid` (and/or host). Clients **must not** pass `tenantId` to escalate.

---

## 2. Authentication & authorization

### 2.1 OAuth2 / OIDC

| Flow | Use |
|---|---|
| Authorization Code + PKCE | Web / mobile interactive |
| Client Credentials | Service-to-service (integrations) |
| Refresh Token | Rotating refresh; revoke on logout |

IdP: Microsoft Entra ID / compatible OIDC. MFA enforced for privileged roles (Senior Pastor, Finance, Admin, Auditor).

### 2.2 Tokens

| Token | Lifetime | Notes |
|---|---|---|
| Access JWT | 15–60 min | `tid`, `sub`, `roles`, `scopes`, `campus_ids` |
| Refresh | 7–30 days | Bound to device; rotation |
| Mobile scoped token | Short-lived | Reduced scopes for offline sync queues |

JWT claims (illustrative):

```json
{
  "sub": "user-uuid",
  "tid": "tenant-uuid",
  "roles": ["care_cell_leader"],
  "scopes": ["members.read", "visitors.create"],
  "campus_ids": ["campus-uuid"],
  "mfa": true
}
```

### 2.3 Scope format

`{module}.{action}` matching permission catalogue, e.g. `members.write`, `welfare.approve`, `finance.post`.

---

## 3. GraphQL outline

Endpoint: `POST /api/v1/graphql` (same auth). Depth/complexity limits enforced. Prefer REST for bulk writes and file upload.

### 3.1 Queries

```graphql
type Query {
  member(id: ID!): Member
  members(
    campusId: ID
    statusCode: String
    careCellId: ID
    q: String
    page: Int = 1
    pageSize: Int = 25
  ): MemberConnection!

  visitor(id: ID!): Visitor
  visitors(stage: VisitorStage, campusId: ID, page: Int, pageSize: Int): VisitorConnection!
  visitorFollowups(assigneeUserId: ID, status: FollowupStatus, dueBefore: DateTime): [VisitorFollowup!]!

  financeSummary(
    campusId: ID
    from: Date!
    to: Date!
    currency: String
  ): FinanceSummary!
}
```

### 3.2 Mutations

```graphql
type Mutation {
  createMember(input: CreateMemberInput!): MemberPayload!
  updateMember(id: ID!, input: UpdateMemberInput!, rowVersion: Int!): MemberPayload!

  createVisitor(input: CreateVisitorInput!): VisitorPayload!
  completeVisitorFollowup(id: ID!, input: CompleteFollowupInput!): VisitorFollowupPayload!
  convertVisitor(id: ID!, input: ConvertVisitorInput!): ConvertVisitorPayload!

  postDonation(input: PostDonationInput!, idempotencyKey: String!): DonationPayload!
}
```

### 3.3 Finance summary shape

```graphql
type FinanceSummary {
  currency: String!
  totalDonations: Decimal!
  totalTithes: Decimal!
  totalOfferings: Decimal!
  byFund: [FundTotal!]!
  fxAsOf: Date
}
```

Sensitive counselling note fields are **not** exposed in GraphQL schema.

---

## 4. Event-driven topics (Kafka / Azure Event Hubs)

Topic naming: `cms.{env}.{domain}.{event}`  
Payload: CloudEvents 1.0 JSON; **no PII field values** — IDs + codes only.

| Topic / event type | When | Key | Consumers |
|---|---|---|---|
| `member.created` | Member registered | `tenantId:memberId` | COM, ANA, Care Cell notify |
| `member.status_changed` | Status transition | same | COM suppress, roster |
| `visitor.created` | Visitor registered | `tenantId:visitorId` | Automation → followups |
| `visitor.followup.due` | Task due window | `tenantId:followupId` | Notify assignee |
| `visitor.followup.overdue` | Past due | same | Escalation |
| `visitor.converted` | Converted to member | same | Cancel remaining tasks |
| `counselling.case.high_risk` | Risk → high | `tenantId:caseId` | Supervisor alert |
| `prayer.escalated` | Emergency/high escalate | `tenantId:requestId` | Pastor notify |
| `welfare.submitted` | Request created | `tenantId:requestId` | Welfare team |
| `welfare.approved` | Final approval | same | Finance disbursement |
| `welfare.disbursed` | Assistance posted | same | Follow-up schedule |
| `giving.received` | Donation/tithe/offering | `tenantId:txnId` | Tally sync, ANA |
| `expense.approved` | Payment approved | same | Tally, notify |
| `tally.sync.failed` | Dead-letter | same | Finance ops |
| `roster.assigned` | Duty assigned | `tenantId:assignmentId` | Multi-channel notify |
| `roster.published` | Roster published | `tenantId:rosterId` | Bulk notify |
| `ceremony.approved` | Ceremony cleared | `tenantId:ceremonyId` | SLOT/COM |
| `banns.objection.raised` | Objection filed | same | Pastoral review |
| `communication.sent` | Broadcast completed | `tenantId:commId` | ANA delivery |
| `ai.recommendation.created` | Copilot suggestion | entity key | UI inbox |

Delivery: at-least-once; consumers idempotent on `eventId`.

---

## 5. OpenAPI-style endpoint tables

Auth column = required OAuth scope(s). All routes under `/api/v1` unless noted.

### 5.1 Identity & admin

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/me` | Current user profile + roles | `openid` |
| GET | `/roles` | List roles | `admin.rbac` |
| POST | `/roles` | Create custom role | `admin.rbac` |
| PUT | `/roles/{id}/permissions` | Replace role permissions | `admin.rbac` |
| GET | `/users` | List users | `admin.rbac` |
| POST | `/users/{id}/roles` | Assign role | `admin.rbac` |
| GET | `/campuses` | List campuses | `members.read` |
| GET | `/care-cells` | List care cells | `members.read` |
| POST | `/care-cells` | Create care cell | `members.write` |

### 5.2 Membership

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/members` | Search/list members | `members.read` |
| POST | `/members` | Create member | `members.write` |
| GET | `/members/{id}` | Get member | `members.read` |
| PATCH | `/members/{id}` | Update member | `members.write` |
| POST | `/members/{id}/restore` | Soft-delete restore | `members.restore` |
| GET | `/families` | List families | `members.read` |
| POST | `/families` | Create family | `members.write` |
| POST | `/families/{id}/members` | Add family member | `members.write` |
| POST | `/members/{id}/baptisms` | Record baptism | `members.write` |
| POST | `/transfers` | Request transfer | `members.write` |
| POST | `/transfers/{id}/approve` | Approve transfer | `members.write` (+ pastoral) |
| GET | `/membership-classes` | List classes | `members.read` |
| POST | `/membership-classes/{id}/enrollments` | Enroll | `members.write` |
| GET | `/members/{id}/skills` | List skills | `members.read` |
| PUT | `/members/{id}/skills` | Replace skills | `members.write` |
| GET | `/members/{id}/ministries` | List ministries | `members.read` |

### 5.3 Visitors

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/visitor-sources` | Lookup sources | `visitors.create` |
| GET | `/visitors` | Pipeline list | `visitors.create` |
| POST | `/visitors` | Register visitor (+ auto Day 1/3/7/14/30) | `visitors.create` |
| GET | `/visitors/{id}` | Get visitor | `visitors.create` |
| PATCH | `/visitors/{id}` | Update / stage change | `visitors.create` |
| GET | `/visitors/{id}/followups` | List follow-ups | `visitors.followup` |
| POST | `/visitor-followups/{id}/complete` | Complete with outcome | `visitors.followup` |
| POST | `/visitors/{id}/convert` | Convert → member | `visitors.create` + `members.write` |

### 5.4 Counselling

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/counselling/cases` | Caseload | `counselling.create` |
| POST | `/counselling/cases` | Open case | `counselling.create` |
| GET | `/counselling/cases/{id}` | Case header (no note body) | `counselling.create` |
| PATCH | `/counselling/cases/{id}` | Update risk/status | `counselling.create` |
| POST | `/counselling/cases/{id}/sessions` | Add session | `counselling.create` |
| GET | `/counselling/sessions/{id}/summary` | Decrypt summary | `counselling.notes.read` |
| POST | `/counselling/cases/{id}/referrals` | Add referral | `counselling.create` |

### 5.5 Prayer

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| POST | `/prayer-requests` | Submit request | authenticated member/staff |
| GET | `/prayer-requests` | Team inbox | prayer team / pastor |
| POST | `/prayer-requests/{id}/assign` | Assign team/user | prayer lead |
| POST | `/prayer-requests/{id}/escalate` | Escalate emergency | prayer / pastor |
| POST | `/prayer-requests/{id}/testimonies` | Add testimony | assigned |

### 5.6 Welfare & WCE

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| POST | `/welfare/requests` | Create request | `welfare.request` |
| GET | `/welfare/requests` | Queue | `welfare.request` or `welfare.approve` |
| POST | `/welfare/requests/{id}/assessments` | Case assessment | `welfare.approve` |
| POST | `/welfare/requests/{id}/approvals` | Approve/reject | `welfare.approve` |
| POST | `/welfare/requests/{id}/assistances` | Record disbursement | `welfare.approve` + `finance.post` |
| POST | `/welfare/comparisons` | Start WCE session (≤5) | `welfare.approve` |
| POST | `/welfare/comparisons/{id}/scores` | Upsert A–I scores | `welfare.approve` |
| POST | `/welfare/comparisons/{id}/finalize` | Finalize decision | `welfare.approve` |

### 5.7 Ceremonies, slots, roster

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| POST | `/ceremonies` | Create ceremony | pastoral / elder |
| POST | `/ceremonies/{id}/approvals` | Approval step | elder / pastor |
| POST | `/ceremonies/{id}/objections` | Raise banns objection | pastoral |
| POST | `/baby-dedications` | Start dedication workflow | care cell / pastoral |
| GET | `/service-occurrences` | List services | `members.read` |
| POST | `/service-occurrences/{id}/slot-items` | Insert program item | pastoral |
| POST | `/rosters` | Create activity roster | `roster.assign` |
| POST | `/rosters/{id}/assignments` | Assign people | `roster.assign` |
| POST | `/rosters/{id}/publish` | Publish + notify | `roster.assign` |

### 5.8 Communication

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| POST | `/communications` | Create draft | COM editor |
| POST | `/communications/{id}/attachments` | Upload file (see §8) | COM editor |
| POST | `/communications/{id}/schedule` | Schedule send | COM editor |
| POST | `/communications/{id}/send` | Send now | COM editor |
| GET | `/communications/{id}/deliveries` | Delivery statuses | COM editor |
| GET | `/notifications` | User notification inbox | authenticated |

### 5.9 Finance

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/funds` | List funds | `finance.post` |
| POST | `/donations` | Post donation | `finance.post` |
| POST | `/tithes` | Post tithe | `finance.post` |
| POST | `/offerings` | Post offering | `finance.post` |
| GET | `/finance/summary` | Aggregates | `finance.post` or exec |
| GET | `/budgets` | List budgets | `finance.post` |
| POST | `/vendors` | Create vendor | `finance.post` |
| POST | `/recurring-expenses` | Create template | `finance.post` |
| POST | `/expense-payments` | Create payment | `finance.post` |
| POST | `/expense-payments/{id}/approve` | Approve (SoD) | `finance.approve` |
| GET | `/tally/sync-events` | Sync queue | `finance.post` |
| POST | `/tally/sync-events/{id}/retry` | Retry failed | `finance.post` |

### 5.10 Analytics & AI

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/analytics/snapshots` | KPI snapshots | role-filtered |
| GET | `/analytics/dashboards/{code}` | Dashboard payload | role-filtered |
| GET | `/ai/recommendations` | Pending suggestions | module scopes |
| POST | `/ai/recommendations/{id}/decide` | accept/edit/reject | module scopes |

### 5.11 Audit

| Method | Path | Summary | Auth scope |
|---|---|---|---|
| GET | `/audit-events` | Query audit log | `audit.read` |

---

## 6. Webhooks (outbound)

Tenants register HTTPS endpoints; signed with HMAC-SHA256 (`X-CMS-Signature`).

| Event | Payload (IDs only) | Retry |
|---|---|---|
| `member.created` | memberId, campusId | 8× exponential |
| `visitor.followup.due` | visitorId, followupId, dayOffset | same |
| `welfare.approved` | requestId, amount, currency | same |
| `giving.received` | txnType, txnId, fundId | same |
| `roster.assigned` | rosterId, assignmentId | same |
| `tally.sync.failed` | syncEventId, errorCode | same |

Response must be `2xx` within 10s. Secrets in KMS-backed store; never returned in full after create.

---

## 7. Rate limits

| Client class | Limit | Burst |
|---|---|---|
| Interactive user | 120 req/min | 30 |
| Mobile sync | 60 req/min | 20 |
| Integration (client credentials) | 300 req/min | 50 |
| File upload | 20 req/min | 5 |
| GraphQL | 60 req/min + complexity budget | — |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` on 429.

---

## 8. File upload API

| Item | Rule |
|---|---|
| Endpoint | `POST /api/v1/files` (direct) or nested `.../attachments` |
| Max size | **50 MB** (`52428800` bytes) |
| Allowed MIME | `application/pdf`, `image/jpeg`, `image/jpg`, `image/png`, `image/bmp`, `image/gif`, `video/mp4` |
| Email channel | Images + PDF **only**; **MP4 disallowed** (FR-COM-005) |
| Storage | Object storage; API returns `objectKey` + short-lived upload URL |
| Virus scan | Async; attachment unusable until `scanStatus=clean` |
| Auth | COM/editor scopes; finance docs require finance scopes |

Multipart example fields: `file`, `purpose` (`communication`|`welfare_doc`|`certificate`|`profile_photo`), `allowEmail` (bool).

Validation errors: `FILE_TOO_LARGE`, `CONTENT_TYPE_NOT_ALLOWED`, `EMAIL_CHANNEL_DISALLOWS_VIDEO`.

---

## 9. Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial API-first specification |
