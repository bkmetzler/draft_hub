# Alembic migrations

This folder is reserved for Alembic migration scripts. The current codebase uses SQLModel and creates tables automatically on
startup for local development; run `alembic init migrations` to bootstrap a migration environment when you are ready to manage
schema changes in production.
