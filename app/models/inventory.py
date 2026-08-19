"""Church assets and maintenance logs."""
from app.extensions import db
from app.models.base import TimestampMixin


class InventoryItem(TimestampMixin, db.Model):
    __tablename__ = "inventory_items"

    id = db.Column("ItemID", db.Integer, primary_key=True)
    asset_code = db.Column("AssetCode", db.String(80), unique=True, index=True)
    asset_name = db.Column("AssetName", db.String(150), nullable=False)
    category = db.Column("Category", db.String(80))
    value = db.Column("Value", db.Numeric(12, 2))
    purchase_date = db.Column("PurchaseDate", db.Date)
    assigned_to = db.Column("AssignedTo", db.String(120))
    status = db.Column("Status", db.String(40), default="Active")
    next_maintenance_date = db.Column("NextMaintenanceDate", db.Date)

    maintenance_logs = db.relationship(
        "MaintenanceLog", back_populates="item", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<InventoryItem {self.asset_code} {self.asset_name}>"


class MaintenanceLog(TimestampMixin, db.Model):
    __tablename__ = "maintenance_logs"

    id = db.Column("MaintenanceID", db.Integer, primary_key=True)
    item_id = db.Column(
        "ItemID", db.Integer, db.ForeignKey("inventory_items.ItemID"), nullable=False
    )
    service_date = db.Column("ServiceDate", db.Date)
    remarks = db.Column("Remarks", db.Text)

    item = db.relationship("InventoryItem", back_populates="maintenance_logs")
