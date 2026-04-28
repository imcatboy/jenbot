import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.container import AppContainer
from api.core.settings import Settings
from api.core.openapi import API_METADATA
from api.endpoints import api_router


logger = logging.getLogger(__name__)
container = AppContainer()
settings = Settings()

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


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.PROJECT_HOST,
        port=settings.PROJECT_PORT,
        log_config="log.ini",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
