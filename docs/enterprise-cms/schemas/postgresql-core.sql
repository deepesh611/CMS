-- =============================================================================
-- Enterprise CMS — PostgreSQL DDL
-- File: postgresql-core.sql
-- Scope: CORE + IDENTITY + MEMBERSHIP + VISITOR + CARE CELL
-- PostgreSQL 16+ | Multi-tenant | UUID PKs | Soft delete | Audit columns
-- No real PII — illustrative comments only
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS membership;
CREATE SCHEMA IF NOT EXISTS visitor;

COMMENT ON SCHEMA core IS 'Tenancy, campuses, care cells, shared lookups';
COMMENT ON SCHEMA identity IS 'Users, roles, permissions';
COMMENT ON SCHEMA membership IS 'Members, families, lifecycle events';
COMMENT ON SCHEMA visitor IS 'Visitors and follow-up cadence';

-- -----------------------------------------------------------------------------
-- ENUM types (product-stable)
-- -----------------------------------------------------------------------------

DO $$ BEGIN
  CREATE TYPE core.gender_code AS ENUM (
    'male', 'female', 'unspecified', 'prefer_not_to_say'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE core.marital_status_code AS ENUM (
    'single', 'married', 'widowed', 'divorced', 'separated', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE membership.transfer_direction AS ENUM ('in', 'out');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE membership.enrollment_status AS ENUM (
    'enrolled', 'completed', 'withdrawn'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE membership.family_relationship AS ENUM (
    'spouse', 'child', 'parent', 'sibling', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE visitor.followup_status AS ENUM (
    'pending', 'completed', 'cancelled', 'escalated'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE visitor.pipeline_stage AS ENUM (
    'new', 'contacted', 'engaged', 'class_invited', 'converted', 'lost_closed'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- -----------------------------------------------------------------------------
-- Currencies (shared reference; finance DDL extends usage)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.currencies (
  code            CHAR(3) PRIMARY KEY,
  name            TEXT NOT NULL,
  decimal_places  SMALLINT NOT NULL DEFAULT 2
    CONSTRAINT ck_currencies_decimal_places CHECK (decimal_places BETWEEN 0 AND 4),
  is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE core.currencies IS 'ISO 4217 currencies supported by the platform';

INSERT INTO core.currencies (code, name, decimal_places) VALUES
  ('OMR', 'Omani Rial', 3),
  ('USD', 'US Dollar', 2),
  ('EUR', 'Euro', 2),
  ('GBP', 'Pound Sterling', 2),
  ('AED', 'UAE Dirham', 2),
  ('SAR', 'Saudi Riyal', 2),
  ('INR', 'Indian Rupee', 2),
  ('QAR', 'Qatari Riyal', 2),
  ('KWD', 'Kuwaiti Dinar', 3),
  ('BHD', 'Bahraini Dinar', 3)
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- CORE: tenants & campuses
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.tenants (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code               TEXT NOT NULL,
  name               TEXT NOT NULL,
  primary_currency   CHAR(3) NOT NULL REFERENCES core.currencies (code),
  timezone           TEXT NOT NULL DEFAULT 'Asia/Muscat',
  status             TEXT NOT NULL DEFAULT 'active'
    CONSTRAINT ck_tenants_status CHECK (status IN ('active', 'suspended', 'provisioning')),
  settings           JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_tenants_code UNIQUE (code)
);

COMMENT ON TABLE core.tenants IS 'Top-level multi-tenant boundary; hard isolation via tenant_id + RLS';

CREATE TABLE IF NOT EXISTS core.campuses (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  code            TEXT NOT NULL,
  name            TEXT NOT NULL,
  timezone        TEXT NOT NULL DEFAULT 'Asia/Muscat',
  address_line1   TEXT,
  address_line2   TEXT,
  city            TEXT,
  region          TEXT,
  postal_code     TEXT,
  country_code    CHAR(2),
  is_primary      BOOLEAN NOT NULL DEFAULT FALSE,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by      UUID,
  deleted_at      TIMESTAMPTZ,
  row_version     INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_campuses_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_campuses_tenant_active
  ON core.campuses (tenant_id)
  WHERE deleted_at IS NULL AND is_active;

COMMENT ON TABLE core.campuses IS 'Physical/logical campuses within a tenant';

-- -----------------------------------------------------------------------------
-- Lookups: member statuses, visitor sources
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS membership.member_statuses (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID REFERENCES core.tenants (id), -- NULL = system seed
  code         TEXT NOT NULL,
  label        TEXT NOT NULL,
  sort_order   INT NOT NULL DEFAULT 0,
  is_terminal  BOOLEAN NOT NULL DEFAULT FALSE,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_member_statuses_tenant_code UNIQUE (tenant_id, code)
);

COMMENT ON TABLE membership.member_statuses IS 'Membership lifecycle statuses (Prospect…Deceased)';

INSERT INTO membership.member_statuses (tenant_id, code, label, sort_order, is_terminal) VALUES
  (NULL, 'prospect', 'Prospect', 10, FALSE),
  (NULL, 'in_class', 'In Class', 20, FALSE),
  (NULL, 'active', 'Active', 30, FALSE),
  (NULL, 'inactive', 'Inactive', 40, FALSE),
  (NULL, 'transferred_out', 'Transferred Out', 50, TRUE),
  (NULL, 'transferred_in', 'Transferred In', 60, FALSE),
  (NULL, 'suspended', 'Suspended', 70, FALSE),
  (NULL, 'deceased', 'Deceased', 80, TRUE)
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS visitor.visitor_sources (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID REFERENCES core.tenants (id),
  code               TEXT NOT NULL,
  label              TEXT NOT NULL,
  requires_referrer  BOOLEAN NOT NULL DEFAULT FALSE,
  sort_order         INT NOT NULL DEFAULT 0,
  is_active          BOOLEAN NOT NULL DEFAULT TRUE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at         TIMESTAMPTZ,
  CONSTRAINT uq_visitor_sources_tenant_code UNIQUE (tenant_id, code)
);

COMMENT ON TABLE visitor.visitor_sources IS 'Attribution sources per FR-VIS-001';

INSERT INTO visitor.visitor_sources (tenant_id, code, label, requires_referrer, sort_order) VALUES
  (NULL, 'friend', 'Friend', TRUE, 10),
  (NULL, 'church_member', 'Church Member', TRUE, 20),
  (NULL, 'family_member', 'Family Member', TRUE, 30),
  (NULL, 'care_cell_member', 'Care Cell Member', TRUE, 40),
  (NULL, 'pastor', 'Pastor', TRUE, 50),
  (NULL, 'ministry_leader', 'Ministry Leader', TRUE, 60),
  (NULL, 'church_event', 'Church Event', FALSE, 70),
  (NULL, 'outreach_program', 'Outreach Program', FALSE, 80),
  (NULL, 'website', 'Website', FALSE, 90),
  (NULL, 'facebook', 'Facebook', FALSE, 100),
  (NULL, 'instagram', 'Instagram', FALSE, 110),
  (NULL, 'youtube', 'YouTube', FALSE, 120),
  (NULL, 'whatsapp', 'WhatsApp', FALSE, 130),
  (NULL, 'google_search', 'Google Search', FALSE, 140),
  (NULL, 'walk_in', 'Walk-In', FALSE, 150),
  (NULL, 'advertisement', 'Advertisement', FALSE, 160),
  (NULL, 'other', 'Other', FALSE, 170)
ON CONFLICT DO NOTHING;

-- -----------------------------------------------------------------------------
-- IDENTITY: users & RBAC (created before members for FK flexibility)
-- members created next; users.member_id added after members exist
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS identity.permissions (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code         TEXT NOT NULL,
  module       TEXT NOT NULL,
  description  TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_permissions_code UNIQUE (code)
);

COMMENT ON TABLE identity.permissions IS 'Global permission catalogue (module.action)';

CREATE TABLE IF NOT EXISTS identity.roles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES core.tenants (id),
  code         TEXT NOT NULL,
  name         TEXT NOT NULL,
  description  TEXT,
  is_system    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by   UUID,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by   UUID,
  deleted_at   TIMESTAMPTZ,
  row_version  INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_roles_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_roles_tenant
  ON identity.roles (tenant_id)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS identity.role_permissions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  role_id         UUID NOT NULL REFERENCES identity.roles (id),
  permission_id   UUID NOT NULL REFERENCES identity.permissions (id),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  CONSTRAINT uq_role_permissions UNIQUE (role_id, permission_id)
);

CREATE INDEX IF NOT EXISTS ix_role_permissions_tenant_role
  ON identity.role_permissions (tenant_id, role_id);

CREATE TABLE IF NOT EXISTS identity.users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       UUID NOT NULL REFERENCES core.tenants (id),
  email           CITEXT NOT NULL,
  display_name    TEXT NOT NULL,
  member_id       UUID, -- FK added after membership.members
  idp_subject     TEXT,
  mfa_required    BOOLEAN NOT NULL DEFAULT FALSE,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at   TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by      UUID,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by      UUID,
  deleted_at      TIMESTAMPTZ,
  row_version     INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_tenant_idp_subject
  ON identity.users (tenant_id, idp_subject)
  WHERE idp_subject IS NOT NULL AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_users_tenant_active
  ON identity.users (tenant_id)
  WHERE deleted_at IS NULL AND is_active;

COMMENT ON TABLE identity.users IS 'Authenticated principals; link to members for portal users';

CREATE TABLE IF NOT EXISTS identity.user_roles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES core.tenants (id),
  user_id      UUID NOT NULL REFERENCES identity.users (id),
  role_id      UUID NOT NULL REFERENCES identity.roles (id),
  campus_id    UUID REFERENCES core.campuses (id),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by   UUID,
  deleted_at   TIMESTAMPTZ,
  CONSTRAINT uq_user_roles_scope UNIQUE NULLS NOT DISTINCT (tenant_id, user_id, role_id, campus_id)
);

CREATE INDEX IF NOT EXISTS ix_user_roles_user
  ON identity.user_roles (tenant_id, user_id)
  WHERE deleted_at IS NULL;

-- Seed default permission codes (subset; full matrix in security model)
INSERT INTO identity.permissions (code, module, description) VALUES
  ('members.read', 'MEM', 'Read member profiles'),
  ('members.write', 'MEM', 'Create/update members'),
  ('members.restore', 'MEM', 'Restore soft-deleted members'),
  ('visitors.create', 'VIS', 'Register visitors'),
  ('visitors.followup', 'VIS', 'Manage visitor follow-ups'),
  ('counselling.create', 'COUN', 'Open counselling cases'),
  ('counselling.notes.read', 'COUN', 'Read confidential session notes'),
  ('welfare.request', 'WEL', 'Create welfare requests'),
  ('welfare.approve', 'WEL', 'Approve welfare assistance'),
  ('finance.post', 'FIN', 'Post giving and expenses'),
  ('finance.approve', 'FIN', 'Approve payments above threshold'),
  ('roster.assign', 'ROST', 'Assign roster duties'),
  ('admin.rbac', 'SEC', 'Manage roles and permissions'),
  ('audit.read', 'SEC', 'Read audit log')
ON CONFLICT (code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- CARE CELLS (forward-declare leader FKs after members)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.care_cells (
  id                           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id                    UUID NOT NULL REFERENCES core.tenants (id),
  campus_id                    UUID NOT NULL REFERENCES core.campuses (id),
  code                         TEXT NOT NULL,
  name                         TEXT NOT NULL,
  leader_member_id             UUID,
  associate_leader_member_id   UUID,
  meeting_day                  TEXT,
  is_active                    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by                   UUID,
  updated_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by                   UUID,
  deleted_at                   TIMESTAMPTZ,
  row_version                  INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_care_cells_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_care_cells_tenant_campus
  ON core.care_cells (tenant_id, campus_id)
  WHERE deleted_at IS NULL AND is_active;

COMMENT ON TABLE core.care_cells IS 'Care cell small groups; leaders are members';

-- -----------------------------------------------------------------------------
-- MEMBERSHIP: families & members
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS membership.families (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL REFERENCES core.tenants (id),
  campus_id           UUID NOT NULL REFERENCES core.campuses (id),
  family_code         TEXT NOT NULL,
  primary_member_id   UUID, -- set after members
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by          UUID,
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by          UUID,
  deleted_at          TIMESTAMPTZ,
  row_version         INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_families_tenant_code UNIQUE (tenant_id, family_code)
);

CREATE INDEX IF NOT EXISTS ix_families_tenant_campus
  ON membership.families (tenant_id, campus_id)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.members (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id             UUID NOT NULL REFERENCES core.tenants (id),
  campus_id             UUID NOT NULL REFERENCES core.campuses (id),
  membership_number     TEXT NOT NULL,
  family_id             UUID REFERENCES membership.families (id),
  care_cell_id          UUID REFERENCES core.care_cells (id),
  status_id             UUID NOT NULL REFERENCES membership.member_statuses (id),
  legal_name            TEXT NOT NULL,
  preferred_name        TEXT,
  email                 CITEXT,
  mobile_e164           TEXT,
  date_of_birth         DATE,
  gender                core.gender_code,
  marital_status        core.marital_status_code,
  address_line1         TEXT,
  address_line2         TEXT,
  city                  TEXT,
  region                TEXT,
  postal_code           TEXT,
  country_code          CHAR(2),
  profession            TEXT,
  photo_object_key      TEXT,
  classification_tags   TEXT[] NOT NULL DEFAULT '{}',
  engagement_score      NUMERIC(5,2),
  consent_comms_at      TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by            UUID,
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by            UUID,
  deleted_at            TIMESTAMPTZ,
  row_version           INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_members_tenant_membership_number UNIQUE (tenant_id, membership_number),
  CONSTRAINT ck_members_engagement_score
    CHECK (engagement_score IS NULL OR engagement_score BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS ix_members_tenant_campus_status
  ON membership.members (tenant_id, campus_id, status_id)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_members_tenant_care_cell
  ON membership.members (tenant_id, care_cell_id)
  WHERE deleted_at IS NULL AND care_cell_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_members_tenant_family
  ON membership.members (tenant_id, family_id)
  WHERE deleted_at IS NULL AND family_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_members_tenant_email_active
  ON membership.members (tenant_id, email)
  WHERE email IS NOT NULL AND deleted_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_members_tenant_mobile_active
  ON membership.members (tenant_id, mobile_e164)
  WHERE mobile_e164 IS NOT NULL AND deleted_at IS NULL;

COMMENT ON TABLE membership.members IS 'Member registry; PII access controlled; never log column values';

-- Deferred FKs
ALTER TABLE identity.users
  DROP CONSTRAINT IF EXISTS fk_users_member;
ALTER TABLE identity.users
  ADD CONSTRAINT fk_users_member
  FOREIGN KEY (member_id) REFERENCES membership.members (id);

ALTER TABLE membership.families
  DROP CONSTRAINT IF EXISTS fk_families_primary_member;
ALTER TABLE membership.families
  ADD CONSTRAINT fk_families_primary_member
  FOREIGN KEY (primary_member_id) REFERENCES membership.members (id);

ALTER TABLE core.care_cells
  DROP CONSTRAINT IF EXISTS fk_care_cells_leader;
ALTER TABLE core.care_cells
  ADD CONSTRAINT fk_care_cells_leader
  FOREIGN KEY (leader_member_id) REFERENCES membership.members (id);

ALTER TABLE core.care_cells
  DROP CONSTRAINT IF EXISTS fk_care_cells_associate;
ALTER TABLE core.care_cells
  ADD CONSTRAINT fk_care_cells_associate
  FOREIGN KEY (associate_leader_member_id) REFERENCES membership.members (id);

CREATE TABLE IF NOT EXISTS membership.family_members (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES core.tenants (id),
  family_id      UUID NOT NULL REFERENCES membership.families (id),
  member_id      UUID NOT NULL REFERENCES membership.members (id),
  relationship   membership.family_relationship NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by     UUID,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by     UUID,
  deleted_at     TIMESTAMPTZ,
  CONSTRAINT uq_family_members UNIQUE (tenant_id, family_id, member_id)
);

CREATE INDEX IF NOT EXISTS ix_family_members_member
  ON membership.family_members (tenant_id, member_id)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS core.care_cell_members (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES core.tenants (id),
  care_cell_id   UUID NOT NULL REFERENCES core.care_cells (id),
  member_id      UUID NOT NULL REFERENCES membership.members (id),
  role_in_cell   TEXT NOT NULL DEFAULT 'member'
    CONSTRAINT ck_care_cell_members_role
      CHECK (role_in_cell IN ('member', 'leader', 'associate')),
  joined_at      DATE NOT NULL DEFAULT CURRENT_DATE,
  left_at        DATE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by     UUID,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by     UUID,
  deleted_at     TIMESTAMPTZ,
  CONSTRAINT uq_care_cell_members UNIQUE (tenant_id, care_cell_id, member_id)
);

CREATE INDEX IF NOT EXISTS ix_care_cell_members_member
  ON core.care_cell_members (tenant_id, member_id)
  WHERE deleted_at IS NULL;

-- -----------------------------------------------------------------------------
-- MEMBERSHIP lifecycle: baptisms, transfers, classes, marriages, dedications
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS membership.baptisms (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  member_id               UUID NOT NULL REFERENCES membership.members (id),
  campus_id               UUID NOT NULL REFERENCES core.campuses (id),
  baptism_date            DATE NOT NULL,
  officiant_user_id       UUID REFERENCES identity.users (id),
  certificate_object_key  TEXT,
  notes                   TEXT,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_baptisms_tenant_member
  ON membership.baptisms (tenant_id, member_id)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.transfers (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  member_id               UUID NOT NULL REFERENCES membership.members (id),
  direction               membership.transfer_direction NOT NULL,
  effective_date          DATE NOT NULL,
  source_church           TEXT,
  destination_church      TEXT,
  source_campus_id        UUID REFERENCES core.campuses (id),
  destination_campus_id   UUID REFERENCES core.campuses (id),
  status                  TEXT NOT NULL DEFAULT 'requested'
    CONSTRAINT ck_transfers_status CHECK (status IN (
      'requested', 'approved', 'completed', 'rejected', 'cancelled'
    )),
  reason                  TEXT,
  approved_by             UUID REFERENCES identity.users (id),
  approved_at             TIMESTAMPTZ,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_transfers_tenant_status
  ON membership.transfers (tenant_id, status, effective_date)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.membership_classes (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    UUID NOT NULL REFERENCES core.tenants (id),
  campus_id    UUID NOT NULL REFERENCES core.campuses (id),
  name         TEXT NOT NULL,
  description  TEXT,
  starts_on    DATE NOT NULL,
  ends_on      DATE,
  capacity     INT,
  is_active    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by   UUID,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by   UUID,
  deleted_at   TIMESTAMPTZ,
  row_version  INT NOT NULL DEFAULT 1,
  CONSTRAINT ck_membership_classes_dates
    CHECK (ends_on IS NULL OR ends_on >= starts_on)
);

CREATE INDEX IF NOT EXISTS ix_membership_classes_tenant_campus
  ON membership.membership_classes (tenant_id, campus_id, starts_on)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.class_enrollments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id     UUID NOT NULL REFERENCES core.tenants (id),
  class_id      UUID NOT NULL REFERENCES membership.membership_classes (id),
  member_id     UUID NOT NULL REFERENCES membership.members (id),
  status        membership.enrollment_status NOT NULL DEFAULT 'enrolled',
  enrolled_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by    UUID,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by    UUID,
  deleted_at    TIMESTAMPTZ,
  CONSTRAINT uq_class_enrollments UNIQUE (tenant_id, class_id, member_id)
);

CREATE INDEX IF NOT EXISTS ix_class_enrollments_member
  ON membership.class_enrollments (tenant_id, member_id, status)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.marriages (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  campus_id               UUID REFERENCES core.campuses (id),
  bride_member_id         UUID REFERENCES membership.members (id),
  groom_member_id         UUID REFERENCES membership.members (id),
  marriage_date           DATE,
  venue                   TEXT,
  certificate_object_key  TEXT,
  counselling_status      TEXT,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1,
  CONSTRAINT ck_marriages_parties
    CHECK (bride_member_id IS NOT NULL OR groom_member_id IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS ix_marriages_tenant_date
  ON membership.marriages (tenant_id, marriage_date)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.baby_dedications (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id               UUID NOT NULL REFERENCES core.tenants (id),
  campus_id               UUID NOT NULL REFERENCES core.campuses (id),
  family_id               UUID REFERENCES membership.families (id),
  child_given_name        TEXT NOT NULL,
  date_of_birth           DATE,
  place_of_birth          TEXT,
  father_member_id        UUID REFERENCES membership.members (id),
  mother_member_id        UUID REFERENCES membership.members (id),
  status                  TEXT NOT NULL DEFAULT 'recommended'
    CONSTRAINT ck_baby_dedications_status CHECK (status IN (
      'recommended', 'elder_review', 'pastoral_approved', 'scheduled',
      'completed', 'rejected', 'cancelled'
    )),
  ceremony_id             UUID, -- FK to pastoral.ceremonies added in pastoral-ops DDL
  certificate_object_key  TEXT,
  recommended_by          UUID REFERENCES identity.users (id),
  approved_by             UUID REFERENCES identity.users (id),
  approved_at             TIMESTAMPTZ,
  scheduled_at            TIMESTAMPTZ,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by              UUID,
  updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by              UUID,
  deleted_at              TIMESTAMPTZ,
  row_version             INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_baby_dedications_tenant_status
  ON membership.baby_dedications (tenant_id, status)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS membership.member_skills (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES core.tenants (id),
  member_id      UUID NOT NULL REFERENCES membership.members (id),
  skill_code     TEXT NOT NULL,
  proficiency    TEXT
    CONSTRAINT ck_member_skills_proficiency
      CHECK (proficiency IS NULL OR proficiency IN ('beginner', 'intermediate', 'advanced')),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by     UUID,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by     UUID,
  deleted_at     TIMESTAMPTZ,
  CONSTRAINT uq_member_skills UNIQUE (tenant_id, member_id, skill_code)
);

CREATE TABLE IF NOT EXISTS membership.member_ministries (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id      UUID NOT NULL REFERENCES core.tenants (id),
  member_id      UUID NOT NULL REFERENCES membership.members (id),
  ministry_code  TEXT NOT NULL,
  role_title     TEXT,
  started_on     DATE NOT NULL DEFAULT CURRENT_DATE,
  ended_on       DATE,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by     UUID,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by     UUID,
  deleted_at     TIMESTAMPTZ,
  CONSTRAINT ck_member_ministries_dates
    CHECK (ended_on IS NULL OR ended_on >= started_on)
);

CREATE INDEX IF NOT EXISTS ix_member_ministries_member
  ON membership.member_ministries (tenant_id, member_id)
  WHERE deleted_at IS NULL AND ended_on IS NULL;

-- -----------------------------------------------------------------------------
-- VISITOR module
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS visitor.visitors (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id             UUID NOT NULL REFERENCES core.tenants (id),
  campus_id             UUID NOT NULL REFERENCES core.campuses (id),
  visitor_number        TEXT NOT NULL,
  display_name          TEXT NOT NULL,
  email                 CITEXT,
  mobile_e164           TEXT,
  first_visit_at        TIMESTAMPTZ NOT NULL,
  source_id             UUID NOT NULL REFERENCES visitor.visitor_sources (id),
  referrer_member_id    UUID REFERENCES membership.members (id),
  pipeline_stage        visitor.pipeline_stage NOT NULL DEFAULT 'new',
  converted_member_id   UUID REFERENCES membership.members (id),
  interests             TEXT[] NOT NULL DEFAULT '{}',
  has_prayer_need       BOOLEAN NOT NULL DEFAULT FALSE,
  service_attended      TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by            UUID,
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by            UUID,
  deleted_at            TIMESTAMPTZ,
  row_version           INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_visitors_tenant_number UNIQUE (tenant_id, visitor_number)
);

CREATE INDEX IF NOT EXISTS ix_visitors_tenant_stage_visit
  ON visitor.visitors (tenant_id, pipeline_stage, first_visit_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_visitors_tenant_campus
  ON visitor.visitors (tenant_id, campus_id, first_visit_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_visitors_referrer
  ON visitor.visitors (tenant_id, referrer_member_id)
  WHERE deleted_at IS NULL AND referrer_member_id IS NOT NULL;

COMMENT ON TABLE visitor.visitors IS 'Visitor registry and conversion pipeline';
COMMENT ON COLUMN visitor.visitors.has_prayer_need IS 'Flag only; prayer body stored in pastoral module if captured';

CREATE TABLE IF NOT EXISTS visitor.visitor_followups (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES core.tenants (id),
  visitor_id         UUID NOT NULL REFERENCES visitor.visitors (id),
  day_offset         SMALLINT NOT NULL
    CONSTRAINT ck_visitor_followups_day
      CHECK (day_offset IN (1, 3, 7, 14, 30)),
  due_at             TIMESTAMPTZ NOT NULL,
  assignee_user_id   UUID NOT NULL REFERENCES identity.users (id),
  status             visitor.followup_status NOT NULL DEFAULT 'pending',
  outcome_code       TEXT,
  outcome_note       TEXT,
  completed_at       TIMESTAMPTZ,
  escalated_at       TIMESTAMPTZ,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_visitor_followups_day UNIQUE (visitor_id, day_offset)
);

CREATE INDEX IF NOT EXISTS ix_visitor_followups_assignee_due
  ON visitor.visitor_followups (tenant_id, assignee_user_id, due_at)
  WHERE deleted_at IS NULL AND status = 'pending';

CREATE INDEX IF NOT EXISTS ix_visitor_followups_visitor
  ON visitor.visitor_followups (tenant_id, visitor_id, day_offset)
  WHERE deleted_at IS NULL;

COMMENT ON TABLE visitor.visitor_followups IS 'Day 1/3/7/14/30 automated follow-up tasks (FR-VIS-020)';

-- -----------------------------------------------------------------------------
-- Attendance (partitioned) — core shared
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core.attendance_events (
  id               UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL,
  campus_id        UUID NOT NULL,
  member_id        UUID,
  visitor_id       UUID,
  service_type     TEXT NOT NULL
    CONSTRAINT ck_attendance_service_type
      CHECK (service_type IN ('friday_main', 'sunday_main', 'special')),
  occurred_at      TIMESTAMPTZ NOT NULL,
  checkin_method   TEXT NOT NULL DEFAULT 'manual'
    CONSTRAINT ck_attendance_checkin
      CHECK (checkin_method IN ('manual', 'qr', 'kiosk', 'import')),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  PRIMARY KEY (id, occurred_at),
  CONSTRAINT ck_attendance_subject
    CHECK (member_id IS NOT NULL OR visitor_id IS NOT NULL)
) PARTITION BY RANGE (occurred_at);

COMMENT ON TABLE core.attendance_events IS 'Monthly RANGE partitions; include occurred_at in queries for prune';

CREATE TABLE IF NOT EXISTS core.attendance_events_y2026m08
  PARTITION OF core.attendance_events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS core.attendance_events_y2026m09
  PARTITION OF core.attendance_events
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS core.attendance_events_y2026m10
  PARTITION OF core.attendance_events
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE INDEX IF NOT EXISTS ix_attendance_events_tenant_occurred
  ON core.attendance_events (tenant_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS ix_attendance_events_member
  ON core.attendance_events (tenant_id, member_id, occurred_at DESC)
  WHERE member_id IS NOT NULL;

-- -----------------------------------------------------------------------------
-- RLS helpers (enable on tenant tables)
-- -----------------------------------------------------------------------------

ALTER TABLE core.campuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.campuses FORCE ROW LEVEL SECURITY;
ALTER TABLE core.care_cells ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.care_cells FORCE ROW LEVEL SECURITY;
ALTER TABLE membership.members ENABLE ROW LEVEL SECURITY;
ALTER TABLE membership.members FORCE ROW LEVEL SECURITY;
ALTER TABLE visitor.visitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE visitor.visitors FORCE ROW LEVEL SECURITY;
ALTER TABLE visitor.visitor_followups ENABLE ROW LEVEL SECURITY;
ALTER TABLE visitor.visitor_followups FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.users FORCE ROW LEVEL SECURITY;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_campuses ON core.campuses
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_members ON membership.members
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_visitors ON visitor.visitors
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_followups ON visitor.visitor_followups
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_users ON identity.users
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_care_cells ON core.care_cells
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
