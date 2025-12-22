from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Project, User, Task
from app.models.user import UserRole
from app.models.project import ProjectStatus, ProjectPriority
from app.utils.decorators import role_required
from app.utils.responses import success_response, error_response, pagination_response
from app.utils.validators import validate_required_fields

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    """
    Get all projects with pagination and filtering
    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    - status: Filter by status
    - priority: Filter by priority
    - manager_id: Filter by manager
    - search: Search by title or code
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        manager_id = request.args.get('manager_id', type=int)
        search = request.args.get('search')
        
        # Build query
        query = Project.query
        
        # Apply filters
        if status_filter:
            try:
                status = ProjectStatus[status_filter.upper()]
                query = query.filter_by(status=status)
            except KeyError:
                return error_response('Invalid status filter', None, 400)
        
        if priority_filter:
            try:
                priority = ProjectPriority[priority_filter.upper()]
                query = query.filter_by(priority=priority)
            except KeyError:
                return error_response('Invalid priority filter', None, 400)
        
        if manager_id:
            query = query.filter_by(manager_id=manager_id)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Project.title.ilike(search_pattern),
                    Project.code.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Project.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        projects = [project.to_dict() for project in pagination.items]
        
        return pagination_response(
            projects,
            page,
            per_page,
            pagination.total,
            'Projects retrieved successfully'
        )
    
    except Exception as e:
        return error_response(f'Failed to get projects: {str(e)}', None, 500)


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project by ID with tasks"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        project_data = project.to_dict(include_tasks=True)
        
        # Attach manager details
        if project.manager_id:
            manager = User.query.get(project.manager_id)
            if manager:
                project_data['manager'] = manager.to_dict()
        
        return success_response(
            'Project retrieved successfully',
            {'project': project_data},
            200
        )
    
    except Exception as e:
        return error_response(f'Failed to get project: {str(e)}', None, 500)


@projects_bp.route('/', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def create_project(current_user):
    """
    Create a new project
    Body:
    {
        "title": "Project Title",
        "description": "Project description",
        "status": "planning",
        "priority": "high",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "budget": 100000.0,
        "estimated_hours": 500,
        "manager_id": 2
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title']
        is_valid, missing_fields = validate_required_fields(data, required_fields)
        
        if not is_valid:
            return error_response(
                'Missing required fields',
                {'missing_fields': missing_fields},
                400
            )
        
        # Parse status
        status = ProjectStatus.PLANNING
        if 'status' in data:
            try:
                status = ProjectStatus[data['status'].upper()]
            except KeyError:
                return error_response('Invalid status', None, 400)
        
        # Parse priority
        priority = ProjectPriority.MEDIUM
        if 'priority' in data:
            try:
                priority = ProjectPriority[data['priority'].upper()]
            except KeyError:
                return error_response('Invalid priority', None, 400)
        
        # Parse dates
        start_date = None
        end_date = None
        
        if 'start_date' in data and data['start_date']:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid start_date format. Use YYYY-MM-DD', None, 400)
        
        if 'end_date' in data and data['end_date']:
            try:
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid end_date format. Use YYYY-MM-DD', None, 400)
        
        # Validate dates
        if start_date and end_date and start_date > end_date:
            return error_response('Start date cannot be after end date', None, 400)
        
        # Validate manager if provided
        manager_id = data.get('manager_id')
        if manager_id:
            manager = User.query.get(manager_id)
            if not manager:
                return error_response('Manager not found', None, 404)
            if manager.role not in [UserRole.ADMIN, UserRole.TEAM_LEADER]:
                return error_response('Selected user is not a team leader', None, 400)
        
        # Generate project code
        project_code = Project.generate_project_code()
        
        # Create project
        project = Project(
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            code=project_code,
            status=status,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            budget=data.get('budget'),
            estimated_hours=data.get('estimated_hours'),
            created_by=current_user.id,
            manager_id=manager_id or current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        return success_response(
            'Project created successfully',
            {'project': project.to_dict()},
            201
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create project: {str(e)}', None, 500)


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def update_project(project_id, current_user):
    """Update project details"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        # Check permissions (only team leader or admin can update)
        if current_user.role != UserRole.ADMIN and project.manager_id != current_user.id:
            return error_response('You do not have permission to update this project', None, 403)
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            project.title = data['title'].strip()
        
        if 'description' in data:
            project.description = data['description'].strip()
        
        if 'status' in data:
            try:
                project.status = ProjectStatus[data['status'].upper()]
                
                # Set actual_end_date when completed
                if project.status == ProjectStatus.COMPLETED and not project.actual_end_date:
                    project.actual_end_date = datetime.utcnow().date()
            except KeyError:
                return error_response('Invalid status', None, 400)
        
        if 'priority' in data:
            try:
                project.priority = ProjectPriority[data['priority'].upper()]
            except KeyError:
                return error_response('Invalid priority', None, 400)
        
        if 'start_date' in data:
            try:
                project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid start_date format', None, 400)
        
        if 'end_date' in data:
            try:
                project.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid end_date format', None, 400)
        
        if 'budget' in data:
            project.budget = data['budget']
        
        if 'estimated_hours' in data:
            project.estimated_hours = data['estimated_hours']
        
        if 'manager_id' in data:
            manager = User.query.get(data['manager_id'])
            if not manager:
                return error_response('Manager not found', None, 404)
            if manager.role not in [UserRole.ADMIN, UserRole.TEAM_LEADER]:
                return error_response('Selected user is not a team leader', None, 400)
            project.manager_id = data['manager_id']
        
        db.session.commit()
        
        return success_response(
            'Project updated successfully',
            {'project': project.to_dict()},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update project: {str(e)}', None, 500)


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_project(project_id, current_user):
    """Delete project (Admin only)"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        # Check if project has tasks
        task_count = project.tasks.count()
        if task_count > 0:
            return error_response(
                f'Cannot delete project with {task_count} tasks. Archive it instead.',
                None,
                400
            )
        
        db.session.delete(project)
        db.session.commit()
        
        return success_response('Project deleted successfully', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete project: {str(e)}', None, 500)


@projects_bp.route('/<int:project_id>/archive', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def archive_project(project_id, current_user):
    """Archive a project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        # Check permissions
        if current_user.role != UserRole.ADMIN and project.manager_id != current_user.id:
            return error_response('You do not have permission to archive this project', None, 403)
        
        project.status = ProjectStatus.ARCHIVED
        db.session.commit()
        
        return success_response('Project archived successfully', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to archive project: {str(e)}', None, 500)


@projects_bp.route('/<int:project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """
    Get project statistics and analytics
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        # Get task statistics
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter_by(status='completed').count()
        in_progress_tasks = project.tasks.filter_by(status='in_progress').count()
        todo_tasks = project.tasks.filter_by(status='todo').count()
        blocked_tasks = project.tasks.filter_by(status='blocked').count()
        
        # Calculate total hours
        total_estimated_hours = db.session.query(
            db.func.sum(Task.estimated_hours)
        ).filter(Task.project_id == project_id).scalar() or 0
        
        total_actual_hours = db.session.query(
            db.func.sum(Task.actual_hours)
        ).filter(Task.project_id == project_id).scalar() or 0
        
        # Get team members (unique users assigned to tasks)
        from app.models import Assignment
        team_members = db.session.query(User).join(Assignment).join(Task).filter(
            Task.project_id == project_id
        ).distinct().all()
        
        stats = {
            'project': project.to_dict(),
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'todo': todo_tasks,
                'blocked': blocked_tasks,
                'completion_percentage': project.completion_percentage
            },
            'hours': {
                'estimated': total_estimated_hours,
                'actual': total_actual_hours,
                'remaining': max(0, total_estimated_hours - total_actual_hours),
                'variance': total_actual_hours - total_estimated_hours
            },
            'team': {
                'size': len(team_members),
                'members': [member.to_dict() for member in team_members]
            },
            'timeline': {
                'is_overdue': project.is_overdue,
                'days_remaining': project.days_remaining
            }
        }
        
        return success_response('Project stats retrieved successfully', stats, 200)
    
    except Exception as e:
        return error_response(f'Failed to get project stats: {str(e)}', None, 500)


@projects_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get dashboard overview with project statistics
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Get projects based on role
        if current_user.role == UserRole.ADMIN:
            projects = Project.query.all()
        elif current_user.role == UserRole.TEAM_LEADER:
            projects = Project.query.filter_by(manager_id=current_user_id).all()
        else:
            # Get projects where user has assigned tasks
            from app.models import Assignment
            project_ids = db.session.query(Task.project_id).join(Assignment).filter(
                Assignment.user_id == current_user_id
            ).distinct().all()
            project_ids = [pid[0] for pid in project_ids]
            projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        # Calculate statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == ProjectStatus.IN_PROGRESS])
        completed_projects = len([p for p in projects if p.status == ProjectStatus.COMPLETED])
        overdue_projects = len([p for p in projects if p.is_overdue])
        
        dashboard_data = {
            'summary': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'overdue_projects': overdue_projects
            },
            'projects': [project.to_dict() for project in projects[:5]],  # Top 5 recent
            'user': current_user.to_dict()
        }
        
        return success_response('Dashboard data retrieved successfully', dashboard_data, 200)
    
    except Exception as e:
        return error_response(f'Failed to get dashboard: {str(e)}', None, 500)