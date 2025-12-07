from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..database.models import Amendment, AmendmentPatch, Document, Patch, User, Vote
from ..helpers import falsy, truthy
from ..routers.helpers.diff import render_diff
from ..security import get_current_user

router = APIRouter(prefix="/amendment", tags=["Amendment"])


@router.post("/document/{document_id}")
def propose_amendment(
    document_id: int,
    title: str,
    description: Optional[str],
    proposed_text: str = "",
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    amendment = Amendment(
        document_id=document_id,
        title=title,
        description=description,
        proposed_text=proposed_text or document.text,
        created_by=user.id,
    )
    session.add(amendment)
    session.commit()
    session.refresh(amendment)
    return amendment


@router.post("/{amendment_id}/patches")
def attach_patch(
    amendment_id: int,
    patch_text: str,
    description: str | None = None,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    amendment = session.get(Amendment, amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    patch = Patch(patch_text=patch_text, description=description)
    session.add(patch)
    session.flush()
    session.add(AmendmentPatch(amendment_id=amendment_id, patch_id=patch.id))
    session.commit()
    session.refresh(patch)
    return patch


@router.get("/{amendment_id}/diff")
def amendment_diff(amendment_id: int, session: Session = Depends(get_session)):
    amendment = session.get(Amendment, amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    document = session.get(Document, amendment.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    patches = [link.patch for link in amendment.patches]
    patched_text = patches[-1].patch_text if patches else amendment.proposed_text
    return {
        "document_text": document.text,
        "patched_text": patched_text,
        "diff": render_diff(document.text, patched_text),
    }


@router.post("/{amendment_id}/vote")
def vote(amendment_id: int, value: int, session: Session = Depends(get_session), user=Depends(get_current_user)):
    if falsy(value):
        raise HTTPException(status_code=400, detail="Vote must be -1 or 1")
    amendment = session.get(Amendment, amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    existing = session.exec(select(Vote).where(Vote.amendment_id == amendment_id, Vote.user_id == user.id)).first()
    if existing:
        existing.value = truthy(value)
        session.add(existing)
    else:
        session.add(Vote(amendment_id=amendment_id, user_id=user.id, value=value))
    session.commit()
    yes = session.exec(select(Vote).where(Vote.amendment_id == amendment_id, Vote.value == 1)).all()
    no = session.exec(select(Vote).where(Vote.amendment_id == amendment_id, Vote.value == -1)).all()
    return {"approvals": len(yes), "rejections": len(no), "total": len(yes) + len(no)}


@router.get("/{amendment_id}/votes")
def vote_summary(amendment_id: int, session: Session = Depends(get_session)):
    amendment = session.get(Amendment, amendment_id)
    if amendment is None:
        raise HTTPException(status_code=404, detail="Amendment not found")
    yes = session.exec(select(Vote).where(Vote.amendment_id == amendment_id, Vote.value == 1)).all()
    no = session.exec(select(Vote).where(Vote.amendment_id == amendment_id, Vote.value == -1)).all()
    total = len(yes) + len(no)
    approval_pct = (len(yes) / total * 100) if total else 0
    return {
        "approvals": len(yes),
        "rejections": len(no),
        "approval_percentage": round(approval_pct, 1),
        "minimum_votes_met": total >= 5,
        "total": total,
    }
