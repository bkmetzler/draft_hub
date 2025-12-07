from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .documents import Document
from .groups import Group
from .helpers import BaseSQLModel
from .tenants import Tenant


class Project(BaseSQLModel, table=True):
    __tablename__ = "project"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id")

    tenant: Tenant | None = Relationship(back_populates="projects")
    documents: list[Document] = Relationship(back_populates="project")
    groups: list[Group] = Relationship(back_populates="project")
