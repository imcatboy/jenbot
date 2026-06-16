import logging
import uvicorn
import sentry_sdk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.container import AppContainer
from api.core.settings import Settings
from api.core.openapi import API_METADATA
from api.endpoints import *


logger = logging.getLogger(__name__)
container = AppContainer()
settings = Settings()

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
)

container.wire(packages=["api.dependencies", "api.endpoints"])

app = FastAPI(
    **API_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_methods=["*"],
    allow_credentials=True,
)
app.include_router(api_router)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(exceptions.DomainException, domain_exception_handler)
app.add_exception_handler(
    exceptions.ObjectNotFoundException, object_not_found_exception_handler
)
app.add_exception_handler(
    exceptions.ObjectAlreadyExistsException, object_already_exists_exception_handler
)
app.add_exception_handler(
    exceptions.TooManyObjectsFoundException, too_many_objects_found_exception_handler
)
app.add_exception_handler(
    exceptions.DuplicateIdsException, duplicate_ids_exception_handler
)
app.add_exception_handler(
    exceptions.MissingOptionException, missing_option_exception_handler
)
app.add_exception_handler(
    exceptions.InvalidOptionRelationException, invalid_option_relation_exception_handler
)
app.add_exception_handler(
    exceptions.NotEnoughInventoryException, not_enough_inventory_exception_handler
)
app.add_exception_handler(
    exceptions.DealSelfPurchaseException, deal_self_purchase_exception_handler
)
app.add_exception_handler(
    exceptions.InvalidDataException, invalid_data_exception_handler
)
app.add_exception_handler(
    exceptions.DealNotPendingException, deal_not_pending_exception_handler
)
app.add_exception_handler(
    exceptions.ChatParticipantNotFoundException,
    chat_participant_not_found_exception_handler,
)
app.add_exception_handler(
    exceptions.FileNotFoundException, file_not_found_exception_handler
)
app.add_exception_handler(
    exceptions.VersionMismatchException, version_mismatch_exception_handler
)
app.add_exception_handler(
    exceptions.UserNotAllowedToUpdateException,
    user_not_allowed_to_update_exception_handler,
)
app.add_exception_handler(
    exceptions.UserNotAllowedToSetReputationUserException,
    user_not_allowed_to_set_reputation_user_exception_handler,
)

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.PROJECT_HOST,
        port=settings.PROJECT_PORT,
        log_config="log.ini",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
