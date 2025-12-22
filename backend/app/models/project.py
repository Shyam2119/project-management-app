from app import db
from app.models import TimestampMixin
from enum import Enum
from datetime import datetime

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ProjectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Project(db.Model, TimestampMixin):
    __tablename__ = 'projects'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g., PROJ-001
    
    # Status & Priority
    status = db.Column(db.Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    priority = db.Column(db.Enum(ProjectPriority), nullable=False, default=ProjectPriority.MEDIUM)
    
    # Timeline
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    actual_end_date = db.Column(db.Date, nullable=True)
    
    # Budget & Resources
    budget = db.Column(db.Float, nullable=True)
    estimated_hours = db.Column(db.Integer, nullable=True)
    
    # Ownership
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.code}: {self.title}>'
    
    @property
    def completion_percentage(self):
        """Calculate project completion based on tasks"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        
        completed_tasks = self.tasks.filter_by(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 2)
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.end_date and self.status not in [ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED]:
            return datetime.utcnow().date() > self.end_date
        return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining until deadline"""
        if self.end_date:
            delta = self.end_date - datetime.utcnow().date()
            return delta.days
        return None
    
    def to_dict(self, include_tasks=False):
        """Convert project to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'code': self.code,
            'status': self.status.value,
            'priority': self.priority.value,
            'start_date': self.start_date.isoformat() if hasattr(self.start_date, 'isoformat') else str(self.start_date) if self.start_date else None,
            'end_date': self.end_date.isoformat() if hasattr(self.end_date, 'isoformat') else str(self.end_date) if self.end_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if hasattr(self.actual_end_date, 'isoformat') else str(self.actual_end_date) if self.actual_end_date else None,
            'budget': self.budget,
            'estimated_hours': self.estimated_hours,
            'created_by': self.created_by,
            'manager_id': self.manager_id,
            'completion_percentage': self.completion_percentage,
            'is_overdue': self.is_overdue,
            'days_remaining': self.days_remaining,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at) if self.updated_at else None
        }
        
        if include_tasks:
            data['tasks'] = [task.to_dict() for task in self.tasks.all()]
        
        return data
    
    @staticmethod
    def generate_project_code():
        """Generate unique project code"""
        last_project = Project.query.order_by(Project.id.desc()).first()
        if last_project:
            last_number = int(last_project.code.split('-')[1])
            return f"PROJ-{last_number + 1:04d}"
        return "PROJ-0001"