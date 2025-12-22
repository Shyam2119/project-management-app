from app import db
from app.models import TimestampMixin

class Comment(db.Model, TimestampMixin):
    __tablename__ = 'comments'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Optional: Reply to another comment
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # Metadata
    is_edited = db.Column(db.Boolean, default=False)
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent_comment', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f'<Comment {self.id} on Task {self.task_id}>'
    
    def to_dict(self, include_replies=False):
        """Convert comment to dictionary"""
        data = {
            'id': self.id,
            'content': self.content,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else str(self.updated_at) if self.updated_at else None
        }
        
        # Include author info
        if self.author:
            data['author'] = {
                'id': self.author.id,
                'full_name': self.author.full_name,
                'email': self.author.email
            }
        
        # Include replies if requested
        if include_replies:
            data['replies'] = [reply.to_dict() for reply in self.replies.all()]
        
        return data