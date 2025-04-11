from datetime import datetime
from backend.models import db

class Webhook(db.Model):
    __tablename__ = 'webhooks'
    
    id = db.Column(db.String(36), primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    target_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, inactive, error
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)
    last_error = db.Column(db.Text)
    
    # العلاقات
    creator = db.relationship('User', backref='webhooks')
    
    def to_dict(self):
        """تحويل بيانات الـ webhook إلى قاموس"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'target_url': self.target_url,
            'description': self.description,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'last_error': self.last_error
        }
