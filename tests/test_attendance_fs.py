from datetime import date

from app.models.events import Attendance, Event
from app.models.friday_school import FridaySchoolClass
from app.models.member import Member
from tests.conftest import login


def _make_member(db, name="Test"):
    m = Member(first_name=name, last_name="User", member_number=f"MBR-{name}")
    db.session.add(m)
    db.session.commit()
    return m.id


def test_create_event_and_take_attendance(client, app, db):
    login(client)
    with app.app_context():
        mid = _make_member(db, "Ann")
    client.post(
        "/events/new",
        data={"name": "Sunday Service", "event_type": "Sunday Service",
              "event_date": "2026-08-16"},
        follow_redirects=True,
    )
    with app.app_context():
        eid = Event.query.first().id
    resp = client.post(
        f"/attendance/event/{eid}",
        data={"present": [str(mid)]},
        follow_redirects=True,
    )
    assert b"present" in resp.data.lower()
    with app.app_context():
        att = Attendance.query.filter_by(event_id=eid, member_id=mid).first()
        assert att.status == "Present"


def test_create_friday_school_class(client, app):
    login(client)
    resp = client.post(
        "/friday-school/classes/new",
        data={"name": "Little Lambs", "age_group": "3-5", "teacher_id": "0",
              "assistant_teacher_id": "0"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert FridaySchoolClass.query.filter_by(name="Little Lambs").count() == 1


def test_attendance_report_loads(client):
    login(client)
    resp = client.get("/attendance/report")
    assert resp.status_code == 200
