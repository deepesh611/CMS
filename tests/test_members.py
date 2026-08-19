from app.models.member import Child, Member
from tests.conftest import login


def _create_member(client):
    return client.post(
        "/members/new",
        data={
            "first_name": "John",
            "last_name": "Adeyemi",
            "dob": "1990-05-14",
            "gender": "Male",
            "marital_status": "Married",
            "gsm_number": "+2348012345678",
            "joining_date": "2026-08-01",
            "care_cell_id": "0",
            "membership_status": "Active",
        },
        follow_redirects=True,
    )


def test_create_member(client, app):
    login(client)
    resp = _create_member(client)
    assert resp.status_code == 200
    assert b"MBR-00001" in resp.data
    with app.app_context():
        m = Member.query.first()
        assert m.first_name == "John"
        assert m.member_number == "MBR-00001"


def test_member_age_computed(app):
    with app.app_context():
        from datetime import date

        m = Member(first_name="A", last_name="B", dob=date(2000, 1, 1))
        assert m.age == date.today().year - 2000 - (
            (date.today().month, date.today().day) < (1, 1)
        )


def test_member_search(client, app):
    login(client)
    _create_member(client)
    resp = client.get("/members/?q=Adeyemi", follow_redirects=True)
    assert b"Adeyemi" in resp.data
    resp = client.get("/members/?q=ZZZNoMatch", follow_redirects=True)
    assert b"No members found" in resp.data


def test_add_child(client, app):
    login(client)
    _create_member(client)
    with app.app_context():
        mid = Member.query.first().id
    resp = client.post(
        f"/family/{mid}/children/add",
        data={"first_name": "Grace", "last_name": "Adeyemi", "gender": "Female"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Child.query.count() == 1


def test_members_requires_permission(client, app, db):
    # A Read Only user can view but not create
    with app.app_context():
        from app.models.user import Role, User

        ro_role = Role.query.filter_by(name="Read Only User").first()
        u = User(username="viewer", email="v@example.com", role_id=ro_role.id)
        u.set_password("viewer12345")
        db.session.add(u)
        db.session.commit()
    login(client, username="viewer", password="viewer12345")
    resp = client.get("/members/new")
    assert resp.status_code == 403
