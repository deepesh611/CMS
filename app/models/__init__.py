"""Import all models so SQLAlchemy/Alembic can discover every table."""
from app.models.base import TimestampMixin  # noqa: F401
from app.models.user import (  # noqa: F401
    User,
    Role,
    Permission,
    RolePermission,
)
from app.models.member import (  # noqa: F401
    Member,
    Spouse,
    Child,
    MemberPhoto,
    MemberDocument,
)
from app.models.training import TrainingCourse, MemberTraining  # noqa: F401
from app.models.church import (  # noqa: F401
    CareCell,
    CareCellMember,
    Ministry,
    MinistryMember,
    LeadershipRole,
    MemberLeadership,
    MinistryMovement,
)
from app.models.events import (  # noqa: F401
    Event,
    Pastor,
    Sermon,
    EventAssignment,
    Attendance,
)
from app.models.outreach import (  # noqa: F401
    Visitor,
    VisitorFollowup,
    OutreachProgram,
    OutreachVisitor,
)
from app.models.pastoral import (  # noqa: F401
    PrayerRequest,
    CounsellingCase,
    CounsellingFollowup,
    BabyDedication,
)
from app.models.friday_school import (  # noqa: F401
    FridaySchoolClass,
    FridaySchoolStudent,
    FridaySchoolAttendance,
    FridaySchoolActivity,
    FridaySchoolPerformance,
)
from app.models.finance import (  # noqa: F401
    Tithe,
    Offering,
    Donation,
    Mission,
    MissionSupport,
    WelfareRequest,
)
from app.models.inventory import InventoryItem, MaintenanceLog  # noqa: F401
from app.models.communication import (  # noqa: F401
    Communication,
    EmailLog,
    SMSLog,
    WhatsAppLog,
    GoogleForm,
    FormResponse,
)
from app.models.system import (  # noqa: F401
    Backup,
    AuditLog,
    CustomField,
    CustomFieldValue,
)
from app.models.discipleship import (  # noqa: F401
    DiscipleshipProgress,
    EligibilityOverride,
)
from app.models.previous_church import PreviousChurchExperience  # noqa: F401
from app.models.ordination import Ordination  # noqa: F401
from app.models.member_exit import MemberExit  # noqa: F401
from app.models.facility import (  # noqa: F401
    Building,
    Room,
    ExternalChurch,
    RoomBooking,
)
