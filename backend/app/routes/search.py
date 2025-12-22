from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models import Project, Task, User, Comment
from app.utils.responses import success_response, error_response

search_bp = Blueprint('search', __name__)


@search_bp.route('/global', methods=['GET'])
@jwt_required()
def global_search():
    """
    Global search across projects, tasks, and users
    Query params:
    - q: Search query (required)
    - types: Comma-separated list (projects,tasks,users) (optional)
    - limit: Results per type (default: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return error_response('Search query must be at least 2 characters', None, 400)
        
        types = request.args.get('types', 'projects,tasks,users').split(',')
        limit = request.args.get('limit', 10, type=int)
        
        search_pattern = f"%{query}%"
        results = {}
        
        # Search Projects
        if 'projects' in types:
            projects = Project.query.filter(
                db.or_(
                    Project.title.ilike(search_pattern),
                    Project.code.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            ).limit(limit).all()
            
            results['projects'] = [project.to_dict() for project in projects]
        
        # Search Tasks
        if 'tasks' in types:
            tasks = Task.query.filter(
                db.or_(
                    Task.title.ilike(search_pattern),
                    Task.task_number.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            ).limit(limit).all()
            
            results['tasks'] = [task.to_dict() for task in tasks]
        
        # Search Users
        if 'users' in types:
            users = User.query.filter(
                db.or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            ).limit(limit).all()
            
            results['users'] = [user.to_dict() for user in users]
        
        # Calculate total results
        total_results = sum(len(v) for v in results.values())
        
        return success_response(
            f'Found {total_results} results',
            {
                'query': query,
                'results': results,
                'total': total_results
            },
            200
        )
    
    except Exception as e:
        return error_response(f'Search failed: {str(e)}', None, 500)


@search_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def search_suggestions():
    """
    Get search suggestions based on partial input
    Query params:
    - q: Partial search query
    - type: projects, tasks, or users
    """
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'projects')
        
        if not query or len(query) < 2:
            return success_response('Suggestions', {'suggestions': []}, 200)
        
        search_pattern = f"%{query}%"
        suggestions = []
        
        if search_type == 'projects':
            projects = Project.query.filter(
                db.or_(
                    Project.title.ilike(search_pattern),
                    Project.code.ilike(search_pattern)
                )
            ).limit(5).all()
            
            suggestions = [
                {
                    'id': p.id,
                    'type': 'project',
                    'text': f"{p.code}: {p.title}",
                    'code': p.code
                }
                for p in projects
            ]
        
        elif search_type == 'tasks':
            tasks = Task.query.filter(
                db.or_(
                    Task.title.ilike(search_pattern),
                    Task.task_number.ilike(search_pattern)
                )
            ).limit(5).all()
            
            suggestions = [
                {
                    'id': t.id,
                    'type': 'task',
                    'text': f"{t.task_number}: {t.title}",
                    'task_number': t.task_number
                }
                for t in tasks
            ]
        
        elif search_type == 'users':
            users = User.query.filter(
                db.or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            ).limit(5).all()
            
            suggestions = [
                {
                    'id': u.id,
                    'type': 'user',
                    'text': f"{u.full_name} ({u.email})",
                    'email': u.email
                }
                for u in users
            ]
        
        return success_response('Suggestions retrieved', {'suggestions': suggestions}, 200)
    
    except Exception as e:
        return error_response(f'Failed to get suggestions: {str(e)}', None, 500)