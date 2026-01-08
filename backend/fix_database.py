"""
Database Fix Script
This script will recreate the database with the correct schema.
WARNING: This will delete all existing data!
"""
import os
import sys

# Ensure backend imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
# Import all models to ensure they're registered with SQLAlchemy
from app.models import (
    Company, User, Project, Task, Assignment, 
    Comment, Notification, ActivityLog, ChatGroup, GroupMember, Message
)
from app.models.user import UserRole

def fix_database():
    """Recreate database with correct schema"""
    print("=" * 60)
    print("DATABASE FIX SCRIPT")
    print("=" * 60)
    
    db_file = os.path.join(os.path.dirname(__file__), 'project_management.db')
    
    # Check if database exists and is locked
    if os.path.exists(db_file):
        try:
            # Try to open it to check if it's locked
            import sqlite3
            conn = sqlite3.connect(db_file)
            conn.close()
            print(f"Found existing database: {db_file}")
            print("\n⚠️  WARNING: This will DELETE ALL existing data!")
            response = input("Continue? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print("\n❌ ERROR: Database is locked!")
                print("Please STOP the Flask server (Ctrl+C) and try again.")
                sys.exit(1)
            else:
                print(f"Error checking database: {e}")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print(f"No existing database found. Will create new one at: {db_file}")
    
    # Create app
    app = create_app('development')
    
    with app.app_context():
        print("\n1. Dropping all existing tables...")
        try:
            db.drop_all()
            print("   ✓ Tables dropped")
        except Exception as e:
            print(f"   ⚠ Warning: {e}")
        
        print("\n2. Creating new tables with correct schema...")
        try:
            db.create_all()
            print("   ✓ Tables created successfully")
        except Exception as e:
            print(f"   ✗ Error creating tables: {e}")
            sys.exit(1)
        
        # Verify schema
        print("\n3. Verifying schema...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        tables = inspector.get_table_names()
        print(f"   Found {len(tables)} tables: {', '.join(tables)}")
        
        # Check users table
        if 'users' in tables:
            users_columns = [col['name'] for col in inspector.get_columns('users')]
            required_columns = ['id', 'company_id', 'email', 'password_hash', 'first_name', 'last_name']
            missing = [col for col in required_columns if col not in users_columns]
            if missing:
                print(f"   ✗ Users table missing columns: {missing}")
                sys.exit(1)
            else:
                print("   ✓ Users table schema is correct")
        
        # Check companies table
        if 'companies' in tables:
            companies_columns = [col['name'] for col in inspector.get_columns('companies')]
            required_columns = ['id', 'name', 'company_email', 'company_password_hash', 'company_login_enabled']
            missing = [col for col in required_columns if col not in companies_columns]
            if missing:
                print(f"   ✗ Companies table missing columns: {missing}")
                sys.exit(1)
            else:
                print("   ✓ Companies table schema is correct")
        
        print("\n4. Creating default data...")
        try:
            # Create Default Company
            company = Company.query.filter_by(name='Demo Company').first()
            if not company:
                company = Company(name='Demo Company')
                db.session.add(company)
                db.session.flush()
                print("   ✓ Created default company: Demo Company")
            else:
                print("   ✓ Default company already exists")
            
            # Create Admin User
            admin = User.query.filter_by(email='admin@example.com').first()
            if not admin:
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
                print("   ✓ Created default admin: admin@example.com / admin123")
            else:
                print("   ✓ Default admin already exists")
            
        except Exception as e:
            print(f"   ✗ Error creating default data: {e}")
            db.session.rollback()
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("✅ DATABASE FIXED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("  1. Start the Flask server: python run.py")
        print("  2. Register a new company at: http://localhost:5173/admin-register")
        print("  3. Or login with default admin:")
        print("     Email: admin@example.com")
        print("     Password: admin123")
        print("\n💡 The database now has the correct schema with:")
        print("   ✓ Company support (company_id in users table)")
        print("   ✓ Company-wide login (company_email, company_password_hash)")
        print("   ✓ All other required tables and columns")
        print()

if __name__ == "__main__":
    fix_database()

