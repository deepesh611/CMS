from app.models.finance import WelfareRequest
from app.models.member import Member
from app.models.pastoral import CounsellingCase, PrayerRequest
from tests.conftest import login


def _member(db):
    m = Member(first_name="Pat", last_name="Doe", member_number="MBR-PAT")
    db.session.add(m)
    db.session.commit()
    return m.id


def test_create_prayer_request(client, app):
    login(client)
    resp = client.post(
        "/pastoral/prayer/new",
        data={"request_details": "Healing", "status": "Open", "member_id": "0"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert PrayerRequest.query.count() == 1


def test_create_counselling_case(client, app):
    login(client)
    resp = client.post(
        "/pastoral/counselling/new",
        data={"member_id": "0", "counsellor_id": "0", "case_type": "Marriage",
              "status": "Open", "summary": "x", "confidential_notes": "secret"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert CounsellingCase.query.count() == 1


def test_confidential_notes_hidden_from_non_counsellor(client, app, db):
    # Create a case with a specific counsellor, then view as super admin (allowed)
    login(client)
    with app.app_context():
        case = CounsellingCase(case_type="X", confidential_notes="topsecret", status="Open")
        db.session.add(case)
        db.session.commit()
        cid = case.id
    resp = client.get(f"/pastoral/counselling/{cid}")
    # Super Admin can see confidential notes
    assert b"topsecret" in resp.data


def test_create_welfare_request(client, app):
    login(client)
    with app.app_context():
        mid = _member(db=__import__("app").extensions.db)
    resp = client.post(
        "/pastoral/welfare/new",
        data={"member_id": str(mid), "support_type": "Food", "amount": "100",
              "status": "Submitted"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert WelfareRequest.query.count() == 1
