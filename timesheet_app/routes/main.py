from flask import Blueprint, render_template

from ..db import get_cursor

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM employees")
        employee_count = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) AS count FROM projects")
        project_count = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) AS count FROM tasks")
        task_count = cur.fetchone()["count"]

        cur.execute("SELECT COUNT(*) AS count FROM timesheets")
        timesheet_count = cur.fetchone()["count"]

        cur.execute(
            """
            SELECT t.id, e.full_name, p.name AS project_name, tk.title AS task_title,
                   t.work_date, t.hours_worked, t.status
            FROM timesheets t
            JOIN employees e ON e.id = t.employee_id
            JOIN projects p ON p.id = t.project_id
            JOIN tasks tk ON tk.id = t.task_id
            ORDER BY t.work_date DESC, t.id DESC
            LIMIT 10
            """
        )
        recent_timesheets = cur.fetchall()

    return render_template(
        "index.html",
        employee_count=employee_count,
        project_count=project_count,
        task_count=task_count,
        timesheet_count=timesheet_count,
        recent_timesheets=recent_timesheets,
    )
