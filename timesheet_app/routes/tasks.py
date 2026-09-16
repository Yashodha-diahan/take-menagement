from flask import Blueprint, redirect, render_template, request, url_for

from ..db import get_cursor

bp = Blueprint("tasks", __name__)


def _get_form_choices(cur):
    cur.execute("SELECT id, name FROM projects WHERE status='active' ORDER BY name")
    projects = cur.fetchall()
    cur.execute(
        "SELECT id, full_name FROM employees WHERE status='active' ORDER BY full_name"
    )
    employees = cur.fetchall()
    return projects, employees


@bp.route("/")
def list_tasks():
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT tk.id, tk.title, p.name AS project_name, e.full_name AS employee_name,
                   tk.estimated_hours, tk.status, tk.notes
            FROM tasks tk
            JOIN projects p ON p.id = tk.project_id
            LEFT JOIN employees e ON e.id = tk.employee_id
            ORDER BY tk.id
            """
        )
        tasks = cur.fetchall()
    return render_template("tasks/list.html", tasks=tasks)


@bp.route("/new", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        title = request.form["title"]
        project_id = request.form["project_id"]
        employee_id = request.form.get("employee_id") or None
        estimated_hours = request.form.get("estimated_hours") or None
        status = request.form.get("status", "open")
        notes = request.form.get("notes")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, project_id, employee_id, estimated_hours, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (title, project_id, employee_id, estimated_hours, status, notes),
            )
        return redirect(url_for("tasks.list_tasks"))

    with get_cursor() as cur:
        projects, employees = _get_form_choices(cur)
    return render_template(
        "tasks/form.html", task=None, projects=projects, employees=employees
    )


@bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        title = request.form["title"]
        project_id = request.form["project_id"]
        employee_id = request.form.get("employee_id") or None
        estimated_hours = request.form.get("estimated_hours") or None
        status = request.form.get("status", "open")
        notes = request.form.get("notes")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE tasks
                SET title=%s, project_id=%s, employee_id=%s, estimated_hours=%s,
                    status=%s, notes=%s
                WHERE id=%s
                """,
                (title, project_id, employee_id, estimated_hours, status, notes, task_id),
            )
        return redirect(url_for("tasks.list_tasks"))

    with get_cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
        task = cur.fetchone()
        projects, employees = _get_form_choices(cur)
    return render_template(
        "tasks/form.html", task=task, projects=projects, employees=employees
    )


@bp.route("/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    return redirect(url_for("tasks.list_tasks"))
