from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import csv
import io
import json
from app import db
from app.models import Project, Task, User, Assignment
from app.models.user import UserRole
from app.utils.decorators import role_required
from app.utils.responses import success_response, error_response

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/projects/export', methods=['GET'])
@jwt_required()
def export_projects():
    """
    Export projects to CSV
    Query params:
    - status: Filter by status
    - format: csv or json (default: csv)
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Get query parameters
        status_filter = request.args.get('status')
        export_format = request.args.get('format', 'csv')
        
        # Build query
        query = Project.query
        
        # Role-based filtering
        if current_user.role == UserRole.TEAM_LEADER:
            query = query.filter_by(manager_id=current_user_id)
        
        # Apply filters
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        projects = query.all()
        
        if export_format == 'json':
            # JSON Export
            data = [project.to_dict() for project in projects]
            
            json_str = json.dumps(data, indent=2)
            json_bytes = io.BytesIO(json_str.encode('utf-8'))
            
            return send_file(
                json_bytes,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'projects_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        else:
            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Code', 'Title', 'Status', 'Priority',
                'Start Date', 'End Date', 'Budget', 'Estimated Hours',
                'Completion %', 'Is Overdue', 'Manager', 'Created At'
            ])
            
            # Write data
            for project in projects:
                manager_name = project.manager.full_name if project.manager else 'N/A'
                writer.writerow([
                    project.id,
                    project.code,
                    project.title,
                    project.status.value,
                    project.priority.value,
                    project.start_date.isoformat() if project.start_date else '',
                    project.end_date.isoformat() if project.end_date else '',
                    project.budget or '',
                    project.estimated_hours or '',
                    project.completion_percentage,
                    'Yes' if project.is_overdue else 'No',
                    manager_name,
                    project.created_at.isoformat() if project.created_at else ''
                ])
            
            # Convert to bytes
            output.seek(0)
            csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
            
            return send_file(
                csv_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'projects_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            )
    
    except Exception as e:
        return error_response(f'Failed to export projects: {str(e)}', None, 500)


@reports_bp.route('/tasks/export', methods=['GET'])
@jwt_required()
def export_tasks():
    """
    Export tasks to CSV
    Query params:
    - project_id: Filter by project
    - status: Filter by status
    - format: csv or json (default: csv)
    """
    try:
        # Get query parameters
        project_id = request.args.get('project_id', type=int)
        status_filter = request.args.get('status')
        export_format = request.args.get('format', 'csv')
        
        # Build query
        query = Task.query
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        tasks = query.all()
        
        if export_format == 'json':
            # JSON Export
            data = [task.to_dict(include_assignments=True) for task in tasks]
            
            json_str = json.dumps(data, indent=2)
            json_bytes = io.BytesIO(json_str.encode('utf-8'))
            
            return send_file(
                json_bytes,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'tasks_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        else:
            # CSV Export
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'Task Number', 'Title', 'Project', 'Status', 'Priority',
                'Start Date', 'Due Date', 'Estimated Hours', 'Actual Hours',
                'Assigned To', 'Is Overdue', 'Created At'
            ])
            
            # Write data
            for task in tasks:
                project_code = task.project.code if task.project else 'N/A'
                assigned_users = ', '.join([u.full_name for u in task.assigned_users])
                
                writer.writerow([
                    task.id,
                    task.task_number,
                    task.title,
                    project_code,
                    task.status.value,
                    task.priority.value,
                    task.start_date.isoformat() if task.start_date else '',
                    task.due_date.isoformat() if task.due_date else '',
                    task.estimated_hours or '',
                    task.actual_hours or '',
                    assigned_users or 'Unassigned',
                    'Yes' if task.is_overdue else 'No',
                    task.created_at.isoformat() if task.created_at else ''
                ])
            
            output.seek(0)
            csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
            
            return send_file(
                csv_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'tasks_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            )
    
    except Exception as e:
        return error_response(f'Failed to export tasks: {str(e)}', None, 500)


@reports_bp.route('/team/workload-report', methods=['GET'])
@role_required(UserRole.ADMIN, UserRole.TEAM_LEADER)
def export_team_workload(current_user):
    """
    Generate team workload report
    """
    try:
        export_format = request.args.get('format', 'csv')
        
        users = User.query.filter_by(is_active=True, role=UserRole.EMPLOYEE).all()
        
        workload_data = []
        for user in users:
            current_workload = Assignment.get_user_workload(user.id)
            available = user.weekly_capacity - current_workload
            utilization = round((current_workload / user.weekly_capacity * 100), 2) if user.weekly_capacity > 0 else 0
            
            active_tasks = Assignment.query.join(Task).filter(
                Assignment.user_id == user.id,
                Task.status.in_(['todo', 'in_progress', 'review'])
            ).count()
            
            workload_data.append({
                'name': user.full_name,
                'email': user.email,
                'weekly_capacity': user.weekly_capacity,
                'current_workload': current_workload,
                'available_capacity': available,
                'utilization_percentage': utilization,
                'active_tasks': active_tasks,
                'status': 'Overloaded' if current_workload > user.weekly_capacity else 'Available' if available > 10 else 'At Capacity'
            })
        
        if export_format == 'json':
            json_str = json.dumps(workload_data, indent=2)
            json_bytes = io.BytesIO(json_str.encode('utf-8'))
            
            return send_file(
                json_bytes,
                mimetype='application/json',
                as_attachment=True,
                download_name=f'team_workload_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        else:
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow([
                'Name', 'Email', 'Weekly Capacity', 'Current Workload',
                'Available Capacity', 'Utilization %', 'Active Tasks', 'Status'
            ])
            
            for data in workload_data:
                writer.writerow([
                    data['name'],
                    data['email'],
                    data['weekly_capacity'],
                    data['current_workload'],
                    data['available_capacity'],
                    data['utilization_percentage'],
                    data['active_tasks'],
                    data['status']
                ])
            
            output.seek(0)
            csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
            
            return send_file(
                csv_bytes,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'team_workload_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            )
    
    except Exception as e:
        return error_response(f'Failed to generate report: {str(e)}', None, 500)


@reports_bp.route('/project/<int:project_id>/summary', methods=['GET'])
@jwt_required()
def export_project_summary(project_id):
    """
    Generate detailed project summary report
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return error_response('Project not found', None, 404)
        
        # Get project stats
        tasks = project.tasks.all()
        
        summary = {
            'project': project.to_dict(),
            'statistics': {
                'total_tasks': len(tasks),
                'completed': len([t for t in tasks if t.status.value == 'completed']),
                'in_progress': len([t for t in tasks if t.status.value == 'in_progress']),
                'todo': len([t for t in tasks if t.status.value == 'todo']),
                'overdue': len([t for t in tasks if t.is_overdue])
            },
            'tasks': [task.to_dict(include_assignments=True) for task in tasks]
        }
        
        json_str = json.dumps(summary, indent=2)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'project_{project.code}_summary_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
        )
    
    except Exception as e:
        return error_response(f'Failed to generate summary: {str(e)}', None, 500)