import uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class GroupMembership(SQLModel, table=True):
    __tablename__ = "group_membership"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    group_id: uuid.UUID = Field(foreign_key="groups.id")

    user: Optional["User"] = Relationship(back_populates="memberships")
    group: Optional["Group"] = Relationship(back_populates="memberships")
