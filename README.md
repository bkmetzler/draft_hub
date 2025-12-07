# Draft Hub

Draft Hub is a collaborative workspace for drafting laws and managing amendments. Multiple users can propose new draft documents, suggest amendments, and vote to approve or reject proposed changes. Amendments show how close they are to the minimum vote requirement and their approval percentage, making it easy to understand community support.

## Features

- Multi-tenant hierarchy: tenants own projects and projects own documents
- Moderator groups at every tenant/project/document level to approve or reject amendments
- User registration and login with hashed passwords
- Create tenant-specific projects and draft-law documents with full text
- Propose amendments tied to a document and project
- Vote for or against amendments with automatic tallying
- Minimum vote tracking and approval percentages for each amendment
- JWT-protected JSON API for integrating with other systems

### Moderators & Groups

Every tenant, project, and document automatically creates a `moderators` group. The creator is added to that group so they can
curate their workspace immediately. Members of any moderator group in a document's hierarchy can accept or reject amendments
directly from the document page, which also disables further voting. Use these groups to grant trusted collaborators the ability
to finalize changes after the community has weighed in.

### Data relationships:
- User table
- UserPasswordHash Table
- Tenant Table
- TenantGroup Table
- Project Table
- ProjectGroup Table  (One Project -> One Group)
- TenantProject Table  (One Tenant -> Many Project)
- DocumentTenant Table  (One Tenant -> Many Document)
- Document Table
- Amendment Table
- AmendmentPatch Table  (One Amendment -> Many Patch)
- Patch Table


## Tech Stack

- Python 3.12
- FastAPI with SQLModel and Alembic-ready database layer
- Redis (optional) for future caching
- SQLite database stored in `docs.db` by default
- React + Material UI front end (Vite dev server)

## Getting Started

### 1. Clone and set up a virtual environment

```bash
git clone <your repo url>
cd draft_hub
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database

Create the SQLite tables with the FastAPI lifespan hook (called automatically when the server starts) or by importing the
`create_db_and_tables` helper:

```bash
python -c "from app.database import create_db_and_tables; create_db_and_tables()"
```

(Alternatively, running `python app.py` once will create the database automatically.)

1.) Create a web Application and api
# Description
┌ New documents
├─ Copy/Paste into Textbox
├─ Open file (txt, rtf, doc, html, etc)

# Pages
┌ New Document
  ├─ Copy/Paste into textbox
  ├─ Open/Upload
     ├── Need to add as many file types that can be converted to raw text
├ Document Details
  ├─ Allow for current document version
  ├─ Tab on Document Details page that has the current document and a list of patches (one tab per patch)
├ Patch Details
  ├─ Tab for 'diff' of current document versus current document with the patch applied.  Color background coding Green as added characters, Red as removed characters.
  ├─ Tab for 'vote'
  ├─ Tab for current 'vote' count, and who voted Yes versus No
├ User Details
  ├─ Should have user account details
  ├─ Should have the ability to reset password
├ Login
  ├─ /login
    ├── page to prompt for username/password and save JWT to Javascript Local Storage
  ├─ /logout
    ├── page to clear Javascript Local Storage and redirect to '/login'

├ Directory Structure
├── app  # Python Application Source
├── ui   # React Application
├── migrations  # Alembic migrations

2.) Technical outline
## Python Requirements
1.) FastAPI
2.) Alembic
3.) SQLModel
4.) Pydantic Settings
5.) Redis

## UI Requirements
1.) Material UI CSS/Icons
2.) Class that displays text document
3.) Class that displays differences between two text strings

# General Requirements
1.) JWT Authentication that can be used in the UI application to authenticate against the API.

# Python Helper Functions
1.) Python function to decode JWT and query Groups from database.
