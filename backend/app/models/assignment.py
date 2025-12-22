from app import db
from app.models import TimestampMixin
from enum import Enum

class AssignmentStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Assignment(db.Model, TimestampMixin):
    __tablename__ = 'assignments'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Assignment Details
    assigned_hours = db.Column(db.Integer, nullable=False)  # Hours allocated for this task
    actual_hours = db.Column(db.Integer, default=0)         # Hours actually worked
    status = db.Column(db.Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.PENDING)
    
    # Notes
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    assigner = db.relationship('User', foreign_keys=[assigned_by], backref='tasks_assigned_by_me')
    
    # Unique constraint: One user can be assigned to a task only once
    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', name='unique_user_task_assignment'),
    )
    
    def __repr__(self):
        return f'<Assignment: User {self.user_id} -> Task {self.task_id}>'
    
    @property
    def hours_remaining(self):
        """Calculate remaining hours"""
        return max(0, self.assigned_hours - self.actual_hours)
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.assigned_hours == 0:
            return 0
        return min(100, round((self.actual_hours / self.assigned_hours) * 100, 2))
    
    @property
    def is_overallocated(self):
        """Check if actual hours exceed assigned hours"""
        return self.actual_hours > self.assigned_hours
    
    def to_dict(self, include_user=False, include_task=False):
        """Convert assignment to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'assigned_by': self.assigned_by,
            'assigned_hours': self.assigned_hours,
            'actual_hours': self.actual_hours,
            'hours_remaining': self.hours_remaining,
            'completion_percentage': self.completion_percentage,
            'is_overallocated': self.is_overallocated,
            'status': self.status.value,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        
        if include_task and self.task:
            data['task'] = self.task.to_dict()
        
        return data
    
    @staticmethod
    def get_user_workload(user_id, start_date=None, end_date=None):
        """
        Calculate total workload for a user within a date range
        Returns total assigned hours
        """
        from app.models.task import Task, TaskStatus
        
        query = Assignment.query.join(Task).filter(
            Assignment.user_id == user_id,
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW])
        )
        
        if start_date:
            query = query.filter(Task.start_date >= start_date)
        if end_date:
            query = query.filter(Task.due_date <= end_date)
        
        assignments = query.all()
        total_hours = sum([a.assigned_hours for a in assignments])
        
        return total_hours
    
    @staticmethod
    def get_available_users(required_hours, start_date=None, end_date=None):
        """
        Find users who have capacity for the required hours
        """
        from app.models.user import User
        
        available_users = []
        users = User.query.filter_by(is_active=True).all()
        
        for user in users:
            current_workload = Assignment.get_user_workload(user.id, start_date, end_date)
            available_capacity = user.weekly_capacity - current_workload
            
            if available_capacity >= required_hours:
                available_users.append({
                    'user': user.to_dict(),
                    'available_hours': available_capacity,
                    'current_workload': current_workload
                })
        
        return available_users