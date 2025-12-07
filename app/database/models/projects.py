import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Project(SQLModel, table=True):
    __tablename__ = "project"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id")

    tenant: Optional["Tenant"] = Relationship(back_populates="projects")
    documents: List["Document"] = Relationship(back_populates="project")
    groups: List["Group"] = Relationship(back_populates="project")
