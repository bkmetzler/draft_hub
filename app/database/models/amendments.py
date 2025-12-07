from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .documents import Document
from .helpers import BaseSQLModel
from .patches import Patch


class Amendment(BaseSQLModel, table=True):
    __tablename__ = "amendment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    summary: str
    document_id: uuid.UUID = Field(foreign_key="document.id")
    approved: bool = False

    document: Document | None = Relationship(back_populates="amendments")
    patches: list[Patch] = Relationship(back_populates="amendment")
