import uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Patch(SQLModel, table=True):
    __tablename__ = "patch"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    amendment_id: uuid.UUID = Field(foreign_key="amendment.id")

    amendment: Optional["Amendment"] = Relationship(back_populates="patches")
