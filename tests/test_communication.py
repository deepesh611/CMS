from app.models.communication import Communication, EmailLog
from app.models.member import Member
from tests.conftest import login


def test_compose_draft(client, app):
    login(client)
    resp = client.post(
        "/communication/new",
        data={
            "channel": "Email",
            "category": "Announcement",
            "subject": "Service Update",
            "body": "Service moved to 10am.",
            "recipient_group": "email",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        assert Communication.query.count() == 1


def test_send_email_in_log_mode(client, app, db):
    # testing config sets SMS_PROVIDER=log; email send will attempt SMTP and
    # fail gracefully, still logging the attempt.
    login(client)
    with app.app_context():
        m = Member(first_name="Eve", last_name="Ng", member_number="MBR-EVE",
                   email="eve@example.com")
        db.session.add(m)
        db.session.commit()
    client.post(
        "/communication/new",
        data={"channel": "Email", "category": "Announcement", "subject": "Hi",
              "body": "Test", "recipient_group": "email"},
        follow_redirects=True,
    )
    with app.app_context():
        comm = Communication.query.first()
        cid = comm.id
    resp = client.post(
        f"/communication/{cid}/send/email", follow_redirects=True
    )
    assert resp.status_code == 200
    with app.app_context():
        # One email log row created for eve@example.com (Sent or Failed)
        assert EmailLog.query.count() == 1


def test_social_channel_marks_ready(client, app, db):
    login(client)
    client.post(
        "/communication/new",
        data={"channel": "Facebook", "category": "Announcement", "subject": "FB",
              "body": "Post", "recipient_group": "all"},
        follow_redirects=True,
    )
    with app.app_context():
        cid = Communication.query.first().id
    client.post(f"/communication/{cid}/send/all", follow_redirects=True)
    with app.app_context():
        assert db.session.get(Communication, cid).status == "Ready to Publish"


def test_sms_send_log_mode(client, app, db):
    login(client)
    with app.app_context():
        m = Member(first_name="Sam", last_name="Ng", member_number="MBR-SAM",
                   gsm_number="+2348011112222")
        db.session.add(m)
        db.session.commit()
    client.post(
        "/communication/new",
        data={"channel": "SMS", "category": "Announcement", "body": "SMS test",
              "recipient_group": "phone"},
        follow_redirects=True,
    )
    with app.app_context():
        from app.models.communication import SMSLog
        cid = Communication.query.first().id
    resp = client.post(f"/communication/{cid}/send/phone", follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        from app.models.communication import SMSLog
        log = SMSLog.query.first()
        assert log is not None and log.status == "Sent"  # log-mode always "sent"
