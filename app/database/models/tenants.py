import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Tenant(SQLModel, table=True):
    __tablename__ = "tenant"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str

    projects: List["Project"] = Relationship(back_populates="tenant")
    groups: List["Group"] = Relationship(back_populates="tenant")
