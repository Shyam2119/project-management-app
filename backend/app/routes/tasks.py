from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import Task, Project, User, Assignment, Comment
from app.models.user import UserRole
from app.models.task import TaskStatus, TaskPriority
from app.models.assignment import AssignmentStatus
from app.utils.decorators import role_required
from app.utils.responses import success_response, error_response, pagination_response
from app.utils.validators import validate_required_fields
from app.utils.notifications import create_notification
from app.models.notification import NotificationType, Notification

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """
    Get all tasks with pagination and filtering
    Query params:
    - page, per_page
    - project_id: Filter by project
    - status: Filter by status
    - priority: Filter by priority
    - assigned_to: Filter by assigned user ID
    - search: Search by title or description
    """
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        # Convert to int since JWT identity is stored as string but user ID is integer
        try:
            current_user = User.query.get(int(current_user_id))
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        if not current_user:
            return error_response('User not found', None, 404)
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        project_id = request.args.get('project_id', type=int)
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        assigned_to = request.args.get('assigned_to', type=int)
        search = request.args.get('search')
        
        # Build query
        query = Task.query
        
        # Role-based filtering
        if current_user.role == UserRole.EMPLOYEE:
            # Employees only see their assigned tasks
            query = query.join(Assignment).filter(Assignment.user_id == int(current_user_id))
        
        # Apply filters
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if status_filter:
            try:
                status = TaskStatus[status_filter.upper()]
                query = query.filter_by(status=status)
            except KeyError:
                return error_response('Invalid status filter', None, 400)
        
        if priority_filter:
            try:
                priority = TaskPriority[priority_filter.upper()]
                query = query.filter_by(priority=priority)
            except KeyError:
                return error_response('Invalid priority filter', None, 400)
        
        if assigned_to:
            query = query.join(Assignment).filter(Assignment.user_id == assigned_to)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                db.or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                    Task.task_number.ilike(search_pattern)
                )
            )
        
        # Order by due date and priority
        query = query.order_by(Task.due_date.asc(), Task.priority.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        tasks = [task.to_dict(include_assignments=True) for task in pagination.items]
        
        return pagination_response(
            tasks,
            page,
            per_page,
            pagination.total,
            'Tasks retrieved successfully'
        )
    
    except Exception as e:
        return error_response(f'Failed to get tasks: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get task by ID with full details"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return error_response('Task not found', None, 404)
        
        return success_response(
            'Task retrieved successfully',
            {'task': task.to_dict(include_assignments=True, include_comments=True)},
            200
        )
    
    except Exception as e:
        return error_response(f'Failed to get task: {str(e)}', None, 500)


@tasks_bp.route('/', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def create_task(current_user):
    """
    Create a new task
    Body:
    {
        "project_id": 1,
        "title": "Task Title",
        "description": "Task description",
        "status": "todo",
        "priority": "high",
        "start_date": "2024-01-01",
        "due_date": "2024-01-15",
        "estimated_hours": 20,
        "depends_on": 5  // Optional: parent task ID
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['project_id', 'title']
        error = validate_required_fields(data, required_fields)
        if error:
            return error_response(error, None, 400)
        
        # Validate project exists
        project = Project.query.get(data['project_id'])
        if not project:
            return error_response('Project not found', None, 404)
        
        # Check if user has permission for this project
        if current_user.role == UserRole.TEAM_LEADER and project.manager_id != current_user.id:
            return error_response('You do not have permission to create tasks in this project', None, 403)
        
        # Parse status
        status = TaskStatus.TODO
        if 'status' in data:
            try:
                status = TaskStatus[data['status'].upper()]
            except KeyError:
                return error_response('Invalid status', None, 400)
        
        # Parse priority
        priority = TaskPriority.MEDIUM
        if 'priority' in data:
            try:
                priority = TaskPriority[data['priority'].upper()]
            except KeyError:
                return error_response('Invalid priority', None, 400)
        
        # Parse dates
        start_date = None
        due_date = None
        
        if 'start_date' in data and data['start_date']:
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid start_date format. Use YYYY-MM-DD', None, 400)
        
        if 'due_date' in data and data['due_date']:
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid due_date format. Use YYYY-MM-DD', None, 400)
        
        # Validate dates
        if start_date and due_date and start_date > due_date:
            return error_response('Start date cannot be after due date', None, 400)
        
        # Validate dependency
        depends_on = data.get('depends_on')
        if depends_on:
            parent_task = Task.query.get(depends_on)
            if not parent_task:
                return error_response('Parent task not found', None, 404)
            if parent_task.project_id != data['project_id']:
                return error_response('Parent task must be in the same project', None, 400)
        
        # Generate task number
        task_number = Task.generate_task_number(project.code)
        
        # Create task
        task = Task(
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            task_number=task_number,
            status=status,
            priority=priority,
            start_date=start_date,
            due_date=due_date,
            estimated_hours=data.get('estimated_hours'),
            depends_on=depends_on,
            project_id=data['project_id'],
            created_by=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return success_response(
            'Task created successfully',
            {'task': task.to_dict()},
            201
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create task: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task details (Admin/Team Leader full access, Employee limited access)"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return error_response('Invalid token', None, 401)
        
        # Convert to int since JWT identity is stored as string but user ID is integer
        try:
            current_user = User.query.get(int(current_user_id))
        except (ValueError, TypeError):
            return error_response('Invalid user ID', None, 400)
        
        if not current_user:
            return error_response('User not found', None, 404)
        
        task = Task.query.get(task_id)
        
        if not task:
            return error_response('Task not found', None, 404)
        
        data = request.get_json()
        
        # Permission Logic
        is_admin = current_user.role == UserRole.ADMIN
        is_manager = current_user.role == UserRole.TEAM_LEADER
        is_assigned_employee = False
        
        if current_user.role == UserRole.EMPLOYEE:
            # Check assignment
            assignment = Assignment.query.filter_by(
                task_id=task_id,
                user_id=int(current_user_id)
            ).first()
            if assignment:
                is_assigned_employee = True
        
        # Team Leader check: must own project
        if is_manager:
            project = Project.query.get(task.project_id)
            if project.manager_id != current_user.id:
                 return error_response('You do not have permission to update this task', None, 403)

        if not (is_admin or is_manager or is_assigned_employee):
             return error_response('You do not have permission to update this task', None, 403)

        # Update fields based on role
        
        # Admin/Team Leader can update ALL fields
        if is_admin or is_manager:
            if 'title' in data: task.title = data['title'].strip()
            if 'description' in data: task.description = data['description'].strip()
            if 'status' in data:
                try:
                    new_status = TaskStatus[data['status'].upper()]
                    task.status = new_status
                    if new_status == TaskStatus.COMPLETED and not task.completed_date:
                        task.completed_date = datetime.utcnow().date()
                except KeyError: return error_response('Invalid status', None, 400)
            if 'priority' in data:
                try:
                    task.priority = TaskPriority[data['priority'].upper()]
                except KeyError: return error_response('Invalid priority', None, 400)
            if 'start_date' in data:
                task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data['start_date'] else None
            if 'due_date' in data:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data['due_date'] else None
            if 'estimated_hours' in data: task.estimated_hours = data['estimated_hours']
            if 'actual_hours' in data: task.actual_hours = data['actual_hours']
            if 'depends_on' in data: task.depends_on = data['depends_on'] or None

        # Employee can ONLY update status and actual_hours (progress reporting)
        elif is_assigned_employee:
            if 'status' in data:
                try:
                    new_status = TaskStatus[data['status'].upper()]
                    task.status = new_status
                    if new_status == TaskStatus.COMPLETED and not task.completed_date:
                        task.completed_date = datetime.utcnow().date()
                except KeyError: return error_response('Invalid status', None, 400)
            
            if 'actual_hours' in data:
                # Also update the assignment actual_hours
                assignment = Assignment.query.filter_by(task_id=task_id, user_id=int(current_user_id)).first()
                # Simplified: update task total actual hours. Ideally should update assignment too.
                # Assuming task.actual_hours is sum of assignments.
                # For simplicity, we allow direct update of task actual_hours or just add to it.
                # But typically employees log their OWN hours. 
                # Let's stick to updating task.actual_hours for now as per request "submit progress".
                task.actual_hours = data['actual_hours']

        db.session.commit()
        
        return success_response(
            'Task updated successfully',
            {'task': task.to_dict()},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update task: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def delete_task(task_id, current_user):
    """Delete task"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return error_response('Task not found', None, 404)
        
        # Check permissions
        project = Project.query.get(task.project_id)
        if current_user.role == UserRole.TEAM_LEADER and project.manager_id != current_user.id:
            return error_response('You do not have permission to delete this task', None, 403)
        
        # Check for dependent tasks
        dependent_tasks = Task.query.filter_by(depends_on=task_id).count()
        if dependent_tasks > 0:
            return error_response(
                f'Cannot delete task with {dependent_tasks} dependent tasks',
                None,
                400
            )
        
        db.session.delete(task)
        db.session.commit()
        
        return success_response('Task deleted successfully', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete task: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>/assign', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def assign_task(task_id, current_user):
    """
    Assign task to user(s)
    Body:
    {
        "user_id": 5,
        "assigned_hours": 10,
        "notes": "Optional notes"
    }
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return error_response('Task not found', None, 404)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'assigned_hours']
        error = validate_required_fields(data, required_fields)
        if error:
            return error_response(error, None, 400)
        
        # Validate user exists
        user = User.query.get(data['user_id'])
        if not user:
            return error_response('User not found', None, 404)
        
        if not user.is_active:
            return error_response('User is not active', None, 400)
        
        # Check if already assigned
        existing = Assignment.query.filter_by(
            user_id=data['user_id'],
            task_id=task_id
        ).first()
        
        if existing:
            return error_response('User is already assigned to this task', None, 409)
        
        # Check user workload
        current_workload = Assignment.get_user_workload(data['user_id'])
        if current_workload + data['assigned_hours'] > user.weekly_capacity:
            return error_response(
                'User is overloaded',
                {
                    'current_workload': current_workload,
                    'weekly_capacity': user.weekly_capacity,
                    'requested_hours': data['assigned_hours'],
                    'available_capacity': user.weekly_capacity - current_workload
                },
                400
            )
        
        # Create assignment
        assignment = Assignment(
            user_id=data['user_id'],
            task_id=task_id,
            assigned_by=current_user.id,
            assigned_hours=data['assigned_hours'],
            status=AssignmentStatus.PENDING,
            notes=data.get('notes')
        )
        
        db.session.add(assignment)
        # Create notification
        create_notification(
            user_id=data['user_id'],
            notif_type=NotificationType.TASK_ASSIGNED,
            message=f"You have been assigned to task: {task.title}",
            data={'task_id': task.id, 'project_id': task.project_id}
        )
        
        db.session.commit()
        
        return success_response(
            'Task assigned successfully',
            {'assignment': assignment.to_dict(include_user=True, include_task=True)},
            201
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to assign task: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>/unassign/<int:user_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def unassign_task(task_id, user_id, current_user):
    """Unassign task from user"""
    try:
        assignment = Assignment.query.filter_by(
            task_id=task_id,
            user_id=user_id
        ).first()
        
        if not assignment:
            return error_response('Assignment not found', None, 404)
        
        db.session.delete(assignment)
        db.session.commit()
        
        return success_response('Task unassigned successfully', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to unassign task: {str(e)}', None, 500)


@tasks_bp.route('/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    """
    Add comment to task
    Body:
    {
        "content": "Comment text",
        "parent_id": 5  // Optional: for replies
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.get(task_id)
        if not task:
            return error_response('Task not found', None, 404)
        
        data = request.get_json()
        
        if not data or 'content' not in data or not data['content'].strip():
            return error_response('Comment content is required', None, 400)
        
        # Validate parent comment if provided
        parent_id = data.get('parent_id')
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment or parent_comment.task_id != task_id:
                return error_response('Invalid parent comment', None, 400)
        
        # Create comment
        comment = Comment(
            content=data['content'].strip(),
            task_id=task_id,
            user_id=int(current_user_id),
            parent_id=parent_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return success_response(
            'Comment added successfully',
            {'comment': comment.to_dict()},
            201
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to add comment: {str(e)}', None, 500)


@tasks_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update comment"""
    try:
        current_user_id = get_jwt_identity()
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return error_response('Comment not found', None, 404)
        
        # Only author can update
        if comment.user_id != int(current_user_id):
            return error_response('You can only update your own comments', None, 403)
        
        data = request.get_json()
        
        if not data or 'content' not in data or not data['content'].strip():
            return error_response('Comment content is required', None, 400)
        
        comment.content = data['content'].strip()
        comment.is_edited = True
        
        db.session.commit()
        
        return success_response(
            'Comment updated successfully',
            {'comment': comment.to_dict()},
            200
        )
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update comment: {str(e)}', None, 500)


@tasks_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete comment"""
    try:
        current_user_id = get_jwt_identity()
        # Convert to int since JWT identity is stored as string but user ID is integer
        current_user = User.query.get(int(current_user_id)) if current_user_id else None
        
        comment = Comment.query.get(comment_id)
        if not comment:
            return error_response('Comment not found', None, 404)
        
        # Only author or admin can delete
        if comment.user_id != int(current_user_id) and current_user.role != UserRole.ADMIN:
            return error_response('You do not have permission to delete this comment', None, 403)
        
        db.session.delete(comment)
        db.session.commit()
        
        return success_response('Comment deleted successfully', None, 200)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete comment: {str(e)}', None, 500)


@tasks_bp.route('/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    """Get tasks assigned to current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all assignments for current user
        assignments = Assignment.query.filter_by(user_id=int(current_user_id)).all()
        
        tasks_data = []
        for assignment in assignments:
            task_dict = assignment.task.to_dict()
            task_dict['assignment'] = {
                'assigned_hours': assignment.assigned_hours,
                'actual_hours': assignment.actual_hours,
                'status': assignment.status.value,
                'hours_remaining': assignment.hours_remaining
            }
            tasks_data.append(task_dict)
        
        return success_response(
            'Your tasks retrieved successfully',
            {'tasks': tasks_data, 'total': len(tasks_data)},
            200
        )
    
    except Exception as e:
        return error_response(f'Failed to get tasks: {str(e)}', None, 500)