from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import Task, Project, Assignment, User
from app.models.user import UserRole
from app.models.task import TaskStatus, TaskPriority
from app.models.project import ProjectStatus
from app.utils.decorators import role_required
from app.utils.responses import success_response, error_response

bulk_bp = Blueprint('bulk', __name__)


@bulk_bp.route('/tasks/update-status', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def bulk_update_task_status(current_user):
    """
    Update status for multiple tasks
    Body:
    {
        "task_ids": [1, 2, 3],
        "status": "completed"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'task_ids' not in data or 'status' not in data:
            return error_response('task_ids and status are required', None, 400)
        
        task_ids = data['task_ids']
        if not isinstance(task_ids, list) or not task_ids:
            return error_response('task_ids must be a non-empty list', None, 400)
        
        # Validate status
        try:
            new_status = TaskStatus[data['status'].upper()]
        except KeyError:
            return error_response('Invalid status', None, 400)
        
        # Get tasks
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        if not tasks:
            return error_response('No tasks found', None, 404)
        
        # Check permissions for each task
        updated_count = 0
        for task in tasks:
            project = Project.query.get(task.project_id)
            if current_user.role == UserRole.ADMIN or project.manager_id == current_user.id:
                task.status = new_status
                updated_count += 1
        
        db.session.commit()
        
        return success_response(
            f'Successfully updated {updated_count} tasks',
            {'updated': updated_count, 'total': len(task_ids)},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update tasks: {str(e)}', None, 500)


@bulk_bp.route('/tasks/update-priority', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def bulk_update_task_priority(current_user):
    """
    Update priority for multiple tasks
    Body:
    {
        "task_ids": [1, 2, 3],
        "priority": "high"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'task_ids' not in data or 'priority' not in data:
            return error_response('task_ids and priority are required', None, 400)
        
        task_ids = data['task_ids']
        
        # Validate priority
        try:
            new_priority = TaskPriority[data['priority'].upper()]
        except KeyError:
            return error_response('Invalid priority', None, 400)
        
        # Get and update tasks
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        updated_count = 0
        for task in tasks:
            project = Project.query.get(task.project_id)
            if current_user.role == UserRole.ADMIN or project.manager_id == current_user.id:
                task.priority = new_priority
                updated_count += 1
        
        db.session.commit()
        
        return success_response(
            f'Successfully updated {updated_count} tasks',
            {'updated': updated_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update tasks: {str(e)}', None, 500)


@bulk_bp.route('/tasks/assign', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def bulk_assign_tasks(current_user):
    """
    Assign multiple tasks to a user
    Body:
    {
        "task_ids": [1, 2, 3],
        "user_id": 5,
        "assigned_hours_per_task": 8
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'task_ids' not in data or 'user_id' not in data:
            return error_response('task_ids and user_id are required', None, 400)
        
        task_ids = data['task_ids']
        user_id = data['user_id']
        hours_per_task = data.get('assigned_hours_per_task', 8)
        
        # Validate user
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', None, 404)
        
        # Check user workload
        current_workload = Assignment.get_user_workload(user_id)
        total_new_hours = len(task_ids) * hours_per_task
        
        if current_workload + total_new_hours > user.weekly_capacity:
            return error_response(
                'User will be overloaded',
                {
                    'current_workload': current_workload,
                    'new_hours': total_new_hours,
                    'capacity': user.weekly_capacity
                },
                400
            )
        
        # Assign tasks
        assigned_count = 0
        skipped = []
        
        for task_id in task_ids:
            # Check if already assigned
            existing = Assignment.query.filter_by(
                task_id=task_id,
                user_id=user_id
            ).first()
            
            if existing:
                skipped.append(task_id)
                continue
            
            assignment = Assignment(
                task_id=task_id,
                user_id=user_id,
                assigned_by=current_user.id,
                assigned_hours=hours_per_task,
                status='pending'
            )
            db.session.add(assignment)
            assigned_count += 1
        
        db.session.commit()
        
        return success_response(
            f'Successfully assigned {assigned_count} tasks',
            {'assigned': assigned_count, 'skipped': len(skipped)},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to assign tasks: {str(e)}', None, 500)


@bulk_bp.route('/tasks/delete', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def bulk_delete_tasks(current_user):
    """
    Delete multiple tasks (Admin only)
    Body:
    {
        "task_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'task_ids' not in data:
            return error_response('task_ids is required', None, 400)
        
        task_ids = data['task_ids']
        
        # Check for dependent tasks
        dependent_count = Task.query.filter(Task.depends_on.in_(task_ids)).count()
        if dependent_count > 0:
            return error_response(
                f'Cannot delete tasks with {dependent_count} dependent tasks',
                None,
                400
            )
        
        # Delete tasks
        deleted_count = Task.query.filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        return success_response(
            f'Successfully deleted {deleted_count} tasks',
            {'deleted': deleted_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete tasks: {str(e)}', None, 500)


@bulk_bp.route('/projects/update-status', methods=['PUT'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def bulk_update_project_status(current_user):
    """
    Update status for multiple projects
    Body:
    {
        "project_ids": [1, 2, 3],
        "status": "completed"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'project_ids' not in data or 'status' not in data:
            return error_response('project_ids and status are required', None, 400)
        
        project_ids = data['project_ids']
        
        # Validate status
        try:
            new_status = ProjectStatus[data['status'].upper()]
        except KeyError:
            return error_response('Invalid status', None, 400)
        
        # Get and update projects
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
        
        updated_count = 0
        for project in projects:
            if current_user.role == UserRole.ADMIN or project.manager_id == current_user.id:
                project.status = new_status
                updated_count += 1
        
        db.session.commit()
        
        return success_response(
            f'Successfully updated {updated_count} projects',
            {'updated': updated_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update projects: {str(e)}', None, 500)


@bulk_bp.route('/users/activate', methods=['PUT'])
@role_required(UserRole.ADMIN)
def bulk_activate_users(current_user):
    """
    Activate multiple users (Admin only)
    Body:
    {
        "user_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_ids' not in data:
            return error_response('user_ids is required', None, 400)
        
        user_ids = data['user_ids']
        
        # Update users
        updated_count = User.query.filter(User.id.in_(user_ids)).update(
            {'is_active': True},
            synchronize_session=False
        )
        
        db.session.commit()
        
        return success_response(
            f'Successfully activated {updated_count} users',
            {'activated': updated_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to activate users: {str(e)}', None, 500)


@bulk_bp.route('/users/deactivate', methods=['PUT'])
@role_required(UserRole.ADMIN)
def bulk_deactivate_users(current_user):
    """
    Deactivate multiple users (Admin only)
    Body:
    {
        "user_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_ids' not in data:
            return error_response('user_ids is required', None, 400)
        
        user_ids = data['user_ids']
        
        # Prevent deactivating yourself
        if current_user.id in user_ids:
            return error_response('You cannot deactivate your own account', None, 400)
        
        # Update users
        updated_count = User.query.filter(User.id.in_(user_ids)).update(
            {'is_active': False},
            synchronize_session=False
        )
        
        db.session.commit()
        
        return success_response(
            f'Successfully deactivated {updated_count} users',
            {'deactivated': updated_count},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to deactivate users: {str(e)}', None, 500)