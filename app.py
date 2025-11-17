from __future__ import annotations

from datetime import datetime, timezone, timedelta
from functools import wraps

import click
from flask import (
    Flask,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint, func
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DRAFT_HUB_",
        env_file=".env",
        extra="ignore",
    )

    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite:///docs.db"
    sqlalchemy_track_mods: bool = False
    jwt_secret_key: str | None = None
    jwt_expiration_minutes: int = 60


settings = Settings()

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=settings.secret_key,
    SQLALCHEMY_DATABASE_URI=settings.database_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=settings.sqlalchemy_track_mods,
    JWT_SECRET_KEY=settings.jwt_secret_key or settings.secret_key,
    JWT_EXPIRATION_MINUTES=settings.jwt_expiration_minutes,
)

db = SQLAlchemy(app)


MIN_VOTES_REQUIRED = 5
MODERATOR_GROUP_NAME = "moderators"
GROUP_SCOPE_TENANT = "tenant"
GROUP_SCOPE_PROJECT = "project"
GROUP_SCOPE_DOC = "doc"


def datetime_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)

    projects = db.relationship(
        "Project",
        backref="tenant",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Project.created_at.desc()",
    )


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="tenant_project_name_unique"),
    )

    docs = db.relationship(
        "Doc",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Doc.created_at.desc()",
    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)

    docs = db.relationship("Doc", backref="creator", lazy=True)
    projects = db.relationship("Project", backref="owner", lazy=True)
    amendments = db.relationship("Amendment", backref="author", lazy=True)
    votes = db.relationship("Vote", backref="user", lazy=True)
    group_memberships = db.relationship(
        "GroupMembership",
        backref="member",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Doc(db.Model):
    __tablename__ = "doc"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime_utc,
        onupdate=datetime_utc,
        nullable=False,
    )
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    amendments = db.relationship(
        "Amendment",
        backref="doc",
        lazy=True,
        order_by="Amendment.created_at.desc()",
        cascade="all, delete-orphan",
    )


class Amendment(db.Model):
    __tablename__ = "amendment"

    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey("doc.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    proposed_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="open", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    votes = db.relationship(
        "Vote",
        backref="amendment",
        lazy=True,
        cascade="all, delete-orphan",
    )

    @property
    def vote_count(self) -> int:
        return len(self.votes)

    @property
    def approvals(self) -> int:
        return sum(1 for vote in self.votes if vote.value == 1)

    @property
    def rejections(self) -> int:
        return sum(1 for vote in self.votes if vote.value == -1)

    @property
    def score(self) -> int:
        return self.approvals - self.rejections

    @property
    def approval_percentage(self) -> float:
        total = self.vote_count
        if total == 0:
            return 0.0
        return round((self.approvals / total) * 100, 1)

    @property
    def has_minimum_votes(self) -> bool:
        return self.vote_count >= MIN_VOTES_REQUIRED


class Vote(db.Model):
    __tablename__ = "vote"

    id = db.Column(db.Integer, primary_key=True)
    amendment_id = db.Column(db.Integer, db.ForeignKey("amendment.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)

    __table_args__ = (
        CheckConstraint("value IN (-1, 1)", name="vote_value_check"),
        UniqueConstraint("amendment_id", "user_id", name="unique_vote_per_user"),
    )


class Group(db.Model):
    __tablename__ = "group_entity"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    scope_type = db.Column(db.String(50), nullable=False)
    scope_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)

    __table_args__ = (
        UniqueConstraint("scope_type", "scope_id", "name", name="group_scope_name_unique"),
    )

    memberships = db.relationship(
        "GroupMembership",
        backref="group",
        lazy=True,
        cascade="all, delete-orphan",
    )


class GroupMembership(db.Model):
    __tablename__ = "group_membership"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group_entity.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime_utc, nullable=False)

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="unique_group_membership"),
    )


def ensure_moderators_group(scope_type: str, scope_id: int) -> Group:
    group = (
        Group.query.filter_by(
            scope_type=scope_type,
            scope_id=scope_id,
            name=MODERATOR_GROUP_NAME,
        ).first()
    )
    if group is None:
        group = Group(name=MODERATOR_GROUP_NAME, scope_type=scope_type, scope_id=scope_id)
        db.session.add(group)
        db.session.flush()
    return group


def add_user_to_group(group: Group, user_id: int | None) -> None:
    if user_id is None:
        return
    membership = GroupMembership.query.filter_by(group_id=group.id, user_id=user_id).first()
    if membership is None:
        db.session.add(GroupMembership(group_id=group.id, user_id=user_id))


def ensure_creator_moderator(scope_type: str, scope_id: int, user_id: int | None) -> None:
    group = ensure_moderators_group(scope_type, scope_id)
    add_user_to_group(group, user_id)


def user_in_moderators(user_id: int, scope_type: str, scope_id: int) -> bool:
    return (
        GroupMembership.query.join(Group)
        .filter(
            GroupMembership.user_id == user_id,
            Group.name == MODERATOR_GROUP_NAME,
            Group.scope_type == scope_type,
            Group.scope_id == scope_id,
        )
        .first()
        is not None
    )


def user_can_moderate(
    user: User | None,
    *,
    doc: Doc | None = None,
    project: Project | None = None,
    tenant: Tenant | None = None,
) -> bool:
    if user is None:
        return False
    if doc is not None and user_in_moderators(user.id, GROUP_SCOPE_DOC, doc.id):
        return True
    if doc is not None:
        project = doc.project
    if project is not None and user_in_moderators(user.id, GROUP_SCOPE_PROJECT, project.id):
        return True
    if project is not None:
        tenant = project.tenant
    if tenant is not None and user_in_moderators(user.id, GROUP_SCOPE_TENANT, tenant.id):
        return True
    return False


@app.before_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
    g.api_user = None


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.get("user") is None:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(**kwargs)

    return wrapped_view


def generate_jwt(user: User) -> tuple[str, datetime]:
    expires = datetime_utc() + timedelta(minutes=app.config["JWT_EXPIRATION_MINUTES"])
    payload = {"sub": user.id, "username": user.username, "exp": expires}
    token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token, expires


def jwt_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing bearer token"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
                options={"require": ["exp", "sub"]},
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(payload.get("sub"))
        if user is None:
            return jsonify({"error": "User not found"}), 401

        g.api_user = user
        return view(**kwargs)

    return wrapped_view


@app.route("/")
def index():
    tenants = Tenant.query.order_by(Tenant.name.asc()).all()
    return render_template("index.html", tenants=tenants)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if username and User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if email and User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        next_url = request.args.get("next") or request.form.get("next")

        user = None
        if username:
            user = User.query.filter(func.lower(User.username) == username.lower()).first()

        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            flash(f"Welcome back, {user.username}!")
            return redirect(next_url or url_for("index"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", next=request.args.get("next"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/api/token", methods=["POST"])
def api_token():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter(func.lower(User.username) == username.lower()).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    token, expires = generate_jwt(user)
    return jsonify(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires.isoformat(),
            "user_id": user.id,
        }
    )


@app.route("/tenants/new", methods=["GET", "POST"])
@login_required
def create_tenant():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Tenant name is required.", "danger")
        elif Tenant.query.filter(func.lower(Tenant.name) == name.lower()).first():
            flash("Tenant name must be unique.", "danger")
        else:
            tenant = Tenant(name=name, description=description or None)
            db.session.add(tenant)
            db.session.flush()
            ensure_creator_moderator(GROUP_SCOPE_TENANT, tenant.id, g.user.id)
            db.session.commit()
            flash("Tenant created.", "success")
            return redirect(url_for("tenant_detail", tenant_id=tenant.id))

    return render_template("tenant_form.html")


@app.route("/tenants/<int:tenant_id>")
def tenant_detail(tenant_id: int):
    tenant = Tenant.query.get_or_404(tenant_id)
    return render_template("tenant_detail.html", tenant=tenant)


@app.route("/tenants/<int:tenant_id>/projects/new", methods=["GET", "POST"])
@login_required
def create_project(tenant_id: int):
    tenant = Tenant.query.get_or_404(tenant_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Project name is required.", "danger")
        elif Project.query.filter(
            Project.tenant_id == tenant.id,
            func.lower(Project.name) == name.lower(),
        ).first():
            flash("Project name must be unique within the tenant.", "danger")
        else:
            project = Project(
                tenant_id=tenant.id,
                name=name,
                description=description or None,
                created_by=g.user.id,
            )
            db.session.add(project)
            db.session.flush()
            ensure_creator_moderator(GROUP_SCOPE_PROJECT, project.id, g.user.id)
            db.session.commit()
            flash("Project created.", "success")
            return redirect(url_for("project_detail", project_id=project.id))

    return render_template("project_form.html", tenant=tenant)


@app.route("/projects/<int:project_id>")
def project_detail(project_id: int):
    project = Project.query.get_or_404(project_id)
    docs = Doc.query.filter_by(project_id=project.id).order_by(Doc.created_at.desc()).all()
    return render_template("project_detail.html", project=project, docs=docs)


@app.route("/projects/<int:project_id>/docs/new", methods=["GET", "POST"])
@login_required
def create_doc(project_id: int):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        text = request.form.get("text", "").strip()

        if not title or not text:
            flash("Title and full text are required.", "danger")
        else:
            doc = Doc(
                project_id=project.id,
                title=title,
                summary=summary or None,
                text=text,
                created_by=g.user.id,
            )
            db.session.add(doc)
            db.session.flush()
            ensure_creator_moderator(GROUP_SCOPE_DOC, doc.id, g.user.id)
            db.session.commit()
            flash("Document created.", "success")
            return redirect(url_for("doc_detail", doc_id=doc.id))

    return render_template("doc_form.html", project=project)


@app.route("/docs/<int:doc_id>")
def doc_detail(doc_id: int):
    doc = Doc.query.get_or_404(doc_id)
    amendments = Amendment.query.filter_by(doc_id=doc.id).order_by(Amendment.created_at.desc()).all()
    can_moderate = user_can_moderate(g.user, doc=doc)
    return render_template(
        "doc_detail.html",
        doc=doc,
        amendments=amendments,
        min_votes_required=MIN_VOTES_REQUIRED,
        can_moderate=can_moderate,
    )


@app.route("/api/projects/<int:project_id>/docs")
@jwt_required
def api_project_docs(project_id: int):
    project = Project.query.get_or_404(project_id)
    docs = [
        {
            "id": doc.id,
            "title": doc.title,
            "summary": doc.summary,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat(),
            "created_by": doc.creator.username,
            "amendment_count": len(doc.amendments),
        }
        for doc in project.docs
    ]
    return jsonify(
        {
            "project": {
                "id": project.id,
                "name": project.name,
                "tenant": project.tenant.name,
            },
            "docs": docs,
        }
    )


@app.route("/docs/<int:doc_id>/amendments/new", methods=["GET", "POST"])
@login_required
def create_amendment(doc_id: int):
    doc = Doc.query.get_or_404(doc_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        proposed_text = request.form.get("proposed_text", "").strip()

        if not title or not proposed_text:
            flash("Title and proposed text are required.", "danger")
        else:
            amendment = Amendment(
                doc_id=doc.id,
                title=title,
                description=description or None,
                proposed_text=proposed_text,
                created_by=g.user.id,
            )
            db.session.add(amendment)
            db.session.commit()
            flash("Amendment proposed.", "success")
            return redirect(url_for("doc_detail", doc_id=doc.id))

    return render_template("amendment_form.html", doc=doc)


@app.route("/amendments/<int:amendment_id>/moderate", methods=["POST"])
@login_required
def moderate_amendment(amendment_id: int):
    amendment = Amendment.query.get_or_404(amendment_id)
    doc = amendment.doc
    if not user_can_moderate(g.user, doc=doc):
        flash("You are not authorized to moderate this amendment.", "danger")
        return redirect(url_for("doc_detail", doc_id=doc.id))

    if amendment.status != "open":
        flash("This amendment has already been moderated.", "info")
        return redirect(url_for("doc_detail", doc_id=doc.id))

    action = request.form.get("action")
    if action not in {"accept", "reject"}:
        flash("Invalid moderation action.", "danger")
        return redirect(url_for("doc_detail", doc_id=doc.id))

    if action == "accept":
        amendment.status = "accepted"
        flash("Amendment accepted by moderators.", "success")
    else:
        amendment.status = "rejected"
        flash("Amendment rejected by moderators.", "warning")

    db.session.commit()
    return redirect(url_for("doc_detail", doc_id=doc.id))


@app.route("/amendments/<int:amendment_id>/vote", methods=["POST"])
@login_required
def vote(amendment_id: int):
    amendment = Amendment.query.get_or_404(amendment_id)
    if amendment.status != "open":
        flash("Voting is closed for this amendment.", "warning")
        return redirect(url_for("doc_detail", doc_id=amendment.doc_id))
    try:
        value = int(request.form.get("value", "0"))
    except ValueError:
        flash("Invalid vote value.", "danger")
        return redirect(url_for("doc_detail", doc_id=amendment.doc_id))

    if value not in (-1, 1):
        flash("Invalid vote option.", "danger")
        return redirect(url_for("doc_detail", doc_id=amendment.doc_id))

    vote = Vote.query.filter_by(amendment_id=amendment.id, user_id=g.user.id).first()
    if vote:
        if vote.value == value:
            db.session.delete(vote)
            flash("Your vote has been removed.", "info")
        else:
            vote.value = value
            flash("Your vote has been updated.", "success")
    else:
        vote = Vote(amendment_id=amendment.id, user_id=g.user.id, value=value)
        db.session.add(vote)
        flash("Your vote has been recorded.", "success")

    db.session.commit()
    return redirect(url_for("doc_detail", doc_id=amendment.doc_id))


@app.cli.command("init-db")
def init_db() -> None:
    """Initialize the database tables."""
    db.create_all()
    click.echo("Initialized the database.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
