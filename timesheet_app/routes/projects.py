from flask import Blueprint, redirect, render_template, request, url_for

from ..db import get_cursor

bp = Blueprint("projects", __name__)


@bp.route("/")
def list_projects():
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, name, client, start_date, end_date, status, description
            FROM projects
            ORDER BY id
            """
        )
        projects = cur.fetchall()
    return render_template("projects/list.html", projects=projects)


@bp.route("/new", methods=["GET", "POST"])
def new_project():
    if request.method == "POST":
        name = request.form["name"]
        client = request.form.get("client")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        status = request.form.get("status", "active")
        description = request.form.get("description")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO projects (name, client, start_date, end_date, status, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, client, start_date, end_date, status, description),
            )
        return redirect(url_for("projects.list_projects"))

    return render_template("projects/form.html", project=None)


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
def edit_project(project_id):
    if request.method == "POST":
        name = request.form["name"]
        client = request.form.get("client")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        status = request.form.get("status", "active")
        description = request.form.get("description")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE projects
                SET name=%s, client=%s, start_date=%s, end_date=%s, status=%s, description=%s
                WHERE id=%s
                """,
                (name, client, start_date, end_date, status, description, project_id),
            )
        return redirect(url_for("projects.list_projects"))

    with get_cursor() as cur:
        cur.execute("SELECT * FROM projects WHERE id=%s", (project_id,))
        project = cur.fetchone()
    return render_template("projects/form.html", project=project)


@bp.route("/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE projects SET status='archived' WHERE id=%s", (project_id,)
        )
    return redirect(url_for("projects.list_projects"))
