"""Populate the database with realistic sample data for every module.

Usage:
    python seed_data.py

Safe to run on an empty database. Seeds RBAC first, then a super admin
(admin / admin12345), then sample records across all modules.
"""
import random
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.utils.rbac_seed import create_superadmin, seed_rbac

FIRST_NAMES = ["John", "Mary", "David", "Grace", "Samuel", "Ruth", "Peter", "Esther",
               "Daniel", "Sarah", "Joseph", "Rebecca", "Paul", "Hannah", "James"]
LAST_NAMES = ["Adeyemi", "Okafor", "Mensah", "Banda", "Kamau", "Dlamini", "Osei",
              "Nkosi", "Achebe", "Mwangi"]


def _rand_dob(min_age=8, max_age=70):
    age = random.randint(min_age, max_age)
    return date.today() - timedelta(days=age * 365 + random.randint(0, 364))


def seed():
    app = create_app()
    with app.app_context():
        from app.models.church import CareCell, Ministry, MinistryMember
        from app.models.events import Event, Pastor
        from app.models.finance import Donation, Mission, Offering, Tithe
        from app.models.friday_school import FridaySchoolClass
        from app.models.inventory import InventoryItem
        from app.models.member import Child, Member, Spouse
        from app.models.outreach import OutreachProgram, Visitor
        from app.models.pastoral import PrayerRequest
        from app.models.training import TrainingCourse

        seed_rbac()
        create_superadmin("admin", "admin@example.com", "admin12345")

        if Member.query.count() > 0:
            print("Data already present — skipping sample seed.")
            return

        # Training courses
        courses = [
            TrainingCourse(name="Foundations of Faith", level="Basic",
                           is_mandatory_for_leadership=True),
            TrainingCourse(name="Leadership 101", level="Intermediate",
                           is_mandatory_for_leadership=True),
            TrainingCourse(name="Bible School", level="Advanced"),
        ]
        db.session.add_all(courses)

        # Ministries
        ministries = [Ministry(name=n) for n in
                      ["Choir", "Youth Ministry", "Men Fellowship", "Women Fellowship",
                       "Children's Ministry", "Media Team", "Prayer Team",
                       "Evangelism Team", "Hospitality Team"]]
        db.session.add_all(ministries)

        # Care cells
        cells = [CareCell(name=f"{area} Cell", location=area)
                 for area in ["North", "South", "East", "West", "Central"]]
        db.session.add_all(cells)
        db.session.flush()

        # Members
        members = []
        for i in range(40):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            married = random.random() < 0.5
            m = Member(
                member_number=f"MBR-{i + 1:05d}",
                first_name=fn, last_name=ln,
                gender=random.choice(["Male", "Female"]),
                dob=_rand_dob(18, 70),
                marital_status="Married" if married else "Single",
                email=f"{fn.lower()}.{ln.lower()}{i}@example.com",
                gsm_number=f"+23480{random.randint(10000000, 99999999)}",
                membership_status="Active",
                joining_date=date.today() - timedelta(days=random.randint(0, 2000)),
                care_cell_id=random.choice(cells).id,
                professional_category=random.choice(
                    ["Doctor", "Engineer", "Teacher", "Business Owner", "Student", "Other"]
                ),
            )
            members.append(m)
            db.session.add(m)
        db.session.flush()

        # Spouses + children for married members
        for m in members:
            if m.marital_status == "Married":
                db.session.add(Spouse(member_id=m.id, first_name=random.choice(FIRST_NAMES),
                                      last_name=m.last_name))
                for _ in range(random.randint(0, 3)):
                    db.session.add(Child(member_id=m.id,
                                         first_name=random.choice(FIRST_NAMES),
                                         last_name=m.last_name, dob=_rand_dob(1, 15),
                                         gender=random.choice(["Male", "Female"])))

        # Ministry membership
        for m in random.sample(members, 20):
            db.session.add(MinistryMember(ministry_id=random.choice(ministries).id,
                                          member_id=m.id, ministry_role="Member"))

        # Pastors
        for m in random.sample(members, 3):
            db.session.add(Pastor(member_id=m.id, position="Pastor"))

        # Events
        for i in range(8):
            db.session.add(Event(
                name=f"Sunday Service {i + 1}", event_type="Sunday Service",
                event_date=date.today() - timedelta(days=i * 7),
                location="Main Auditorium"))

        # Friday school
        for grp in ["Toddlers (3-5)", "Juniors (6-9)", "Seniors (10-13)"]:
            db.session.add(FridaySchoolClass(name=grp, age_group=grp))

        # Visitors + outreach
        for i in range(10):
            db.session.add(Visitor(first_name=random.choice(FIRST_NAMES),
                                   last_name=random.choice(LAST_NAMES),
                                   phone=f"+23470{random.randint(10000000, 99999999)}",
                                   visit_date=date.today() - timedelta(days=random.randint(0, 60)),
                                   followup_status=random.choice(
                                       ["Pending", "Contacted", "Converted"])))
        db.session.add(OutreachProgram(name="City Crusade", location="City Square",
                                       outreach_date=date.today() - timedelta(days=30)))

        # Finance
        for m in random.sample(members, 30):
            for _ in range(random.randint(1, 4)):
                db.session.add(Tithe(member_id=m.id,
                                     amount=random.randint(50, 500),
                                     payment_date=date.today() - timedelta(days=random.randint(0, 90)),
                                     payment_method="Cash"))
        for i in range(8):
            db.session.add(Offering(amount=random.randint(500, 3000),
                                    service_date=date.today() - timedelta(days=i * 7)))
        for m in random.sample(members, 8):
            db.session.add(Donation(member_id=m.id, amount=random.randint(100, 1000),
                                    purpose="Building Fund",
                                    donation_date=date.today()))
        db.session.add_all([Mission(name="Local Outreach", country="Nigeria",
                                    mission_type="Local"),
                            Mission(name="Overseas Mission", country="Kenya",
                                    mission_type="Overseas")])

        # Prayer requests
        for m in random.sample(members, 6):
            db.session.add(PrayerRequest(member_id=m.id,
                                         request_details="Prayer for healing and provision.",
                                         category="Health", status="Open"))

        # Inventory
        assets = [("Grand Piano", "Instrument"), ("Sound Mixer", "Audio Equipment"),
                  ("Projector", "Projector"), ("Church Bus", "Vehicle"),
                  ("Laptop", "Computer")]
        for i, (name, cat) in enumerate(assets):
            db.session.add(InventoryItem(asset_code=f"AST-{i + 1:05d}", asset_name=name,
                                         category=cat, value=random.randint(500, 20000),
                                         status="Active"))

        db.session.commit()
        print("Sample data seeded successfully.")
        print("Login: admin / admin12345")


if __name__ == "__main__":
    seed()
