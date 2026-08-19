from app.models.base import utcnow
from app.models.user import Role, User
from tests.conftest import login


def test_login_success(client):
    resp = login(client)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_login_wrong_password(client):
    resp = login(client, password="wrong")
    assert b"Invalid username or password" in resp.data


def test_protected_route_requires_login(client):
    resp = client.get("/admin/users", follow_redirects=True)
    assert b"Sign In" in resp.data or b"log in" in resp.data.lower()


def test_account_lockout(client, app, db):
    with app.app_context():
        max_attempts = app.config["MAX_LOGIN_ATTEMPTS"]
    for _ in range(max_attempts):
        login(client, password="wrong")
    with app.app_context():
        user = User.query.filter_by(username="admin").first()
        assert user.locked_until is not None
        assert user.locked_until > utcnow()
    # Even correct password is refused while locked
    resp = login(client)
    assert b"locked" in resp.data.lower()


def test_logout(client):
    login(client)
    resp = client.get("/auth/logout", follow_redirects=True)
    assert b"logged out" in resp.data.lower()
