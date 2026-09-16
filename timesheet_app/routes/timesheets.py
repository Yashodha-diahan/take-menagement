import xml.etree.ElementTree as ET

from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for

from ..db import get_cursor

bp = Blueprint("timesheets", __name__)

STATUSES = ["draft", "submitted", "approved", "rejected"]


def _get_form_choices(cur, task_project_id=None):
    cur.execute("SELECT id, full_name FROM employees WHERE status='active' ORDER BY full_name")
    employees = cur.fetchall()
    cur.execute("SELECT id, name FROM projects WHERE status='active' ORDER BY name")
    projects = cur.fetchall()

    tasks = []
    if task_project_id:
        cur.execute(
            "SELECT id, title FROM tasks WHERE project_id=%s ORDER BY title",
            (task_project_id,),
        )
        tasks = cur.fetchall()

    return employees, projects, tasks


@bp.route("/")
def list_timesheets():
    filters = {
        "employee_id": request.args.get("employee_id", ""),
        "project_id": request.args.get("project_id", ""),
        "task_id": request.args.get("task_id", ""),
        "work_date": request.args.get("work_date", ""),
        "status": request.args.get("status", ""),
    }

    query = """
        SELECT t.id, e.full_name AS employee_name, p.name AS project_name,
               tk.title AS task_title, t.work_date, t.hours_worked, t.notes, t.status
        FROM timesheets t
        JOIN employees e ON e.id = t.employee_id
        JOIN projects p ON p.id = t.project_id
        JOIN tasks tk ON tk.id = t.task_id
        WHERE 1=1
    """
    params = []

    if filters["employee_id"]:
        query += " AND t.employee_id = %s"
        params.append(filters["employee_id"])
    if filters["project_id"]:
        query += " AND t.project_id = %s"
        params.append(filters["project_id"])
    if filters["task_id"]:
        query += " AND t.task_id = %s"
        params.append(filters["task_id"])
    if filters["work_date"]:
        query += " AND t.work_date = %s"
        params.append(filters["work_date"])
    if filters["status"]:
        query += " AND t.status = %s"
        params.append(filters["status"])

    query += " ORDER BY t.work_date DESC, t.id DESC"

    with get_cursor() as cur:
        cur.execute(query, params)
        timesheets = cur.fetchall()

        cur.execute("SELECT id, full_name FROM employees ORDER BY full_name")
        employees = cur.fetchall()
        cur.execute("SELECT id, name FROM projects ORDER BY name")
        projects = cur.fetchall()
        cur.execute("SELECT id, title FROM tasks ORDER BY title")
        tasks = cur.fetchall()

    return render_template(
        "timesheets/list.html",
        timesheets=timesheets,
        employees=employees,
        projects=projects,
        tasks=tasks,
        filters=filters,
        statuses=STATUSES,
    )


@bp.route("/tasks-by-project/<int:project_id>")
def tasks_by_project(project_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, title FROM tasks WHERE project_id=%s ORDER BY title",
            (project_id,),
        )
        tasks = cur.fetchall()
    return jsonify(tasks)


@bp.route("/new", methods=["GET", "POST"])
def new_timesheet():
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        project_id = request.form["project_id"]
        task_id = request.form["task_id"]
        work_date = request.form["work_date"]
        hours_worked = request.form["hours_worked"]
        notes = request.form.get("notes")
        status = request.form.get("status", "draft")

        with get_cursor() as cur:
            cur.execute("SELECT project_id FROM tasks WHERE id=%s", (task_id,))
            task = cur.fetchone()

        if task is None or str(task["project_id"]) != str(project_id):
            error = "Selected task does not belong to the selected project."
            with get_cursor() as cur:
                employees, projects, tasks = _get_form_choices(cur, project_id)
            return render_template(
                "timesheets/form.html",
                timesheet=request.form,
                employees=employees,
                projects=projects,
                tasks=tasks,
                statuses=STATUSES,
                error=error,
            )

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO timesheets
                    (employee_id, project_id, task_id, work_date, hours_worked, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (employee_id, project_id, task_id, work_date, hours_worked, notes, status),
            )
        return redirect(url_for("timesheets.list_timesheets"))

    with get_cursor() as cur:
        employees, projects, tasks = _get_form_choices(cur)
    return render_template(
        "timesheets/form.html",
        timesheet=None,
        employees=employees,
        projects=projects,
        tasks=tasks,
        statuses=STATUSES,
        error=None,
    )


@bp.route("/<int:timesheet_id>/edit", methods=["GET", "POST"])
def edit_timesheet(timesheet_id):
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        project_id = request.form["project_id"]
        task_id = request.form["task_id"]
        work_date = request.form["work_date"]
        hours_worked = request.form["hours_worked"]
        notes = request.form.get("notes")
        status = request.form.get("status", "draft")

        with get_cursor() as cur:
            cur.execute("SELECT project_id FROM tasks WHERE id=%s", (task_id,))
            task = cur.fetchone()

        if task is None or str(task["project_id"]) != str(project_id):
            error = "Selected task does not belong to the selected project."
            with get_cursor() as cur:
                employees, projects, tasks = _get_form_choices(cur, project_id)
            form_data = dict(request.form)
            form_data["id"] = timesheet_id
            return render_template(
                "timesheets/form.html",
                timesheet=form_data,
                employees=employees,
                projects=projects,
                tasks=tasks,
                statuses=STATUSES,
                error=error,
            )

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE timesheets
                SET employee_id=%s, project_id=%s, task_id=%s, work_date=%s,
                    hours_worked=%s, notes=%s, status=%s
                WHERE id=%s
                """,
                (employee_id, project_id, task_id, work_date, hours_worked, notes, status, timesheet_id),
            )
        return redirect(url_for("timesheets.list_timesheets"))

    with get_cursor() as cur:
        cur.execute("SELECT * FROM timesheets WHERE id=%s", (timesheet_id,))
        timesheet = cur.fetchone()
        employees, projects, tasks = _get_form_choices(cur, timesheet["project_id"] if timesheet else None)

    return render_template(
        "timesheets/form.html",
        timesheet=timesheet,
        employees=employees,
        projects=projects,
        tasks=tasks,
        statuses=STATUSES,
        error=None,
    )


@bp.route("/<int:timesheet_id>/delete", methods=["POST"])
def delete_timesheet(timesheet_id):
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM timesheets WHERE id=%s", (timesheet_id,))
    return redirect(url_for("timesheets.list_timesheets"))


@bp.route("/export.xml")
def export_xml():
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT t.id, e.full_name AS employee, p.name AS project,
                   tk.title AS task, t.work_date, t.hours_worked, t.status
            FROM timesheets t
            JOIN employees e ON e.id = t.employee_id
            JOIN projects p ON p.id = t.project_id
            JOIN tasks tk ON tk.id = t.task_id
            ORDER BY t.id
            """
        )
        rows = cur.fetchall()

    root = ET.Element("timesheets")
    for row in rows:
        entry = ET.SubElement(root, "timesheet", id=str(row["id"]))
        ET.SubElement(entry, "employee").text = row["employee"]
        ET.SubElement(entry, "project").text = row["project"]
        ET.SubElement(entry, "task").text = row["task"]
        ET.SubElement(entry, "work_date").text = row["work_date"].isoformat()
        ET.SubElement(entry, "hours_worked").text = str(row["hours_worked"])
        ET.SubElement(entry, "status").text = row["status"]

    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return Response(xml_bytes, mimetype="application/xml")
