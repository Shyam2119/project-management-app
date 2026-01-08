from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from app import db
from app.models import User, Project, Task, Assignment, Comment
from app.models.user import UserRole
from app.models.project import ProjectStatus, ProjectPriority
from app.models.task import TaskStatus, TaskPriority
from app.utils.responses import success_response, error_response

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """
    Get overall system analytics
    Provides high-level statistics for dashboard
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
        
        # Check if user has a company (for scoped queries)
        if not current_user.company_id:
            return error_response('User is not associated with a company', None, 403)
        
        # Basic counts (scoped to company)
        total_users = User.query.filter_by(
            is_active=True, 
            is_bot=False,
            company_id=current_user.company_id
        ).count()
        total_projects = Project.query.filter_by(company_id=current_user.company_id).count()
        total_tasks = Task.query.join(Project).filter(
            Project.company_id == current_user.company_id
        ).count()
        
        # Project statistics (scoped to company)
        active_projects = Project.query.filter_by(
            status=ProjectStatus.IN_PROGRESS,
            company_id=current_user.company_id
        ).count()
        completed_projects = Project.query.filter_by(
            status=ProjectStatus.COMPLETED,
            company_id=current_user.company_id
        ).count()
        overdue_projects = Project.query.filter(
            and_(
                Project.company_id == current_user.company_id,
                Project.end_date < datetime.utcnow().date(),
                Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED])
            )
        ).count()
        
        # Task statistics (scoped to company)
        completed_tasks = Task.query.join(Project).filter(
            and_(
                Project.company_id == current_user.company_id,
                Task.status == TaskStatus.COMPLETED
            )
        ).count()
        in_progress_tasks = Task.query.join(Project).filter(
            and_(
                Project.company_id == current_user.company_id,
                Task.status == TaskStatus.IN_PROGRESS
            )
        ).count()
        overdue_tasks = Task.query.join(Project).filter(
            and_(
                Task.due_date < datetime.utcnow().date(),
                Task.status != TaskStatus.COMPLETED
            )
        ).count()
        
        # Hours statistics
        total_estimated_hours = db.session.query(func.sum(Task.estimated_hours)).scalar() or 0
        total_actual_hours = db.session.query(func.sum(Task.actual_hours)).scalar() or 0
        
        # Team utilization
        total_capacity = db.session.query(func.sum(User.weekly_capacity)).filter_by(is_active=True).scalar() or 0
        total_workload = db.session.query(func.sum(Assignment.assigned_hours)).join(Task).filter(
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW])
        ).scalar() or 0
        
        utilization_rate = round((total_workload / total_capacity * 100), 2) if total_capacity > 0 else 0
        
        overview = {
            'users': {
                'total': total_users,
                'admins': User.query.filter_by(
                    role=UserRole.ADMIN, 
                    is_active=True,
                    company_id=current_user.company_id
                ).count(),
                'managers': User.query.filter_by(
                    role=UserRole.TEAM_LEADER, 
                    is_active=True,
                    company_id=current_user.company_id
                ).count(),
                'employees': User.query.filter_by(
                    role=UserRole.EMPLOYEE, 
                    is_active=True,
                    company_id=current_user.company_id
                ).count()
            },
            'projects': {
                'total': total_projects,
                'active': active_projects,
                'completed': completed_projects,
                'overdue': overdue_projects,
                'completion_rate': round((completed_projects / total_projects * 100), 2) if total_projects > 0 else 0
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'in_progress': in_progress_tasks,
                'overdue': overdue_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0
            },
            'hours': {
                'estimated': total_estimated_hours,
                'actual': total_actual_hours,
                'variance': total_actual_hours - total_estimated_hours,
                'efficiency': round((total_estimated_hours / total_actual_hours * 100), 2) if total_actual_hours > 0 else 0
            },
            'team': {
                'total_capacity': total_capacity,
                'current_workload': total_workload,
                'available_capacity': total_capacity - total_workload,
                'utilization_rate': utilization_rate
            }
        }
        
        return success_response('Overview analytics retrieved successfully', overview, 200)
    
    except Exception as e:
        return error_response(f'Failed to get overview: {str(e)}', None, 500)


@analytics_bp.route('/projects-by-status', methods=['GET'])
@jwt_required()
def get_projects_by_status():
    """Get project count grouped by status"""
    try:
        status_counts = db.session.query(
            Project.status,
            func.count(Project.id)
        ).group_by(Project.status).all()
        
        data = [
            {
                'status': status.value,
                'count': count
            }
            for status, count in status_counts
        ]
        
        return success_response('Project status distribution retrieved', {'data': data}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get projects by status: {str(e)}', None, 500)


@analytics_bp.route('/projects-by-priority', methods=['GET'])
@jwt_required()
def get_projects_by_priority():
    """Get project count grouped by priority"""
    try:
        priority_counts = db.session.query(
            Project.priority,
            func.count(Project.id)
        ).group_by(Project.priority).all()
        
        data = [
            {
                'priority': priority.value,
                'count': count
            }
            for priority, count in priority_counts
        ]
        
        return success_response('Project priority distribution retrieved', {'data': data}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get projects by priority: {str(e)}', None, 500)


@analytics_bp.route('/tasks-by-status', methods=['GET'])
@jwt_required()
def get_tasks_by_status():
    """Get task count grouped by status"""
    try:
        # Optional: filter by project
        project_id = request.args.get('project_id', type=int)
        
        query = db.session.query(
            Task.status,
            func.count(Task.id)
        )
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        status_counts = query.group_by(Task.status).all()
        
        data = [
            {
                'status': status.value,
                'count': count
            }
            for status, count in status_counts
        ]
        
        return success_response('Task status distribution retrieved', {'data': data}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get tasks by status: {str(e)}', None, 500)


@analytics_bp.route('/team-workload', methods=['GET'])
@jwt_required()
def get_team_workload():
    """
    Get workload distribution across team members
    Shows who is overloaded, available, etc.
    """
    try:
        users = User.query.filter_by(is_active=True, role=UserRole.EMPLOYEE).all()
        
        workload_data = []
        for user in users:
            current_workload = Assignment.get_user_workload(user.id)
            available = user.weekly_capacity - current_workload
            utilization = round((current_workload / user.weekly_capacity * 100), 2) if user.weekly_capacity > 0 else 0
            
            # Count active assignments
            active_assignments = Assignment.query.join(Task).filter(
                Assignment.user_id == user.id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW])
            ).count()
            
            workload_data.append({
                'user_id': user.id,
                'name': user.full_name,
                'email': user.email,
                'weekly_capacity': user.weekly_capacity,
                'current_workload': current_workload,
                'available_capacity': available,
                'utilization_percentage': utilization,
                'is_overloaded': current_workload > user.weekly_capacity,
                'active_tasks': active_assignments,
                'status': 'overloaded' if current_workload > user.weekly_capacity else 'available' if available > 10 else 'at_capacity'
            })
        
        # Sort by utilization (highest first)
        workload_data.sort(key=lambda x: x['utilization_percentage'], reverse=True)
        
        # Summary
        overloaded_count = len([w for w in workload_data if w['is_overloaded']])
        available_count = len([w for w in workload_data if w['available_capacity'] > 10])
        
        result = {
            'team_members': workload_data,
            'summary': {
                'total_members': len(workload_data),
                'overloaded': overloaded_count,
                'available': available_count,
                'at_capacity': len(workload_data) - overloaded_count - available_count
            }
        }
        
        return success_response('Team workload retrieved successfully', result, 200)
    
    except Exception as e:
        return error_response(f'Failed to get team workload: {str(e)}', None, 500)


@analytics_bp.route('/productivity-trends', methods=['GET'])
@jwt_required()
def get_productivity_trends():
    """
    Get productivity trends over time
    Query params:
    - days: Number of days to analyze (default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        # Tasks completed per day
        completed_tasks = db.session.query(
            func.date(Task.completed_date).label('date'),
            func.count(Task.id).label('count')
        ).filter(
            Task.completed_date >= start_date,
            Task.status == TaskStatus.COMPLETED
        ).group_by(func.date(Task.completed_date)).all()
        
        # Format data
        tasks_completed = [
            {
                'date': date.isoformat() if date else None,
                'count': count
            }
            for date, count in completed_tasks
        ]
        
        # Calculate average
        total_completed = sum([item['count'] for item in tasks_completed])
        avg_per_day = round(total_completed / days, 2) if days > 0 else 0
        
        result = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().date().isoformat(),
                'days': days
            },
            'tasks_completed': tasks_completed,
            'summary': {
                'total_completed': total_completed,
                'average_per_day': avg_per_day
            }
        }
        
        return success_response('Productivity trends retrieved successfully', result, 200)
    
    except Exception as e:
        return error_response(f'Failed to get productivity trends: {str(e)}', None, 500)


@analytics_bp.route('/upcoming-deadlines', methods=['GET'])
@jwt_required()
def get_upcoming_deadlines():
    """
    Get tasks with upcoming deadlines
    Query params:
    - days: Look ahead this many days (default: 7)
    """
    try:
        days = request.args.get('days', 7, type=int)
        end_date = datetime.utcnow().date() + timedelta(days=days)
        
        upcoming_tasks = Task.query.filter(
            and_(
                Task.due_date.isnot(None),
                Task.due_date <= end_date,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.REVIEW])
            )
        ).order_by(Task.due_date.asc()).all()
        
        # Group by days remaining
        critical = []  # 0-2 days
        warning = []   # 3-5 days
        upcoming = []  # 6+ days
        
        for task in upcoming_tasks:
            days_remaining = (task.due_date - datetime.utcnow().date()).days
            task_data = task.to_dict()
            task_data['days_remaining'] = days_remaining
            
            if days_remaining <= 2:
                critical.append(task_data)
            elif days_remaining <= 5:
                warning.append(task_data)
            else:
                upcoming.append(task_data)
        
        result = {
            'critical': critical,
            'warning': warning,
            'upcoming': upcoming,
            'total': len(upcoming_tasks)
        }
        
        return success_response('Upcoming deadlines retrieved successfully', result, 200)
    
    except Exception as e:
        return error_response(f'Failed to get upcoming deadlines: {str(e)}', None, 500)


@analytics_bp.route('/project-completion-forecast', methods=['GET'])
@jwt_required()
def get_project_completion_forecast():
    """
    Forecast project completion dates based on current progress
    """
    try:
        active_projects = Project.query.filter(
            Project.status.in_([ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS])
        ).all()
        
        forecasts = []
        for project in active_projects:
            completion_rate = project.completion_percentage
            
            if completion_rate > 0 and project.start_date:
                # Calculate days elapsed
                days_elapsed = (datetime.utcnow().date() - project.start_date).days
                
                if days_elapsed > 0:
                    # Forecast total days needed
                    total_days_forecast = (days_elapsed / completion_rate) * 100
                    remaining_days = total_days_forecast - days_elapsed
                    forecast_completion = datetime.utcnow().date() + timedelta(days=remaining_days)
                    
                    # Check if on track
                    on_track = forecast_completion <= project.end_date if project.end_date else True
                    
                    forecasts.append({
                        'project': project.to_dict(),
                        'forecast': {
                            'completion_date': forecast_completion.isoformat(),
                            'days_remaining': int(remaining_days),
                            'on_track': on_track,
                            'delay_days': (forecast_completion - project.end_date).days if project.end_date and not on_track else 0
                        }
                    })
        
        return success_response('Project completion forecast retrieved', {'projects': forecasts}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get forecast: {str(e)}', None, 500)


@analytics_bp.route('/top-performers', methods=['GET'])
@jwt_required()
def get_top_performers():
    """
    Get top performing team members based on completed tasks
    Query params:
    - limit: Number of users to return (default: 5)
    - period: Days to look back (default: 30)
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        period = request.args.get('period', 30, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=period)
        
        # Get completed tasks per user
        top_users = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            func.count(Task.id).label('completed_tasks')
        ).join(Assignment).join(Task).filter(
            Task.status == TaskStatus.COMPLETED,
            Task.completed_date >= start_date
        ).group_by(User.id).order_by(func.count(Task.id).desc()).limit(limit).all()
        
        performers = [
            {
                'user_id': user_id,
                'name': f"{first_name} {last_name}",
                'email': email,
                'completed_tasks': completed
            }
            for user_id, first_name, last_name, email, completed in top_users
        ]
        
        return success_response('Top performers retrieved successfully', {'performers': performers}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get top performers: {str(e)}', None, 500)


@analytics_bp.route('/activity-feed', methods=['GET'])
@jwt_required()
def get_activity_feed():
    """
    Get recent activity feed
    Shows recent tasks created, completed, comments, etc.
    Query params:
    - limit: Number of activities (default: 20)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        activities = []
        
        # Recent tasks created
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(limit).all()
        for task in recent_tasks:
            activities.append({
                'type': 'task_created',
                'timestamp': task.created_at.isoformat() if task.created_at else None,
                'task': task.to_dict(),
                'user': task.creator.to_dict() if task.creator else None
            })
        
        # Recent comments
        recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(limit).all()
        for comment in recent_comments:
            activities.append({
                'type': 'comment_added',
                'timestamp': comment.created_at.isoformat() if comment.created_at else None,
                'comment': comment.to_dict(),
                'task_id': comment.task_id
            })
        
        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return success_response(
            'Activity feed retrieved successfully',
            {'activities': activities[:limit]},
            200
        )
    
    except Exception as e:
        return error_response(f'Failed to get activity feed: {str(e)}', None, 500)