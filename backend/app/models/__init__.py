from datetime import datetime
from app import db

class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

# Import all models here for easy access
# This ensures all models are registered with SQLAlchemy when db.create_all() is called
from app.models.company import Company
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.assignment import Assignment
from app.models.comment import Comment
from app.models.notification import Notification
from app.models.activity_log import ActivityLog
from app.models.chat import ChatGroup, GroupMember, Message

__all__ = ['Company', 'User', 'Project', 'Task', 'Assignment', 'Comment', 'Notification', 'ActivityLog', 'ChatGroup', 'GroupMember', 'Message']