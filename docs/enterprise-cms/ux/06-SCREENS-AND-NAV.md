# Screens & Navigation

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | UX 06 — Screens and Navigation |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Status** | Baseline |
| **Related** | [04-MODULE-DESIGN](../04-MODULE-DESIGN.md) · [modules/](../modules/) · [05-USER-STORIES](../05-USER-STORIES.md) |
| **A11y target** | WCAG 2.2 AA |

---

## 1. Purpose

Define navigation trees for **Web Admin/Ops**, **Mobile App**, and **Member Portal**, plus a screen inventory and wireframe-level layouts per module. No ASCII mock dumps—structured regions only. No real PII in examples.

---

## 2. Navigation structure

### 2.1 Web (Staff / Ops console)

```text
Web App
├── Home / Executive Overview          [ANA]
├── People
│   ├── Members                        [MEM]
│   ├── Families                       [MEM]
│   ├── Membership Classes             [MEM]
│   ├── Transfers                      [MEM]
│   └── Visitors
│       ├── Visitor List               [VIS]
│       ├── Pipeline Board             [VIS]
│       └── Follow-Up Tasks            [VIS]
├── Care
│   ├── Counselling Cases              [COUN]
│   ├── Prayer Requests                [PRAY]
│   ├── Prayer Teams                   [PRAY]
│   ├── Welfare Requests               [WEL]
│   └── Welfare Comparison             [WCE]
├── Church Life
│   ├── Ceremonies                     [CER]
│   ├── Service Slots / Agendas        [SLOT]
│   └── Activity Roster                [ROST]
├── Communication
│   ├── Campaigns                      [COM]
│   ├── Devotions                      [COM]
│   ├── Templates                      [COM]
│   └── Delivery Monitor               [COM]
├── Finance
│   ├── Giving & Receipts              [FIN]
│   ├── Funds                          [FIN]
│   ├── Budgets                        [FIN]
│   ├── Vendors & Recurring            [FIN]
│   ├── Approvals                      [FIN]
│   ├── Tally Sync / Exceptions        [FIN]
│   └── Anomalies                      [FIN]
├── Analytics
│   ├── Dashboards Hub                 [ANA]
│   ├── Insights                       [ANA]
│   └── Exports / Power BI             [ANA]
└── Admin
    ├── Users & Roles                  [SEC]
    ├── Campuses & Care Cells          [MEM/SEC]
    ├── Workflow Policies              [WF]
    ├── Integrations Health            [INT]
    └── Audit Log                      [AUD]
```

Role-based nav pruning: e.g., Volunteer sees Roster + limited COM; Counsellor sees Care → Counselling; Finance roles see Finance + ANA finance widgets.

### 2.2 Mobile App (Staff + Member hybrid)

```text
Mobile App
├── Today (agenda + my duties)         [SLOT/ROST]
├── People (search Member/Visitor)*    [MEM/VIS]
├── Care
│   ├── My Counselling Caseload*       [COUN]
│   ├── Prayer (submit / team queue)   [PRAY]
│   └── Welfare (create / approve)*    [WEL]
├── Roster (confirm / decline / sub)   [ROST]
├── Give (member) / Approvals*         [FIN]
├── Messages / Devotion                [COM]
├── More
│   ├── Ceremonies (status)*           [CER]
│   ├── Visitors check-in*             [VIS]
│   ├── Analytics (KPI cards)*         [ANA]
│   ├── Profile & Consent
│   └── Settings / MFA
```

\*Staff-only tabs hidden for pure member login.

### 2.3 Member Portal (Web + embedded in app)

```text
Member Portal
├── Home (devotion + upcoming events)
├── My Profile & Family                [MEM]
├── My Care Cell
├── Prayer (submit / my requests)      [PRAY]
├── Events & Service Agenda            [COM/SLOT]
├── My Roster Duties                   [ROST]
├── Giving & Receipts                  [FIN]
├── Documents / Certificates (mine)    [CER/MEM]
└── Preferences (channels, privacy)
```

---

## 3. Global chrome (all authenticated web apps)

| Region | Contents |
|---|---|
| **Header** | Tenant/campus switcher, global search, AI Copilot entry, notifications bell, user menu (MFA status) |
| **Primary nav** | Left rail (collapsible) — structure in §2.1 |
| **Context bar** | Breadcrumb + campus filter chip + date range when relevant |
| **Main** | Screen body |
| **Side** | Optional detail inspector / AI rationale panel |
| **Actions** | Primary CTA sticky footer or top-right page actions |
| **Skip link** | “Skip to main content” (a11y) |

---

## 4. Screen inventory by module

Legend: **Actors** = primary; widgets = key UI blocks.

### M01 Membership

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| MEM-S01 | Member List | Admin, Care Cell Leader | Filters, data table, bulk tags, export |
| MEM-S02 | Member Profile | Pastor, Care Cell Leader | Header summary, family, ministries, score |
| MEM-S03 | Member Create/Edit | Admin | Form sections, validation, photo upload |
| MEM-S04 | Family Hub | Care Cell Leader | Household graph, members list |
| MEM-S05 | Status Transition | Pastor | Allowed-next matrix, reason |
| MEM-S06 | Baptism Record | Elder | Form + certificate upload |
| MEM-S07 | Transfer Desk | Pastor, Admin | In/out queues, approve |
| MEM-S08 | Classes Board | Ministry Leader | Cohorts, attendance, completion |
| MEM-S09 | Portal Application Queue | Admin | Verify / reject |
| MEM-S10 | Engagement Score Panel | Care Cell Leader | Score + factors + AI actions |

### M02 Visitor

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| VIS-S01 | Visitor List | Volunteer, Care Cell | Source filter, duplicate badge |
| VIS-S02 | Visitor Register | Volunteer | Source enum, referrer picker |
| VIS-S03 | Visitor Detail | Care Cell Leader | Timeline, visits, AI score |
| VIS-S04 | Pipeline Kanban | Ministry Leader | Stages columns, counts |
| VIS-S05 | Follow-Up Task Queue | Care Cell Leader | Day-N chips, SLA overdue |
| VIS-S06 | Complete Follow-Up | Care Cell Leader | Outcome codes, note |
| VIS-S07 | Convert Wizard | Pastor | Field mapping → MEM |
| VIS-S08 | Visitor Analytics | Senior Pastor | Source charts, conversion |

### M03 Counselling

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| COUN-S01 | Case List | Counsellor, Senior Pastor | Risk badges, ACL-filtered |
| COUN-S02 | Open Case | Counsellor | Category, risk, counselee |
| COUN-S03 | Case Workspace | Counsellor | Sessions, referrals, status |
| COUN-S04 | Confidential Notes | Counsellor, Senior Pastor | Encrypted editor, watermark |
| COUN-S05 | Session Scheduler | Counsellor | Calendar, reminder prefs |
| COUN-S06 | Risk Oversight | Senior Pastor | Aggregates only |

### M04 Prayer

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| PRAY-S01 | Submit Prayer | Member, Portal | Category, confidential flag |
| PRAY-S02 | Team Queue | Prayer Team | Assign, escalate |
| PRAY-S03 | Prayer Wall | Member | Non-confidential cards |
| PRAY-S04 | Emergency Queue | Pastor | Ack actions |
| PRAY-S05 | Testimony Composer | Care Cell Leader | Consent toggle |
| PRAY-S06 | AI Draft Assist | Pastor | Scripture + prayer draft |

### M05 Welfare

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| WEL-S01 | Request List | Welfare Team | Status pipeline |
| WEL-S02 | Create Request | Care Cell / Pastor / … | Role-gated form, docs |
| WEL-S03 | Assessment Form | Welfare Team | Checklist, prior aid |
| WEL-S04 | Approval Desk | Pastor, Finance | Threshold steps |
| WEL-S05 | Disbursement | Treasurer | Fund + voucher link |
| WEL-S06 | AI Eligibility Panel | Welfare Team | Score + factors |

### M06 Welfare Comparison

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| WCE-S01 | Session List | Welfare Lead | Recent comparisons |
| WCE-S02 | Case Picker | Welfare Lead | Max 5 selector |
| WCE-S03 | Scoring Matrix | Senior Pastor | A–I grid |
| WCE-S04 | Rankings & Charts | Finance Manager | Radar/bar, rank table |
| WCE-S05 | Decision & Lock | Senior Pastor | Outcome, finalize |
| WCE-S06 | Weight Admin | Administrator | Sum=100 editor |
| WCE-S07 | Power BI Export | Analyst | Job status |

### M07 Ceremonies

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| CER-S01 | Ceremony Catalogue | Admin | Type cards |
| CER-S02 | Dedication Request | Care Cell Leader | Child/parent fields |
| CER-S03 | Dedication Approvals | Elder, Pastor | Stepper Care→Elder→Pastor |
| CER-S04 | Schedule & Certificate | Pastor, Admin | SLOT picker, PDF |
| CER-S05 | Banns Desk | Pastor | Publication + objections |
| CER-S06 | Wedding Scheduler | Pastor | Counselling gate banner |
| CER-S07 | Reception Candidates | Pastor | Class completers |

### M08 Service Slots

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| SLOT-S01 | Service Calendar | Pastor, Admin | Friday/Sunday/Special |
| SLOT-S02 | Agenda Builder | Pastor | Program slot lanes |
| SLOT-S03 | Insert Function | Pastor, Elder | Duration, owner, CER link |
| SLOT-S04 | Conflict Inspector | Elder | Conflict list + suggestions |
| SLOT-S05 | Publish Agenda | Ministry Leader | Channel select |
| SLOT-S06 | Mobile Agenda | Volunteer | Read-only timeline |
| SLOT-S07 | Template Manager | Admin | Special service templates |

### M09 Activity Roster

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| ROST-S01 | Roster Calendar | Ministry Leader | Activity type filters |
| ROST-S02 | Occurrence Detail | Ministry Leader | Assignments, conflicts |
| ROST-S03 | My Duties | Volunteer, Member | Confirm/decline |
| ROST-S04 | Substitution Flow | Volunteer | Suggest substitute |
| ROST-S05 | Availability Editor | Volunteer | Weekly grid |
| ROST-S06 | AI Scheduler | Pastor | Fairness metrics, draft |
| ROST-S07 | Friday School Board | Teacher / Coord | Scoped classes |
| ROST-S08 | Hospital Visits | Care Cell Leader | Sensitivity flag |

### M10 Communication

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| COM-S01 | Campaign List | Ministry Leader | Status, channels |
| COM-S02 | Composer | Ministry Leader | Multi-channel, segment |
| COM-S03 | Attachment Manager | Admin | Policy validator (50MB/MP4) |
| COM-S04 | Devotion Studio | Pastor | Verse/prayer/reflection/article |
| COM-S05 | Push Scheduler | Admin | Immediate/Scheduled/Recurring |
| COM-S06 | Emergency Alert | Senior Pastor | Confirm override |
| COM-S07 | Template Library | Admin, Care Cell | WhatsApp templates |
| COM-S08 | Delivery Monitor | Admin | Provider status |

### M11 Finance

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| FIN-S01 | Giving Desk | Treasurer | Tithe/offering/donation |
| FIN-S02 | Funds Board | Finance Manager | Restricted funds |
| FIN-S03 | Budget Workspace | Finance Manager | Vs actual |
| FIN-S04 | Vendor List | Finance Manager | Risk flags |
| FIN-S05 | Recurring Expenses | Finance Manager | Rental/utilities templates |
| FIN-S06 | Approval Queue | Finance Manager | SoD |
| FIN-S07 | Tally Exceptions | Treasurer, Admin | DLQ resolve |
| FIN-S08 | Bank Recon | Treasurer | Match workspace |
| FIN-S09 | Anomaly Center | Finance Manager | AI flags |
| FIN-S10 | FX / Missions | Treasurer | Multi-currency |

### M12 Analytics

| Screen ID | Name | Actors | Key widgets |
|---|---|---|---|
| ANA-S01 | Dashboards Hub | Senior Pastor | Module tiles |
| ANA-S02 | Membership Dash | Senior Pastor | Growth KPIs |
| ANA-S03 | Visitor Funnel Dash | Pastor | Source enum charts |
| ANA-S04 | Care Cell Dash | Care Cell Leader | Scoped |
| ANA-S05 | Care Aggregates | Senior Pastor | Welfare + counselling counts |
| ANA-S06 | Finance Dash | Finance Manager | Giving/funds |
| ANA-S07 | COM Performance | Ministry Leader | Channel success |
| ANA-S08 | Insights Feed | Senior Pastor | AI cards |
| ANA-S09 | Export Center | Analyst, Admin | Async + Power BI |

---

## 5. Wireframe-level layouts (representative)

Layouts use regions: **Header / Filters / Main / Side / Actions**. Apply the same pattern to sibling screens.

### 5.1 MEM-S02 Member Profile

| Region | Content |
|---|---|
| Header | Membership ID chip, status badge, campus, photo |
| Filters | N/A (profile context) |
| Main | Tabs: Overview · Family · Ministries/Skills · Classes · Documents · Timeline |
| Side | Engagement score + AI ministry suggestions; Care Cell card |
| Actions | Edit, Change Status, Transfer, Message (COM) |

### 5.2 VIS-S04 Pipeline Kanban

| Region | Content |
|---|---|
| Header | “Visitor Pipeline”, campus switcher |
| Filters | Date range, source enum multi-select, assignee |
| Main | Columns New→Contacted→Engaged→Class Invited→Converted / Lost; cards with Day-N SLA dots |
| Side | Selected visitor summary + next follow-up |
| Actions | Register Visitor, Convert, Export |

### 5.3 COUN-S03 Case Workspace

| Region | Content |
|---|---|
| Header | Case id, category, risk pill (Low/Moderate/High) |
| Filters | Session date range |
| Main | Session list + referral panel; **Notes behind explicit “Reveal confidential”** with audit |
| Side | AI risk/referral suggestions (confirm) |
| Actions | Schedule Session, Set Risk, Refer, Close |

### 5.4 WEL-S04 Approval Desk

| Region | Content |
|---|---|
| Header | Request id, amount/currency, beneficiary label (masked) |
| Filters | Pending my approval / all |
| Main | Stepper: Assessment → Review → Approvals; narrative ACL-gated |
| Side | Prior aid summary + AI eligibility |
| Actions | Approve, Reject (reason), Request info, Open in WCE |

### 5.5 WCE-S03 / S04 Scoring & Rankings

| Region | Content |
|---|---|
| Header | Session name, weight profile version |
| Filters | Case toggle (≤5) |
| Main | Matrix rows = cases, columns = A–I; below: rank table + radar |
| Side | AI outlier callouts |
| Actions | Save scores, Finalize decision, Export Power BI |

### 5.6 CER-S03 Dedication Approvals

| Region | Content |
|---|---|
| Header | Ceremony type, child given name (ACL) |
| Filters | Status steps |
| Main | Vertical stepper Care Cell → Elder → Pastor with comments |
| Side | Family link, Care Cell |
| Actions | Approve, Reject, Advance to Schedule |

### 5.7 SLOT-S02 Agenda Builder

| Region | Content |
|---|---|
| Header | Service type (Fri/Sun/Special), datetime, publish state |
| Filters | Program slot visibility |
| Main | Six lanes (Before Worship … Before Closing Prayer) with timed cards |
| Side | Conflict list + AI capacity meter |
| Actions | Insert, Link Ceremony, Publish, Optimize (AI) |

### 5.8 ROST-S06 AI Scheduler

| Region | Content |
|---|---|
| Header | Week range, activity types |
| Filters | Campus, ministry |
| Main | Proposed assignments grid with fairness heatmap |
| Side | Conflicts + alternates |
| Actions | Regenerate, Accept draft, Publish & Notify (4 channels) |

### 5.9 COM-S02 Composer

| Region | Content |
|---|---|
| Header | Content type (Flyer/Video/Announcement/Event/Devotion) |
| Filters | Audience builder |
| Main | Channel toggles; body editor; attachment dropzone with live policy (Email blocks MP4) |
| Side | Consent coverage estimate; AI tone/devotion assist |
| Actions | Save draft, Approve, Send/Schedule |

### 5.10 FIN-S06 / S09 Approvals & Anomalies

| Region | Content |
|---|---|
| Header | Queue type |
| Filters | Amount threshold, currency, fund |
| Main | Voucher table with initiator ≠ approver indicator; anomaly rationale |
| Side | Tally sync status |
| Actions | Approve, Override anomaly (reason), Sync |

### 5.11 ANA-S01 Dashboards Hub

| Region | Content |
|---|---|
| Header | Executive Overview, staleness clock |
| Filters | Campus, date range, ministry |
| Main | Widget grid (RBAC-pruned); insight cards strip |
| Side | Saved filter presets; export jobs |
| Actions | Refresh cache, Open Power BI export, Pin insight |

---

## 6. Responsive / mobile considerations

| Breakpoint | Behavior |
|---|---|
| ≥1280px | Left rail + optional side inspector |
| 768–1279px | Collapsed rail icons; side becomes bottom sheet |
| &lt;768px | Bottom tab bar (mobile IA §2.2); tables → card lists; steppers full-width |
| Kanban (VIS) | Horizontal scroll columns; drag optional on mobile (button “Move stage”) |
| Agenda (SLOT) | Single-column timeline by program slot |
| Scoring (WCE) | Category accordion per case instead of wide matrix |
| Charts | Prefer simple bars; radar optional desktop-only with data table alternative |
| Attachments | Camera roll / file picker; show remaining size vs 50MB |
| Offline | Read-only agenda/duties cache (Phase 3); no offline confidential COUN notes |

Touch targets ≥44×44 CSS px; sticky primary actions above safe-area insets.

---

## 7. Accessibility notes (WCAG 2.2 AA)

| Area | Requirement |
|---|---|
| Perceivable | Text alternatives for icons; charts need data table or text summary; don’t rely on color alone for risk (Low/Moderate/High) — include text + icon |
| Contrast | 4.5:1 body text; 3:1 UI components; status badges meet contrast |
| Operable | Full keyboard: rail, dialogs, Kanban move menus; focus visible; no keyboard trap in Copilot panel |
| Target size | WCAG 2.2 target size (minimum) for icon buttons |
| Consistent help | Help/Copilot control in consistent header location |
| Forms | Labels, errors linked via `aria-describedby`; required fields announced |
| Confidential reveal | Explicit control; announce state to AT; confirm before show |
| Motion | Respect `prefers-reduced-motion`; avoid auto-playing MP4 in portal |
| Auth | MFA flows operable without mouse; timeout warnings with extend option |
| Language | Page `lang`; avoid images of text for critical instructions |
| Testing | Automated axe + manual NVDA/VoiceOver on MEM profile, COUN notes reveal, COM composer policy errors, FIN approve |

---

## 8. Cross-cutting UI patterns

| Pattern | Usage |
|---|---|
| Empty states | Guidance + primary CTA |
| Soft-delete restore | Admin banner |
| Audit “why” drawer | Status/approval changes |
| Copilot | Side panel; accept/edit/reject |
| Masked PII | Lists show partial mobile/email |
| Export jobs | Toast + notification when ready |
| Campus switcher | Persists per session; cleared on logout |

---

## 9. Traceability

| Module | Design spec | Screens prefix |
|---|---|---|
| MEM | [M01](../modules/M01-membership.md) | MEM-S* |
| VIS | [M02](../modules/M02-visitor.md) | VIS-S* |
| COUN | [M03](../modules/M03-counselling.md) | COUN-S* |
| PRAY | [M04](../modules/M04-prayer.md) | PRAY-S* |
| WEL | [M05](../modules/M05-welfare.md) | WEL-S* |
| WCE | [M06](../modules/M06-welfare-comparison.md) | WCE-S* |
| CER | [M07](../modules/M07-ceremonies.md) | CER-S* |
| SLOT | [M08](../modules/M08-service-slots.md) | SLOT-S* |
| ROST | [M09](../modules/M09-activity-roster.md) | ROST-S* |
| COM | [M10](../modules/M10-communication.md) | COM-S* |
| FIN | [M11](../modules/M11-finance.md) | FIN-S* |
| ANA | [M12](../modules/M12-analytics.md) | ANA-S* |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial screens & navigation baseline |
