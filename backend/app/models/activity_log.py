from app import db
from app.models import TimestampMixin
from enum import Enum

class ActivityType(str, Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_ASSIGNED = "task_assigned"
    COMMENT_ADDED = "comment_added"
    PASSWORD_CHANGED = "password_changed"

class ActivityLog(db.Model, TimestampMixin):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.Enum(ActivityType), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Related entities
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='activities')
    project = db.relationship('Project', backref='activity_logs')
    task = db.relationship('Task', backref='activity_logs')
    
    def __repr__(self):
        return f'<ActivityLog {self.id}: {self.activity_type.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'activity_type': self.activity_type.value,
            'description': self.description,
            'ip_address': self.ip_address,
            'project_id': self.project_id,
            'task_id': self.task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def log_activity(user_id, activity_type, description, request=None, 
                     project_id=None, task_id=None):
        """Helper method to log an activity"""
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')[:255]
        
        activity = ActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            project_id=project_id,
            task_id=task_id
        )
        db.session.add(activity)
        return activity