-- Time Sheet Management System - PostgreSQL Schema

CREATE TABLE employees (
    id            SERIAL PRIMARY KEY,
    full_name     VARCHAR(150) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    phone         VARCHAR(30),
    role          VARCHAR(100),
    status        VARCHAR(20) NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active', 'inactive'))
);

CREATE TABLE projects (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    client        VARCHAR(150),
    start_date    DATE,
    end_date      DATE,
    status        VARCHAR(20) NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active', 'archived')),
    description   TEXT
);

CREATE TABLE tasks (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(150) NOT NULL,
    project_id       INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    employee_id      INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    estimated_hours  NUMERIC(6,2) CHECK (estimated_hours >= 0),
    status           VARCHAR(20) NOT NULL DEFAULT 'open'
                     CHECK (status IN ('open', 'in_progress', 'done', 'cancelled')),
    notes            TEXT
);

CREATE TABLE timesheets (
    id             SERIAL PRIMARY KEY,
    employee_id    INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    project_id     INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id        INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    work_date      DATE NOT NULL,
    hours_worked   NUMERIC(5,2) NOT NULL CHECK (hours_worked >= 0),
    notes          TEXT,
    status         VARCHAR(20) NOT NULL DEFAULT 'draft'
                   CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    created_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for time-sheet lookups
CREATE INDEX idx_timesheets_employee   ON timesheets(employee_id);
CREATE INDEX idx_timesheets_project    ON timesheets(project_id);
CREATE INDEX idx_timesheets_task       ON timesheets(task_id);
CREATE INDEX idx_timesheets_work_date  ON timesheets(work_date);

-- Helpful index for filtering tasks by project (used by the task dropdown)
CREATE INDEX idx_tasks_project ON tasks(project_id);
