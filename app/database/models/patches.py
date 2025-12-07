from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .amendments import Amendment
from .helpers import BaseSQLModel


class Patch(BaseSQLModel, table=True):
    __tablename__ = "patch"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    amendment_id: uuid.UUID = Field(foreign_key="amendment.id")

    amendment: Amendment | None = Relationship(back_populates="patches")
