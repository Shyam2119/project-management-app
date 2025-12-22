from datetime import datetime
from app import db

class ChatGroup(db.Model):
    __tablename__ = 'chat_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('GroupMember', backref='group', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None,
            'members_count': self.members.count()
        }

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # For DM
    group_id = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=True) # For Group Chat
    content = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(255), nullable=True)
    message_type = db.Column(db.String(20), default='text') # text, image, file, voice
    is_read = db.Column(db.Boolean, default=False)
    is_deleted_globally = db.Column(db.Boolean, default=False)
    deleted_by = db.Column(db.Text, default='') # Comma separated user IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def to_dict(self):
        sender_name = "Unknown User"
        if self.sender:
             sender_name = f"{self.sender.first_name} {self.sender.last_name}"
             
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': sender_name,
            'recipient_id': self.recipient_id,
            'group_id': self.group_id,
            'content': self.content,
            'attachment_url': self.attachment_url,
            'message_type': self.message_type,
            'is_read': self.is_read,
            'is_deleted_globally': self.is_deleted_globally,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None
        }
