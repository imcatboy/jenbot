import logging
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.container import AppContainer
from core.settings import Settings
from core.openapi import API_METADATA


logger = logging.getLogger(__name__)
container = AppContainer()
settings = Settings()


app = FastAPI(
    **API_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    dependencies=[container.wire(packages=["api.dependencies", "api.endpoints"])],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_methods=["*"],
    allow_credentials=True,
)


if __name__ == "__main__":
    uvicorn.run(
        app="api.main:app",
        host=settings.PROJECT_HOST,
        port=settings.PROJECT_PORT,
        log_config="log.ini",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
