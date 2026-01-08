from app import create_app, db
# Import all models to ensure they're registered with SQLAlchemy
from app.models import (
    Company, User, Project, Task, Assignment, Comment, 
    Notification, ActivityLog, ChatGroup, GroupMember, Message
)
from app.models.user import UserRole

app = create_app('development')

with app.app_context():
    # Drop all tables to ensure clean slate for schema changes
    print("Dropping all tables for fresh schema...")
    db.drop_all()
    
    print("Creating database tables...")
    db.create_all()
    print("Tables created.")

    # Create Default Company
    company = Company.query.filter_by(name='Demo Company').first()
    if not company:
        print("Creating default company...")
        company = Company(name='Demo Company')
        db.session.add(company)
        db.session.flush()

    # Check for admin
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        print("Creating default admin user...")
        admin = User(
            email='admin@example.com',
            first_name='System',
            last_name='Admin',
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            company_id=company.id
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created: admin@example.com / admin123 (Company: {company.name})")
    else:
        print("Admin user already exists.")
