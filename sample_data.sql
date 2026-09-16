-- Time Sheet Management System - Sample Data
-- Run after schema.sql

INSERT INTO employees (full_name, email, phone, role, status) VALUES
    ('Yashod Dishan', 'yashod@example.com', '0771234567', 'Developer', 'active'),
    ('Nimal Perera', 'nimal@example.com', '0779876543', 'Project Manager', 'active'),
    ('Kamal Silva', 'kamal@example.com', '0712223344', 'QA Engineer', 'inactive');

INSERT INTO projects (name, client, start_date, end_date, status, description) VALUES
    ('Time Sheet Management', 'Internal', '2026-09-01', NULL, 'active', 'Web based time sheet management system'),
    ('Inventory Portal', 'Acme Corp', '2026-06-01', '2026-08-31', 'archived', 'Stock tracking web portal');

INSERT INTO tasks (title, project_id, employee_id, estimated_hours, status, notes) VALUES
    ('Build employee form', 1, 1, 6.0, 'in_progress', 'Employee CRUD screen'),
    ('Design PostgreSQL schema', 1, 1, 4.0, 'done', 'Tables, keys, indexes'),
    ('Set up project dropdown', 1, 2, 3.0, 'open', 'Filter active projects'),
    ('Fix stock report bug', 2, 3, 2.0, 'done', 'Closed project task, kept for history');

INSERT INTO timesheets (employee_id, project_id, task_id, work_date, hours_worked, notes, status) VALUES
    (1, 1, 2, '2026-09-15', 4.0, 'Wrote schema.sql with constraints and indexes', 'submitted'),
    (1, 1, 1, '2026-09-16', 3.5, 'Started employee form markup', 'draft'),
    (2, 1, 3, '2026-09-16', 1.5, 'Reviewed dropdown requirements', 'draft');
