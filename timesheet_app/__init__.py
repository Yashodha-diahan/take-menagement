from flask import Flask

from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.main import bp as main_bp
    from .routes.employees import bp as employees_bp
    from .routes.projects import bp as projects_bp
    from .routes.tasks import bp as tasks_bp
    from .routes.timesheets import bp as timesheets_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(timesheets_bp, url_prefix="/timesheets")

    return app
