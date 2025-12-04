from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Generator, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import get_settings, Settings
from .database import create_db_and_tables
from .routers import amendments, auth, tenants, users


@dataclass
class AppState:
    settings: Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setattr(app, "state", AppState(settings=settings))
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(tenants.router)
    app.include_router(amendments.router)

    return app
