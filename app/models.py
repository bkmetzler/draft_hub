from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


def datetime_now() -> datetime:
    return datetime.now(tz=timezone.utc)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime_now, nullable=False)

    def touch(self) -> None:
        self.updated_at = datetime_now()


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    password_hash: str

    password_history: List["UserPasswordHash"] = Relationship(back_populates="user")
    groups: List["GroupMembership"] = Relationship(back_populates="user")
    amendments: List["Amendment"] = Relationship(back_populates="author")
    votes: List["Vote"] = Relationship(back_populates="user")


class UserPasswordHash(SQLModel, table=True):
    __tablename__ = "user_password_hash"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)

    user: User = Relationship(back_populates="password_history")


class Tenant(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tenant"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, sa_column_kwargs={"unique": True})
    description: Optional[str] = None

    projects: List["TenantProject"] = Relationship(back_populates="tenant")
    documents: List["DocumentTenant"] = Relationship(back_populates="tenant")
    groups: List["Group"] = Relationship(back_populates="tenant")


class Project(TimestampMixin, SQLModel, table=True):
    __tablename__ = "project"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="tenant_project_unique"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    name: str
    description: Optional[str] = None
    created_by: int = Field(foreign_key="user.id")

    tenant_link: Optional["TenantProject"] = Relationship(back_populates="project")
    documents: List["Document"] = Relationship(back_populates="project")


class TenantProject(SQLModel, table=True):
    __tablename__ = "tenant_project"
    __table_args__ = (UniqueConstraint("tenant_id", "project_id", name="tenant_project_unique_link"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    project_id: int = Field(foreign_key="project.id")

    tenant: Tenant = Relationship(back_populates="projects")
    project: Project = Relationship(back_populates="tenant_link")


class Document(TimestampMixin, SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    title: str
    summary: Optional[str] = None
    text: str
    created_by: int = Field(foreign_key="user.id")

    project: Project = Relationship(back_populates="documents")
    amendments: List["Amendment"] = Relationship(back_populates="document")
    tenant_links: List["DocumentTenant"] = Relationship(back_populates="document")


class DocumentTenant(SQLModel, table=True):
    __tablename__ = "document_tenant"
    __table_args__ = (UniqueConstraint("tenant_id", "document_id", name="document_tenant_unique"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    document_id: int = Field(foreign_key="document.id")

    tenant: Tenant = Relationship(back_populates="documents")
    document: Document = Relationship(back_populates="tenant_links")


class Amendment(TimestampMixin, SQLModel, table=True):
    __tablename__ = "amendment"

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    title: str
    description: Optional[str] = None
    proposed_text: str
    status: str = Field(default="open")
    created_by: int = Field(foreign_key="user.id")

    document: Document = Relationship(back_populates="amendments")
    author: User = Relationship(back_populates="amendments")
    patches: List["AmendmentPatch"] = Relationship(back_populates="amendment")
    votes: List["Vote"] = Relationship(back_populates="amendment")


class Patch(TimestampMixin, SQLModel, table=True):
    __tablename__ = "patch"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = None
    patch_text: str

    amendments: List["AmendmentPatch"] = Relationship(back_populates="patch")


class AmendmentPatch(SQLModel, table=True):
    __tablename__ = "amendment_patch"
    __table_args__ = (UniqueConstraint("amendment_id", "patch_id", name="amendment_patch_unique"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    amendment_id: int = Field(foreign_key="amendment.id")
    patch_id: int = Field(foreign_key="patch.id")

    amendment: Amendment = Relationship(back_populates="patches")
    patch: Patch = Relationship(back_populates="amendments")


class Vote(SQLModel, table=True):
    __tablename__ = "vote"
    __table_args__ = (UniqueConstraint("amendment_id", "user_id", name="unique_vote_per_user"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    amendment_id: int = Field(foreign_key="amendment.id")
    user_id: int = Field(foreign_key="user.id")
    value: int

    amendment: Amendment = Relationship(back_populates="votes")
    user: User = Relationship(back_populates="votes")


class Group(SQLModel, table=True):
    __tablename__ = "group_entity"
    __table_args__ = (UniqueConstraint("scope_type", "scope_id", "name", name="group_scope_name_unique"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    scope_type: str
    scope_id: int

    memberships: List["GroupMembership"] = Relationship(back_populates="group")
    tenant: Optional[Tenant] = Relationship(back_populates="groups")


class GroupMembership(SQLModel, table=True):
    __tablename__ = "group_membership"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="unique_group_membership"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="group_entity.id")
    user_id: int = Field(foreign_key="user.id")

    group: Group = Relationship(back_populates="memberships")
    user: User = Relationship(back_populates="groups")
