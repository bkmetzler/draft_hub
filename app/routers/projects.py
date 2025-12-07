import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlmodel import select
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.database.models import Group
from app.database.models import Project
from app.database.models import Tenant
from app.database.models.groups import Permissions

router = APIRouter(prefix="/api/v1/project", tags=["project"])


class ProjectCreate(SQLModel):
    name: str
    tenant_id: uuid.UUID


@router.post("", response_model=Project)
async def create_project(payload: ProjectCreate, session: AsyncSession = Depends(get_session)) -> Project:
    tenant_result = await session.exec(select(Tenant).where(Tenant.id == payload.tenant_id))
    if not tenant_result.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    project = Project(name=payload.name, tenant_id=payload.tenant_id)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    moderator_group = Group(
        name="moderators", project_id=project.id, permissions=int(Permissions.APPROVE | Permissions.DENY)
    )
    session.add(moderator_group)
    await session.commit()
    return project


@router.get("", response_model=list[Project])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[Project]:
    result = await session.exec(select(Project))
    return result.all()


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> Project:
    result = await session.exec(select(Project).where(Project.id == project_id))
    project = result.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
