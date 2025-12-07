from __future__ import annotations

import uuid

from sqlmodel import Field
from sqlmodel import Relationship

from .amendments import Amendment
from .groups import Group
from .helpers import BaseSQLModel
from .projects import Project


class Document(BaseSQLModel, table=True):
    __tablename__ = "document"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    body: str
    project_id: uuid.UUID = Field(foreign_key="project.id")

    project: Project | None = Relationship(back_populates="documents")
    amendments: list[Amendment] = Relationship(back_populates="document")
    groups: list[Group] = Relationship(back_populates="document")
