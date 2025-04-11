from datetime import datetime
from backend.models import db

# إضافة نماذج التسويق إلى ملف models.py

class MarketingCampaign(db.Model):
    __tablename__ = 'marketing_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, whatsapp, social, mixed
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='جديدة')  # جديدة، نشطة، متوقفة، مكتملة
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    messages = db.relationship('MarketingMessage', backref='campaign', lazy=True)
    creator = db.relationship('User', backref='marketing_campaigns', lazy=True)
    
    def to_dict(self):
        """تحويل بيانات الحملة التسويقية إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MarketingMessage(db.Model):
    __tablename__ = 'marketing_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # email, whatsapp, social
    campaign_id = db.Column(db.Integer, db.ForeignKey('marketing_campaigns.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    creator = db.relationship('User', backref='marketing_messages', lazy=True)
    
    def to_dict(self):
        """تحويل بيانات الرسالة التسويقية إلى قاموس"""
        return {
            'id': self.id,
            'subject': self.subject,
            'content': self.content,
            'type': self.type,
            'campaign_id': self.campaign_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MarketingDelivery(db.Model):
    __tablename__ = 'marketing_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('marketing_messages.id'))
    recipient = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, delivered, opened
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # العلاقات
    message = db.relationship('MarketingMessage', backref='deliveries', lazy=True)
    
    def to_dict(self):
        """تحويل بيانات التسليم التسويقي إلى قاموس"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'recipient': self.recipient,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'error_message': self.error_message
        }
