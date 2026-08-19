from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from app.extensions import db
from app.forms.inventory import InventoryItemForm, MaintenanceLogForm
from app.models.inventory import InventoryItem, MaintenanceLog
from app.utils.decorators import require_permission

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


def _next_asset_code():
    last = InventoryItem.query.order_by(InventoryItem.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f"AST-{n:05d}"


@inventory_bp.route("/")
@login_required
@require_permission("inventory", "view")
def list_items():
    items = InventoryItem.query.order_by(InventoryItem.asset_name).all()
    return render_template("inventory/list.html", items=items)


@inventory_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_permission("inventory", "edit")
def item_create():
    form = InventoryItemForm()
    if form.validate_on_submit():
        item = InventoryItem(
            asset_code=form.asset_code.data or _next_asset_code(),
            asset_name=form.asset_name.data,
            category=form.category.data,
            value=form.value.data,
            purchase_date=form.purchase_date.data,
            assigned_to=form.assigned_to.data,
            status=form.status.data,
            next_maintenance_date=form.next_maintenance_date.data,
        )
        db.session.add(item)
        db.session.commit()
        flash("Asset added.", "success")
        return redirect(url_for("inventory.item_detail", item_id=item.id))
    return render_template("inventory/form.html", form=form, is_new=True)


@inventory_bp.route("/<int:item_id>", methods=["GET", "POST"])
@login_required
@require_permission("inventory", "view")
def item_detail(item_id):
    item = db.get_or_404(InventoryItem, item_id)
    form = MaintenanceLogForm()
    if form.validate_on_submit():
        db.session.add(
            MaintenanceLog(
                item_id=item.id,
                service_date=form.service_date.data,
                remarks=form.remarks.data,
            )
        )
        db.session.commit()
        flash("Maintenance log added.", "success")
        return redirect(url_for("inventory.item_detail", item_id=item.id))
    return render_template("inventory/detail.html", item=item, form=form)


@inventory_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("inventory", "edit")
def item_edit(item_id):
    item = db.get_or_404(InventoryItem, item_id)
    form = InventoryItemForm(obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        flash("Asset updated.", "success")
        return redirect(url_for("inventory.item_detail", item_id=item.id))
    return render_template("inventory/form.html", form=form, is_new=False)
