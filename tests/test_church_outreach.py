from app.models.church import CareCell, Ministry
from app.models.outreach import OutreachProgram, Visitor
from tests.conftest import login


def test_create_ministry(client, app):
    login(client)
    resp = client.post(
        "/church/ministries/new",
        data={"name": "Choir", "description": "Music ministry"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Ministry.query.filter_by(name="Choir").count() == 1


def test_create_care_cell(client, app):
    login(client)
    resp = client.post(
        "/church/care-cells/new",
        data={
            "name": "North Cell",
            "leader_id": "0",
            "assistant_leader_id": "0",
            "location": "123 St",
            "meeting_schedule": "Wed 6pm",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert CareCell.query.filter_by(name="North Cell").count() == 1


def test_create_outreach_program(client, app):
    login(client)
    resp = client.post(
        "/outreach/programs/new",
        data={"name": "City Crusade", "location": "Downtown"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert OutreachProgram.query.count() == 1


def test_create_visitor_and_followup(client, app):
    login(client)
    client.post(
        "/outreach/visitors/new",
        data={
            "first_name": "Mary",
            "last_name": "Guest",
            "phone": "12345",
            "followup_status": "Pending",
        },
        follow_redirects=True,
    )
    with app.app_context():
        v = Visitor.query.first()
        assert v is not None
        vid = v.id
    resp = client.post(
        f"/outreach/visitors/{vid}",
        data={"assigned_worker": "Pastor A", "outcome": "Called"},
        follow_redirects=True,
    )
    assert b"Pastor A" in resp.data
