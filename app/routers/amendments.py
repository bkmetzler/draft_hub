import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.database.models import Amendment, Document, Patch

router = APIRouter(prefix="/api/v1/amendment", tags=["amendment"])


class AmendmentCreate(SQLModel):
    summary: str
    document_id: uuid.UUID
    patch_content: str


@router.get("/{amendment_id}", response_model=Amendment)
async def get_amendment(amendment_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> Amendment:
    result = await session.exec(select(Amendment).where(Amendment.id == amendment_id))
    amendment = result.first()
    if not amendment:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return amendment


@router.post("/{document_id}", response_model=Amendment)
async def create_amendment(document_id: uuid.UUID, payload: AmendmentCreate, session: AsyncSession = Depends(get_session)) -> Amendment:
    document_result = await session.exec(select(Document).where(Document.id == document_id))
    document = document_result.first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    amendment = Amendment(summary=payload.summary, document_id=document_id)
    session.add(amendment)
    await session.commit()
    await session.refresh(amendment)
    patch = Patch(content=payload.patch_content, amendment_id=amendment.id)
    session.add(patch)
    await session.commit()
    return amendment


@router.get("/{document_id}/patches", response_model=list[Patch])
async def list_patches(document_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> list[Patch]:
    amendment_ids = await session.exec(select(Amendment.id).where(Amendment.document_id == document_id))
    ids = amendment_ids.all()
    if not ids:
        return []
    patches = await session.exec(select(Patch).where(Patch.amendment_id.in_(ids)))
    return patches.all()
