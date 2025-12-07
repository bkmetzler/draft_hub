from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database.models import Document, Project, Tenant, User, Group, GroupMembership, TenantProject
from ..database import get_session
from ..security import get_current_user

router = APIRouter(prefix="/tenant", tags=["Tenants"])


@router.get("/")
def list_tenants(session: Session = Depends(get_session)):
    tenants = session.exec(select(Tenant)).all()
    return tenants


@router.post("/")
def create_tenant(
    name: str,
    description: str | None = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if session.exec(select(Tenant).where(Tenant.name == name)).first():
        raise HTTPException(status_code=400, detail="Tenant already exists")
    tenant = Tenant(name=name, description=description)
    session.add(tenant)
    session.flush()

    admin_group = Group(name="Admin", scope_type="tenant", scope_id=tenant.id, tenant=tenant)
    session.add(admin_group)
    session.flush()

    session.add(GroupMembership(group_id=admin_group.id, user_id=user.id))

    session.commit()
    session.refresh(tenant)
    return tenant


@router.post("/{tenant_id}/projects")
def create_project(
    tenant_id: int,
    name: str,
    description: str | None = None,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    tenant = session.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if session.exec(select(Project).where(Project.tenant_id == tenant_id, Project.name == name)).first():
        raise HTTPException(status_code=400, detail="Project already exists")
    project = Project(tenant_id=tenant_id, name=name, description=description, created_by=user.id)
    session.add(project)
    session.flush()
    session.add(TenantProject(tenant_id=tenant_id, project_id=project.id))

    project_admin_group = Group(
        name="Admin",
        scope_type="project",
        scope_id=project.id,
    )
    session.add(project_admin_group)
    session.flush()

    session.add(GroupMembership(group_id=project_admin_group.id, user_id=user.id))

    session.commit()
    session.refresh(project)
    return project


@router.post("/{tenant_id}/projects/{project_id}/documents")
def create_document(
    tenant_id: int,
    project_id: int,
    title: str,
    text: str,
    summary: str | None = None,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None or project.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Project not found for tenant")
    document = Document(project_id=project_id, title=title, summary=summary, text=text, created_by=user.id)
    session.add(document)
    session.commit()
    return document
