from app import db
from app.models import Notification, User
from app.models.notification import NotificationType

def create_notification(user_id, notif_type, message, data=None, title=None):
    """
    Create a notification considering user preferences.
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return None
            
        # Check preferences
        if not user.push_notifications:
            print(f"Skipping notification for user {user.email} (Push Disabled)")
            return None
            
        # Determine title if not provided
        if not title:
            title = notif_type.replace('_', ' ').title() if isinstance(notif_type, str) else notif_type.value.replace('_', ' ').title()

        # Extract related IDs from data
        task_id = data.get('task_id') if data else None
        project_id = data.get('project_id') if data else None
        comment_id = data.get('comment_id') if data else None

        # Create notification
        notif = Notification(
            user_id=user_id,
            type=notif_type,
            title=title,
            message=message,
            task_id=task_id,
            project_id=project_id,
            comment_id=comment_id,
            is_read=False
        )
        db.session.add(notif)
        db.session.flush() # Ensure ID is generated if needed, but committing is up to caller usually
        # Actually, let's keep it add-only. 
        # But wait, the original code had `return notif`.
        
        return notif
        
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None
