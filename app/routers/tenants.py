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
from app.database.models import Tenant
from app.database.models.groups import Permissions

router = APIRouter(prefix="/api/v1/tenant", tags=["tenant"])


class TenantCreate(SQLModel):
    name: str


@router.post("", response_model=Tenant)
async def create_tenant(payload: TenantCreate, session: AsyncSession = Depends(get_session)) -> Tenant:
    tenant = Tenant(name=payload.name)
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    moderator_group = Group(
        name="moderators", tenant_id=tenant.id, permissions=int(Permissions.APPROVE | Permissions.DENY)
    )
    session.add(moderator_group)
    await session.commit()
    return tenant


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> Tenant:
    result = await session.exec(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant
