# Church ERP & Ministry Management System

An enterprise-grade, modular church management system built with Flask,
SQLAlchemy, and Bootstrap 5. Runs on SQLite out of the box and migrates to
PostgreSQL / MySQL / SQL Server with a single configuration change. Docker-ready.

---

## Features

- **RBAC** — 16 configurable roles, per-module/action permissions, editable by IT Admin
- **Security** — bcrypt password hashing, TOTP 2FA, account lockout, session timeout, CSRF, CSP, full audit logging
- **Membership & Family** — full profiles, photos, documents, spouse & unlimited children, training records
- **Ministries, Care Cells, Leadership**
- **Events, Sermons, Programme Scheduling, Attendance** (bulk entry + reports)
- **Outreach & Visitor follow-up**
- **Friday School** — classes, students, attendance, activities, performance (teacher-scoped access)
- **Counselling** (confidential notes), **Prayer Requests**, **Baby Dedications**, **Welfare** workflow
- **Finance** — tithes, offerings, donations, missions + dashboard with charts
- **Inventory** — assets + maintenance logs
- **Communication** — Email (SMTP), SMS & WhatsApp (Twilio), social placeholders, flyers, automated birthday greetings
- **Google Forms** import
- **Reports** — membership, attendance, finance, welfare, inventory, visitors, birthdays; export to PDF / Excel / CSV / JSON
- **Backup & Recovery** — automatic daily/weekly/monthly + manual backup/restore/verify
- **REST API** (`/api/v1`)
- **Pluggable file storage** — local disk (default) or MinIO / S3-compatible (free, self-hosted)

---

## Installation (Windows / macOS / Linux)

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Set up

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # then edit .env as needed
```

### 3. Initialize the database

```bash
flask db upgrade
python seed_data.py           # optional: loads sample data + admin user
```

### 4. Run

```bash
python run.py
```

Open http://localhost:5000 and log in with **admin / admin12345**
(if you ran `seed_data.py`; otherwise create an admin with `flask create-admin`).

---

## Configuration

All configuration is via environment variables in `.env` (see `.env.example`).
Key settings:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | DB connection. Leave unset for SQLite; set to `postgresql://…` to switch |
| `STORAGE_BACKEND` | `local` (default) or `minio` |
| `SMS_PROVIDER` | `twilio` for real sends, `log` to disable |
| `TWILIO_*` | Twilio SID/token/numbers for SMS & WhatsApp |
| `MAIL_*` | SMTP settings for email |
| `SESSION_TIMEOUT_MINUTES`, `MAX_LOGIN_ATTEMPTS` | Security tuning |

---

## Migrating to PostgreSQL / MySQL / SQL Server

1. Provision the target database.
2. Copy the data:
   ```bash
   python scripts/migrate_db.py "postgresql://user:pass@host:5432/cms"
   ```
3. Set `DATABASE_URL` in `.env` to the new connection string.
4. Restart the app.

No code changes required — the ORM is database-agnostic.

---

## Docker

```bash
docker compose up --build
```

`docker-compose.yml` includes optional **PostgreSQL** and **MinIO** services.
Data (uploads, backups, SQLite file) is stored on mounted volumes under `./data`.
Point `DATABASE_URL` at the `db` service and `STORAGE_BACKEND=minio` to use them.

---

## CLI commands

| Command | Description |
|---|---|
| `flask db upgrade` | Apply database migrations |
| `flask init-rbac` | Seed roles, permissions, and grants |
| `flask create-admin` | Create a Super Administrator |
| `python seed_data.py` | Load full sample dataset |
| `python scripts/migrate_db.py <url>` | Migrate data to another database |

---

## Testing

```bash
pytest -q
```

---

## User Manual (quick reference)

- **Dashboard** — KPIs: total members, new members, monthly giving, open welfare.
- **Members** — search, create, edit; profile tabs for Personal / Family / Church / Training / Documents. Add spouse and children from the Family tab.
- **Attendance** — open an event → tick present members → save. View rates under *Attendance → Report*.
- **Friday School** — teachers see only their own classes; coordinators/admins see all.
- **Counselling** — confidential notes are visible only to the assigned counsellor and the Senior Pastor.
- **Communication** — compose a draft, then send. Email/SMS/WhatsApp deliver immediately and log every recipient; social channels are prepared for manual posting.
- **Reports** — open any report, then export to PDF/Excel/CSV/JSON (requires the `reports.export` permission).
- **Backup** — automatic backups run in the background; use *Backup Now* for a manual one, and *Restore* to recover.
- **Administration** — manage users, edit the role-permission matrix, and review the audit log.

---

## Project structure

```
app/
  models/      SQLAlchemy models (mirrors the ER diagram)
  routes/      One Blueprint per domain
  forms/       WTForms
  templates/   Jinja2 + Bootstrap 5
  utils/       storage, audit, decorators, backup, reports, scheduler, ...
migrations/    Alembic migrations
scripts/       DB migration helper
tests/         pytest suite
seed_data.py   Sample data loader
run.py         Dev entry point
```

## Technology

Flask · SQLAlchemy · Flask-Migrate · Flask-Login · Flask-WTF · Bcrypt · pyotp ·
Pillow · pandas · OpenPyXL · ReportLab · Twilio · APScheduler · boto3 · Bootstrap 5 · Chart.js
