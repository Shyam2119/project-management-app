from app import db, bcrypt
from app.models import TimestampMixin

class Company(db.Model, TimestampMixin):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subscription_status = db.Column(db.String(20), default='active')
    
    # Company-wide authentication credentials
    company_email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    company_password_hash = db.Column(db.String(255), nullable=True)
    company_login_enabled = db.Column(db.Boolean, default=False)  # Enable/disable company login
    
    # Relationships
    users = db.relationship('User', backref='company', lazy='dynamic')
    projects = db.relationship('Project', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def set_company_password(self, password):
        """Hash and set company password"""
        if password:
            self.company_password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        else:
            self.company_password_hash = None
    
    def check_company_password(self, password):
        """Check if password matches company password hash"""
        if not self.company_password_hash or not password:
            return False
        return bcrypt.check_password_hash(self.company_password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert company to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'subscription_status': self.subscription_status,
            'company_email': self.company_email,
            'company_login_enabled': self.company_login_enabled,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at) if self.updated_at else None
        }
        
        if include_sensitive:
            data['company_password_hash'] = self.company_password_hash
        
        return data
    
    @staticmethod
    def find_by_company_email(email):
        """Find company by company email"""
        return Company.query.filter_by(company_email=email).first()
