import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .groups import Group


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

    memberships: List["GroupMembership"] = Relationship(back_populates="user")

    def has_groups(self, grps: list[str]) -> bool:
        group_names = {membership.group.name for membership in self.memberships if membership.group}
        return any(name in group_names for name in grps)

    def has_scope(self, scope_type: str, scope_id: str) -> bool:
        for membership in self.memberships:
            group = membership.group
            if not group:
                continue
            match scope_type:
                case "tenant" if group.tenant_id and str(group.tenant_id) == scope_id:
                    return True
                case "project" if group.project_id and str(group.project_id) == scope_id:
                    return True
                case "document" if group.document_id and str(group.document_id) == scope_id:
                    return True
        return False


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    id: uuid.UUID
    username: str
    email: str


class UserPasswordHash(SQLModel, table=True):
    __tablename__ = "user_password_hash"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    hashed_password: str
