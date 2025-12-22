from app import create_app, db
from app.models import User, Project, Task, Assignment, Comment

app = create_app('development')

with app.app_context():
    print("=" * 50)
    print("DATABASE VERIFICATION")
    print("=" * 50)
    
    # Count records
    user_count = User.query.count()
    project_count = Project.query.count()
    task_count = Task.query.count()
    assignment_count = Assignment.query.count()
    comment_count = Comment.query.count()
    
    print(f"\n📊 Record Counts:")
    print(f"   Users: {user_count}")
    print(f"   Projects: {project_count}")
    print(f"   Tasks: {task_count}")
    print(f"   Assignments: {assignment_count}")
    print(f"   Comments: {comment_count}")
    
    # Test user authentication
    print(f"\n🔐 Testing Authentication:")
    admin = User.find_by_email('admin@company.com')
    if admin:
        password_match = admin.check_password('admin123')
        print(f"   Admin login test: {'✅ PASS' if password_match else '❌ FAIL'}")
        print(f"   Admin name: {admin.full_name}")
        print(f"   Admin role: {admin.role.value}")
    
    # Test project relationships
    print(f"\n📁 Testing Relationships:")
    first_project = Project.query.first()
    if first_project:
        print(f"   Project: {first_project.title}")
        print(f"   Code: {first_project.code}")
        print(f"   Tasks: {first_project.tasks.count()}")
        print(f"   Completion: {first_project.completion_percentage}%")
        print(f"   Manager: {first_project.manager.full_name if first_project.manager else 'None'}")
    
    # Test task assignments
    print(f"\n👥 Testing Assignments:")
    first_task = Task.query.first()
    if first_task:
        print(f"   Task: {first_task.title}")
        print(f"   Task Number: {first_task.task_number}")
        print(f"   Assigned to: {len(first_task.assigned_users)} user(s)")
        for user in first_task.assigned_users:
            print(f"      - {user.full_name}")
    
    # Test bandwidth calculation
    print(f"\n⚡ Testing Bandwidth Calculation:")
    employee = User.query.filter_by(role='employee').first()
    if employee:
        workload = Assignment.get_user_workload(employee.id)
        print(f"   Employee: {employee.full_name}")
        print(f"   Weekly Capacity: {employee.weekly_capacity}h")
        print(f"   Current Workload: {workload}h")
        print(f"   Available: {employee.weekly_capacity - workload}h")
    
    print(f"\n{'=' * 50}")
    print("✅ All tests completed!")
    print("=" * 50)