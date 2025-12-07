from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.middleware.configure import add_middlewares
from app.routers import amendments, auth, documents, general, projects, tenants, users


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Draft Hub", version="0.1.0", lifespan=lifespan)
    add_middlewares(app)

    app.include_router(general.router)
    app.include_router(auth.router)
    app.include_router(tenants.router)
    app.include_router(projects.router)
    app.include_router(documents.router)
    app.include_router(amendments.router)
    app.include_router(users.router)
    return app


app = create_app()
