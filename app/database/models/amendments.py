import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Amendment(SQLModel, table=True):
    __tablename__ = "amendment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    summary: str
    document_id: uuid.UUID = Field(foreign_key="document.id")
    approved: bool = False

    document: Optional["Document"] = Relationship(back_populates="amendments")
    patches: List["Patch"] = Relationship(back_populates="amendment")
