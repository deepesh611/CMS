-- =============================================================================
-- Enterprise CMS — PostgreSQL DDL
-- File: postgresql-finance-analytics.sql
-- Scope: Finance (multi-currency, funds, giving, budgets, vendors, Tally),
--        Analytics snapshots, AI recommendation store
-- Depends on: postgresql-core.sql, postgresql-pastoral-ops.sql (welfare fund link)
-- PostgreSQL 16+ | No real PII
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS analytics;

COMMENT ON SCHEMA finance IS 'Multi-currency funds, giving, expenses, Tally sync';
COMMENT ON SCHEMA analytics IS 'KPI snapshots and AI recommendation store';

-- -----------------------------------------------------------------------------
-- ENUM types
-- -----------------------------------------------------------------------------

DO $$ BEGIN
  CREATE TYPE finance.giving_instrument AS ENUM (
    'cash', 'card', 'bank_transfer', 'cheque', 'online', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE finance.fund_type_code AS ENUM (
    'general', 'welfare', 'mission', 'building', 'other'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE finance.tally_sync_status AS ENUM (
    'pending', 'in_progress', 'succeeded', 'failed', 'dead_letter'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE finance.expense_status AS ENUM (
    'draft', 'pending_approval', 'approved', 'paid', 'cancelled', 'rejected'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE analytics.recommendation_status AS ENUM (
    'pending', 'accepted', 'edited', 'rejected', 'expired'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- -----------------------------------------------------------------------------
-- FX rates
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.exchange_rates (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID REFERENCES core.tenants (id), -- NULL = platform default feed
  base_currency    CHAR(3) NOT NULL REFERENCES core.currencies (code),
  quote_currency   CHAR(3) NOT NULL REFERENCES core.currencies (code),
  rate_date        DATE NOT NULL,
  rate             NUMERIC(18,8) NOT NULL
    CONSTRAINT ck_exchange_rates_positive CHECK (rate > 0),
  source           TEXT NOT NULL DEFAULT 'manual',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  CONSTRAINT uq_exchange_rates UNIQUE (tenant_id, base_currency, quote_currency, rate_date),
  CONSTRAINT ck_exchange_rates_pair CHECK (base_currency <> quote_currency)
);

CREATE INDEX IF NOT EXISTS ix_exchange_rates_pair_date
  ON finance.exchange_rates (base_currency, quote_currency, rate_date DESC);

COMMENT ON TABLE finance.exchange_rates IS 'Daily FX for multi-currency posting and gain/loss';

-- -----------------------------------------------------------------------------
-- Funds
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.funds (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES core.tenants (id),
  campus_id        UUID REFERENCES core.campuses (id),
  code             TEXT NOT NULL,
  name             TEXT NOT NULL,
  fund_type        finance.fund_type_code NOT NULL DEFAULT 'general',
  currency_code    CHAR(3) NOT NULL REFERENCES core.currencies (code),
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  tally_ledger_ref TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by       UUID,
  deleted_at       TIMESTAMPTZ,
  row_version      INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_funds_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_funds_tenant_type
  ON finance.funds (tenant_id, fund_type)
  WHERE deleted_at IS NULL AND is_active;

COMMENT ON TABLE finance.funds IS 'Chart of funds: general, welfare, mission, building';

-- Wire pastoral welfare_assistances.fund_id
ALTER TABLE pastoral.welfare_assistances
  DROP CONSTRAINT IF EXISTS fk_welfare_assistances_fund;
ALTER TABLE pastoral.welfare_assistances
  ADD CONSTRAINT fk_welfare_assistances_fund
  FOREIGN KEY (fund_id) REFERENCES finance.funds (id);

-- -----------------------------------------------------------------------------
-- Giving: donations, tithes, offerings
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.donations (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES core.tenants (id),
  campus_id          UUID NOT NULL REFERENCES core.campuses (id),
  fund_id            UUID NOT NULL REFERENCES finance.funds (id),
  member_id          UUID REFERENCES membership.members (id),
  amount             NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_donations_amount CHECK (amount > 0),
  currency_code      CHAR(3) NOT NULL REFERENCES core.currencies (code),
  fx_rate            NUMERIC(18,8),
  amount_base        NUMERIC(18,4),
  base_currency      CHAR(3) REFERENCES core.currencies (code),
  received_at        TIMESTAMPTZ NOT NULL,
  instrument         finance.giving_instrument NOT NULL DEFAULT 'cash',
  reference_code     TEXT,
  idempotency_key    TEXT NOT NULL,
  notes              TEXT,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_donations_idempotency UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_donations_tenant_received
  ON finance.donations (tenant_id, received_at DESC)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_donations_member
  ON finance.donations (tenant_id, member_id, received_at DESC)
  WHERE deleted_at IS NULL AND member_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_donations_fund
  ON finance.donations (tenant_id, fund_id, received_at DESC)
  WHERE deleted_at IS NULL;

COMMENT ON TABLE finance.donations IS 'General donations; idempotent posts via idempotency_key';

CREATE TABLE IF NOT EXISTS finance.tithes (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES core.tenants (id),
  campus_id          UUID NOT NULL REFERENCES core.campuses (id),
  fund_id            UUID NOT NULL REFERENCES finance.funds (id),
  member_id          UUID NOT NULL REFERENCES membership.members (id),
  amount             NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_tithes_amount CHECK (amount > 0),
  currency_code      CHAR(3) NOT NULL REFERENCES core.currencies (code),
  fx_rate            NUMERIC(18,8),
  amount_base        NUMERIC(18,4),
  base_currency      CHAR(3) REFERENCES core.currencies (code),
  period_year        INT NOT NULL
    CONSTRAINT ck_tithes_year CHECK (period_year BETWEEN 2000 AND 2100),
  period_month       SMALLINT
    CONSTRAINT ck_tithes_month CHECK (period_month IS NULL OR period_month BETWEEN 1 AND 12),
  received_at        TIMESTAMPTZ NOT NULL,
  instrument         finance.giving_instrument NOT NULL DEFAULT 'cash',
  reference_code     TEXT,
  idempotency_key    TEXT NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_tithes_idempotency UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_tithes_tenant_period
  ON finance.tithes (tenant_id, period_year, period_month)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_tithes_member
  ON finance.tithes (tenant_id, member_id, received_at DESC)
  WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS finance.offerings (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL REFERENCES core.tenants (id),
  campus_id          UUID NOT NULL REFERENCES core.campuses (id),
  fund_id            UUID NOT NULL REFERENCES finance.funds (id),
  member_id          UUID REFERENCES membership.members (id),
  service_type       TEXT
    CONSTRAINT ck_offerings_service CHECK (
      service_type IS NULL OR service_type IN ('friday_main', 'sunday_main', 'special')
    ),
  amount             NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_offerings_amount CHECK (amount > 0),
  currency_code      CHAR(3) NOT NULL REFERENCES core.currencies (code),
  fx_rate            NUMERIC(18,8),
  amount_base        NUMERIC(18,4),
  base_currency      CHAR(3) REFERENCES core.currencies (code),
  received_at        TIMESTAMPTZ NOT NULL,
  instrument         finance.giving_instrument NOT NULL DEFAULT 'cash',
  reference_code     TEXT,
  idempotency_key    TEXT NOT NULL,
  is_anonymous       BOOLEAN NOT NULL DEFAULT FALSE,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by         UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by         UUID,
  deleted_at         TIMESTAMPTZ,
  row_version        INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_offerings_idempotency UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_offerings_tenant_received
  ON finance.offerings (tenant_id, campus_id, received_at DESC)
  WHERE deleted_at IS NULL;

-- -----------------------------------------------------------------------------
-- Budgets
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.budgets (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES core.tenants (id),
  campus_id        UUID REFERENCES core.campuses (id),
  name             TEXT NOT NULL,
  fiscal_year      INT NOT NULL,
  currency_code    CHAR(3) NOT NULL REFERENCES core.currencies (code),
  status           TEXT NOT NULL DEFAULT 'draft'
    CONSTRAINT ck_budgets_status CHECK (status IN ('draft', 'active', 'closed')),
  starts_on        DATE NOT NULL,
  ends_on          DATE NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by       UUID,
  deleted_at       TIMESTAMPTZ,
  row_version      INT NOT NULL DEFAULT 1,
  CONSTRAINT ck_budgets_window CHECK (ends_on >= starts_on),
  CONSTRAINT uq_budgets_tenant_name_year UNIQUE (tenant_id, name, fiscal_year)
);

CREATE TABLE IF NOT EXISTS finance.budget_lines (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES core.tenants (id),
  budget_id        UUID NOT NULL REFERENCES finance.budgets (id),
  fund_id          UUID REFERENCES finance.funds (id),
  category_code    TEXT NOT NULL,
  amount_planned   NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_budget_lines_planned CHECK (amount_planned >= 0),
  amount_actual    NUMERIC(18,4) NOT NULL DEFAULT 0
    CONSTRAINT ck_budget_lines_actual CHECK (amount_actual >= 0),
  notes            TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by       UUID,
  deleted_at       TIMESTAMPTZ,
  CONSTRAINT uq_budget_lines UNIQUE (budget_id, category_code, fund_id)
);

CREATE INDEX IF NOT EXISTS ix_budget_lines_budget
  ON finance.budget_lines (tenant_id, budget_id)
  WHERE deleted_at IS NULL;

-- -----------------------------------------------------------------------------
-- Vendors & recurring expenses
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.vendors (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL REFERENCES core.tenants (id),
  code             TEXT NOT NULL,
  name             TEXT NOT NULL,
  contact_email    CITEXT,
  contact_phone    TEXT,
  payment_terms    TEXT,
  default_currency CHAR(3) REFERENCES core.currencies (code),
  is_active        BOOLEAN NOT NULL DEFAULT TRUE,
  risk_flag        BOOLEAN NOT NULL DEFAULT FALSE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by       UUID,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by       UUID,
  deleted_at       TIMESTAMPTZ,
  row_version      INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_vendors_tenant_code UNIQUE (tenant_id, code)
);

CREATE INDEX IF NOT EXISTS ix_vendors_tenant_active
  ON finance.vendors (tenant_id)
  WHERE deleted_at IS NULL AND is_active;

COMMENT ON COLUMN finance.vendors.contact_email IS 'Operational contact; access-controlled; never log';

CREATE TABLE IF NOT EXISTS finance.recurring_expenses (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  campus_id            UUID REFERENCES core.campuses (id),
  vendor_id            UUID REFERENCES finance.vendors (id),
  fund_id              UUID REFERENCES finance.funds (id),
  code                 TEXT NOT NULL,
  name                 TEXT NOT NULL,
  category_code        TEXT NOT NULL,
  amount               NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_recurring_expenses_amount CHECK (amount > 0),
  currency_code        CHAR(3) NOT NULL REFERENCES core.currencies (code),
  frequency            TEXT NOT NULL DEFAULT 'monthly'
    CONSTRAINT ck_recurring_expenses_freq CHECK (frequency IN (
      'weekly', 'monthly', 'quarterly', 'yearly'
    )),
  next_due_on          DATE NOT NULL,
  is_active            BOOLEAN NOT NULL DEFAULT TRUE,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ,
  row_version          INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_recurring_expenses_code UNIQUE (tenant_id, code)
);

COMMENT ON TABLE finance.recurring_expenses
  IS 'Templates e.g. Friday Worship Hall Rental, Utilities, Security (FR-FIN-002)';

CREATE TABLE IF NOT EXISTS finance.expense_payments (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL REFERENCES core.tenants (id),
  campus_id            UUID REFERENCES core.campuses (id),
  vendor_id            UUID NOT NULL REFERENCES finance.vendors (id),
  fund_id              UUID NOT NULL REFERENCES finance.funds (id),
  recurring_expense_id UUID REFERENCES finance.recurring_expenses (id),
  amount               NUMERIC(18,4) NOT NULL
    CONSTRAINT ck_expense_payments_amount CHECK (amount > 0),
  currency_code        CHAR(3) NOT NULL REFERENCES core.currencies (code),
  fx_rate              NUMERIC(18,8),
  amount_base          NUMERIC(18,4),
  base_currency        CHAR(3) REFERENCES core.currencies (code),
  status               finance.expense_status NOT NULL DEFAULT 'draft',
  requested_by         UUID NOT NULL REFERENCES identity.users (id),
  approved_by          UUID REFERENCES identity.users (id),
  paid_at              TIMESTAMPTZ,
  idempotency_key      TEXT NOT NULL,
  tally_voucher_ref    TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by           UUID,
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by           UUID,
  deleted_at           TIMESTAMPTZ,
  row_version          INT NOT NULL DEFAULT 1,
  CONSTRAINT uq_expense_payments_idempotency UNIQUE (tenant_id, idempotency_key),
  CONSTRAINT ck_expense_sod CHECK (
    approved_by IS NULL OR approved_by <> requested_by
  )
);

CREATE INDEX IF NOT EXISTS ix_expense_payments_status
  ON finance.expense_payments (tenant_id, status, created_at DESC)
  WHERE deleted_at IS NULL;

COMMENT ON CONSTRAINT ck_expense_sod ON finance.expense_payments
  IS 'Segregation of duties: approver must differ from requester (FR-FIN-006)';

-- -----------------------------------------------------------------------------
-- Tally Prime sync
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS finance.tally_sync_events (
  id                 UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id          UUID NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  entity_type        TEXT NOT NULL,
  entity_id          UUID NOT NULL,
  operation          TEXT NOT NULL
    CONSTRAINT ck_tally_operation CHECK (operation IN (
      'ledger_sync', 'receipt_voucher', 'payment_voucher', 'journal', 'bank_recon'
    )),
  status             finance.tally_sync_status NOT NULL DEFAULT 'pending',
  attempt_count      INT NOT NULL DEFAULT 0,
  request_hash       BYTEA,
  response_code      TEXT,
  error_code         TEXT,
  external_ref       TEXT,
  correlation_id     UUID,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE finance.tally_sync_events
  IS 'Idempotent Tally sync queue with dead-letter (FR-FIN-020/021); no secrets in row';

CREATE TABLE IF NOT EXISTS finance.tally_sync_events_y2026m08
  PARTITION OF finance.tally_sync_events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS finance.tally_sync_events_y2026m09
  PARTITION OF finance.tally_sync_events
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS finance.tally_sync_events_y2026m10
  PARTITION OF finance.tally_sync_events
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE INDEX IF NOT EXISTS ix_tally_sync_status
  ON finance.tally_sync_events (tenant_id, status, created_at);

CREATE INDEX IF NOT EXISTS ix_tally_sync_entity
  ON finance.tally_sync_events (tenant_id, entity_type, entity_id, created_at DESC);

-- -----------------------------------------------------------------------------
-- Analytics snapshots (partitioned)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS analytics.analytics_snapshots (
  id               UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id        UUID NOT NULL,
  snapshot_at      TIMESTAMPTZ NOT NULL,
  campus_id        UUID,
  metric_domain    TEXT NOT NULL
    CONSTRAINT ck_analytics_domain CHECK (metric_domain IN (
      'membership', 'visitors', 'care_cells', 'prayer', 'counselling',
      'welfare', 'finance', 'communication', 'events', 'roster'
    )),
  metric_code      TEXT NOT NULL,
  dimensions       JSONB NOT NULL DEFAULT '{}'::jsonb,
  value_num        NUMERIC(18,4),
  value_json       JSONB,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, snapshot_at)
) PARTITION BY RANGE (snapshot_at);

COMMENT ON TABLE analytics.analytics_snapshots
  IS 'Pre-aggregated KPIs; dimensions must not include confidential free text';

CREATE TABLE IF NOT EXISTS analytics.analytics_snapshots_y2026m08
  PARTITION OF analytics.analytics_snapshots
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE TABLE IF NOT EXISTS analytics.analytics_snapshots_y2026m09
  PARTITION OF analytics.analytics_snapshots
  FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE TABLE IF NOT EXISTS analytics.analytics_snapshots_y2026m10
  PARTITION OF analytics.analytics_snapshots
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE INDEX IF NOT EXISTS ix_analytics_snapshots_domain
  ON analytics.analytics_snapshots (tenant_id, metric_domain, metric_code, snapshot_at DESC);

CREATE INDEX IF NOT EXISTS ix_analytics_snapshots_campus
  ON analytics.analytics_snapshots (tenant_id, campus_id, snapshot_at DESC)
  WHERE campus_id IS NOT NULL;

-- -----------------------------------------------------------------------------
-- AI recommendation store
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS analytics.ai_recommendations (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id             UUID NOT NULL REFERENCES core.tenants (id),
  campus_id             UUID REFERENCES core.campuses (id),
  domain                TEXT NOT NULL,
  entity_type           TEXT NOT NULL,
  entity_id             UUID NOT NULL,
  recommendation_type   TEXT NOT NULL,
  title                 TEXT NOT NULL,
  rationale             TEXT NOT NULL,
  confidence            NUMERIC(5,4)
    CONSTRAINT ck_ai_confidence CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
  payload               JSONB NOT NULL DEFAULT '{}'::jsonb,
  status                analytics.recommendation_status NOT NULL DEFAULT 'pending',
  model_version         TEXT NOT NULL,
  feature_flag_key      TEXT,
  decided_by            UUID REFERENCES identity.users (id),
  decided_at            TIMESTAMPTZ,
  expires_at            TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by            UUID,
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by            UUID,
  deleted_at            TIMESTAMPTZ,
  row_version           INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_ai_recommendations_entity
  ON analytics.ai_recommendations (tenant_id, entity_type, entity_id, status)
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS ix_ai_recommendations_pending
  ON analytics.ai_recommendations (tenant_id, domain, created_at DESC)
  WHERE deleted_at IS NULL AND status = 'pending';

COMMENT ON TABLE analytics.ai_recommendations
  IS 'Advisory AI outputs; human accept/edit/reject logged (FR-AI-002); no counselling note text';

COMMENT ON COLUMN analytics.ai_recommendations.payload
  IS 'Structured suggestion only; scrub PII before persist (FR-AI-003)';

-- -----------------------------------------------------------------------------
-- RLS
-- -----------------------------------------------------------------------------

ALTER TABLE finance.funds ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance.funds FORCE ROW LEVEL SECURITY;
ALTER TABLE finance.donations ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance.donations FORCE ROW LEVEL SECURITY;
ALTER TABLE finance.tithes ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance.tithes FORCE ROW LEVEL SECURITY;
ALTER TABLE finance.offerings ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance.offerings FORCE ROW LEVEL SECURITY;
ALTER TABLE finance.expense_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance.expense_payments FORCE ROW LEVEL SECURITY;
ALTER TABLE analytics.ai_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics.ai_recommendations FORCE ROW LEVEL SECURITY;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_funds ON finance.funds
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_donations ON finance.donations
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_tithes ON finance.tithes
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_offerings ON finance.offerings
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_expenses ON finance.expense_payments
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY tenant_isolation_ai ON analytics.ai_recommendations
    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
           AND deleted_at IS NULL)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;
