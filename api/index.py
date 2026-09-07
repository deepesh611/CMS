"""Vercel serverless entry point — Church ERP Demo.

This file (+ vercel.json) is the ONLY addition for Vercel deployment.
No existing project files are modified.

What it does
------------
1. Points DATABASE_URL at a writable /tmp SQLite copy  → login & CRUD work
2. Seeds RBAC + 40 sample members on cold start         → demo data ready
3. Disables APScheduler (no persistent threads on serverless)
4. Injects a demo banner into every HTML response
5. Catches unhandled errors with a friendly "not available" page
"""

import os
import re
import sys
from pathlib import Path

# ── 1. Project root on sys.path ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── 2. Environment (set BEFORE any app import) ───────────────────────
os.environ["DATABASE_URL"] = "sqlite:////tmp/cms.db"
os.environ["APP_DATA_DIR"] = "/tmp/cms_data"
os.environ.setdefault("SECRET_KEY", "vercel-demo-secret-replace-in-prod")
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("SMS_PROVIDER", "log")
os.environ.setdefault("STORAGE_BACKEND", "local")

# Writable dirs that the app expects
Path("/tmp/cms_data/uploads").mkdir(parents=True, exist_ok=True)
Path("/tmp/cms_data/backups").mkdir(parents=True, exist_ok=True)

# ── 3. Disable APScheduler (serverless ≠ background threads) ────────
import app.utils.scheduler as _sched_mod          # noqa: E402
_sched_mod.init_scheduler = lambda _app: None      # no-op

# ── 4. Cold-start: create tables & seed demo data ────────────────────
if not Path("/tmp/cms.db").exists():
    from app import create_app as _boot_create     # noqa: E402
    from app.extensions import db as _boot_db      # noqa: E402

    _boot_app = _boot_create()
    with _boot_app.app_context():
        _boot_db.create_all()

    # seed() creates its own app context and is idempotent.
    from seed_data import seed as _seed_fn         # noqa: E402
    _seed_fn()

# ── 5. Create the serving app instance ───────────────────────────────
from app import create_app                         # noqa: E402

app = create_app()

# ── 6. Demo banner (injected into every HTML response) ───────────────
_BANNER = (
    '<div id="demo-banner" style="'
    "position:fixed;top:0;left:0;right:0;z-index:99999;"
    "background:linear-gradient(135deg,#0d6efd,#6610f2);"
    "color:#fff;text-align:center;padding:8px 16px;"
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
    "font-size:13px;font-weight:500;"
    "box-shadow:0 2px 8px rgba(0,0,0,.25);letter-spacing:.3px;"
    '">'
    "🚀 <b>Demo Mode</b> &mdash; Data resets periodically &nbsp;|&nbsp; "
    'Login: <code style="background:rgba(255,255,255,.2);padding:2px 6px;'
    'border-radius:3px">admin</code> / '
    '<code style="background:rgba(255,255,255,.2);padding:2px 6px;'
    'border-radius:3px">admin12345</code>'
    " &nbsp;|&nbsp; Some features may be limited"
    "</div>"
    # Push sidebar & auth pages down so the banner doesn't overlap content.
    "<style>"
    ".sidebar{top:36px !important}"
    ".app-main .topbar{top:36px !important}"
    "body>div.d-flex{padding-top:42px}"          # login page centering div
    "</style>"
)

_BODY_RE = re.compile(r"(<body[^>]*>)", re.IGNORECASE)


@app.after_request
def _inject_banner(response):
    ct = response.content_type or ""
    if "text/html" in ct and response.status_code < 400:
        html = response.get_data(as_text=True)
        if "<body" in html.lower() and "demo-banner" not in html:
            html = _BODY_RE.sub(r"\1" + _BANNER, html, count=1)
            response.set_data(html)
            response.headers.pop("Content-Length", None)   # let WSGI recalc
    return response


# ── 7. Friendly error page for demo limitations ─────────────────────
_ERR_PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Demo Limitation — Church ERP</title>
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
</head>
<body class="bg-light">
""" + _BANNER + """
<div class="container py-5" style="padding-top:80px !important">
 <div class="row justify-content-center">
  <div class="col-md-6">
   <div class="card shadow-sm border-0">
    <div class="card-body text-center p-5">
     <div style="font-size:48px;margin-bottom:16px">🔒</div>
     <h4 class="mb-3">Not Available in Demo</h4>
     <p class="text-muted mb-4">
       This feature requires a live backend service (email, SMS, file
       storage …) that isn't configured in the demo deployment.<br>
       Deploy your own instance to unlock everything!
     </p>
     <a href="/" class="btn btn-primary px-4">
       <i class="bi bi-arrow-left"></i> Back to Dashboard
     </a>
    </div>
   </div>
  </div>
 </div>
</div>
</body></html>"""

from flask import render_template_string as _rts   # noqa: E402


@app.errorhandler(Exception)
def _handle_demo_error(exc):
    from werkzeug.exceptions import HTTPException
    if isinstance(exc, HTTPException):
        return exc                                 # 404 / 403 handled normally
    app.logger.warning("Demo error — %s: %s", type(exc).__name__, exc)
    return _rts(_ERR_PAGE), 500
