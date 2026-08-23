-- =============================================================================
-- Enterprise CMS — PostgreSQL DDL
-- File: postgresql-pastoral-ops.sql
-- Scope: Counselling, Prayer, Welfare, WCE, Ceremonies, Service Slots,
--        Activity Roster, Communications, Notifications
-- Depends on: postgresql-core.sql
-- PostgreSQL 16+ | No real PII in comments/samples
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS pastoral;
CREATE SCHEMA IF NOT EXISTS ops;
CREATE SCHEMA IF NOT EXISTS comms;

COMMENT ON SCHEMA pastoral IS 'Counselling, prayer, welfare, ceremonies';
COMMENT ON SCHEMA ops IS 'Service slots and activity roster';
COMMENT ON SCHEMA comms IS 'Communications and notifications';

-- -----------------------------------------------------------------------------
-- ENUM types
-- -----------------------------------------------------------------------------

DO $$ BEGIN
  CREATE TYPE pastoral.risk_level_code AS ENUM ('low', 'moderate', 'high');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE pastoral.urgency_code AS ENUM ('normal', 'high', 'emergency');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE pastoral.counselling_case_status AS ENUM (
    'open', 'active', 'on_hold', 'referred', 'closed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE pastoral.welfare_request_status AS ENUM (
    'submitted', 'assessment', 'review', 'approved', 'rejected', 'disbursed', 'closed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE pastoral.ceremony_type_code AS ENUM (
    'baby_dedication', 'baptism', 'membership_reception', 'thanksgiving',
    'wedding_anniversary', 'house_blessing', 'marriage_banns', 'wedding_service',
    'funeral_service', 'memorial_service'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE pastoral.wce_category_code AS ENUM (
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ops.service_type_code AS ENUM (
    'friday_main', 'sunday_main', 'special'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ops.program_slot_code AS ENUM (
    'before_worship', 'after_worship', 'before_sermon',
    'after_sermon', 'during_announcements', 'before_closing_prayer'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ops.roster_activity_type AS ENUM (
    'sermon', 'counselling', 'hospital_visit', 'care_cell_meeting',
    'ministry_event', 'worship_team', 'volunteer', 'friday_school'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE comms.notification_channel AS ENUM (
    'email', 'sms', 'whatsapp', 'push', 'portal'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE comms.notification_status AS ENUM (
    'queued', 'sent', 'delivered', 'failed', 'suppressed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE comms.content_type_code AS ENUM (
    'flyer', 'video', 'announcement', 'event', 'daily_devotion'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- -----------------------------------------------------------------------------
-- Lookups
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.counselling_categories (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID REFERENCES core.tenants (id),
  code         TEXT NOT NULL,
  label        TEXT NOT NULL,
  sort_order   INT NOT NULL DEFAULT 0,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_counselling_categories UNIQUE (tenant_id, code)
);

INSERT INTO pastoral.counselling_categories (tenant_id, code, label, sort_order) VALUES
  (NULL, 'marriage', 'Marriage', 10),
  (NULL, 'family', 'Family', 20),
  (NULL, 'youth', 'Youth', 30),
  (NULL, 'addiction', 'Addiction', 40),
  (NULL, 'mental_health', 'Mental Health', 50),
  (NULL, 'career', 'Career', 60),
  (NULL, 'grief', 'Grief', 70),
  (NULL, 'trauma', 'Trauma', 80),
  (NULL, 'financial', 'Financial', 90),
  (NULL, 'spiritual_care', 'Spiritual Care', 100),
  (NULL, 'leadership_mentoring', 'Leadership Mentoring', 110),
  (NULL, 'church_conflict', 'Church Conflict', 120)
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS pastoral.prayer_categories (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID REFERENCES core.tenants (id),
  code         TEXT NOT NULL,
  label        TEXT NOT NULL,
  sort_order   INT NOT NULL DEFAULT 0,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_prayer_categories UNIQUE (tenant_id, code)
);

INSERT INTO pastoral.prayer_categories (tenant_id, code, label, sort_order) VALUES
  (NULL, 'spiritual_growth', 'Spiritual Growth', 10),
  (NULL, 'healing', 'Healing', 20),
  (NULL, 'family', 'Family', 30),
  (NULL, 'financial', 'Financial', 40),
  (NULL, 'career', 'Career', 50),
  (NULL, 'education', 'Education', 60),
  (NULL, 'emotional_support', 'Emotional Support', 70),
  (NULL, 'church_growth', 'Church Growth', 80),
  (NULL, 'ministry', 'Ministry', 90),
  (NULL, 'emergency', 'Emergency', 100),
  (NULL, 'special_needs', 'Special Needs', 110)
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS pastoral.welfare_need_types (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID REFERENCES core.tenants (id),
  code         TEXT NOT NULL,
  label        TEXT NOT NULL,
  sort_order   INT NOT NULL DEFAULT 0,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_welfare_need_types UNIQUE (tenant_id, code)
);

INSERT INTO pastoral.welfare_need_types (tenant_id, code, label, sort_order) VALUES
  (NULL, 'food', 'Food', 10),
  (NULL, 'housing', 'Housing', 20),
  (NULL, 'medical', 'Medical', 30),
  (NULL, 'education', 'Education', 40),
  (NULL, 'utilities', 'Utilities', 50),
  (NULL, 'emergency_relief', 'Emergency Relief', 60),
  (NULL, 'other', 'Other', 70)
ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- COUNSELLING
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.counselling_cases (
  id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id                   UUID NOT NULL REFERENCES core.tenants (id),
  campus_id                   UUID NOT NULL REFERENCES core.campuses (id),
  case_number                 TEXT NOT NULL,
  counselee_member_id         UUID REFERENCES membership.members (id),
  counselee_visitor_id        UUID REFERENCES visitor.visitors (id),
  category_id                 UUID NOT NULL REFERENCES pastoral.counselling_categories (id),
  risk_level                  pastoral.risk_level_code NOT NULL DEFAULT 'low',
  status                      pastoral.counselling_case_status NOT NULL DEFAULT 'open',
  assigned_counsellor_user_id UUID NOT NULL REFERENCES identity.users (id),
  supervisor_user_id          UUID REFERENCES identity.users (id),
  opened_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at                   TIMESTAMPTZ,
  high_risk_notified_at       TIMESTAMPTZ,
  created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by                  UUID,
  updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by                  UUID,
  deleted_at                  TIMESTAMPTZ,
  row_version                 INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_counselling_cases_number UNIQUE (tenant_id, case_number),
  CONSTRAINT ck_counselling_counselee
    CHECK (counselee_member_id IS NOT NULL OR counselee_visitor_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS ix_counselling_cases_counsellor_status
  ON pastoral.counselling_cases (tenant_id, assigned_counsellor_user_id, status)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_counselling_cases_risk
  ON pastoral.counselling_cases (tenant_id, risk_level, status)
  WHERE deleted_at IS NULL AND risk_level = 'high';

COMMENT ON TABLE pastoral.counselling_cases IS 'Christian counselling cases; confidential notes in sessions';

CREATE TABLE IF NOT EXISTS pastoral.counselling_sessions (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  case_id              UUID NOT NULL REFERENCES pastoral.counselling_cases (id),
  scheduled_at         TIMESTAMPTZ NOT NULL,
  attended_at          TIMESTAMPTZ,
  duration_minutes     INT,
  summary_ciphertext   BYTEA, -- encrypted at rest; field-level ACL
  encryption_key_id    TEXT,
  next_followup_at     TIMESTAMPTZ,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ,
  row_version          INT NOT NULL DEFAULT 1,
  CONSTRAINT ck_counselling_sessions_duration
    CHECK (duration_minutes IS NULL OR duration_minutes > 0)
);

CREATE INDEX IF NOT EXISTS ix_counselling_sessions_case
  ON pastoral.counselling_sessions (tenant_id, case_id, scheduled_at)
  WHERE deleted_at IS NULL;

COMMENT ON COLUMN pastoral.counselling_sessions.summary_ciphertext
  IS 'Encrypted session summary; never log plaintext; SMS/WhatsApp forbidden (FR-COUN-041)';

CREATE TABLE IF NOT EXISTS pastoral.counselling_referrals (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES core.tenants (id),
  case_id        UUID NOT NULL REFERENCES pastoral.counselling_cases (id),
  referral_type  TEXT NOT NULL
    CONSTRAINT ck_counselling_referral_type CHECK (referral_type IN ('internal', 'external')),
  target_label   TEXT NOT NULL,
  status         TEXT NOT NULL DEFAULT 'pending'
    CONSTRAINT ck_counselling_referral_status
      CHECK (status IN ('pending', 'accepted', 'declined', 'completed')),
  referred_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by     UUID,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by     UUID,
  deleted_at     TIMESTAMPTZ
);

-- -----------------------------------------------------------------------------
-- PRAYER
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.prayer_teams (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES core.tenants (id),
  campus_id    UUID REFERENCES core.campuses (id),
  code         TEXT NOT NULL,
  name         TEXT NOT NULL,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by   UUID,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by   UUID,
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_prayer_teams UNIQUE (tenant_id, code)
);

CREATE TABLE IF NOT EXISTS pastoral.prayer_team_members (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL REFERENCES core.tenants (id),
  team_id       UUID NOT NULL REFERENCES pastoral.prayer_teams (id),
  user_id       UUID NOT NULL REFERENCES identity.users (id),
  joined_at     DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at    TIMESTAMPTZ,
  CONSTRAINT uq_prayer_team_members UNIQUE (tenant_id, team_id, user_id)
);

CREATE TABLE IF NOT EXISTS pastoral.prayer_requests (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id              UUID NOT NULL REFERENCES core.tenants (id),
  campus_id              UUID REFERENCES core.campuses (id),
  request_number         TEXT NOT NULL,
  requester_member_id    UUID REFERENCES membership.members (id),
  requester_user_id      UUID REFERENCES identity.users (id),
  category_id            UUID NOT NULL REFERENCES pastoral.prayer_categories (id),
  urgency                pastoral.urgency_code NOT NULL DEFAULT 'normal',
  is_confidential        BOOLEAN NOT NULL DEFAULT FALSE,
  status                 TEXT NOT NULL DEFAULT 'open'
    CONSTRAINT ck_prayer_requests_status CHECK (status IN (
      'open', 'assigned', 'praying', 'answered', 'escalated', 'closed'
    )),
  body_ciphertext        BYTEA,
  encryption_key_id      TEXT,
  assigned_team_id       UUID REFERENCES pastoral.prayer_teams (id),
  escalated_at           TIMESTAMPTZ,
  escalated_to_user_id   UUID REFERENCES identity.users (id),
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by             UUID,
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by             UUID,
  deleted_at             TIMESTAMPTZ,
  row_version            INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_prayer_requests_number UNIQUE (tenant_id, request_number)
);

CREATE INDEX IF NOT EXISTS ix_prayer_requests_urgency
  ON pastoral.prayer_requests (tenant_id, urgency, status)
  WHERE deleted_at IS NULL AND urgency IN ('high', 'emergency');

CREATE INDEX IF NOT EXISTS ix_prayer_requests_team
  ON pastoral.prayer_requests (tenant_id, assigned_team_id, status)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS pastoral.prayer_assignments (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL REFERENCES core.tenants (id),
  prayer_request_id   UUID NOT NULL REFERENCES pastoral.prayer_requests (id),
  assignee_user_id    UUID NOT NULL REFERENCES identity.users (id),
  assigned_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  prayed_at           TIMESTAMPTZ,
  followup_at         TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at          TIMESTAMPTZ,
  CONSTRAINT uq_prayer_assignments UNIQUE (prayer_request_id, assignee_user_id)
);

CREATE TABLE IF NOT EXISTS pastoral.prayer_testimonies (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL REFERENCES core.tenants (id),
  prayer_request_id   UUID NOT NULL REFERENCES pastoral.prayer_requests (id),
  body_ciphertext     BYTEA,
  encryption_key_id   TEXT,
  is_public           BOOLEAN NOT NULL DEFAULT FALSE,
  published_at        TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by          UUID,
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by          UUID,
  deleted_at          TIMESTAMPTZ
);

-- -----------------------------------------------------------------------------
-- WELFARE
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.welfare_requests (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  campus_id               UUID NOT NULL REFERENCES core.campuses (id),
  request_number          TEXT NOT NULL,
  beneficiary_member_id   UUID NOT NULL REFERENCES membership.members (id),
  requestor_user_id       UUID NOT NULL REFERENCES identity.users (id),
  need_type_id            UUID NOT NULL REFERENCES pastoral.welfare_need_types (id),
  amount_requested        NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_welfare_amount_positive CHECK (amount_requested > 0),
  currency_code           CHAR(3) NOT NULL REFERENCES core.currencies (code),
  narrative_ciphertext    BYTEA,
  encryption_key_id       TEXT,
  status                  pastoral.welfare_request_status NOT NULL DEFAULT 'submitted',
  submitted_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_welfare_requests_number UNIQUE (tenant_id, request_number)
);

CREATE INDEX IF NOT EXISTS ix_welfare_requests_tenant_status
  ON pastoral.welfare_requests (tenant_id, status, submitted_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_welfare_requests_beneficiary
  ON pastoral.welfare_requests (tenant_id, beneficiary_member_id)
  WHERE deleted_at IS NULL;

COMMENT ON TABLE pastoral.welfare_requests IS 'Welfare aid requests; requestor roles enforced in app (FR-WEL-001)';

CREATE TABLE IF NOT EXISTS pastoral.welfare_assessments (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  welfare_request_id   UUID NOT NULL REFERENCES pastoral.welfare_requests (id),
  assessor_user_id     UUID NOT NULL REFERENCES identity.users (id),
  household_size       INT,
  income_band_code     TEXT,
  prior_aid_count      INT NOT NULL DEFAULT 0,
  assessment_notes_ciphertext BYTEA,
  encryption_key_id    TEXT,
  assessed_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS pastoral.welfare_approvals (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  welfare_request_id   UUID NOT NULL REFERENCES pastoral.welfare_requests (id),
  approver_user_id     UUID NOT NULL REFERENCES identity.users (id),
  approval_level       TEXT NOT NULL
    CONSTRAINT ck_welfare_approval_level CHECK (approval_level IN (
      'welfare_team', 'pastor', 'finance', 'senior_pastor'
    )),
  decision             TEXT NOT NULL
    CONSTRAINT ck_welfare_approval_decision CHECK (decision IN ('approved', 'rejected', 'returned')),
  decision_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  comments             TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID
);

CREATE INDEX IF NOT EXISTS ix_welfare_approvals_request
  ON pastoral.welfare_approvals (tenant_id, welfare_request_id, decision_at);

CREATE TABLE IF NOT EXISTS pastoral.welfare_assistances (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  welfare_request_id   UUID NOT NULL REFERENCES pastoral.welfare_requests (id),
  fund_id              UUID, -- FK finance.funds added in finance DDL
  amount               NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_welfare_assist_amount CHECK (amount > 0),
  currency_code        CHAR(3) NOT NULL REFERENCES core.currencies (code),
  disbursement_method  TEXT NOT NULL
    CONSTRAINT ck_welfare_disburse_method CHECK (disbursement_method IN (
      'cash', 'bank_transfer', 'voucher', 'in_kind', 'other'
    )),
  voucher_id           UUID,
  disbursed_at         TIMESTAMPTZ,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ,
  row_version          INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pastoral.welfare_followup_reviews (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  welfare_request_id   UUID NOT NULL REFERENCES pastoral.welfare_requests (id),
  due_at               TIMESTAMPTZ NOT NULL,
  completed_at         TIMESTAMPTZ,
  reviewer_user_id     UUID REFERENCES identity.users (id),
  outcome_code         TEXT,
  notes                TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ
);

-- -----------------------------------------------------------------------------
-- WELFARE COMPARISON ENGINE (WCE)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.welfare_comparisons (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES core.tenants (id),
  session_number    TEXT NOT NULL,
  title             TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'open'
    CONSTRAINT ck_welfare_comparisons_status CHECK (status IN (
      'open', 'scored', 'finalized', 'cancelled'
    )),
  weights           JSONB NOT NULL DEFAULT '{}'::jsonb,
  decision_summary  TEXT,
  finalized_at      TIMESTAMPTZ,
  finalized_by      UUID REFERENCES identity.users (id),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by        UUID,
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by        UUID,
  deleted_at        TIMESTAMPTZ,
  row_version       INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_welfare_comparisons_number UNIQUE (tenant_id, session_number)
);

CREATE TABLE IF NOT EXISTS pastoral.welfare_comparison_items (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  comparison_id           UUID NOT NULL REFERENCES pastoral.welfare_comparisons (id),
  welfare_request_id      UUID NOT NULL REFERENCES pastoral.welfare_requests (id),
  display_order           SMALLINT NOT NULL
    CONSTRAINT ck_wce_item_order CHECK (display_order BETWEEN 1 AND 5),
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_wce_items_request UNIQUE (comparison_id, welfare_request_id),
  CONSTRAINT uq_wce_items_order UNIQUE (comparison_id, display_order)
);

CREATE TABLE IF NOT EXISTS pastoral.welfare_comparison_scores (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES core.tenants (id),
  comparison_id    UUID NOT NULL REFERENCES pastoral.welfare_comparisons (id),
  item_id          UUID NOT NULL REFERENCES pastoral.welfare_comparison_items (id),
  category         pastoral.wce_category_code NOT NULL,
  score            NUMERIC(5,2) NOT NULL
    CONSTRAINT ck_wce_score CHECK (score BETWEEN 0 AND 100),
  weight_pct       NUMERIC(5,2) NOT NULL
    CONSTRAINT ck_wce_weight CHECK (weight_pct BETWEEN 0 AND 100),
  notes            TEXT,
  scored_by        UUID REFERENCES identity.users (id),
  scored_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_wce_scores UNIQUE (item_id, category)
);

COMMENT ON TABLE pastoral.welfare_comparisons IS 'Compare up to 5 welfare cases (A–I categories, FR-WCE)';

-- -----------------------------------------------------------------------------
-- CEREMONIES
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pastoral.ceremonies (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  campus_id               UUID NOT NULL REFERENCES core.campuses (id),
  ceremony_number         TEXT NOT NULL,
  ceremony_type           pastoral.ceremony_type_code NOT NULL,
  status                  TEXT NOT NULL DEFAULT 'draft'
    CONSTRAINT ck_ceremonies_status CHECK (status IN (
      'draft', 'pending_approval', 'approved', 'scheduled',
      'published_banns', 'completed', 'cancelled', 'on_hold'
    )),
  title                   TEXT NOT NULL,
  scheduled_at            TIMESTAMPTZ,
  venue                   TEXT,
  baby_dedication_id      UUID REFERENCES membership.baby_dedications (id),
  marriage_id             UUID REFERENCES membership.marriages (id),
  service_slot_item_id    UUID, -- FK ops.service_slot_items after create
  certificate_object_key  TEXT,
  counselling_complete    BOOLEAN NOT NULL DEFAULT FALSE,
  banns_start_at          TIMESTAMPTZ,
  banns_end_at            TIMESTAMPTZ,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_ceremonies_number UNIQUE (tenant_id, ceremony_number)
);

CREATE INDEX IF NOT EXISTS ix_ceremonies_tenant_type_status
  ON pastoral.ceremonies (tenant_id, ceremony_type, status)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS pastoral.ceremony_approvals (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  ceremony_id     UUID NOT NULL REFERENCES pastoral.ceremonies (id),
  approval_step   TEXT NOT NULL
    CONSTRAINT ck_ceremony_approval_step CHECK (approval_step IN (
      'care_cell', 'elder', 'pastor', 'senior_pastor'
    )),
  decision        TEXT NOT NULL
    CONSTRAINT ck_ceremony_approval_decision CHECK (decision IN ('approved', 'rejected', 'returned')),
  approver_user_id UUID NOT NULL REFERENCES identity.users (id),
  decision_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  comments        TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pastoral.ceremony_objections (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  ceremony_id     UUID NOT NULL REFERENCES pastoral.ceremonies (id),
  raised_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  raised_by       UUID REFERENCES identity.users (id),
  summary         TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'open'
    CONSTRAINT ck_ceremony_objection_status CHECK (status IN (
      'open', 'under_review', 'sustained', 'dismissed'
    )),
  resolved_at     TIMESTAMPTZ,
  resolved_by     UUID REFERENCES identity.users (id),
  resolution      TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_ceremony_objections_open
  ON pastoral.ceremony_objections (tenant_id, ceremony_id, status)
  WHERE deleted_at IS NULL AND status IN ('open', 'under_review');

-- Link baby dedications.ceremony_id
ALTER TABLE membership.baby_dedications
  DROP CONSTRAINT IF EXISTS fk_baby_dedications_ceremony;
ALTER TABLE membership.baby_dedications
  ADD CONSTRAINT fk_baby_dedications_ceremony
  FOREIGN KEY (ceremony_id) REFERENCES pastoral.ceremonies (id);

-- -----------------------------------------------------------------------------
-- SERVICE SLOTS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.service_occurrences (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  campus_id       UUID NOT NULL REFERENCES core.campuses (id),
  service_type    ops.service_type_code NOT NULL,
  service_date    DATE NOT NULL,
  starts_at       TIMESTAMPTZ NOT NULL,
  ends_at         TIMESTAMPTZ NOT NULL,
  title           TEXT,
  is_published    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by      UUID,
  deleted_at      TIMESTAMPTZ,
  row_version     INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_service_occurrences UNIQUE (tenant_id, campus_id, service_type, service_date),
  CONSTRAINT ck_service_occurrence_window CHECK (ends_at > starts_at)
);

CREATE TABLE IF NOT EXISTS ops.service_slot_items (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id              UUID NOT NULL REFERENCES core.tenants (id),
  service_occurrence_id  UUID NOT NULL REFERENCES ops.service_occurrences (id),
  program_slot           ops.program_slot_code NOT NULL,
  sequence_no            INT NOT NULL DEFAULT 1,
  title                  TEXT NOT NULL,
  duration_minutes       INT NOT NULL
    CONSTRAINT ck_slot_item_duration CHECK (duration_minutes > 0),
  owner_user_id          UUID REFERENCES identity.users (id),
  ceremony_id            UUID REFERENCES pastoral.ceremonies (id),
  starts_offset_minutes  INT NOT NULL DEFAULT 0,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by             UUID,
  updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by             UUID,
  deleted_at             TIMESTAMPTZ,
  row_version            INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_service_slot_items
    UNIQUE (service_occurrence_id, program_slot, sequence_no)
);

CREATE INDEX IF NOT EXISTS ix_service_slot_items_occurrence
  ON ops.service_slot_items (tenant_id, service_occurrence_id)
  WHERE deleted_at IS NULL;

ALTER TABLE pastoral.ceremonies
  DROP CONSTRAINT IF EXISTS fk_ceremonies_slot_item;
ALTER TABLE pastoral.ceremonies
  ADD CONSTRAINT fk_ceremonies_slot_item
  FOREIGN KEY (service_slot_item_id) REFERENCES ops.service_slot_items (id);

-- -----------------------------------------------------------------------------
-- ACTIVITY ROSTER
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.activity_rosters (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  campus_id       UUID NOT NULL REFERENCES core.campuses (id),
  activity_type   ops.roster_activity_type NOT NULL,
  title           TEXT NOT NULL,
  activity_date   DATE NOT NULL,
  starts_at       TIMESTAMPTZ NOT NULL,
  ends_at         TIMESTAMPTZ NOT NULL,
  location        TEXT,
  status          TEXT NOT NULL DEFAULT 'draft'
    CONSTRAINT ck_activity_rosters_status CHECK (status IN (
      'draft', 'published', 'completed', 'cancelled'
    )),
  published_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by      UUID,
  deleted_at      TIMESTAMPTZ,
  row_version     INT NOT NULL DEFAULT 1,
  CONSTRAINT ck_activity_roster_window CHECK (ends_at > starts_at)
);

CREATE INDEX IF NOT EXISTS ix_activity_rosters_tenant_date
  ON ops.activity_rosters (tenant_id, campus_id, activity_date)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS ops.roster_assignments (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         UUID NOT NULL REFERENCES core.tenants (id),
  roster_id         UUID NOT NULL REFERENCES ops.activity_rosters (id),
  member_id         UUID REFERENCES membership.members (id),
  user_id           UUID REFERENCES identity.users (id),
  role_title        TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'assigned'
    CONSTRAINT ck_roster_assignment_status CHECK (status IN (
      'assigned', 'accepted', 'declined', 'substituted', 'completed'
    )),
  substitute_member_id UUID REFERENCES membership.members (id),
  notified_at       TIMESTAMPTZ,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by        UUID,
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by        UUID,
  deleted_at        TIMESTAMPTZ,
  CONSTRAINT ck_roster_assignment_subject
    CHECK (member_id IS NOT NULL OR user_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS ix_roster_assignments_member_date
  ON ops.roster_assignments (tenant_id, member_id)
  WHERE deleted_at IS NULL AND member_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_roster_assignments_roster
  ON ops.roster_assignments (tenant_id, roster_id)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS ops.roster_availability (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  member_id       UUID NOT NULL REFERENCES membership.members (id),
  available_from  TIMESTAMPTZ NOT NULL,
  available_to    TIMESTAMPTZ NOT NULL,
  is_available    BOOLEAN NOT NULL DEFAULT TRUE,
  notes           TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ,
  CONSTRAINT ck_roster_availability_window CHECK (available_to > available_from)
);

-- -----------------------------------------------------------------------------
-- COMMUNICATIONS
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS comms.communications (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES core.tenants (id),
  campus_id          UUID REFERENCES core.campuses (id),
  content_type       comms.content_type_code NOT NULL,
  subject            TEXT NOT NULL,
  body_object_key    TEXT,
  body_preview       TEXT,
  channel_flags      TEXT[] NOT NULL DEFAULT '{}',
  audience_filter    JSONB NOT NULL DEFAULT '{}'::jsonb,
  status             TEXT NOT NULL DEFAULT 'draft'
    CONSTRAINT ck_communications_status CHECK (status IN (
      'draft', 'scheduled', 'sending', 'sent', 'cancelled', 'failed'
    )),
  scheduled_at       TIMESTAMPTZ,
  sent_at            TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_communications_tenant_status
  ON comms.communications (tenant_id, status, scheduled_at)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS comms.communication_attachments (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL REFERENCES core.tenants (id),
  communication_id    UUID NOT NULL REFERENCES comms.communications (id),
  object_key          TEXT NOT NULL,
  file_name           TEXT NOT NULL,
  content_type        TEXT NOT NULL,
  byte_size           BIGINT NOT NULL
    CONSTRAINT ck_attachment_size CHECK (byte_size > 0 AND byte_size <= 52428800), -- 50 MB
  allow_email         BOOLEAN NOT NULL DEFAULT TRUE,
  allow_whatsapp      BOOLEAN NOT NULL DEFAULT TRUE,
  allow_portal        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by          UUID,
  deleted_at          TIMESTAMPTZ,
  CONSTRAINT ck_attachment_content_type CHECK (
    content_type IN (
      'application/pdf',
      'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/gif',
      'video/mp4'
    )
  ),
  CONSTRAINT ck_attachment_email_no_mp4 CHECK (
    NOT (allow_email AND content_type = 'video/mp4')
  )
);

COMMENT ON TABLE comms.communication_attachments
  IS 'Max 50MB; Email allows images+PDF only (FR-COM-004/005)';

CREATE TABLE IF NOT EXISTS comms.communication_deliveries (
  id                  UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL,
  communication_id    UUID NOT NULL,
  channel             comms.notification_channel NOT NULL,
  recipient_user_id   UUID,
  recipient_member_id UUID,
  provider_message_id TEXT,
  status              comms.notification_status NOT NULL DEFAULT 'queued',
  error_code          TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS comms.communication_deliveries_y2026m08
  PARTITION OF comms.communication_deliveries
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS comms.communication_deliveries_y2026m09
  PARTITION OF comms.communication_deliveries
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE INDEX IF NOT EXISTS ix_communication_deliveries_comm
  ON comms.communication_deliveries (tenant_id, communication_id, created_at);

-- -----------------------------------------------------------------------------
-- NOTIFICATIONS (partitioned)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS comms.notifications (
  id               UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL,
  user_id          UUID NOT NULL,
  channel          comms.notification_channel NOT NULL,
  template_code    TEXT NOT NULL,
  payload_ref      TEXT,
  entity_type      TEXT,
  entity_id        UUID,
  status           comms.notification_status NOT NULL DEFAULT 'queued',
  idempotency_key  TEXT,
  error_code       TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at          TIMESTAMPTZ,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE comms.notifications
  IS 'Outbound notification queue; payload_ref points to object store — no PII bodies in row';

CREATE TABLE IF NOT EXISTS comms.notifications_y2026m08
  PARTITION OF comms.notifications
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS comms.notifications_y2026m09
  PARTITION OF comms.notifications
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS comms.notifications_y2026m10
  PARTITION OF comms.notifications
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE INDEX IF NOT EXISTS ix_notifications_tenant_user_created
  ON comms.notifications (tenant_id, user_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS uq_notifications_idempotency
  ON comms.notifications (tenant_id, idempotency_key, created_at)
  WHERE idempotency_key IS NOT NULL;

-- -----------------------------------------------------------------------------
-- AUDIT LOG (partitioned, immutable)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.audit_log (
  id               UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL,
  occurred_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor_user_id    UUID,
  action           TEXT NOT NULL,
  entity_type      TEXT NOT NULL,
  entity_id        UUID,
  correlation_id   UUID,
  ip_hash          BYTEA,
  before_hash      BYTEA,
  after_hash       BYTEA,
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

COMMENT ON TABLE core.audit_log
  IS 'Immutable audit trail; never store PII/PHI field values in metadata';

CREATE TABLE IF NOT EXISTS core.audit_log_y2026m08
  PARTITION OF core.audit_log
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS core.audit_log_y2026m09
  PARTITION OF core.audit_log
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS core.audit_log_y2026m10
  PARTITION OF core.audit_log
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE INDEX IF NOT EXISTS ix_audit_log_tenant_entity
  ON core.audit_log (tenant_id, entity_type, entity_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS ix_audit_log_tenant_actor
  ON core.audit_log (tenant_id, actor_user_id, occurred_at DESC);

-- -----------------------------------------------------------------------------
-- RLS (representative set)
-- -----------------------------------------------------------------------------

ALTER TABLE pastoral.counselling_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE pastoral.counselling_cases FORCE ROW LEVEL SECURITY;
ALTER TABLE pastoral.counselling_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE pastoral.counselling_sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE pastoral.welfare_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE pastoral.welfare_requests FORCE ROW LEVEL SECURITY;
ALTER TABLE pastoral.prayer_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE pastoral.prayer_requests FORCE ROW LEVEL SECURITY;
ALTER TABLE ops.activity_rosters ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.activity_rosters FORCE ROW LEVEL SECURITY;
ALTER TABLE comms.communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE comms.communications FORCE ROW LEVEL SECURITY;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_counselling ON pastoral.counselling_cases
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_welfare ON pastoral.welfare_requests
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_prayer ON pastoral.prayer_requests
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_rosters ON ops.activity_rosters
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
