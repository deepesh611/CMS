from flask import Blueprint, render_template
from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    from app.utils.metrics import dashboard_kpis

    return render_template("dashboard/index.html", kpis=dashboard_kpis())
