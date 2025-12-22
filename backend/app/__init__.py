from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app(config_name='development'):
    """Application factory pattern"""
    
    # CRITICAL: Disable instance folder completely
    app = Flask(__name__, 
                instance_relative_config=False,
                instance_path=None)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp
    from app.routes.analytics import analytics_bp
    from app.routes.bulk import bulk_bp
    from app.routes.notifications import notifications_bp
    from app.routes.reports import reports_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(bulk_bp, url_prefix='/api/bulk')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    from app.routes.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    from app.routes.upload import upload_bp
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    
    # Health check route
    @app.route('/')
    def health_check():
        return {
            'status': 'success',
            'message': 'Project Management API is running!',
            'version': '1.0.0'
        }
    
    @app.route('/api/health')
    def api_health():
        return {
            'status': 'healthy',
            'database': 'connected'
        }
    
    return app