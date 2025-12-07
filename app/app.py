from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from fastapi import FastAPI

from .database import create_db_and_tables
from .middleware.configure import configure_middleware
from .routers import amendments, auth, general, tenants, users
from .settings import Settings, get_settings


@dataclass
class AppState:
    settings: Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setattr(app, "state", AppState(settings=settings))
    create_db_and_tables()
    yield


ROUTES = [
    general.router,
    users.router,
    auth.router,
    amendments.router,
    tenants.router,
]


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    configure_middleware(app)

    for route in ROUTES:
        app.include_router(route)

    return app
