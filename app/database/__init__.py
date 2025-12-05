from __future__ import annotations

from fastapi import Depends
from sqlalchemy import Engine

from app.settings import Settings
from app.settings import get_settings
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine


def get_engine(settings: Settings = Depends(get_settings)) -> Engine:
    return create_engine(settings.database_url, echo=False)


def create_db_and_tables() -> None:
    engine = get_engine(settings=get_settings())
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Complete database tables...")


@contextmanager
def get_session(engine: Engine = Depends(get_engine)) -> Iterator[Session]:
    with Session(engine) as session:
        yield session
