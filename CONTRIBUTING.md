# Functionality
## New user must register with '/auth/register'
## User must be invited to a Tenant or Project



# Directory Structure
- /app
- /app/database
- /app/routers
- /app/routers/helpers
- /app.py
- /security.py
- /settings.py

# API Endpoints
## Health/General 
- GET /api/v1/health

## Tenant
- GET /api/v1/tenant/{tenant_id}
- POST /api/v1/tenant/{tenant_id}/invite
- POST /api/v1/tenant/{tenant_id}/project



## Document
- POST /api/v1/document/{document_id}/invite
- GET /api/v1/document/{document_id}/members
- POST /api/v1/document/{document_id}/members
- GET /api/v1/document/{document_id}/amendments
- POST /api/v1/document/{document_id}/amendments
 
 
## Project
- GET /api/v1/project
- POST /api/v1/project
- GET /api/v1/project/{project_id}
- POST /api/v1/project/{project_id}/invite

## Amendment
- GET /api/v1/amendment/{amendment_id}
- POST /api/v1/amendment/{document_id}

