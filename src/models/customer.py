from src.models.user import db
from datetime import datetime
import uuid

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Personal Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Loyalty Program
    total_bookings = db.Column(db.Integer, default=0)
    completed_bookings = db.Column(db.Integer, default=0)
    loyalty_points = db.Column(db.Integer, default=0)
    
    # Rewards Status
    free_washes_earned = db.Column(db.Integer, default=0)
    free_washes_used = db.Column(db.Integer, default=0)
    discount_15_earned = db.Column(db.Integer, default=0)
    discount_15_used = db.Column(db.Integer, default=0)
    
    # Subscription Status
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_date = db.Column(db.DateTime, nullable=True)
    subscription_discount_code = db.Column(db.String(20), nullable=True)
    
    # Preferences
    preferred_vehicle_type = db.Column(db.String(50))
    preferred_service_location = db.Column(db.String(255))
    preferred_time_slot = db.Column(db.String(20))
    
    # Communication Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=True)
    marketing_emails = db.Column(db.Boolean, default=True)
    
    # Timestamps
    first_booking_date = db.Column(db.DateTime, nullable=True)
    last_booking_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='customer_record', lazy=True, 
                              foreign_keys='Booking.customer_email',
                              primaryjoin='Customer.email == foreign(Booking.customer_email)')
    
    def to_dict(self):
        """Convert customer object to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'personal_info': {
                'name': self.name,
                'email': self.email,
                'phone': self.phone
            },
            'loyalty_stats': {
                'total_bookings': self.total_bookings,
                'completed_bookings': self.completed_bookings,
                'loyalty_points': self.loyalty_points
            },
            'rewards': {
                'free_washes_earned': self.free_washes_earned,
                'free_washes_used': self.free_washes_used,
                'free_washes_available': self.free_washes_earned - self.free_washes_used,
                'discount_15_earned': self.discount_15_earned,
                'discount_15_used': self.discount_15_used,
                'discount_15_available': self.discount_15_earned - self.discount_15_used
            },
            'subscription': {
                'is_subscribed': self.is_subscribed,
                'subscription_date': self.subscription_date.isoformat() if self.subscription_date else None,
                'discount_code': self.subscription_discount_code
            },
            'preferences': {
                'vehicle_type': self.preferred_vehicle_type,
                'service_location': self.preferred_service_location,
                'time_slot': self.preferred_time_slot
            },
            'communication': {
                'email_notifications': self.email_notifications,
                'sms_notifications': self.sms_notifications,
                'marketing_emails': self.marketing_emails
            },
            'dates': {
                'first_booking': self.first_booking_date.isoformat() if self.first_booking_date else None,
                'last_booking': self.last_booking_date.isoformat() if self.last_booking_date else None,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
        }
    
    def check_loyalty_rewards(self):
        """Check if customer is eligible for new rewards"""
        rewards_earned = []
        
        # Check for free wash (every 5 completed bookings)
        if self.completed_bookings > 0 and self.completed_bookings % 5 == 0:
            if self.free_washes_earned < (self.completed_bookings // 5):
                self.free_washes_earned = self.completed_bookings // 5
                rewards_earned.append('free_wash')
        
        # Check for 15% discount (every 10 completed bookings)
        if self.completed_bookings > 0 and self.completed_bookings % 10 == 0:
            if self.discount_15_earned < (self.completed_bookings // 10):
                self.discount_15_earned = self.completed_bookings // 10
                rewards_earned.append('15_percent_discount')
        
        return rewards_earned
    
    def get_available_rewards(self):
        """Get list of available unused rewards"""
        rewards = []
        
        # Available free washes
        free_washes_available = self.free_washes_earned - self.free_washes_used
        if free_washes_available > 0:
            rewards.append({
                'type': 'free_wash',
                'count': free_washes_available,
                'description': f'{free_washes_available} Free Wash{"es" if free_washes_available > 1 else ""} Available'
            })
        
        # Available 15% discounts
        discounts_available = self.discount_15_earned - self.discount_15_used
        if discounts_available > 0:
            rewards.append({
                'type': '15_percent_discount',
                'count': discounts_available,
                'description': f'{discounts_available} 15% Discount{"s" if discounts_available > 1 else ""} Available'
            })
        
        return rewards
    
    @staticmethod
    def generate_customer_id():
        """Generate unique customer ID"""
        import random
        import string
        year = datetime.now().year
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"CUST-{year}-{random_part}"
    
    def __repr__(self):
        return f'<Customer {self.name} ({self.customer_id})>'

