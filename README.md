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

### 4. Run the API server

Launch FastAPI with uvicorn:

```bash
uvicorn app.main:app --reload
```

The server exposes JWT-backed routes for authentication (`/auth/login`, `/auth/register`), user info (`/users/me`), tenants,
documents, amendments, and voting.

### 5. Run the React UI

Install the UI dependencies and start the Vite dev server:

```bash
cd ui
npm install
npm run start
```

Open http://localhost:5173 to access the Material UI front end that provides copy/paste document intake, file upload, diff
visualization, voting previews, and a client-side JWT locker.

## Project Structure

```
app.py              # Legacy Flask application and models
app/                # FastAPI application source (SQLModel models, routers, security)
ui/                 # React front end (Vite + Material UI)
migrations/         # Alembic migrations (seed folder)
requirements.txt    # Python dependencies
README.md           # This file
```

## License

MIT License (or add your preferred license).
