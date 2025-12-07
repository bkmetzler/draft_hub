from __future__ import annotations

import enum
import uuid

from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from .documents import Document
from .group_memberships import GroupMembership
from .helpers import BaseSQLModel
from .projects import Project
from .tenants import Tenant


class Permissions(enum.IntFlag):
    READ = 1
    WRITE = 2
    CREATE = 4
    APPROVE = 8
    DENY = 16
    COMMIT = 32


class Group(BaseSQLModel, table=True):
    __tablename__ = "groups"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    permissions: int = Field(default=int(Permissions.READ | Permissions.WRITE))
    tenant_id: uuid.UUID | None = Field(default=None, foreign_key="tenant.id")
    project_id: uuid.UUID | None = Field(default=None, foreign_key="project.id")
    document_id: uuid.UUID | None = Field(default=None, foreign_key="document.id")

    tenant: Tenant | None = Relationship(back_populates="groups")
    project: Project | None = Relationship(back_populates="groups")
    document: Document | None = Relationship(back_populates="groups")
    memberships: list[GroupMembership] = Relationship(back_populates="group")


class GroupRead(SQLModel):
    id: uuid.UUID
    name: str
    permissions: int
