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
- Flask 3 with Flask-SQLAlchemy
- SQLite database stored in `docs.db`

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

Create the SQLite tables with the Flask CLI command:

```bash
flask --app app init-db
```

(Alternatively, running `python app.py` once will create the database automatically.)

### 4. Run the development server

Use the Flask CLI with auto-reload and debugger enabled:

```bash
flask --app app run --debug
```

You can also run the module directly:

```bash
python app.py
```

Then open http://127.0.0.1:5000/ in your browser and start drafting laws!

### 5. Requesting JWT tokens

The app exposes a simple bearer-token API that surfaces project documents.

1. Request a token:

   ```bash
   curl -X POST http://127.0.0.1:5000/api/token \
     -H "Content-Type: application/json" \
     -d '{"username": "youruser", "password": "yourpass"}'
   ```

2. Use the returned token when calling JWT-protected endpoints, such as:

   ```bash
   curl http://127.0.0.1:5000/api/projects/1/docs \
     -H "Authorization: Bearer <token>"
   ```

Tokens expire after one hour by default.

## Project Structure

```
app.py              # Flask application and models
requirements.txt    # Python dependencies
templates/          # Jinja templates for pages
README.md           # This file
```

## License

MIT License (or add your preferred license).
