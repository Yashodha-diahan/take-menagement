from flask import Blueprint, redirect, render_template, request, url_for

from ..db import get_cursor

bp = Blueprint("employees", __name__)


@bp.route("/")
def list_employees():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, full_name, email, phone, role, status FROM employees ORDER BY id"
        )
        employees = cur.fetchall()
    return render_template("employees/list.html", employees=employees)


@bp.route("/new", methods=["GET", "POST"])
def new_employee():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form.get("phone")
        role = request.form.get("role")
        status = request.form.get("status", "active")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO employees (full_name, email, phone, role, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (full_name, email, phone, role, status),
            )
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/form.html", employee=None)


@bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form.get("phone")
        role = request.form.get("role")
        status = request.form.get("status", "active")

        with get_cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE employees
                SET full_name=%s, email=%s, phone=%s, role=%s, status=%s
                WHERE id=%s
                """,
                (full_name, email, phone, role, status, employee_id),
            )
        return redirect(url_for("employees.list_employees"))

    with get_cursor() as cur:
        cur.execute("SELECT * FROM employees WHERE id=%s", (employee_id,))
        employee = cur.fetchone()
    return render_template("employees/form.html", employee=employee)


@bp.route("/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE employees SET status='inactive' WHERE id=%s", (employee_id,)
        )
    return redirect(url_for("employees.list_employees"))
