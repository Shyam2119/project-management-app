from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.models.chat import Message
from datetime import datetime
from app import db

class AIService:
    @staticmethod
    def process_message(user_id, content):
        """
        Process a message from a user and generate a response from the AI Bot.
        """
        content = content.lower().strip()
        user = User.query.get(user_id)
        
        if not user:
            return "I'm sorry, I can't find your user profile."

        response = ""

        # Router Logic
        if "help" in content:
            response = AIService._get_help_message()
        
        elif "project" in content and ("status" in content or "progress" in content or "list" in content):
            response = AIService._get_project_progress(user)
            
        elif "task" in content and ("my" in content or "list" in content or "how many" in content):
             response = AIService._get_my_tasks(user)
             
        elif "report" in content:
            response = "To view detailed reports, please visit the 'Dashboard' section of the application."
            
        elif "how to use" in content:
            response = AIService._get_usage_guide()

        elif "hello" in content or "hi" in content:
            response = f"Hello {user.first_name}! I am your AI Assistant. Ask me about your 'tasks', 'projects', or help on 'how to use' the app."
            
        else:
            response = "I'm not sure I understand. Try asking about 'my tasks', 'project status', or 'help'."

        return response

    @staticmethod
    def _get_help_message():
        return (
            "Here's what I can do:\n"
            "- 'My tasks': List your pending assignments.\n"
            "- 'Project status': Summary of projects you lead.\n"
            "- 'How to use': General usage tips.\n"
            "- 'Report': Where to find analytics."
        )

    @staticmethod
    def _get_usage_guide():
        return (
            "To use the app:\n"
            "1. **Projects**: Create and manage projects.\n"
            "2. **Tasks**: Assign tasks to team members.\n"
            "3. **Chat**: Collaborate with your team.\n"
            "Navigate using the sidebar on the left."
        )

    @staticmethod
    def _get_project_progress(user):
        # Logic: Find projects where user is manager or creator
        projects = user.managed_projects.all()
        if not projects:
            return "You are not managing any projects currently."
        
        summary = "Here are your projects:\n"
        for p in projects:
            # simple progress calc (if not stored)
            total_tasks = p.tasks.count()
            completed = p.tasks.filter_by(status='completed').count()
            pct = int((completed / total_tasks * 100)) if total_tasks > 0 else 0
            summary += f"- **{p.name}**: {pct}% complete ({completed}/{total_tasks} tasks)\n"
            
        return summary

    @staticmethod
    def _get_my_tasks(user):
        tasks = Task.query.filter_by(assignee_id=user.id).filter(Task.status != 'completed').all()
        if not tasks:
            return "You have no pending tasks. Great job!"
        
        msg = f"You have {len(tasks)} pending tasks:\n"
        for t in tasks[:5]: # Limit to 5
            msg += f"- {t.title} (Due: {t.due_date.strftime('%Y-%m-%d') if t.due_date else 'No date'})\n"
        
        if len(tasks) > 5:
            msg += f"...and {len(tasks)-5} more."
            
        return msg
