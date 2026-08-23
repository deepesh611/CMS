# Use Cases

| Field | Value |
|---|---|
| **Product** | Enterprise Church Management System (CMS) |
| **Document** | 03 — Use Cases |
| **Version** | 1.0 |
| **Date** | 2026-08-23 |
| **Related** | [00-INDEX](00-INDEX.md) · [01-BRS](01-BRS.md) · [02-FRS](02-FRS.md) · [05-USER-STORIES](05-USER-STORIES.md) |

**Conventions:** Actors use role names from FR-SEC. Persons referenced as Member A, Visitor B, Case C-1001 (no real names).

---

## UC-01 — Register New Member

| Field | Content |
|---|---|
| **UC-ID** | UC-01 |
| **Name** | Register New Member |
| **Actor** | Administrator, Care Cell Leader, Pastor |
| **Preconditions** | Actor authenticated with `members.create`; campus selected; tenant active. |
| **Main Flow** | 1. Actor opens Membership → New. 2. Enters profile fields (name, contacts, DOB, address, profession, skills/talents). 3. Assigns Care Cell and ministries. 4. Sets status (e.g., Prospect/In Class). 5. System generates Membership ID and optional Family ID. 6. Saves; audit written. 7. Notification sent to Care Cell Leader. |
| **Alternate Flows** | A1 Duplicate mobile/email → warn/block per policy. A2 Missing required field → validation errors. A3 Self-registration via portal → pending verification (FR-MEM-006). |
| **Postconditions** | Member record exists; assignment notification queued; audit entry created. |
| **Related FRs** | FR-MEM-001…005, FR-MEM-020, FR-MEM-040, FR-SEC-002 |

---

## UC-02 — Manage Family Links

| Field | Content |
|---|---|
| **UC-ID** | UC-02 |
| **Name** | Link Spouse and Children |
| **Actor** | Administrator, Care Cell Leader |
| **Preconditions** | Member A exists. |
| **Main Flow** | 1. Open Member A Family tab. 2. Link spouse Member B (or create). 3. Add children records under Family ID. 4. Save; family graph updated. |
| **Alternate Flows** | A1 Spouse already linked elsewhere → conflict resolution wizard. |
| **Postconditions** | Shared Family ID; relationships queryable. |
| **Related FRs** | FR-MEM-003 |

---

## UC-03 — Membership Status Transition

| Field | Content |
|---|---|
| **UC-ID** | UC-03 |
| **Name** | Change Membership Status |
| **Actor** | Pastor, Elder, Administrator |
| **Preconditions** | Member A Active/Prospect; actor has `members.status`. |
| **Main Flow** | 1. Select new status. 2. Enter reason. 3. System validates transition matrix. 4. Commit + audit. |
| **Alternate Flows** | A1 Illegal transition → reject. A2 Deceased → stop marketing COM (FR-MEM-022). |
| **Postconditions** | Status history updated. |
| **Related FRs** | FR-MEM-010, FR-MEM-011, FR-MEM-022 |

---

## UC-04 — Register Visitor with Source

| Field | Content |
|---|---|
| **UC-ID** | UC-04 |
| **Name** | Register Visitor |
| **Actor** | Care Cell Leader, Volunteer (Visitor Team), Pastor |
| **Preconditions** | Actor has `visitors.create`. |
| **Main Flow** | 1. Enter Visitor B details and campus/service. 2. Select Visitor Source from mandatory list (Friend…Other). 3. If source is person-referrer type, link referrer Member A. 4. Save. 5. System creates Day 1/3/7/14/30 follow-up tasks. |
| **Alternate Flows** | A1 Source=Other → require free-text note. A2 Possible duplicate → merge suggestion. |
| **Postconditions** | Visitor in pipeline New; five tasks scheduled; assignees notified. |
| **Related FRs** | FR-VIS-001…003, FR-VIS-020…022, FR-VIS-040 |

---

## UC-05 — Complete Visitor Follow-Up Task

| Field | Content |
|---|---|
| **UC-ID** | UC-05 |
| **Name** | Complete Day-N Visitor Follow-Up |
| **Actor** | Care Cell Leader, Volunteer |
| **Preconditions** | Task due for Visitor B exists. |
| **Main Flow** | 1. Open task. 2. Contact via preferred channel. 3. Record outcome + note. 4. Mark complete. 5. Pipeline may advance to Contacted/Engaged. |
| **Alternate Flows** | A1 Overdue → escalate to Pastor. A2 No answer → reschedule within policy. |
| **Postconditions** | Task closed; engagement metrics updated. |
| **Related FRs** | FR-VIS-020…022, FR-VIS-010 |

---

## UC-06 — Convert Visitor to Member

| Field | Content |
|---|---|
| **UC-ID** | UC-06 |
| **Name** | Convert Visitor to Member |
| **Actor** | Pastor, Care Cell Leader, Administrator |
| **Preconditions** | Visitor B Engaged/Class Invited; consent captured. |
| **Main Flow** | 1. Actor selects Convert. 2. System maps fields to member form; actor confirms Care Cell. 3. Creates Member; links visitor history. 4. Sets visitor stage Converted. 5. Cancels remaining follow-ups. 6. Notifies Care Cell. |
| **Alternate Flows** | A1 Existing member match → link instead of create. A2 Actor lacks permission → deny. |
| **Postconditions** | Member exists; visitor Converted; audit trail. |
| **Related FRs** | FR-VIS-011, FR-MEM-001, FR-MEM-020 |

---

## UC-07 — Open Counselling Case

| Field | Content |
|---|---|
| **UC-ID** | UC-07 |
| **Name** | Open Counselling Case |
| **Actor** | Counsellor, Pastor, Senior Pastor |
| **Preconditions** | Actor has `counselling.create`; counselee Member A or Visitor B identified. |
| **Main Flow** | 1. Select category (Marriage…Church Conflict). 2. Set risk Low/Moderate/High. 3. Assign counsellor. 4. Create case C-1001. 5. If High, notify Senior Pastor. |
| **Alternate Flows** | A1 High risk without supervisor → blocked until acknowledge. |
| **Postconditions** | Case Open; confidential container ready. |
| **Related FRs** | FR-COUN-001, FR-COUN-002, FR-COUN-003, FR-COUN-010 |

---

## UC-08 — Record Counselling Session

| Field | Content |
|---|---|
| **UC-ID** | UC-08 |
| **Name** | Record Counselling Session |
| **Actor** | Assigned Counsellor |
| **Preconditions** | Case C-1001 Active; actor is assignee or Senior Pastor. |
| **Main Flow** | 1. Schedule/attend session. 2. Enter confidential notes (field-level secured). 3. Set next follow-up. 4. Save; audit without note body. |
| **Alternate Flows** | A1 Unauthorized role opens notes → access denied + security audit. A2 SMS reminder sent with time only (no notes) FR-COUN-041. |
| **Postconditions** | Session stored; reminder queued. |
| **Related FRs** | FR-COUN-011, FR-COUN-012, FR-COUN-014, FR-COUN-040, FR-COUN-041, FR-SEC-005 |

---

## UC-09 — Submit Prayer Request

| Field | Content |
|---|---|
| **UC-ID** | UC-09 |
| **Name** | Submit Prayer Request |
| **Actor** | Member (portal), Care Cell Leader, Pastor |
| **Preconditions** | Authenticated or approved public form for tenant. |
| **Main Flow** | 1. Select category (Spiritual Growth…Special Needs). 2. Set confidentiality/urgency. 3. Submit. 4. Assign to Prayer Team. |
| **Alternate Flows** | A1 Emergency → escalate immediately (UC-10). |
| **Postconditions** | Request queued; team notified. |
| **Related FRs** | FR-PRAY-001, FR-PRAY-010, FR-PRAY-011, FR-PRAY-040 |

---

## UC-10 — Escalate Prayer Request

| Field | Content |
|---|---|
| **UC-ID** | UC-10 |
| **Name** | Escalate Prayer (Emergency) |
| **Actor** | Prayer Team Lead, Pastor |
| **Preconditions** | Request exists; urgency Emergency or manual escalate. |
| **Main Flow** | 1. Actor escalates to Pastor/Senior Pastor. 2. System sends Push/SMS/WhatsApp alerts (no sensitive body on SMS if flagged confidential). 3. Status=Escalated. |
| **Alternate Flows** | A1 Quiet hours overridden for Emergency. |
| **Postconditions** | Escalation audit; pastoral ack required. |
| **Related FRs** | FR-PRAY-013, FR-PRAY-014, FR-PRAY-040 |

---

## UC-11 — Create Welfare Request

| Field | Content |
|---|---|
| **UC-ID** | UC-11 |
| **Name** | Create Welfare Request |
| **Actor** | Care Cell Leader, Associate Care Cell Leader, Counsellor, Ministry Leader, Pastor |
| **Preconditions** | Actor is allowed requestor; beneficiary Member A. |
| **Main Flow** | 1. Enter need, amount, currency, narrative, docs. 2. Submit for assessment. 3. Notify Welfare Team. |
| **Alternate Flows** | A1 Non-allowed role → deny. A2 Missing docs → return to draft. |
| **Postconditions** | Request in Submit/Assessment state. |
| **Related FRs** | FR-WEL-001, FR-WEL-010, FR-WEL-011, FR-WEL-040 |

---

## UC-12 — Approve Welfare Assistance

| Field | Content |
|---|---|
| **UC-ID** | UC-12 |
| **Name** | Approve and Disburse Welfare |
| **Actor** | Welfare Team, Pastor, Finance Manager, Treasurer |
| **Preconditions** | Assessment complete; within approval matrix. |
| **Main Flow** | 1. Review case. 2. Approve at required level(s). 3. Create assistance/disbursement linked to Welfare Fund. 4. Optional FIN voucher. 5. Schedule Follow-Up Review. 6. Notify requestor. |
| **Alternate Flows** | A1 Above threshold needs dual approval. A2 Reject with reason → notify requestor. A3 AI recommendation shown but not auto-applied. |
| **Postconditions** | Assistance recorded; fund balance updated; audit complete. |
| **Related FRs** | FR-WEL-011…014, FR-WEL-033, FR-FIN-001, FR-FIN-006 |

---

## UC-13 — Welfare Compare Five Cases

| Field | Content |
|---|---|
| **UC-ID** | UC-13 |
| **Name** | Compare Up to Five Welfare Cases |
| **Actor** | Welfare Team, Senior Pastor, Finance Manager |
| **Preconditions** | ≥2 and ≤5 open assessed cases; actor has `wce.compare`. |
| **Main Flow** | 1. Select up to 5 cases. 2. Score categories A–I (Eligibility…Recommendation) with weights. 3. View rankings/charts. 4. Record board decision. 5. Optionally export to Power BI. |
| **Alternate Flows** | A1 Attempt 6th case → validation error. A2 Adjust weights → recalculate. |
| **Postconditions** | Comparison session persisted for audit. |
| **Related FRs** | FR-WCE-001, FR-WCE-002, FR-WCE-010…014, FR-WCE-020 |

---

## UC-14 — Baby Dedication Workflow

| Field | Content |
|---|---|
| **UC-ID** | UC-14 |
| **Name** | Baby Dedication End-to-End |
| **Actor** | Care Cell Leader, Elder, Pastor, Administrator |
| **Preconditions** | Parents Member A / Member B on record. |
| **Main Flow** | 1. Capture Child Name, Given Name, DOB, Place of Birth, Father Name, Mother Name. 2. Care Cell Recommendation. 3. Elder Review. 4. Pastoral Approval. 5. Schedule into service slot. 6. Generate certificate. |
| **Alternate Flows** | A1 Elder rejects → return with comments. A2 Slot conflict → choose another (UC-16). |
| **Postconditions** | Ceremony Completed/Scheduled; family linked; certificate stored. |
| **Related FRs** | FR-CER-010…012, FR-SLOT-003, FR-MEM-015 |

---

## UC-15 — Marriage Banns and Objection

| Field | Content |
|---|---|
| **UC-ID** | UC-15 |
| **Name** | Publish Marriage Banns |
| **Actor** | Pastor, Elder, Administrator |
| **Preconditions** | Bride/Groom data, parents, wedding date/venue, counselling status captured. |
| **Main Flow** | 1. Create Marriage Banns record. 2. Publish for banns period. 3. Monitor objections. 4. If clear and counselling OK, allow Wedding Service schedule. 5. Issue certificates post-wedding. |
| **Alternate Flows** | A1 Objection filed → hold + pastoral review. A2 Counselling incomplete → block wedding schedule. |
| **Postconditions** | Banns status Closed/Cleared or On Hold; audit of objections. |
| **Related FRs** | FR-CER-020…023 |

---

## UC-16 — Insert Service Slot Function

| Field | Content |
|---|---|
| **UC-ID** | UC-16 |
| **Name** | Insert Function into Service Program Slot |
| **Actor** | Pastor, Elder, Administrator |
| **Preconditions** | Service instance exists (Friday/Sunday/Special). |
| **Main Flow** | 1. Choose service date. 2. Choose program slot (Before Worship…Before Closing Prayer). 3. Insert ceremony/announcement with duration/owner. 4. System validates conflicts. 5. Publish agenda (optional). |
| **Alternate Flows** | A1 Conflict → propose alternate slot. A2 AI capacity warning if over time budget. |
| **Postconditions** | Agenda item saved; owners notified. |
| **Related FRs** | FR-SLOT-001…004, FR-SLOT-030…032, FR-SLOT-040 |

---

## UC-17 — Assign Roster Duty

| Field | Content |
|---|---|
| **UC-ID** | UC-17 |
| **Name** | Assign Activity Roster |
| **Actor** | Ministry Leader, Pastor, Administrator |
| **Preconditions** | Activity type in scope (Sermons…Friday School). |
| **Main Flow** | 1. Create activity occurrence. 2. Assign Member A / Volunteer. 3. Conflict check. 4. Confirm. 5. Notify via Email/SMS/WhatsApp/Push. |
| **Alternate Flows** | A1 Conflict → suggest substitute. A2 AI fair-assignment suggests alternate person. A3 Assignee declines → reassign workflow. |
| **Postconditions** | Roster entry active; notifications sent. |
| **Related FRs** | FR-ROST-001…003, FR-ROST-030…033, FR-ROST-040 |

---

## UC-18 — Send Daily Devotion

| Field | Content |
|---|---|
| **UC-ID** | UC-18 |
| **Name** | Compose and Broadcast Daily Devotion |
| **Actor** | Ministry Leader, Pastor, Administrator |
| **Preconditions** | COM permissions; audience segment selected; channel consents OK. |
| **Main Flow** | 1. Compose Verse, Prayer, Reflection, Article (or AI draft). 2. Human approves. 3. Attach files ≤50MB within type rules. 4. Broadcast to WhatsApp/Email/App/Portal. 5. Log deliveries. |
| **Alternate Flows** | A1 Email with MP4 → reject attachment. A2 AI draft rejected → edit manually. |
| **Postconditions** | Devotion published; delivery metrics available. |
| **Related FRs** | FR-COM-001…005, FR-COM-010, FR-COM-011, FR-COM-030, FR-AI-005 |

---

## UC-19 — Send Announcement with Attachments

| Field | Content |
|---|---|
| **UC-ID** | UC-19 |
| **Name** | Multi-Channel Announcement |
| **Actor** | Administrator, Ministry Leader |
| **Preconditions** | Audience + channels selected. |
| **Main Flow** | 1. Create announcement. 2. Attach PDF/images (and MP4 only for non-email channels). 3. Schedule Immediate/Scheduled/Recurring. 4. Send. |
| **Alternate Flows** | A1 File &gt;50MB → reject. A2 Quiet hours → queue. |
| **Postconditions** | Messages accepted by providers; logs stored. |
| **Related FRs** | FR-COM-002…007, FR-COM-020, FR-COM-021 |

---

## UC-20 — Record Donation and Sync Tally

| Field | Content |
|---|---|
| **UC-ID** | UC-20 |
| **Name** | Donation Capture + Tally Prime Sync |
| **Actor** | Treasurer, Finance Manager |
| **Preconditions** | Member A (or anonymous gift policy); currency in supported list; Tally connector configured (Phase 2). |
| **Main Flow** | 1. Record donation/tithe/offering with amount + currency. 2. Post to fund/ledger. 3. Create Receipt Voucher payload. 4. Sync to Tally Prime. 5. On success, mark synced; on fail, exception queue. |
| **Alternate Flows** | A1 Duplicate payment detected by AI → hold for review. A2 FX conversion applies rate date. A3 Sync retry/backoff. |
| **Postconditions** | Finance record posted; Tally sync status terminal or queued. |
| **Related FRs** | FR-FIN-001, FR-FIN-003…005, FR-FIN-020, FR-FIN-021, FR-FIN-031, FR-INT-005 |

---

## UC-21 — Manage Recurring Expense

| Field | Content |
|---|---|
| **UC-ID** | UC-21 |
| **Name** | Configure Recurring Hall/Utility Expense |
| **Actor** | Finance Manager, Treasurer |
| **Preconditions** | Vendor and budget exist. |
| **Main Flow** | 1. Create recurring expense (e.g., Friday Worship Hall Rental). 2. Set cadence, currency, amount. 3. System generates due payment drafts. 4. Approve payment (SoD). |
| **Alternate Flows** | A1 Budget overrun alert. |
| **Postconditions** | Schedule active; payment draft awaiting approval. |
| **Related FRs** | FR-FIN-002, FR-FIN-006, FR-FIN-031 |

---

## UC-22 — AI Ministry Recommendation

| Field | Content |
|---|---|
| **UC-ID** | UC-22 |
| **Name** | AI Recommend Ministry Suitability |
| **Actor** | Care Cell Leader, Ministry Leader, Pastor |
| **Preconditions** | Member A has skills/talents; AI feature flag on. |
| **Main Flow** | 1. Open Copilot on Member A. 2. Request ministry suitability. 3. Review rationale/confidence. 4. Accept → create ministry invite / Reject → log. |
| **Alternate Flows** | A1 Low confidence → require human only. A2 Feature disabled → hide Copilot. |
| **Postconditions** | Decision logged (accept/edit/reject). |
| **Related FRs** | FR-MEM-032, FR-AI-001…005 |

---

## UC-23 — MFA Login

| Field | Content |
|---|---|
| **UC-ID** | UC-23 |
| **Name** | Login with MFA |
| **Actor** | Any user (privileged roles required) |
| **Preconditions** | Account active; MFA enrolled for role policy. |
| **Main Flow** | 1. Enter username/password. 2. Prompt TOTP/IdP second factor. 3. Validate. 4. Issue session; audit success. |
| **Alternate Flows** | A1 Bad password → increment lockout counter. A2 Bad MFA → deny; audit. A3 Locked → admin unlock. |
| **Postconditions** | Authenticated session with roles loaded. |
| **Related FRs** | FR-SEC-003, FR-SEC-004, FR-SEC-008 |

---

## UC-24 — View Executive Dashboard

| Field | Content |
|---|---|
| **UC-ID** | UC-24 |
| **Name** | View Role-Filtered Executive Dashboard |
| **Actor** | Senior Pastor, Finance Manager, Administrator |
| **Preconditions** | Actor has `analytics.view`. |
| **Main Flow** | 1. Open Analytics home. 2. Filter campus/date. 3. View permitted widgets (membership, visitors, welfare, finance, etc.). 4. Drill into report. |
| **Alternate Flows** | A1 Finance widgets hidden for non-finance roles. A2 Export async for large range. |
| **Postconditions** | View audit optional; no confidential note text shown. |
| **Related FRs** | FR-ANA-001…004, FR-ANA-011 |

---

## UC-25 — M365 Calendar Sync for Roster Event

| Field | Content |
|---|---|
| **UC-ID** | UC-25 |
| **Name** | Sync Roster/Event to Microsoft 365 Calendar |
| **Actor** | Administrator, Ministry Leader |
| **Preconditions** | M365 integration enabled; user consented. |
| **Main Flow** | 1. Create roster/event. 2. Toggle Sync to M365. 3. Connector creates/updates calendar event. 4. Store external id. |
| **Alternate Flows** | A1 Token expired → re-auth. A2 Sync fail → exception queue + notify admin. |
| **Postconditions** | External calendar reflects assignment. |
| **Related FRs** | FR-INT-006, FR-ROST-002, FR-INT-008 |

---

## UC-26 — AI Visitor Conversion Assist

| Field | Content |
|---|---|
| **UC-ID** | UC-26 |
| **Name** | AI Follow-Up and Escalation Assist |
| **Actor** | Care Cell Leader, Pastor |
| **Preconditions** | Visitor B with incomplete follow-ups; AI enabled. |
| **Main Flow** | 1. Copilot shows engagement score + suggested next action/channel. 2. Actor accepts suggestion → prefill message. 3. Human sends. 4. If escalation threshold, notify Pastor. |
| **Alternate Flows** | A1 Actor rejects suggestion → log. |
| **Postconditions** | Action taken or deferred; AI feedback captured. |
| **Related FRs** | FR-VIS-030…033, FR-AI-002, FR-AI-005 |

---

## UC-27 — Baptism Record and Certificate

| Field | Content |
|---|---|
| **UC-ID** | UC-27 |
| **Name** | Record Baptism Ceremony |
| **Actor** | Pastor, Elder, Administrator |
| **Preconditions** | Candidate Member A; ceremony type Baptism. |
| **Main Flow** | 1. Create Baptism ceremony. 2. Approve/schedule. 3. Complete with officiant/date/campus. 4. Generate certificate. 5. Update member baptism fields. |
| **Alternate Flows** | A1 Schedule into Sunday Main Service slot. |
| **Postconditions** | Baptism on member profile; certificate stored. |
| **Related FRs** | FR-CER-001, FR-CER-030, FR-MEM-012, FR-SLOT-003 |

---

## UC-28 — Push Emergency Alert

| Field | Content |
|---|---|
| **UC-ID** | UC-28 |
| **Name** | Send Emergency Push Alert |
| **Actor** | Senior Pastor, Administrator |
| **Preconditions** | `com.emergency` permission; devices registered. |
| **Main Flow** | 1. Compose emergency alert. 2. Select campuses/audiences. 3. Send Immediate Push (+ optional SMS). 4. Confirm delivery stats. |
| **Alternate Flows** | A1 Quiet hours bypass confirmed by actor. |
| **Postconditions** | Alert logged; recipients notified. |
| **Related FRs** | FR-COM-020, FR-COM-021, FR-SEC-002 |

---

## UC-29 — Bank Reconciliation via Tally

| Field | Content |
|---|---|
| **UC-ID** | UC-29 |
| **Name** | Bank Reconciliation Assisted by Tally Sync |
| **Actor** | Treasurer, Finance Manager, Auditor (read) |
| **Preconditions** | Bank statement imported/linked; vouchers synced. |
| **Main Flow** | 1. Open recon workspace. 2. Match CMS transactions to bank/Tally. 3. Flag exceptions. 4. Close period. |
| **Alternate Flows** | A1 Unmatched items → assign owner. |
| **Postconditions** | Period recon status Closed; Auditor can review. |
| **Related FRs** | FR-FIN-020, FR-SEC-001, FR-FIN-006 |

---

## UC-30 — Multi-Currency Mission Gift

| Field | Content |
|---|---|
| **UC-ID** | UC-30 |
| **Name** | Record Foreign Mission Donation in Non-Base Currency |
| **Actor** | Treasurer, Finance Manager |
| **Preconditions** | Mission fund exists; rate table available. |
| **Main Flow** | 1. Enter gift in AED (example). 2. Convert to tenant base (e.g., OMR) with rate date. 3. Post exchange gain/loss if applicable. 4. Attribute to Foreign Missions report. |
| **Alternate Flows** | A1 Missing rate → block post. |
| **Postconditions** | Dual-currency amounts stored; mission report updated. |
| **Related FRs** | FR-FIN-003, FR-FIN-004, FR-FIN-005 |

---

## Traceability matrix (sample)

| UC | Modules |
|---|---|
| UC-01…03 | MEM |
| UC-04…06, UC-26 | VIS |
| UC-07…08 | COUN |
| UC-09…10 | PRAY |
| UC-11…13 | WEL/WCE |
| UC-14…15, UC-27 | CER |
| UC-16 | SLOT |
| UC-17, UC-25 | ROST/INT |
| UC-18…19, UC-28 | COM |
| UC-20…21, UC-29…30 | FIN/INT |
| UC-22, UC-26 | AI |
| UC-23 | SEC |
| UC-24 | ANA |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-23 | Initial use case set (30) |
