from datetime import datetime
from app import db

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

# Import all models here for easy access
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.assignment import Assignment
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.chat import ChatGroup, GroupMember, Message

__all__ = ['User', 'Project', 'Task', 'Assignment', 'Comment', 'Notification', 'ChatGroup', 'GroupMember', 'Message']