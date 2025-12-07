from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session
from sqlmodel import select

from ..database import get_session
from ..database.models import Document

router = APIRouter(prefix="/document", tags=["Documents"])


class CreateDocument(BaseModel):
    tenant_id: int
    project_id: int
    title: str
    text: str
    summary: str | None = Field(default=None)


@router.post("/")
def create_document_detail(data: CreateDocument, session: Session = Depends(get_session)) -> Document:
    doc = Document(
        tenant_id=data.tenant_id,
        project_id=data.project_id,
        title=data.title,
        text=data.text,
        summary=data.summary,
    ).create(session=session)
    return doc


class DocumentDiff(BaseModel):
    title: str
    text: str
    summary: str | None = None


# @router.post("/{document_id}/diff")
# async def create_document_diff(
#     document_id: int,
#     doc: DocumentDiff,
#     session: Session = Depends(get_session),
# )


# @router.get("/")
# async def get_documents(user: User = Depends(get_current_user),) -> list[Document]:
#     user.projects


@router.get("/{document_id}")
def document_detail(document_id: int, session: Session = Depends(get_session)):
    stmt = select(Document).where(Document.id == document_id)
    results = session.exec(stmt).one_or_none()
    if results is None:
        raise HTTPException(status_code=404, detail="Document not found for tenant")
    document = results.document  # type: ignore[attr-defined]
    session.refresh(document)
    return {
        "document": document,
        "amendments": document.amendments,
    }


# @router.get("/{document_id}/amendments")
# async def document_amendments(document_id: int, session: Session = Depends(get_session)) -> list[Amendment]:
#     doc = session.get(Document, document_id)
#     return doc.amendments


# @router.post("/{document_id}/invite")
# @router.post("/{document_id}/members")
