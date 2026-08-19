import pytest

from app import create_app
from app.extensions import db as _db
from app.utils.rbac_seed import create_superadmin, seed_rbac


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        seed_rbac()
        create_superadmin("admin", "admin@example.com", "admin12345")
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


def login(client, username="admin", password="admin12345"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
