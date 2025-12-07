import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    body: str
    project_id: uuid.UUID = Field(foreign_key="project.id")

    project: Optional["Project"] = Relationship(back_populates="documents")
    amendments: List["Amendment"] = Relationship(back_populates="document")
    groups: List["Group"] = Relationship(back_populates="document")
