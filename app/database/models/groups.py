import enum
import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Permissions(enum.IntFlag):
    READ = 1
    WRITE = 2
    CREATE = 4
    APPROVE = 8
    DENY = 16
    COMMIT = 32


class Group(SQLModel, table=True):
    __tablename__ = "groups"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    permissions: int = Field(default=int(Permissions.READ | Permissions.WRITE))
    tenant_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tenant.id")
    project_id: Optional[uuid.UUID] = Field(default=None, foreign_key="project.id")
    document_id: Optional[uuid.UUID] = Field(default=None, foreign_key="document.id")

    tenant: Optional["Tenant"] = Relationship(back_populates="groups")
    project: Optional["Project"] = Relationship(back_populates="groups")
    document: Optional["Document"] = Relationship(back_populates="groups")
    memberships: List["GroupMembership"] = Relationship(back_populates="group")


class GroupRead(SQLModel):
    id: uuid.UUID
    name: str
    permissions: int
