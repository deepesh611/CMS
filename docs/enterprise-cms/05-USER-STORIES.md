# User Stories

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 05 — User Stories |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Related** | [00-INDEX](00-INDEX.md) · [01-BRS](01-BRS.md) · [02-FRS](02-FRS.md) · [03-USE-CASES](03-USE-CASES.md) |

**Story points:** S ≈ 1–2d · M ≈ 3–5d · L ≈ 1–2w · XL ≈ multi-sprint  
**Format:** As a [role], I want [capability], so that [outcome]  
**AC:** Acceptance Criteria (3–5 bullets)

---

## EPIC-01 — Membership Management

**Goal:** Full membership lifecycle, families, status, baptism/transfer/classes, AI engagement assist.  
**FRs:** FR-MEM-* · **UCs:** UC-01…03, UC-27

### US-01-001 — Register member
**As an** Administrator, **I want** to register Member A with required profile fields and generated Membership ID, **so that** the church has a system of record.  
**AC:**
- Required fields enforced; Membership ID unique per tenant
- Care Cell and ministries assignable on create
- Audit event without PII values in logs
- Campus scoped correctly  
**Points:** M

### US-01-002 — Family management
**As a** Care Cell Leader, **I want** to link spouse and children under one Family ID, **so that** household pastoral care is coordinated.  
**AC:**
- Spouse link bidirectional
- Unlimited children supported
- Conflict if spouse already linked resolved via UI
- Family searchable from either member  
**Points:** M

### US-01-003 — Status transitions
**As a** Pastor, **I want** controlled membership status changes with reasons, **so that** lifecycle is auditable.  
**AC:**
- Only allowed transitions succeed
- Reason mandatory
- History visible to authorized roles
- Deceased stops marketing COM  
**Points:** S

### US-01-004 — Baptism tracking
**As an** Elder, **I want** to record baptism date/campus/officiant/certificate, **so that** sacramental history is complete.  
**AC:**
- Fields saved on member
- Certificate upload ≤50MB allowed types
- Links to CER baptism ceremony when present  
**Points:** S

### US-01-005 — Membership transfer
**As a** Pastor, **I want** transfer-in/out workflows, **so that** multi-campus/church moves are tracked.  
**AC:**
- Source/destination and effective date captured
- Local roster/ministry closures prompted on transfer-out
- Status set Transferred Out/In  
**Points:** M

### US-01-006 — Membership classes
**As a** Ministry Leader, **I want** to enrol prospects in classes and mark completion, **so that** reception eligibility is clear.  
**AC:**
- Enrolment + attendance
- Completion unlocks Membership Reception path
- Reports by class cohort  
**Points:** M

### US-01-007 — Member classification tags
**As an** Administrator, **I want** multi-select classification tags, **so that** segments drive COM and analytics.  
**AC:**
- Configurable tag list per tenant
- Filter members by tags
- Tags appear in ANA filters  
**Points:** S

### US-01-008 — Document & photo storage
**As an** Administrator, **I want** secure document/photo storage, **so that** records are complete without local disk risk.  
**AC:**
- Pluggable storage backend
- Access controlled by RBAC
- Virus/type/size validation  
**Points:** M

### US-01-009 — AI engagement score
**As a** Care Cell Leader, **I want** an explainable engagement score for Member A, **so that** I prioritize follow-up.  
**AC:**
- Score + top factors shown
- Accept/dismiss logged
- Feature-flagged; no auto actions  
**Points:** L

### US-01-010 — AI ministry suitability
**As a** Ministry Leader, **I want** AI ministry recommendations from skills/talents, **so that** volunteering fit improves.  
**AC:**
- Rationale + confidence
- One-click invite draft
- Human must confirm assignment  
**Points:** L

### US-01-011 — New member notification
**As a** Care Cell Leader, **I want** WhatsApp/Email/Push when Member A is assigned to my cell, **so that** I welcome promptly.  
**AC:**
- Respects channel prefs/consent
- Deep link to member profile
- Delivery logged  
**Points:** S

### US-01-012 — Portal self-registration
**As a** Visitor converting online, **I want** to submit a membership application, **so that** admin can verify and activate.  
**AC:**
- Campus required
- Status pending until verified
- Duplicate checks run  
**Points:** L

---

## EPIC-02 — Visitor Management

**Goal:** Intelligent visitor-to-member conversion with mandatory Day 1/3/7/14/30 follow-ups.  
**FRs:** FR-VIS-* · **UCs:** UC-04…06, UC-26

### US-02-001 — Register visitor with source enum
**As a** Volunteer, **I want** to register Visitor B with the exact Visitor Source list, **so that** acquisition analytics are accurate.  
**AC:**
- Dropdown values exactly: Friend, Church Member, Family Member, Care Cell Member, Pastor, Ministry Leader, Church Event, Outreach Program, Website, Facebook, Instagram, YouTube, WhatsApp, Google Search, Walk-In, Advertisement, Other
- Referrer required for person-based sources
- Campus/service captured  
**Points:** M

### US-02-002 — Auto follow-up plan
**As a** Care Cell Leader, **I want** Day 1, 3, 7, 14, 30 tasks auto-created, **so that** no visitor is dropped.  
**AC:**
- Five tasks with due dates from first visit
- Default assignee configurable
- Notifications on create/due/overdue  
**Points:** L

### US-02-003 — Complete follow-up task
**As a** Care Cell Leader, **I want** to log outcomes on follow-ups, **so that** the pipeline reflects reality.  
**AC:**
- Outcome code mandatory
- Overdue escalation works
- Pipeline stage updates  
**Points:** S

### US-02-004 — Conversion to member
**As a** Pastor, **I want** one-click convert Visitor B → Member, **so that** history is preserved.  
**AC:**
- Field mapping confirmed by actor
- Visitor stage=Converted
- Remaining tasks cancelled  
**Points:** M

### US-02-005 — Visitor analytics
**As a** Senior Pastor, **I want** conversion analytics by source/campus, **so that** outreach investment is guided.  
**AC:**
- Conversion rate and time-to-convert
- Filters by date/campus
- Export CSV  
**Points:** M

### US-02-006 — Duplicate detection
**As an** Administrator, **I want** merge suggestions for likely duplicate visitors, **so that** data quality stays high.  
**AC:**
- Heuristics on mobile/email/name+DOB
- Merge preserves follow-up history
- Audited  
**Points:** L

### US-02-007 — AI engagement & conversion assist
**As a** Care Cell Leader, **I want** AI engagement score and next-best follow-up, **so that** I prioritize hot leads.  
**AC:**
- Score + suggested channel
- Human sends message
- Escalation suggestion for Pastor when threshold hit  
**Points:** L

### US-02-008 — Pastoral escalation
**As a** Pastor, **I want** alerts when Visitor B needs pastoral attention, **so that** sensitive cases get care.  
**AC:**
- Threshold configurable
- Push/Email to Pastor
- No confidential prayer text on SMS  
**Points:** M

### US-02-009 — Pipeline Kanban
**As a** Ministry Leader, **I want** a visitor pipeline board, **so that** team workload is visible.  
**AC:**
- Stages New→…→Converted/Lost
- Drag-drop with permission
- Counts per stage  
**Points:** M

### US-02-010 — WhatsApp follow-up template
**As a** Care Cell Leader, **I want** approved WhatsApp templates for Day-N messages, **so that** outreach is compliant.  
**AC:**
- Template picker
- Opt-in enforced
- Delivery webhook updates status  
**Points:** M

---

## EPIC-03 — Counselling Management

**Goal:** Confidential Christian counselling cases with categories, risk, sessions, referrals.  
**FRs:** FR-COUN-* · **UCs:** UC-07, UC-08

### US-03-001 — Open case with category
**As a** Counsellor, **I want** to open a case with standard categories, **so that** caseload is classifiable.  
**AC:**
- Categories: Marriage, Family, Youth, Addiction, Mental Health, Career, Grief, Trauma, Financial, Spiritual Care, Leadership Mentoring, Church Conflict
- Counselee linked
- Campus set  
**Points:** M

### US-03-002 — Set risk level
**As a** Counsellor, **I want** to set risk Low/Moderate/High, **so that** urgency is clear.  
**AC:**
- Only three levels allowed
- High notifies Senior Pastor
- SLA tighter for High  
**Points:** S

### US-03-003 — Session notes confidentiality
**As a** Counsellor, **I want** confidential session notes visible only to me and Senior Pastor, **so that** pastoral trust is protected.  
**AC:**
- Field-level ACL enforced
- Unauthorized access denied + audited
- Notes never sent via SMS/WhatsApp  
**Points:** L

### US-03-004 — Schedule follow-up session
**As a** Counsellor, **I want** to schedule follow-ups with reminders, **so that** care continuity holds.  
**AC:**
- Calendar entry
- Reminder without note body
- Missed session flaggable  
**Points:** S

### US-03-005 — Referral management
**As a** Counsellor, **I want** to record internal/external referrals, **so that** handoffs are tracked.  
**AC:**
- Referral type/status
- No EHR clinical detail required
- Case can move to Referred  
**Points:** M

### US-03-006 — Case closure
**As a** Counsellor, **I want** to close cases with outcome codes, **so that** backlog is accurate.  
**AC:**
- Outcome mandatory
- Closed cases read-only except Senior Pastor reopen
- Stats feed ANA (aggregates only)  
**Points:** S

### US-03-007 — AI risk suggestion
**As a** Counsellor, **I want** AI risk suggestions I can confirm, **so that** High cases are not missed.  
**AC:**
- Suggestion not auto-applied
- Rationale shown
- Confirm updates risk + audit  
**Points:** L

### US-03-008 — AI referral suggestions
**As a** Counsellor, **I want** AI referral suggestions, **so that** I consider appropriate next steps.  
**AC:**
- List of options + reasons
- Accept creates draft referral
- Feature-flagged  
**Points:** M

### US-03-009 — Counselling dashboard widget
**As a** Senior Pastor, **I want** open-case counts by risk (no note text), **so that** I oversee safely.  
**AC:**
- Aggregates only
- Drill-down respects ACL
- Campus filter  
**Points:** S

### US-03-010 — Session reminder push
**As a** Member A, **I want** a push reminder for my counselling appointment time, **so that** I attend.  
**AC:**
- Time/location only
- Opt-in respected
- Cancellable with session  
**Points:** S

---

## EPIC-04 — Prayer Support Management

**Goal:** Prayer requests, teams, escalations, testimonies, AI prayer assist.  
**FRs:** FR-PRAY-* · **UCs:** UC-09, UC-10

### US-04-001 — Submit categorized prayer
**As a** Member, **I want** to submit a prayer request in a standard category, **so that** teams can respond.  
**AC:**
- Categories: Spiritual Growth, Healing, Family, Financial, Career, Education, Emotional Support, Church Growth, Ministry, Emergency, Special Needs
- Confidentiality flag
- Confirmation to submitter  
**Points:** M

### US-04-002 — Assign prayer team
**As a** Pastor, **I want** to assign requests to prayer teams, **so that** coverage is organized.  
**AC:**
- Team roster
- Assign/reassign audited
- Team notified  
**Points:** S

### US-04-003 — Emergency escalation
**As a** Prayer Team Lead, **I want** Emergency escalation to Pastor/Senior Pastor, **so that** urgent needs get immediate care.  
**AC:**
- Immediate Push/SMS/WhatsApp
- Quiet hours override with confirm
- Ack required  
**Points:** M

### US-04-004 — Confidential prayer wall exclusion
**As a** Member, **I want** confidential requests hidden from public walls, **so that** privacy is kept.  
**AC:**
- Not listed on portal wall
- Team-only visibility
- Export excludes body by default  
**Points:** S

### US-04-005 — Record testimony
**As a** Care Cell Leader, **I want** to link a testimony to an answered request, **so that** the church celebrates safely.  
**AC:**
- Consent to publish
- Linked request status updated
- Share via COM optional  
**Points:** S

### US-04-006 — AI scripture & prayer draft
**As a** Pastor, **I want** AI scripture suggestions and prayer drafts, **so that** I prepare faster.  
**AC:**
- Draft editable
- Must approve before share
- Rejection logged  
**Points:** L

### US-04-007 — Follow-up on prayer
**As a** Prayer Team member, **I want** follow-up tasks on open requests, **so that** people are not forgotten.  
**AC:**
- Due dates
- Completion outcomes
- Reminders  
**Points:** S

### US-04-008 — Prayer analytics
**As a** Senior Pastor, **I want** category volume trends (no request text), **so that** pastoral themes are visible.  
**AC:**
- Aggregates by category/campus
- Confidential bodies excluded
- Date filters  
**Points:** S

### US-04-009 — Mobile prayer submit
**As a** Member on mobile, **I want** to submit prayer from the app, **so that** barriers are low.  
**AC:**
- Same validations as web
- Offline draft optional (Phase 3)
- Push on team response (non-sensitive)  
**Points:** M

### US-04-010 — Integration: WhatsApp prayer acknowledge
**As a** Prayer Team Lead, **I want** WhatsApp ack templates, **so that** requesters know they are covered.  
**AC:**
- Template-only outbound
- Opt-in required
- No confidential text in template vars beyond first name policy  
**Points:** M

---

## EPIC-05 — Welfare Management

**Goal:** Request → assess → approve → assist → review with allowed requestors only.  
**FRs:** FR-WEL-* · **UCs:** UC-11, UC-12

### US-05-001 — Create welfare request (allowed roles)
**As a** Care Cell Leader, **I want** to create a welfare request for Member A, **so that** needs enter the formal process.  
**AC:**
- Only Care Cell Leader, Associate Care Cell Leader, Counsellor, Ministry Leader, Pastor can create
- Amount + currency + docs
- Status Submit  
**Points:** M

### US-05-002 — Case assessment
**As a** Welfare Team member, **I want** structured assessment fields, **so that** decisions are consistent.  
**AC:**
- Household/prior aid captured
- Checklist complete before review
- Attachments validated  
**Points:** M

### US-05-003 — Multi-level approval
**As a** Pastor, **I want** threshold-based approvals with SoD, **so that** funds are stewarded.  
**AC:**
- Matrix by amount
- Approver ≠ requestor for high tiers
- Reject with reason  
**Points:** L

### US-05-004 — Disburse assistance
**As a** Treasurer, **I want** to record disbursement linked to Welfare Fund, **so that** books reconcile.  
**AC:**
- Fund balance updates
- Optional FIN voucher
- Beneficiary notified (non-sensitive)  
**Points:** M

### US-05-005 — Follow-up review
**As a** Welfare Team member, **I want** post-assistance reviews, **so that** impact is verified.  
**AC:**
- Scheduled tasks
- Outcomes recorded
- Re-open request possible  
**Points:** S

### US-05-006 — AI eligibility score
**As a** Welfare Team member, **I want** AI eligibility/risk scores, **so that** I triage faster.  
**AC:**
- Explainable factors
- Not auto-approve
- Logged accept/override  
**Points:** L

### US-05-007 — Notifications on state change
**As a** Requestor, **I want** Email/Push/WhatsApp on approvals/rejections, **so that** I can update Member A.  
**AC:**
- Channel prefs
- No bank details in SMS
- Delivery logged  
**Points:** S

### US-05-008 — Welfare history on member
**As a** Pastor, **I want** to see prior assistance summary for Member A, **so that** patterns are visible.  
**AC:**
- ACL protected
- Aggregates + dates
- Links to cases  
**Points:** S

### US-05-009 — Document pack upload
**As a** Care Cell Leader, **I want** to upload supporting PDFs/images ≤50MB, **so that** assessment is evidenced.  
**AC:**
- Type/size validation
- Virus scan hook
- Access limited to WEL roles  
**Points:** S

### US-05-010 — Finance anomaly on welfare pay
**As a** Finance Manager, **I want** duplicate payment detection on welfare disbursements, **so that** errors are caught.  
**AC:**
- Flag before final post
- Override requires reason
- Feeds FR-FIN-031  
**Points:** M

---

## EPIC-06 — Welfare Comparison Engine

**Goal:** Compare ≤5 cases across A–I categories with weights, rankings, Power BI.  
**FRs:** FR-WCE-* · **UCs:** UC-13

### US-06-001 — Select up to five cases
**As a** Welfare Team lead, **I want** to select up to 5 cases for comparison, **so that** board decisions are fair.  
**AC:**
- Hard cap 5
- Only assessed cases eligible
- Session named/saved  
**Points:** M

### US-06-002 — Score categories A–I
**As a** Senior Pastor, **I want** to score A–I categories, **so that** trade-offs are explicit.  
**AC:**
- Categories exactly A.Eligibility … I.Recommendation
- Scores persisted
- Incomplete scoring warned  
**Points:** L

### US-06-003 — Configurable weights
**As an** Administrator, **I want** tenant weights summing to 100%, **so that** policy reflects leadership priorities.  
**AC:**
- Weight editor
- Validation sum=100
- Versioned with effective date  
**Points:** M

### US-06-004 — Rankings and charts
**As a** Finance Manager, **I want** rankings and radar/bar charts, **so that** meetings are data-driven.  
**AC:**
- Rank by weighted total
- Charts render for session
- Printable summary  
**Points:** M

### US-06-005 — Record board decision
**As a** Senior Pastor, **I want** to record the comparison outcome, **so that** audit shows why cases won/lost.  
**AC:**
- Decision + notes (ACL)
- Links back to WEL cases
- Immutable after lock  
**Points:** S

### US-06-006 — Power BI export
**As an** Analyst, **I want** to export comparison datasets to Power BI, **so that** exec packs are reusable.  
**AC:**
- No confidential free-text by default
- Secure export permission
- Job status visible  
**Points:** L

### US-06-007 — Executive WCE widget
**As a** Senior Pastor, **I want** a dashboard widget of recent comparisons, **so that** I track decision throughput.  
**AC:**
- Last N sessions
- Drill to session
- Role gated  
**Points:** S

### US-06-008 — AI outlier highlight
**As a** Welfare Team lead, **I want** AI to highlight scoring outliers, **so that** human error is reduced.  
**AC:**
- Advisory only
- Accept/dismiss
- Feature-flagged  
**Points:** M

### US-06-009 — Notify decision board
**As an** Administrator, **I want** notifications when a comparison is finalized, **so that** stakeholders align.  
**AC:**
- Email/Push
- Deep link
- Recipients configurable  
**Points:** S

### US-06-010 — Audit comparison session
**As an** Auditor, **I want** read-only access to who compared which cases and weights, **so that** governance holds.  
**AC:**
- Full session metadata
- No silent edits post-lock
- Export for audit pack  
**Points:** S

---

## EPIC-07 — Church Ceremonies & Member Functions

**Goal:** Catalogue ceremonies; baby dedication workflow; banns/weddings; certificates.  
**FRs:** FR-CER-* · **UCs:** UC-14, UC-15, UC-27

### US-07-001 — Ceremony catalogue
**As an** Administrator, **I want** all ceremony types available, **so that** ops are standardized.  
**AC:**
- Types: Baby Dedication, Baptism, Membership Reception, Thanksgiving, Wedding Anniversary, House Blessing, Marriage Banns, Wedding Service, Funeral Service, Memorial Service
- Request→approve→schedule pattern  
**Points:** M

### US-07-002 — Baby dedication data capture
**As a** Care Cell Leader, **I want** to capture child and parent fields, **so that** dedication records are complete.  
**AC:**
- Child Name, Given Name, DOB, Place of Birth, Father Name, Mother Name
- Linked to family
- Validation on dates  
**Points:** M

### US-07-003 — Dedication approval chain
**As an** Elder, **I want** Care Cell → Elder → Pastoral approval, **so that** polity is respected.  
**AC:**
- Each step records actor/time
- Reject returns with comments
- Cannot schedule until Pastoral Approval  
**Points:** L

### US-07-004 — Schedule dedication in service
**As a** Pastor, **I want** to place dedication in a service slot, **so that** the agenda is accurate.  
**AC:**
- Integrates with SLOT
- Conflict detection
- Certificate generation after complete  
**Points:** M

### US-07-005 — Marriage banns
**As a** Pastor, **I want** to publish banns with objection tracking, **so that** weddings proceed orderly.  
**AC:**
- Bride/Groom/Parents/Date/Venue/Counselling Status
- Objection workflow
- Hold blocks wedding schedule  
**Points:** L

### US-07-006 — Counselling gate for wedding
**As an** Elder, **I want** incomplete counselling to block wedding scheduling when configured, **so that** preparation standards hold.  
**AC:**
- Config flag per tenant
- Clear error message
- Override only Senior Pastor + audit  
**Points:** S

### US-07-007 — Wedding certificate
**As an** Administrator, **I want** certificate generation for weddings, **so that** records are official.  
**AC:**
- Template per tenant
- PDF stored
- Access controlled  
**Points:** M

### US-07-008 — Funeral / memorial records
**As a** Pastor, **I want** funeral/memorial ceremony records linked to Member A, **so that** care and COM can respond appropriately.  
**AC:**
- Sensitive flags
- Stops birthday automation
- Limited distribution lists  
**Points:** M

### US-07-009 — Baptism ceremony + member update
**As a** Pastor, **I want** completing baptism to update member baptism fields, **so that** data stays consistent.  
**AC:**
- Single source of truth
- Certificate optional
- Slot link optional  
**Points:** S

### US-07-010 — Ceremony notifications
**As a** Ministry Leader, **I want** Email/WhatsApp/Push on schedule changes, **so that** teams show up.  
**AC:**
- Owners notified
- Prefs respected
- Agenda deep link  
**Points:** S

### US-07-011 — Membership reception after class
**As a** Pastor, **I want** to schedule Membership Reception for class completers, **so that** new members are welcomed.  
**AC:**
- Eligibility from MEM classes
- Bulk candidates list
- Ceremony record created  
**Points:** M

---

## EPIC-08 — Service Slot Management

**Goal:** Insert functions into Friday/Sunday/Special services across defined program slots.  
**FRs:** FR-SLOT-* · **UCs:** UC-16

### US-08-001 — Define service instances
**As an** Administrator, **I want** Friday Main, Sunday Main, and Special Service instances, **so that** calendars are structured.  
**AC:**
- Three service types
- Campus + datetime
- Publish state  
**Points:** M

### US-08-002 — Insert into program slot
**As a** Pastor, **I want** to insert a function into a program slot, **so that** order of service is clear.  
**AC:**
- Slots: Before Worship, After Worship, Before Sermon, After Sermon, During Announcements, Before Closing Prayer
- Duration + owner required
- Conflict blocked  
**Points:** M

### US-08-003 — Conflict detection
**As an** Elder, **I want** automatic conflict detection, **so that** double-booking is avoided.  
**AC:**
- Same slot/time conflict
- Resource/person conflicts when linked
- Suggestions offered  
**Points:** M

### US-08-004 — Publish agenda
**As a** Ministry Leader, **I want** to publish the agenda to COM channels, **so that** the church is informed.  
**AC:**
- Channel select
- Versioned agenda
- Notify owners on change  
**Points:** S

### US-08-005 — AI capacity validation
**As a** Pastor, **I want** AI to warn if agenda exceeds service length, **so that** services stay on time.  
**AC:**
- Warning non-blocking or blocking per config
- Rationale shown
- Override audited  
**Points:** M

### US-08-006 — AI agenda optimization
**As a** Pastor, **I want** optimization suggestions for slot order, **so that** flow improves.  
**AC:**
- Suggestions accept/edit/reject
- Feature-flagged
- No auto-reorder without confirm  
**Points:** L

### US-08-007 — Special service template
**As an** Administrator, **I want** templates for Special Services, **so that** setup is fast.  
**AC:**
- Clone template
- Edit slots
- Retain owners optional  
**Points:** S

### US-08-008 — Mobile agenda view
**As a** Volunteer, **I want** to see today’s agenda on mobile, **so that** I know my cue.  
**AC:**
- Read-only
- Campus filtered
- Offline cache optional later  
**Points:** S

### US-08-009 — Link ceremony to slot
**As a** Pastor, **I want** to link CER ceremonies into slots, **so that** dedications/baptisms appear on the agenda.  
**AC:**
- Bidirectional link
- Status sync
- Certificate still from CER  
**Points:** M

### US-08-010 — Owner change notification
**As a** Ministry Leader, **I want** Push/Email when my agenda item changes, **so that** I adapt.  
**AC:**
- Diff summary
- Quiet hours except publish day policy
- Delivery log  
**Points:** S

---

## EPIC-09 — Church Activity Roster

**Goal:** Central rostering with AI fairness/conflicts and omnichannel notify.  
**FRs:** FR-ROST-* · **UCs:** UC-17, UC-25

### US-09-001 — Roster activity types
**As a** Ministry Leader, **I want** roster support for core activity types, **so that** scheduling is centralized.  
**AC:**
- Sermons, Counselling, Hospital Visits, Care Cell Meetings, Ministry Events, Worship Teams, Volunteers, Friday School
- Campus/location fields  
**Points:** M

### US-09-002 — Assign person to occurrence
**As a** Ministry Leader, **I want** to assign Member A to a dated activity, **so that** coverage is clear.  
**AC:**
- Assignment saved
- Conflict check runs
- History retained  
**Points:** S

### US-09-003 — Substitution workflow
**As a** Volunteer, **I want** to decline and suggest a substitute, **so that** gaps are filled.  
**AC:**
- Decline reason
- Leader notified
- Substitute confirm path  
**Points:** M

### US-09-004 — Omnichannel assignment notify
**As a** Volunteer, **I want** Email/SMS/WhatsApp/Push when assigned, **so that** I never miss duty.  
**AC:**
- All four channels supported
- Prefs/consent applied
- Reminder cadence configurable  
**Points:** M

### US-09-005 — AI conflict detection
**As a** Ministry Leader, **I want** AI/system conflict detection on double-booking, **so that** people are not over-scheduled.  
**AC:**
- Blocks or warns per config
- Shows conflicting items
- Suggests alternates  
**Points:** M

### US-09-006 — AI rotation & fairness
**As a** Pastor, **I want** fair rotation suggestions, **so that** load is balanced.  
**AC:**
- Fairness metrics visible
- Accept creates draft roster
- Human publish required  
**Points:** L

### US-09-007 — Availability capture
**As a** Volunteer, **I want** to set weekly availability, **so that** matching is realistic.  
**AC:**
- Recurring availability
- Exceptions for dates
- Used by matcher  
**Points:** M

### US-09-008 — Friday School teacher scope
**As a** Friday School teacher, **I want** to see only my classes, **so that** privacy/least privilege holds.  
**AC:**
- Scoped lists
- Coordinator sees all
- Aligns RBAC  
**Points:** S

### US-09-009 — M365 calendar sync
**As a** Ministry Leader, **I want** roster items synced to Microsoft 365 calendars, **so that** staff plan in Outlook.  
**AC:**
- OIDC consent
- External id stored
- Failure queued + admin alert  
**Points:** L

### US-09-010 — Hospital visit roster
**As a** Care Cell Leader, **I want** to schedule hospital visits with pastoral sensitivity flags, **so that** care is coordinated without oversharing.  
**AC:**
- Flag limits COM content
- Assignee notified
- Outcome log  
**Points:** M

### US-09-011 — Sermon speaker schedule
**As a** Senior Pastor, **I want** sermon roster with series metadata, **so that** preaching calendar is planned.  
**AC:**
- Series/title fields
- Conflict with other duties
- Publish to agenda optional  
**Points:** S

---

## EPIC-10 — Communication & Digital Engagement

**Goal:** Omnichannel COM with file rules, devotion, push scheduling.  
**FRs:** FR-COM-* · **UCs:** UC-18, UC-19, UC-28

### US-10-001 — Multi-channel composer
**As a** Ministry Leader, **I want** to compose once and send via Email/WhatsApp/SMS/Push/Portal, **so that** messaging is consistent.  
**AC:**
- Channel toggles
- Segment audience
- Consent enforced  
**Points:** L

### US-10-002 — Attachment policy
**As an** Administrator, **I want** file type/size rules enforced, **so that** channels stay reliable.  
**AC:**
- Max 50MB
- Allow PDF/JPG/JPEG/PNG/BMP/GIF/MP4
- Email rejects MP4; allows images+PDF only  
**Points:** M

### US-10-003 — Daily devotion broadcast
**As a** Pastor, **I want** to publish Verse/Prayer/Reflection/Article to WhatsApp/Email/App/Portal, **so that** daily discipleship scales.  
**AC:**
- Four content parts
- Human approve if AI-drafted
- Delivery metrics  
**Points:** L

### US-10-004 — Push scheduling modes
**As an** Administrator, **I want** Immediate/Scheduled/Recurring push, **so that** ops can automate reminders.  
**AC:**
- Three modes work
- Timezone = campus
- Cancel/update supported  
**Points:** M

### US-10-005 — Emergency alert
**As a** Senior Pastor, **I want** emergency push (+ optional SMS), **so that** the church gets urgent instructions.  
**AC:**
- Permission-gated
- Quiet hours override confirm
- Delivery dashboard  
**Points:** M

### US-10-006 — Event reminder push
**As a** Member, **I want** event reminders, **so that** attendance improves.  
**AC:**
- Types include Event Reminders
- Opt-out possible
- Deep link to event  
**Points:** S

### US-10-007 — AI devotion draft
**As a** Pastor, **I want** AI to draft devotion content, **so that** preparation time drops.  
**AC:**
- Editable draft
- Must approve to send
- Safety filter  
**Points:** L

### US-10-008 — Flyer distribution
**As a** Ministry Leader, **I want** to attach flyers (images/PDF) to announcements, **so that** events are promoted.  
**AC:**
- Preview
- Channel-specific attachment rules applied
- Portal listing  
**Points:** S

### US-10-009 — Delivery logging
**As an** Administrator, **I want** provider delivery logs without unnecessary PII, **so that** we debug safely.  
**AC:**
- Status + provider ids
- No full message body in logs
- Retention policy  
**Points:** M

### US-10-010 — WhatsApp template library
**As a** Care Cell Leader, **I want** an approved template library, **so that** outreach stays compliant.  
**AC:**
- Template CRUD by Admin
- Variables sanitized
- Failed template send surfaces error  
**Points:** M

### US-10-011 — M365 email send path
**As an** Administrator, **I want** optional send-via Microsoft Graph, **so that** mail aligns with church M365 tenant.  
**AC:**
- Config switch SMTP vs Graph
- Secrets in store
- Health check  
**Points:** L

### US-10-012 — Video share non-email
**As a** Ministry Leader, **I want** to share MP4 via WhatsApp/Portal/App but not Email, **so that** policy is respected.  
**AC:**
- Email path strips/blocks MP4
- Other channels accept ≤50MB
- User warned in UI  
**Points:** S

---

## EPIC-11 — Finance Management

**Goal:** Enterprise giving/funds/expenses, multi-currency, Tally, AI anomalies.  
**FRs:** FR-FIN-* · **UCs:** UC-20, UC-21, UC-29, UC-30

### US-11-001 — Record tithe/offering/donation
**As a** Treasurer, **I want** to record giving against Member A or anonymous policy, **so that** funds are tracked.  
**AC:**
- Types supported
- Currency from approved list
- Receipt number  
**Points:** M

### US-11-002 — Multi-currency capture
**As a** Finance Manager, **I want** OMR/USD/EUR/GBP/AED/SAR/INR/QAR/KWD/BHD, **so that** regional giving works.  
**AC:**
- All 10 codes selectable
- Base currency conversion with rate date
- Exchange gain/loss posting  
**Points:** L

### US-11-003 — Welfare & mission funds
**As a** Treasurer, **I want** dedicated welfare and mission funds, **so that** restricted money is not co-mingled.  
**AC:**
- Fund balances
- Restriction flags
- Reports by fund  
**Points:** M

### US-11-004 — Recurring expenses
**As a** Finance Manager, **I want** recurring expenses (hall rentals, utilities, etc.), **so that** operations are predictable.  
**AC:**
- Examples configurable including Friday Worship Hall Rental, Intercession Hall Rental, Friday School Rental, Women's/Men's Fellowship Rental, Utilities, Internet, Cleaning, Security
- Draft payments generated
- SoD on approve  
**Points:** L

### US-11-005 — Vendor management
**As a** Finance Manager, **I want** vendor records and payment history, **so that** vendor risk is visible.  
**AC:**
- Vendor master
- Payment link
- AI vendor risk flag optional  
**Points:** M

### US-11-006 — Budgeting
**As a** Finance Manager, **I want** budgets by campus/ministry/fund, **so that** overruns are visible.  
**AC:**
- Budget vs actual
- Alerts on overrun
- Period lock  
**Points:** L

### US-11-007 — Tally Prime voucher sync
**As a** Treasurer, **I want** receipt/payment/journal vouchers synced to Tally Prime, **so that** statutory books stay aligned.  
**AC:**
- Idempotent sync
- Exception queue UI
- Ledger sync  
**Points:** XL

### US-11-008 — Bank reconciliation
**As a** Treasurer, **I want** bank reconciliation assisted by Tally sync, **so that** periods close cleanly.  
**AC:**
- Match workspace
- Unmatched queue
- Auditor read access  
**Points:** L

### US-11-009 — AI anomaly detection
**As a** Finance Manager, **I want** detection of duplicates/overspend/FX/vendor risks, **so that** issues surface early.  
**AC:**
- Alerts with rationale
- Acknowledge/override
- No silent auto-void  
**Points:** L

### US-11-010 — AI cashflow forecast
**As a** Senior Pastor, **I want** cashflow/budget forecasts, **so that** leadership plans ahead.  
**AC:**
- Horizon selectable
- Assumptions visible
- Feature-flagged  
**Points:** XL

### US-11-011 — Foreign missions gift
**As a** Treasurer, **I want** to post non-base currency mission gifts with FX, **so that** missions reporting is accurate.  
**AC:**
- Dual amounts stored
- Mission project tag
- Reportable in ANA  
**Points:** M

### US-11-012 — SoD payment approval
**As an** Auditor, **I want** initiator ≠ approver above threshold, **so that** fraud risk drops.  
**AC:**
- Enforced in workflow
- Bypass impossible without break-glass + audit
- Reports of violations attempt  
**Points:** M

### US-11-013 — Integration health for Tally/M365
**As an** Administrator, **I want** integration health metrics, **so that** failures are fixed fast.  
**AC:**
- Last success/error rate
- Alerting
- Aligns FR-INT-008  
**Points:** M

---

## EPIC-12 — Analytics & Executive Dashboards

**Goal:** Cross-module dashboards, exports, AI insights without leaking confidential text.  
**FRs:** FR-ANA-* · **UCs:** UC-24

### US-12-001 — Membership dashboard
**As a** Senior Pastor, **I want** membership KPIs by campus, **so that** growth is visible.  
**AC:**
- Active/new/churn proxies
- Date/campus filters
- Role gated  
**Points:** M

### US-12-002 — Visitor funnel dashboard
**As a** Pastor, **I want** visitor funnel and source performance, **so that** outreach is optimized.  
**AC:**
- Stages + conversion
- Source breakdown uses exact enum
- Export  
**Points:** M

### US-12-003 — Care cell health
**As a** Care Cell Leader, **I want** cell engagement widgets for my cells only, **so that** I shepherd well.  
**AC:**
- Scope by assignment
- Attendance/giving aggregates only
- No counselling note text  
**Points:** M

### US-12-004 — Welfare & counselling aggregates
**As a** Senior Pastor, **I want** welfare demand and counselling trend aggregates, **so that** care capacity is planned.  
**AC:**
- Counts by category/risk
- Bodies excluded
- Campus filter  
**Points:** M

### US-12-005 — Finance executive dashboard
**As a** Finance Manager, **I want** giving/fund/budget widgets, **so that** stewardship is real-time.  
**AC:**
- Multi-currency views
- Restricted to FIN roles
- Drill to reports  
**Points:** L

### US-12-006 — Communication performance
**As a** Ministry Leader, **I want** delivery success by channel, **so that** we fix poor channels.  
**AC:**
- Email/WhatsApp/SMS/Push stats
- No message bodies
- Date range  
**Points:** S

### US-12-007 — Events dashboard
**As an** Administrator, **I want** event attendance trends, **so that** programming decisions improve.  
**AC:**
- Attendance rates
- Campus compare
- Export  
**Points:** S

### US-12-008 — Power BI export
**As an** Analyst, **I want** secure Power BI dataset export, **so that** board packs are richer.  
**AC:**
- Permissioned
- No confidential note fields
- Job history  
**Points:** L

### US-12-009 — AI insights engine
**As a** Senior Pastor, **I want** AI insights on growth/attendance/giving/ministry/volunteer/welfare/counselling trends, **so that** I see narratives quickly.  
**AC:**
- Insight cards with rationale
- Dismiss/save
- Feature-flagged  
**Points:** XL

### US-12-010 — Async heavy reports
**As an** Administrator, **I want** large exports to run async, **so that** UI stays responsive at 100k scale.  
**AC:**
- Job queue
- Download when ready
- Notify on complete  
**Points:** M

### US-12-011 — Widget RBAC
**As an** Auditor, **I want** dashboards to hide unauthorized widgets, **so that** least privilege holds.  
**AC:**
- Matrix-driven visibility
- Attempted access audited
- Consistent on mobile  
**Points:** M

### US-12-012 — Near-real-time KPI cache
**As a** Product Owner, **I want** cached KPIs refreshed via events, **so that** exec views are timely without crushing DB.  
**AC:**
- Redis (or equiv) cache
- Staleness indicator
- Manual refresh for Admin  
**Points:** L

---

## Cross-epic story index (AI & integrations)

| Theme | Stories |
|---|---|
| AI | US-01-009/010, US-02-007, US-03-007/008, US-04-006, US-05-006, US-06-008, US-08-005/006, US-09-005/006, US-10-007, US-11-009/010, US-12-009 |
| WhatsApp/Email/SMS/Push | US-01-011, US-02-010, US-04-010, US-05-007, US-09-004, US-10-* |
| Tally Prime | US-11-007, US-11-008, US-11-013 |
| M365 | US-09-009, US-10-011 |
| Power BI | US-06-006, US-12-008 |
| MFA / RBAC | Covered in SEC via UC-23; enforce in all epics via AC on permissions |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial epics EPIC-01..12 with full story sets |
