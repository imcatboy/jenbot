from .moderation import moderation_router
from .reputation import reputation_router
from .exceptions import exception_router
from .report import report_router
from .event import event_router
from .admin import admin_router
from .user import user_router


handler_routers = [
    moderation_router,
    reputation_router,
    exception_router,
    report_router,
    event_router,
    admin_router,
    user_router,
]