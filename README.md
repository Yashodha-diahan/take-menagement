# Time Sheet Management System

A web application for managing employees, projects, tasks, and employee time sheets. Built with Python (Flask), PostgreSQL, HTML, and CSS.

## Requirements

- Python 3.10+
- PostgreSQL 13+ (tested on PostgreSQL 17)

## 1. Set up the Python environment

```bash
pip install -r requirements.txt
```

## 2. Create the PostgreSQL database

Create a database named `timesheet_db` (or any name you like — you'll set it in `.env`):

```bash
createdb -U postgres timesheet_db
```

If `createdb` isn't on your PATH, use `psql` directly instead:

```bash
psql -U postgres -c "CREATE DATABASE timesheet_db;"
```

## 3. Import the schema and sample data

```bash
psql -U postgres -d timesheet_db -f schema.sql
psql -U postgres -d timesheet_db -f sample_data.sql
```

`schema.sql` creates the four tables (`employees`, `projects`, `tasks`, `timesheets`) with primary/foreign keys, status/hours validation checks, and indexes on the timesheet lookup columns (employee, project, task, work date). `sample_data.sql` inserts a few example rows into each table so the app has data to show immediately.

## 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your actual PostgreSQL credentials:

```bash
cp .env.example .env
```

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=timesheet_db
DB_USER=postgres
DB_PASSWORD=your_password_here
FLASK_SECRET_KEY=change-this-to-something-random
```

The app reads these via `python-dotenv` — no credentials are hard-coded anywhere in the source.

## 5. Run the application

```bash
python run.py
```

The app starts at **http://localhost:5000**.

## Using the app

| Page | URL |
|---|---|
| Dashboard | `/` |
| Employees | `/employees/` |
| Projects | `/projects/` |
| Tasks | `/tasks/` |
| Time Sheet Entries (main screen) | `/timesheets/` |
| New time sheet entry | `/timesheets/new` |

Each module (Employees, Projects, Tasks, Time Sheets) supports create, list/filter, update, and delete (or deactivate/archive for Employees/Projects).

The main **Time Sheet Entry** screen (`/timesheets/new`) requires selecting an employee, then a project, then a task — the task dropdown is filtered live (via AJAX) to only show tasks belonging to the selected project, so an entry can never be saved against a mismatched task/project pair.

## XML export

All time sheet entries can be exported as XML at:

```
GET /timesheets/export.xml
```

Each `<timesheet>` element includes the linked employee, project, task, work date, hours worked, and status, e.g.:

```xml
<timesheets>
  <timesheet id="1">
    <employee>Yashod Dishan</employee>
    <project>Time Sheet Management</project>
    <task>Design PostgreSQL schema</task>
    <work_date>2026-09-15</work_date>
    <hours_worked>4.00</hours_worked>
    <status>submitted</status>
  </timesheet>
</timesheets>
```

An "Export as XML" link is also available on the Time Sheet list page.

## Project structure

```
schema.sql               PostgreSQL schema (tables, keys, indexes)
sample_data.sql          Sample rows for all four tables
requirements.txt         Python dependencies
.env.example             Environment variable template
run.py                   Application entry point
timesheet_app/
    __init__.py           Flask app factory, blueprint registration
    config.py             Loads DB/secret config from environment variables
    db.py                 PostgreSQL connection helper (psycopg2)
    routes/
        main.py             Dashboard
        employees.py        Employee CRUD
        projects.py         Project CRUD
        tasks.py            Task CRUD (linked to a project and employee)
        timesheets.py        Time sheet CRUD, cascading task lookup, XML export
    templates/            Jinja2 HTML templates
    static/css/           Stylesheet
```
