from app import db, bcrypt
from app.models import TimestampMixin
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TEAM_LEADER = "teamleader"
    EMPLOYEE = "employee"

class User(db.Model, TimestampMixin):
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True) # URL to uploaded image
    role = db.Column(db.String(20), nullable=False, default="employee")
    
    # Skills & Capacity
    skills = db.Column(db.Text, nullable=True)  # JSON string of skills array
    weekly_capacity = db.Column(db.Integer, default=40)  # Hours per week
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_bot = db.Column(db.Boolean, default=False)
    
    # Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    
    # Relationships
    created_projects = db.relationship('Project', backref='creator', lazy='dynamic', foreign_keys='Project.created_by')
    managed_projects = db.relationship('Project', backref='manager', lazy='dynamic', foreign_keys='Project.manager_id')
    assignments = db.relationship('Assignment', backref='user', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Assignment.user_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'skills': self.skills,
            'weekly_capacity': self.weekly_capacity,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_bot': self.is_bot,
            'email_notifications': self.email_notifications,
            'push_notifications': self.push_notifications,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at) if self.updated_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return User.query.get(user_id)