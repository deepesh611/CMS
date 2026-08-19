from app.models.member import Member
from app.models.system import Backup
from tests.conftest import login


def _seed_member(db):
    db.session.add(Member(first_name="Rep", last_name="Ort", member_number="MBR-REP"))
    db.session.commit()


def test_reports_index(client):
    login(client)
    resp = client.get("/reports/")
    assert resp.status_code == 200
    assert b"Membership" in resp.data


def test_membership_report_view(client, app, db):
    login(client)
    with app.app_context():
        _seed_member(db)
    resp = client.get("/reports/membership")
    assert resp.status_code == 200
    assert b"MBR-REP" in resp.data


def test_report_pdf_export(client):
    login(client)
    resp = client.get("/reports/membership?format=pdf")
    assert resp.status_code == 200
    assert resp.data[:4] == b"%PDF"


def test_report_csv_export(client, app, db):
    login(client)
    with app.app_context():
        _seed_member(db)
    resp = client.get("/reports/membership?format=csv")
    assert resp.status_code == 200
    assert b"Number" in resp.data


def test_manual_backup(client, app):
    login(client)
    resp = client.post("/backup/create", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert Backup.query.count() == 1
        assert Backup.query.first().verified is True


def test_api_health(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_api_members_requires_login(client):
    resp = client.get("/api/v1/members")
    # redirect to login (302) or 401
    assert resp.status_code in (302, 401)
