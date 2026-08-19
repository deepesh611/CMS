from app.models.finance import Donation, Offering, Tithe
from app.models.inventory import InventoryItem
from tests.conftest import login


def test_finance_dashboard_loads(client):
    login(client)
    resp = client.get("/finance/")
    assert resp.status_code == 200
    assert b"Finance Dashboard" in resp.data


def test_record_tithe(client, app):
    login(client)
    resp = client.post(
        "/finance/tithes/new",
        data={"member_id": "0", "amount": "150.00", "payment_method": "Cash"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Tithe.query.count() == 1
        assert float(Tithe.query.first().amount) == 150.0


def test_record_offering_and_donation(client, app):
    login(client)
    client.post("/finance/offerings/new", data={"amount": "500"}, follow_redirects=True)
    client.post(
        "/finance/donations/new",
        data={"member_id": "0", "donor_name": "Anon", "amount": "75"},
        follow_redirects=True,
    )
    with app.app_context():
        assert Offering.query.count() == 1
        assert Donation.query.count() == 1


def test_create_inventory_item_autocode(client, app):
    login(client)
    resp = client.post(
        "/inventory/new",
        data={"asset_name": "Keyboard", "category": "Instrument", "status": "Active"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        item = InventoryItem.query.first()
        assert item.asset_code.startswith("AST-")
