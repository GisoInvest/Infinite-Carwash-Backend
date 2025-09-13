from src.models.user import db
from datetime import datetime
import uuid

class ServiceNotification(db.Model):
    __tablename__ = 'service_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.String(50), unique=True, nullable=False)
    subscription_id = db.Column(db.String(50), db.ForeignKey('customer_subscriptions.subscription_id'), nullable=False)
    
    # Notification details
    notification_type = db.Column(db.String(30), nullable=False)  # 'service_reminder', 'service_confirmed', 'service_completed'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Scheduling
    scheduled_send_time = db.Column(db.DateTime, nullable=False)
    actual_send_time = db.Column(db.DateTime)
    
    # Delivery channels
    send_email = db.Column(db.Boolean, default=True)
    send_sms = db.Column(db.Boolean, default=True)
    send_push = db.Column(db.Boolean, default=True)
    send_website = db.Column(db.Boolean, default=True)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # 'pending', 'sent', 'delivered', 'failed'
    delivery_status = db.Column(db.JSON)  # Track delivery status for each channel
    
    # Related service
    service_date = db.Column(db.Date)
    service_time = db.Column(db.String(10))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_notification_id():
        return f"NOT_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
    
    def mark_as_sent(self, channel, success=True, error_message=None):
        """Mark notification as sent for a specific channel"""
        if not self.delivery_status:
            self.delivery_status = {}
        
        self.delivery_status[channel] = {
            'sent': success,
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_message if not success else None
        }
        
        # Update overall status
        if success and not self.actual_send_time:
            self.actual_send_time = datetime.utcnow()
            self.status = 'sent'
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'subscription_id': self.subscription_id,
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'scheduled_send_time': self.scheduled_send_time.isoformat() if self.scheduled_send_time else None,
            'actual_send_time': self.actual_send_time.isoformat() if self.actual_send_time else None,
            'send_email': self.send_email,
            'send_sms': self.send_sms,
            'send_push': self.send_push,
            'send_website': self.send_website,
            'status': self.status,
            'delivery_status': self.delivery_status,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'service_time': self.service_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LiveNotification(db.Model):
    __tablename__ = 'live_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Target audience
    target_type = db.Column(db.String(20), nullable=False)  # 'customer', 'admin', 'all'
    target_id = db.Column(db.String(50))  # customer_id or admin_id
    
    # Notification content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(30), nullable=False)  # 'info', 'warning', 'success', 'error'
    priority = db.Column(db.String(10), default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Display settings
    show_on_website = db.Column(db.Boolean, default=True)
    show_on_mobile = db.Column(db.Boolean, default=True)
    auto_dismiss = db.Column(db.Boolean, default=False)
    dismiss_after_seconds = db.Column(db.Integer, default=30)
    
    # Action buttons
    action_buttons = db.Column(db.JSON)  # [{'text': 'View Details', 'action': 'view_subscription', 'url': '/subscription/123'}]
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'dismissed', 'expired'
    read_at = db.Column(db.DateTime)
    dismissed_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_notification_id():
        return f"LIVE_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read_at = datetime.utcnow()
        self.status = 'read'
    
    def dismiss(self):
        """Dismiss notification"""
        self.dismissed_at = datetime.utcnow()
        self.status = 'dismissed'
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'show_on_website': self.show_on_website,
            'show_on_mobile': self.show_on_mobile,
            'auto_dismiss': self.auto_dismiss,
            'dismiss_after_seconds': self.dismiss_after_seconds,
            'action_buttons': self.action_buttons,
            'status': self.status,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

