from app import db
from app.models import TimestampMixin
from enum import Enum

class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    COMMENT_ADDED = "comment_added"
    COMMENT_MENTION = "comment_mention"
    PROJECT_UPDATE = "project_update"
    DEADLINE_APPROACHING = "deadline_approaching"
    WORKLOAD_WARNING = "workload_warning"

class Notification(db.Model, TimestampMixin):
    __tablename__ = 'notifications'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Recipient
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification Details
    type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Related Entities (optional references)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])
    task = db.relationship('Task', backref='notifications', foreign_keys=[task_id])
    project = db.relationship('Project', backref='notifications', foreign_keys=[project_id])
    comment = db.relationship('Comment', backref='notifications', foreign_keys=[comment_id])
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type.value}>'
    
    def to_dict(self):
        """Convert notification to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'task_id': self.task_id,
            'project_id': self.project_id,
            'comment_id': self.comment_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_notification(user_id, notification_type, title, message, task_id=None, project_id=None, comment_id=None):
        """Helper method to create a notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            task_id=task_id,
            project_id=project_id,
            comment_id=comment_id
        )
        db.session.add(notification)
        return notification