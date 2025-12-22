# Import all blueprints here for easy registration
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.projects import projects_bp

__all__ = ['auth_bp', 'users_bp', 'projects_bp']