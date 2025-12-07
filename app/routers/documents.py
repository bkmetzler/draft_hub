import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import get_session
from app.database.models import Document, Project

router = APIRouter(prefix="/api/v1/document", tags=["document"])


class DocumentCreate(SQLModel):
    title: str
    body: str
    project_id: uuid.UUID


@router.get("", response_model=list[Document])
async def list_documents(session: AsyncSession = Depends(get_session)) -> list[Document]:
    result = await session.exec(select(Document))
    return result.all()


@router.post("", response_model=Document)
async def create_document(payload: DocumentCreate, session: AsyncSession = Depends(get_session)) -> Document:
    project_result = await session.exec(select(Project).where(Project.id == payload.project_id))
    if not project_result.first():
        raise HTTPException(status_code=404, detail="Project not found")

    document = Document(title=payload.title, body=payload.body, project_id=payload.project_id)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> Document:
    result = await session.exec(select(Document).where(Document.id == document_id))
    document = result.first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
