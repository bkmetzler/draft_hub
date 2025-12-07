from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .groups import Group
from .helpers import BaseSQLModel
from .users import User


class GroupMembership(BaseSQLModel, table=True):
    __tablename__ = "group_membership"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    group_id: uuid.UUID = Field(foreign_key="groups.id")

    user: User | None = Relationship(back_populates="memberships")
    group: Group | None = Relationship(back_populates="memberships")
