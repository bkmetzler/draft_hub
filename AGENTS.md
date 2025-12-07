# Application
The web application is a way to agree on documents and changes to documents(Amendments).

## Logic
- Alembic migration setup wired to SQLModel.metadata
- Add Auth (JWT with Password Hashing)
- Add CORSMiddleware to FastAPI APP allowing all "*"
- All database should use Async (AsyncEngine + AsyncSession)
- Tenant and Project could have multiple groups assigned.
- SQLModel Group should have an 8-bit bitwise field of "Permissions" with Python's enum
  - Permissions Enum should have the following:
    - Read
    - Write
    - Create
    - Approve
    - Deny
    - Commit

## Directory Structure
├── app.py
├── database
│   ├── __init__.py
│   └── models
│       ├── users
│       ├── groups
│       ├── group_memberships
│       ├── tenants
│       └── projects
├── helpers
│   └── __init__.py
├── __init__.py
├── middleware
│   ├── configure.py
│   └── __init__.py
├── routers
│   ├── amendments.py
│   ├── auth.py
│   ├── documents.py
│   ├── general.py
│   ├── helpers
│   │   ├── diff.py
│   │   └── __init__..py
│   ├── __init__.py
│   ├── tenants.py
│   └── users.py
├── security.py
└── settings.py


## Programming
### Python
#### Formatting
    - pre-commit
    - black
    - flake8
    - mypy
    - isort
#### Requirements
    - pydantic-settings
    - fastapi
    - sqlmodel
    - alembic

#### Version
Python version 3.12+


## Database Modeling
### With FastAPI and SQLModel
#### Models
    - User
    - HashPasswordHistory
    - Tenant
    - Project
    - Document
    - Amendment
    - Patch

#### Model References
User (One 2 Many) HashPasswordHistory
Tenant (One 2 Many) Project
Project (One 2 Many) Document
Document (One 2 Many) Amendment
Amendment (One 2 Many) Patch
User (Many 2 Many) Group using GroupMembership as the joining table

#### Model Notes
##### User
   - Should have 'has_groups(grps: list[str]) -> bool'
   - Should have 'has_scope(scope_type: str, scope_id: str) -> bool'


# API Endpoints
## Health/General
- GET /api/v1/health

## Tenant
- GET /api/v1/tenant/{tenant_id}
- POST /api/v1/tenant/{tenant_id}/invite
- POST /api/v1/tenant/{tenant_id}/project



## Document
- GET /api/v1/document
- GET /api/v1/document/{document_id}
- GET /api/v1/document/{document_id}/amendments
- POST /api/v1/document/{document_id}/amendments


## Project
- GET /api/v1/project
- POST /api/v1/project
- GET /api/v1/project/{project_id}
- GET /api/v1/project/{project_id}/users
- POST /api/v1/project/{project_id}/invite

## Amendment
- GET /api/v1/amendment/{amendment_id}
- POST /api/v1/amendment/{document_id}
