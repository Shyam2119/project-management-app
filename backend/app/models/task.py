from app import db
from app.models import TimestampMixin
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(db.Model, TimestampMixin):
    __tablename__ = 'tasks'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    task_number = db.Column(db.String(20), nullable=False, index=True)  # e.g., PROJ-001-T001
    
    # Status & Priority
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = db.Column(db.Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    
    # Timeline
    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completed_date = db.Column(db.Date, nullable=True)
    
    # Effort Estimation
    estimated_hours = db.Column(db.Integer, nullable=True)  # Estimated effort
    actual_hours = db.Column(db.Integer, nullable=True)     # Actual time spent
    
    # Dependencies
    depends_on = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # Parent task
    
    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    
    def __repr__(self):
        return f'<Task {self.task_number}: {self.title}>'
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in [TaskStatus.COMPLETED]:
            return datetime.utcnow().date() > self.due_date
        return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining until deadline"""
        if self.due_date:
            delta = self.due_date - datetime.utcnow().date()
            return delta.days
        return None
    
    @property
    def assigned_users(self):
        """Get list of assigned users"""
        return [assignment.user for assignment in self.assignments.all()]
    
    @property
    def total_assigned_hours(self):
        """Calculate total hours assigned"""
        return sum([assignment.assigned_hours for assignment in self.assignments.all()])
    
    def to_dict(self, include_assignments=False, include_comments=False):
        """Convert task to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'task_number': self.task_number,
            'status': self.status.value,
            'priority': self.priority.value,
            'start_date': self.start_date.isoformat() if hasattr(self.start_date, 'isoformat') else str(self.start_date) if self.start_date else None,
            'due_date': self.due_date.isoformat() if hasattr(self.due_date, 'isoformat') else str(self.due_date) if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if hasattr(self.completed_date, 'isoformat') else str(self.completed_date) if self.completed_date else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'depends_on': self.depends_on,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'is_overdue': self.is_overdue,
            'days_remaining': self.days_remaining,
            'total_assigned_hours': self.total_assigned_hours,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at) if self.updated_at else None
        }
        
        if include_assignments:
            data['assignments'] = [assignment.to_dict() for assignment in self.assignments.all()]
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.comments.all()]
        
        return data
    
    @staticmethod
    def generate_task_number(project_code):
        """Generate unique task number for a project"""
        from app.models.project import Project
        
        last_task = Task.query.join(Project).filter(
            Project.code == project_code
        ).order_by(Task.id.desc()).first()
        
        if last_task:
            last_number = int(last_task.task_number.split('-')[-1][1:])
            return f"{project_code}-T{last_number + 1:03d}"
        return f"{project_code}-T001"