from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


def datetime_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Permissions(Enum):
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 4

    def has_read(self) -> bool:
        if self.READ == self:
            return True
        return False

    def has_write(self) -> bool:
        if self.WRITE == self:
            return True
        return False

    def has_execute(self) -> bool:
        if self.EXECUTE == self:
            return True
        return False


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime_now, nullable=False)

    def touch(self) -> None:
        self.updated_at = datetime_now()


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[str] = Field(primary_key=True, default_factory=generate_uuid)
    email: str = Field(index=True, unique=True)
    password_hash: str

    password_history: List["UserPasswordHash"] = Relationship(back_populates="user")
    groups: List["GroupMembership"] = Relationship(back_populates="user")
    amendments: List["Amendment"] = Relationship(back_populates="author")
    votes: List["Vote"] = Relationship(back_populates="user")

    def has_group(
        self,
        name: str,
        *,
        scope_type: str | None = None,
        scope_id: int | None = None,
    ) -> bool:
        """Return True when the user belongs to a matching group.

        The optional ``scope_type`` and ``scope_id`` filters allow checking for a
        group within a particular scope (for example, a tenant or project). When
        omitted, only the group name is considered.
        """

        for membership in self.groups:
            group = membership.group
            if group is None:
                continue
            if group.name != name:
                continue
            if scope_type is not None and group.scope_type != scope_type:
                continue
            if scope_id is not None and group.scope_id != scope_id:
                continue
            return True

        return False

    def has_groups(self, in_list: list[str]) -> bool:
        """Return True when the user belongs to any named group in ``in_list``."""

        if not in_list:
            return False

        names = set(in_list)

        for membership in self.groups:
            group = membership.group
            if group is None:
                continue
            if group.name in names:
                return True

        return False

    def is_root(self) -> bool:
        """Indicate whether the user is a member of the root scope.

        Root-scope users are intended to have access across all tenants,
        projects, and documents regardless of their specific group membership
        elsewhere.
        """

        return self.has_group("Admin", scope_type="root")


class UserPasswordHash(SQLModel, table=True):
    __tablename__ = "user_password_hash"

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    user_id: str = Field(foreign_key="user.id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime_now, nullable=False)

    user: User = Relationship(back_populates="password_history")


class Tenant(TimestampMixin, SQLModel, table=True):
    __tablename__ = "tenant"

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    name: str = Field(index=True)
    description: Optional[str] = None

    projects: List["TenantProject"] = Relationship(back_populates="tenant")
    groups: List["Group"] = Relationship(back_populates="tenant")


class Project(TimestampMixin, SQLModel, table=True):
    __tablename__ = "project"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="tenant_project_unique"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    tenant_id: str = Field(foreign_key="tenant.id")
    name: str
    description: Optional[str] = None
    created_by: int = Field(foreign_key="user.id")

    tenant_link: Optional["TenantProject"] = Relationship(back_populates="project")
    documents: List["Document"] = Relationship(back_populates="project")


class TenantProject(SQLModel, table=True):
    __tablename__ = "tenant_project"
    __table_args__ = (UniqueConstraint("tenant_id", "project_id", name="tenant_project_unique_link"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    tenant_id: str = Field(foreign_key="tenant.id")
    project_id: str = Field(foreign_key="project.id")

    tenant: Tenant = Relationship(back_populates="projects")
    project: Project = Relationship(back_populates="tenant_link")


class Document(TimestampMixin, SQLModel, table=True):
    __tablename__ = "document"

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    project_id: str = Field(foreign_key="project.id")
    title: str
    summary: Optional[str] = None
    text: str
    created_by: str = Field(foreign_key="user.id")

    project: Project = Relationship(back_populates="documents")
    amendments: List["Amendment"] = Relationship(back_populates="document")


class Amendment(TimestampMixin, SQLModel, table=True):
    __tablename__ = "amendment"

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    document_id: str = Field(foreign_key="document.id")
    title: str
    description: Optional[str] = None
    proposed_text: str
    status: str = Field(default="open")
    created_by: str = Field(foreign_key="user.id")

    document: Document = Relationship(back_populates="amendments")
    author: User = Relationship(back_populates="amendments")
    patches: List["AmendmentPatch"] = Relationship(back_populates="amendment")
    votes: List["Vote"] = Relationship(back_populates="amendment")


class Patch(TimestampMixin, SQLModel, table=True):
    __tablename__ = "patch"

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    description: Optional[str] = None
    patch_text: str

    amendments: List["AmendmentPatch"] = Relationship(back_populates="patch")


class AmendmentPatch(SQLModel, table=True):
    __tablename__ = "amendment_patch"
    __table_args__ = (UniqueConstraint("amendment_id", "patch_id", name="amendment_patch_unique"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    amendment_id: int = Field(foreign_key="amendment.id")
    patch_id: int = Field(foreign_key="patch.id")

    amendment: Amendment = Relationship(back_populates="patches")
    patch: Patch = Relationship(back_populates="amendments")


class Vote(SQLModel, table=True):
    __tablename__ = "vote"
    __table_args__ = (UniqueConstraint("amendment_id", "user_id", name="unique_vote_per_user"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    amendment_id: str = Field(foreign_key="amendment.id")
    user_id: str = Field(foreign_key="user.id")
    value: bool
    amendment: Amendment = Relationship(back_populates="votes")
    user: User = Relationship(back_populates="votes")


class Group(SQLModel, table=True):
    __tablename__ = "group_entity"
    __table_args__ = (UniqueConstraint("scope_type", "scope_id", "name", name="group_scope_name_unique"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    name: str
    scope_type: str
    scope_id: int

    permissions: Permissions = Field(default=Permissions.READ)
    memberships: List["GroupMembership"] = Relationship(back_populates="group")
    tenant: Optional[Tenant] = Relationship(back_populates="groups")


class GroupMembership(SQLModel, table=True):
    __tablename__ = "group_membership"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="unique_group_membership"),)

    id: str = Field(primary_key=True, default_factory=generate_uuid)
    group_id: str = Field(foreign_key="group_entity.id")
    user_id: str = Field(foreign_key="user.id")

    group: Group = Relationship(back_populates="memberships")
    user: User = Relationship(back_populates="groups")
