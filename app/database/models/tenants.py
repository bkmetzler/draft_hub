from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .groups import Group
from .helpers import BaseSQLModel
from .projects import Project


class Tenant(BaseSQLModel, table=True):
    __tablename__ = "tenant"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str

    projects: list[Project] = Relationship(back_populates="tenant")
    groups: list[Group] = Relationship(back_populates="tenant")
